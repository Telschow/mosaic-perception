"""Regression tests for per-group association, sequential fusion and gating."""

from __future__ import annotations

import numpy as np
import pytest

from mosaic_perception.domain.models import TrackStatus
from mosaic_perception.tracking import MultiSensorTracker
from tests.helpers import make_pose, make_track, range_observation, vision_observation


def test_one_track_receives_both_modalities_in_one_epoch():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    track = make_track()
    tracker.tracks[track.track_id] = track
    range_obs = range_observation()
    vision_obs = vision_observation()

    tracker.process_observations([range_obs, vision_obs], 0.0)

    assert range_obs.associated_track_id == track.track_id
    assert vision_obs.associated_track_id == track.track_id
    assert set(track.associated_observations) == {
        range_obs.observation_id,
        vision_obs.observation_id,
    }
    assert track.hits == 1
    assert track.misses == 0
    assert tracker.snapshots[-1].updated_this_epoch is True

    # Reproduce the sequential EKF updates independently to prove the stored
    # posterior reflects both measurements, not just the first one.
    state = np.array([10.0, 0.0, 0.0, 0.0])
    covariance = np.eye(4)
    pose = make_pose()
    predicted_range = tracker.ekf.measurement_range_bearing(state, pose)
    state, covariance = tracker.ekf.update(
        state,
        covariance,
        np.array([10.0, 0.0, 0.0]),
        tracker.ekf.jacobian_range_bearing(state, pose),
        np.array([[0.25, 0.0, 0.0], [0.0, 1e-4, 0.0], [0.0, 0.0, 0.01]]),
        predicted_range,
        angle_indices=(1,),
    )
    predicted_vision = tracker.ekf.measurement_bearing(state, pose)
    state, covariance = tracker.ekf.update(
        state,
        covariance,
        np.array([0.0]),
        tracker.ekf.jacobian_bearing(state, pose),
        np.array([[2.5e-5]]),
        predicted_vision,
        angle_indices=(0,),
    )
    assert np.allclose(track.state_array(), state)
    assert np.allclose(track.cov_array(), covariance)


def test_sequential_fusion_reduces_covariance_relative_to_range_only():
    fused_tracker = MultiSensorTracker(use_vision=True)
    fused_track = make_track("track_0000")
    fused_tracker.tracks[fused_track.track_id] = fused_track
    fused_tracker.process_observations(
        [range_observation("range-fused"), vision_observation("vision-fused")], 0.0
    )

    range_tracker = MultiSensorTracker(use_vision=False)
    range_track = make_track("track_0000")
    range_tracker.tracks[range_track.track_id] = range_track
    range_tracker.process_observations(
        [range_observation("range-only"), vision_observation("vision-ignored")], 0.0
    )

    assert np.trace(fused_track.cov_array()) < np.trace(range_track.cov_array())
    assert fused_track.associated_observations == [
        "range-fused",
        "vision-fused",
    ]
    assert range_track.associated_observations == ["range-only"]


def test_one_observation_cannot_update_two_tracks():
    tracker = MultiSensorTracker(use_vision=True)
    first = make_track("track_0000", (10.0, 0.0))
    second = make_track("track_0001", (10.2, 0.0))
    tracker.tracks[first.track_id] = first
    tracker.tracks[second.track_id] = second
    observation = range_observation("range-1", distance=10.1)

    tracker.process_observations([observation], 0.0)

    associated = [first, second]
    associated = [track for track in associated if track.associated_observations]
    assert len(associated) == 1
    assert len(observation.associated_track_id or "") == len("track_0000")
    assert sum(track.misses for track in (first, second)) == 1
    assert observation.associated_track_id in {first.track_id, second.track_id}


def test_range_only_mode_ignores_vision_completely():
    tracker = MultiSensorTracker(use_vision=False)
    track = make_track()
    tracker.tracks[track.track_id] = track
    initial_state = track.state_array().copy()
    initial_covariance = track.cov_array().copy()
    vision = vision_observation("vision-only")

    tracker.process_observations([vision], 0.0)

    assert vision.associated_track_id is None
    assert track.associated_observations == []
    assert track.hits == 0
    assert track.misses == 1
    assert np.allclose(track.state_array(), initial_state)
    assert np.allclose(track.cov_array(), initial_covariance)
    statistics = tracker.statistics()
    assert statistics.delivered_observations == 0
    assert statistics.rejected_observations == 0
    assert statistics.pending_observations == 0
    assert len(tracker.tracks) == 1


def test_vision_observation_does_not_initiate_a_track():
    tracker = MultiSensorTracker(use_vision=True)
    observation = vision_observation("vision-with-no-track")

    tracker.process_observations([observation], 0.0)

    assert tracker.tracks == {}
    assert observation.associated_track_id is None
    assert tracker.statistics().delivered_observations == 1
    assert tracker.statistics().rejected_observations == 0


def test_gated_false_vision_observation_does_not_update_track():
    tracker = MultiSensorTracker(use_vision=True)
    track = make_track()
    tracker.tracks[track.track_id] = track
    false_observation = vision_observation("vision-false", bearing=np.pi / 2.0)

    tracker.process_observations([false_observation], 0.0)

    assert false_observation.associated_track_id is None
    assert track.associated_observations == []
    assert track.misses == 1
    assert tracker.rejected_invalid == 0


def test_gated_false_range_observation_does_not_update_but_may_initiate():
    tracker = MultiSensorTracker(use_vision=True)
    track = make_track()
    tracker.tracks[track.track_id] = track
    false_observation = range_observation("range-false", distance=100.0, bearing=0.0)

    tracker.process_observations([false_observation], 0.0)

    assert track.associated_observations == []
    assert track.misses == 1
    # The gate rejected it from updating the existing track; a new tentative
    # track is the explicit, documented initiation policy for range detections.
    assert len(tracker.tracks) == 2
    assert false_observation.associated_track_id is not None
    assert false_observation.associated_track_id != track.track_id


def test_same_group_policy_assigns_one_observation_and_initiates_from_the_other():
    tracker = MultiSensorTracker(use_vision=False)
    track = make_track()
    tracker.tracks[track.track_id] = track
    close = range_observation("range-close", distance=10.0, bearing=0.0)
    farther = range_observation("range-farther", distance=10.2, bearing=0.02)

    tracker.process_observations([farther, close], 0.0)

    assert track.associated_observations == ["range-close"]
    assert close.associated_track_id == track.track_id
    assert farther.associated_track_id is not None
    assert farther.associated_track_id != track.track_id
    assert len(tracker.tracks) == 2


def test_association_requires_observer_pose():
    tracker = MultiSensorTracker(use_vision=False)
    track = make_track()
    tracker.tracks[track.track_id] = track
    observation = range_observation("range-no-pose")
    observation.observer_pose = None

    tracker.process_observations([observation], 0.0)

    assert observation.associated_track_id is None
    assert track.associated_observations == []
    assert track.misses == 1
    assert tracker.rejected_invalid == 1


def test_range_bearing_2d_gate_uses_two_dof():
    """2D range/bearing observation (no range_rate) must use 2-DOF chi2 gate."""
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    track = make_track(status=TrackStatus.CONFIRMED)
    track.state = [10.0, 0.0, 0.0, 0.0]
    # Very small state covariance so innovation covariance ≈ measurement covariance
    track.covariance = (np.eye(4) * 1e-8).tolist()
    tracker.tracks[track.track_id] = track

    # 2D observation: range=11.2, bearing=0.008
    # Residual ≈ (1.2, 0.008), covariance diag(0.25, 1e-4)
    # d^2 = 1.2^2/0.25 + 0.008^2/1e-4 = 5.76 + 0.64 = 6.40
    # 2-DOF 95% gate: chi2(2, 0.95) ≈ 5.991 -> should REJECT
    # 3-DOF 95% gate: chi2(3, 0.95) ≈ 7.815 -> would incorrectly ACCEPT
    obs = range_observation(
        "2d-obs", distance=11.2, bearing=0.008, capture_time=0.0, delivery_time=0.0
    )
    obs.measurements.pop("range_rate", None)
    obs.measurement_covariance = [[0.25, 0.0], [0.0, 1e-4]]

    initial_state = track.state_array().copy()
    initial_cov = track.cov_array().copy()

    tracker.process_observations([obs], 0.0)

    # Original track must be unchanged and receive a miss
    assert obs.associated_track_id != track.track_id
    assert np.allclose(track.state_array(), initial_state)
    assert np.allclose(track.cov_array(), initial_cov)
    assert track.hits == 0
    assert track.misses == 1
    # Observation initiates a new track (documented policy for range detections)
    assert obs.associated_track_id is not None
    assert obs.associated_track_id != track.track_id


def test_range_bearing_3d_gate_uses_three_dof():
    """3D range/bearing/range-rate observation must use 3-DOF chi2 gate."""
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    track = make_track(status=TrackStatus.CONFIRMED)
    track.state = [10.0, 0.0, 0.0, 0.0]
    track.covariance = (np.eye(4) * 1e-8).tolist()
    tracker.tracks[track.track_id] = track

    # 3D observation with d^2 ≈ 6.40 (same spatial residual, plus range_rate=0)
    # Should PASS the 3-DOF gate (7.815) but would fail 2-DOF (5.991)
    obs = range_observation(
        "3d-obs", distance=11.2, bearing=0.008, range_rate=0.0, capture_time=0.0, delivery_time=0.0
    )

    tracker.process_observations([obs], 0.0)

    # Should be associated to the original track
    assert obs.associated_track_id == track.track_id
    assert track.hits == 1
    assert track.misses == 0
    # State should be updated
    assert not np.allclose(track.state_array(), [10.0, 0.0, 0.0, 0.0])


def test_vision_bearing_1d_gate_uses_one_dof():
    """Vision bearing-only observation must use 1-DOF chi2 gate."""
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    track = make_track(status=TrackStatus.CONFIRMED)
    track.state = [10.0, 0.0, 0.0, 0.0]
    track.covariance = (np.eye(4) * 1e-8).tolist()
    tracker.tracks[track.track_id] = track

    # Vision observation with bearing residual ~0.05 rad
    # covariance = (0.005)^2 = 2.5e-5
    # d^2 = 0.05^2 / 2.5e-5 = 100
    # 1-DOF 95% gate: chi2(1, 0.95) ≈ 3.841 -> should REJECT
    obs = vision_observation("vision-far", bearing=0.05, capture_time=0.0, delivery_time=0.0)
    # Ensure covariance is small to make the test deterministic
    obs.measurement_covariance = [[2.5e-5]]

    initial_state = track.state_array().copy()
    initial_cov = track.cov_array().copy()

    tracker.process_observations([obs], 0.0)

    # Should be rejected
    assert obs.associated_track_id is None
    assert np.allclose(track.state_array(), initial_state)
    assert np.allclose(track.cov_array(), initial_cov)
    assert track.hits == 0
    assert track.misses == 1


def test_vision_bearing_1d_gate_accepts_within_gate():
    """Vision bearing-only observation within 1-DOF gate should be accepted."""
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    track = make_track(status=TrackStatus.CONFIRMED)
    track.state = [10.0, 0.0, 0.0, 0.0]
    track.covariance = (np.eye(4) * 1e-8).tolist()
    tracker.tracks[track.track_id] = track

    # Bearing residual ~0.005 rad, covariance = (0.005)^2 = 2.5e-5
    # d^2 = 0.005^2 / 2.5e-5 = 1.0 < 3.841 -> should ACCEPT
    obs = vision_observation("vision-near", bearing=0.005, capture_time=0.0, delivery_time=0.0)
    obs.measurement_covariance = [[2.5e-5]]

    tracker.process_observations([obs], 0.0)

    assert obs.associated_track_id == track.track_id
    assert track.hits == 1
    assert track.misses == 0


def _confirmed_track(track_id: str, position: tuple[float, float], position_var: float):
    track = make_track(track_id, position, status=TrackStatus.CONFIRMED)
    track.covariance = np.diag([position_var, position_var, 1e-6, 1e-6]).tolist()
    return track


def test_large_vision_bias_is_gate_rejected_without_touching_track():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    track = _confirmed_track("t0", (10.0, 0.0), 0.01)
    tracker.tracks[track.track_id] = track
    state_before = track.state_array().copy()
    tracker.record_vision_generated(1)

    # 0.12 rad bias: innovation variance ~ 1e-4 + 2.5e-5 -> d^2 ~ 115 >> 3.84
    obs = vision_observation("big", bearing=0.12)
    tracker.process_observations([obs], 0.0)

    stats = tracker.statistics()
    assert obs.associated_track_id is None
    assert np.allclose(track.state_array(), state_before)
    assert (stats.vision_generated, stats.vision_delivered) == (1, 1)
    assert stats.vision_gate_rejected == 1
    assert stats.vision_lost_competition == 0
    assert stats.vision_applied == 0
    assert track.hits == 0
    assert track.misses == 1


def test_within_gate_vision_bias_is_fused_and_biases_the_track():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    track = _confirmed_track("t0", (10.0, 0.0), 0.01)
    tracker.tracks[track.track_id] = track
    y_before = track.state_array()[1]
    tracker.record_vision_generated(1)

    # 0.015 rad bias: d^2 ~ 0.015^2 / 1.25e-4 = 1.8 < 3.84 -> accepted
    obs = vision_observation("small", bearing=0.015)
    tracker.process_observations([obs], 0.0)

    stats = tracker.statistics()
    assert obs.associated_track_id == "t0"
    assert stats.vision_applied == 1
    assert stats.vision_gate_rejected == 0
    assert track.hits == 1
    # The biased bearing pulls the estimate toward positive y.
    assert track.state_array()[1] > y_before + 1e-3


def test_vision_observation_loses_competition_is_not_counted_as_gate_rejection():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    tracker.tracks["t0"] = _confirmed_track("t0", (10.0, 0.0), 0.01)
    tracker.record_vision_generated(2)

    # Both observations are inside the gate of the single track; only one wins.
    obs_a = vision_observation("a", bearing=0.001)
    obs_b = vision_observation("b", bearing=0.004)
    tracker.process_observations([obs_a, obs_b], 0.0)

    stats = tracker.statistics()
    assert stats.vision_delivered == 2
    assert stats.vision_applied == 1
    assert stats.vision_lost_competition == 1
    assert stats.vision_gate_rejected == 0
    assert obs_a.associated_track_id == "t0"
    assert obs_b.associated_track_id is None


def test_cross_modal_association_prefers_matching_track_over_nearby_track():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    # Two range-initialized tracks 0.02 rad apart in bearing at 10 m.
    tracker.tracks["near_zero"] = _confirmed_track("near_zero", (10.0, 0.0), 1e-6)
    tracker.tracks["near_off"] = _confirmed_track("near_off", (10.0, 0.2), 1e-6)
    off_before = tracker.tracks["near_off"].state_array().copy()

    obs = vision_observation("v", bearing=0.0)
    tracker.process_observations([obs], 0.0)

    assert obs.associated_track_id == "near_zero"
    assert np.allclose(tracker.tracks["near_off"].state_array(), off_before)
    assert tracker.tracks["near_off"].hits == 0
    assert tracker.tracks["near_off"].misses == 1


def test_cross_modal_observation_not_forced_onto_wrong_track():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    tracker.tracks["near_off"] = _confirmed_track("near_off", (10.0, 0.2), 1e-6)
    tracker.record_vision_generated(1)

    obs = vision_observation("v", bearing=0.0)
    tracker.process_observations([obs], 0.0)

    assert obs.associated_track_id is None
    assert tracker.statistics().vision_gate_rejected == 1
    assert tracker.tracks["near_off"].hits == 0


def test_gate_lookup_has_no_dimensionless_fallback():
    import pytest

    from mosaic_perception.tracking.association import GatedHungarianAssociator

    associator = GatedHungarianAssociator()
    assert associator.gate_for("range_bearing", 2) == pytest.approx(5.9915, abs=1e-3)
    assert associator.gate_for("range_bearing", 3) == pytest.approx(7.8147, abs=1e-3)
    assert associator.gate_for("vision_bearing", 1) == pytest.approx(3.8415, abs=1e-3)
    with pytest.raises(ValueError):
        associator.gate_for("range_bearing", 1)
    with pytest.raises(ValueError):
        associator.gate_for("range_bearing", None)  # type: ignore[arg-type]


def test_tracker_records_nis_for_applied_updates():
    import numpy as np

    from mosaic_perception.tracking.ekf import ExtendedKalmanFilter

    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    track = _confirmed_track("t0", (10.0, 0.0), 0.01)
    tracker.tracks[track.track_id] = track
    state, cov = track.state_array().copy(), track.cov_array().copy()

    obs = vision_observation("v", bearing=0.004)
    tracker.process_observations([obs], 0.0)

    ekf = ExtendedKalmanFilter(dt=0.1)
    pose = obs.observer_pose
    residual, innovation_cov = ekf.innovation(
        state,
        cov,
        np.array([0.004]),
        ekf.measurement_bearing(state, pose),
        ekf.jacobian_bearing(state, pose),
        obs.get_measurement_cov(),
        (0,),
    )
    expected = float(residual @ np.linalg.solve(innovation_cov, residual))
    stats = tracker.statistics()
    assert stats.nis_updates == 1
    assert stats.nis_dof_sum == 1
    assert stats.nis_sum == pytest.approx(expected)


def test_rejected_observations_do_not_contribute_to_nis():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    tracker.tracks["t0"] = _confirmed_track("t0", (10.0, 0.0), 0.01)
    tracker.process_observations([vision_observation("far", bearing=0.12)], 0.0)
    stats = tracker.statistics()
    assert stats.nis_updates == 0 and stats.nis_sum == 0.0


# --- vision bias estimation (opt-in, issue #20) ---------------------------------------


def _bias_tracker(position_var=1e-6, **kwargs):
    tracker = MultiSensorTracker(dt=0.1, use_vision=True, bias_estimation=True, **kwargs)
    tracker.tracks["t0"] = _confirmed_track("t0", (10.0, 0.0), position_var)
    return tracker


def test_bias_estimation_is_off_by_default():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    assert tracker.vision_bias_estimate is None
    tracker.tracks["t0"] = _confirmed_track("t0", (10.0, 0.0), 1e-6)
    tracker.process_observations([vision_observation("v", bearing=0.004)], 0.0)
    assert tracker.vision_bias_estimate is None


def test_bias_estimate_stays_near_zero_for_unbiased_vision():
    tracker = _bias_tracker()
    for step in range(10):
        tracker.process_observations(
            [
                vision_observation(
                    f"v{step}", bearing=0.0, capture_time=0.1 * step, delivery_time=0.1 * step
                )
            ],
            0.1 * step,
        )
    assert abs(tracker.vision_bias_estimate) < 1e-4


def test_a_large_bias_is_gate_rejected_before_any_bias_can_be_learned():
    tracker = _bias_tracker()
    for step in range(5):
        tracker.process_observations(
            [
                vision_observation(
                    f"v{step}", bearing=0.12, capture_time=0.1 * step, delivery_time=0.1 * step
                )
            ],
            0.1 * step,
        )
    assert tracker.vision_bias_updates == 0
    assert tracker.vision_bias_estimate == 0.0
    assert tracker.statistics().vision_applied == 0


def test_association_applies_the_bearing_correction_before_gating():
    from mosaic_perception.tracking.association import GatedHungarianAssociator
    from mosaic_perception.tracking.ekf import ExtendedKalmanFilter

    associator = GatedHungarianAssociator()
    ekf = ExtendedKalmanFilter(dt=0.1)
    track = _confirmed_track("t0", (10.0, 0.0), 1e-6)
    biased = vision_observation("v", bearing=0.015)  # d^2 = 9 against a 3.84 gate
    assert associator.associate([track], [biased], ekf).matches == {}
    corrected = associator.associate([track], [biased], ekf, bearing_correction=0.015)
    assert list(corrected.matches) == ["t0"]


def test_bias_corrected_updates_use_the_corrected_bearing():
    tracker = _bias_tracker()
    tracker._bias = 0.012  # as if already learned
    tracker._bias_var = 1e-6
    tracker.process_observations([vision_observation("v", bearing=0.012)], 0.0)
    track = tracker.tracks["t0"]
    # The corrected bearing equals the track's bearing (0), so y barely moves.
    assert abs(track.state_array()[1]) < 1e-3


def _feed(tracker, bias, steps, anchor=True):
    """Stationary target at (10, 0); vision reports `bias` extra rad, range-bearing is unbiased."""
    for step in range(steps):
        t = 0.1 * step
        observations = [
            vision_observation(f"v{step}", bearing=bias, capture_time=t, delivery_time=t)
        ]
        if anchor:
            observations.append(
                range_observation(f"r{step}", 10.0, 0.0, 0.0, capture_time=t, delivery_time=t)
            )
        tracker.process_observations(observations, t)


def test_a_bias_the_gate_rejects_is_never_learned():
    # Against a tight track a 0.02 rad bias has d^2 ~ 16 > 3.84, so it is never applied.
    tracker = _bias_tracker(position_var=0.01)
    _feed(tracker, 0.02, 20)
    assert tracker.vision_bias_updates == 0
    assert tracker.vision_bias_estimate == 0.0


def test_bias_estimate_converges_to_a_gate_passing_bias_using_the_range_bearing_anchor():
    # The measurement is (vision bearing - contemporaneous range-bearing bearing), which does
    # not depend on the track state, so the estimate converges to the injected bias.
    tracker = _bias_tracker(position_var=0.01)
    _feed(tracker, 0.012, 10)
    assert tracker.vision_bias_estimate == pytest.approx(0.012, abs=2e-4)
    assert tracker.vision_bias_updates == 10


def test_bias_estimate_stays_at_zero_for_unbiased_vision():
    tracker = _bias_tracker(position_var=0.01)
    _feed(tracker, 0.0, 20)
    assert abs(tracker.vision_bias_estimate) < 1e-9


def test_bias_is_not_learned_without_a_contemporaneous_range_bearing_observation():
    tracker = _bias_tracker(position_var=0.01)
    _feed(tracker, 0.012, 5, anchor=False)
    assert tracker.vision_bias_updates == 0
    assert tracker.vision_bias_estimate == 0.0
    assert tracker.statistics().vision_applied == 5  # the observations are still fused


def test_bias_is_not_learned_when_the_range_bearing_observation_is_from_another_time():
    tracker = _bias_tracker(position_var=0.01)
    tracker.process_observations([], 0.0)
    for step in range(1, 6):
        t = 0.1 * step
        tracker.process_observations(
            [
                vision_observation(f"v{step}", bearing=0.012, capture_time=t, delivery_time=t),
                # captured 0.03 s earlier but delivered in the same epoch: not contemporaneous
                range_observation(
                    f"r{step}", 10.0, 0.0, 0.0, capture_time=t - 0.03, delivery_time=t
                ),
            ],
            t,
        )
    assert tracker.vision_bias_updates == 0


def test_the_estimate_does_not_depend_on_what_the_track_state_does():
    # A track that absorbed the biased bearing (anchored only weakly) must not stall learning:
    # compare a tight range-bearing weight with the loose default.
    tight = _bias_tracker(position_var=1e-3)
    loose = _bias_tracker(position_var=0.5)
    _feed(tight, 0.010, 12)
    _feed(loose, 0.010, 12)
    assert tight.vision_bias_estimate == pytest.approx(0.010, abs=3e-4)
    assert loose.vision_bias_estimate == pytest.approx(0.010, abs=3e-4)


def test_gating_and_updating_use_one_bias_correction_for_the_whole_vision_group():
    tracker = _bias_tracker(position_var=0.01)
    tracker.tracks["t1"] = _confirmed_track("t1", (10.0, 3.0), 0.01)
    seen = []
    original = tracker._update_state

    def spy(state, covariance, observation, bias_correction=0.0):
        if observation.measurement_group() == "vision_bearing":
            seen.append(bias_correction)
        return original(state, covariance, observation, bias_correction)

    tracker._update_state = spy
    bearing_t1 = float(np.arctan2(3.0, 10.0))
    tracker.process_observations(
        [
            range_observation("r0", 10.0, 0.0, 0.0),
            vision_observation("v0", bearing=0.01),
            vision_observation("v1", bearing=bearing_t1 + 0.01),
        ],
        0.0,
    )
    assert len(seen) == 2
    assert seen[0] == seen[1]


def test_bias_correction_wraps_a_bearing_near_pi():
    from mosaic_perception.tracking.association import GatedHungarianAssociator
    from mosaic_perception.tracking.ekf import ExtendedKalmanFilter

    track = _confirmed_track("t0", (-10.0, 0.0), 0.01)  # bearing +pi
    observation = vision_observation("v", bearing=float(np.pi) - 0.001)
    result = GatedHungarianAssociator().associate(
        [track], [observation], ExtendedKalmanFilter(dt=0.1), bearing_correction=-0.002
    )
    assert list(result.matches) == ["t0"]


def test_previous_posteriors_are_evicted_when_a_track_is_deleted():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False, delayed_update="retrodiction")
    tracker.tracks["gone"] = make_track("gone", status=TrackStatus.TENTATIVE)
    for step in range(12):
        tracker.process_observations([], 0.1 * step)
    assert "gone" not in tracker.tracks
    assert "gone" not in tracker._prev_posterior
