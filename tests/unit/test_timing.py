"""Tests for delivery timing, frame-rate honoring and lifecycle transitions."""

from __future__ import annotations

import numpy as np
import pytest

from mosaic_perception.domain.models import SensorConfig, TrackStatus
from mosaic_perception.sensors import RangeBearingSensor
from mosaic_perception.simulation.world import SyntheticWorld
from mosaic_perception.tracking import MultiSensorTracker
from tests.helpers import make_track, range_observation, vision_observation


def test_future_delivery_is_queued_not_dropped():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    observation = range_observation("delayed", capture_time=0.0, delivery_time=0.1)

    tracker.process_observations([observation], 0.0)
    assert tracker.pending_count() == 1
    assert tracker.statistics().delivered_observations == 0

    tracker.process_observations([], 0.1)
    assert tracker.pending_count() == 0
    statistics = tracker.statistics()
    assert statistics.delivered_observations == 1
    assert statistics.rejected_observations == 0
    assert statistics.age_samples == 1
    assert statistics.mean_age_of_information == pytest.approx(0.1)
    assert len(tracker.tracks) == 1
    assert observation.associated_track_id is not None


def test_observation_older_than_one_epoch_is_rejected_and_counted():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    observation = range_observation("stale", capture_time=0.0, delivery_time=0.2)

    tracker.process_observations([observation], 0.0)
    tracker.process_observations([], 0.1)
    assert tracker.pending_count() == 1

    tracker.process_observations([], 0.2)
    statistics = tracker.statistics()
    assert statistics.delivered_observations == 1
    assert statistics.rejected_observations == 1
    assert statistics.rejected_out_of_sequence == 1
    assert statistics.age_samples == 0
    assert statistics.mean_age_of_information is None
    assert tracker.tracks == {}
    assert observation.associated_track_id is None


def test_rejected_observation_does_not_count_as_hit_or_reset_misses():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    track = make_track()
    track.hits = 2
    track.misses = 3
    tracker.tracks[track.track_id] = track
    stale = range_observation("stale", capture_time=-1.0, delivery_time=0.0)

    tracker.process_observations([stale], 0.0)

    assert track.hits == 2
    assert track.misses == 4
    assert stale.associated_track_id is None
    assert tracker.rejected_out_of_sequence == 1
    assert tracker.rejection_log
    assert tracker.rejection_log[0][1].startswith("stale")


def test_failed_update_does_not_count_as_hit():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    track = make_track()
    track.hits = 1
    tracker.tracks[track.track_id] = track
    invalid = vision_observation("invalid-covariance")
    invalid.measurement_covariance = [[-1.0]]

    tracker.process_observations([invalid], 0.0)

    assert track.hits == 1
    assert track.misses == 1
    assert track.associated_observations == []
    assert tracker.rejected_invalid == 1
    assert invalid.associated_track_id is None


def test_sensor_frame_rate_is_honored():
    world = SyntheticWorld(seed=11, duration=2.0, dt=0.1, num_objects=1)
    config = SensorConfig(
        sensor_id="r1",
        sensor_type="range_bearing",
        frame_rate=5.0,
        noise_std={"range": 0.0, "bearing": 0.0, "range_rate": 0.0},
        detection_probability=1.0,
        false_alarm_rate=0.0,
    )
    sensor = RangeBearingSensor(config, np.random.RandomState(1))
    emitted = 0
    for state in world.get_all_states():
        if sensor.generate_observations(state, state.time):
            emitted += 1
    assert emitted == 11  # t = 0.0, 0.2, ..., 2.0


def test_tracker_rejects_non_monotonic_time():
    tracker = MultiSensorTracker(dt=0.1)
    tracker.process_observations([], 0.2)
    with pytest.raises(ValueError):
        tracker.process_observations([], 0.1)


def test_tracker_rejects_time_step_not_aligned_with_dt():
    tracker = MultiSensorTracker(dt=0.1)
    tracker.process_observations([], 0.0)
    with pytest.raises(ValueError):
        tracker.process_observations([], 0.15)


def test_track_lifecycle_confirm_coast_delete():
    tracker = MultiSensorTracker(
        dt=0.1,
        use_vision=False,
        min_hits_confirm=3,
        max_misses_coast=2,
        max_misses_delete=5,
    )
    track = make_track()
    tracker.tracks[track.track_id] = track

    for index, time in enumerate((0.0, 0.1, 0.2)):
        observation = range_observation(f"hit-{index}", capture_time=time, delivery_time=time)
        tracker.process_observations([observation], time)
    assert track.status.value == "confirmed"
    assert track.hits == 3

    tracker.process_observations([], 0.3)
    tracker.process_observations([], 0.4)
    assert track.status.value == "coasting"
    assert track.misses == 2

    for index, time in enumerate((0.5, 0.6, 0.7)):
        tracker.process_observations([], time)
        if index < 2:
            assert track.track_id in tracker.tracks
    assert track.track_id not in tracker.tracks
    deleted_snapshots = [
        snapshot
        for snapshot in tracker.snapshots
        if snapshot.track_id == track.track_id and snapshot.status.value == "deleted"
    ]
    assert len(deleted_snapshots) == 1


def test_ground_truth_identity_is_not_used_by_tracker():
    tracker = MultiSensorTracker(use_vision=False)
    track = make_track()
    tracker.tracks[track.track_id] = track
    observation = range_observation("truth-test")
    observation._true_object_id = "obj_intentionally_wrong"
    tracker.process_observations([observation], 0.0)
    assert observation.associated_track_id == track.track_id
    assert track.associated_observations == ["truth-test"]


def _delay_scenario(observer_velocity, target_velocity, bearing=0.0, range_rate=0.0):
    """Track at t=0, observation captured t=0, delivered t=0.05, processed t=0.1.

    Returns the tracker's resulting track plus the independently computed
    current-state update (the documented policy), the capture-time
    rewind/replay alternative and the wrong-pose alternative.
    """
    from mosaic_perception.domain.models import Pose2D, Vector2
    from mosaic_perception.tracking.ekf import ExtendedKalmanFilter

    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    track = make_track(velocity=target_velocity, status=TrackStatus.CONFIRMED)
    track.covariance = np.diag([0.25, 0.25, 0.01, 0.01]).tolist()
    tracker.tracks[track.track_id] = track
    x0, p0 = track.state_array().copy(), track.cov_array().copy()

    capture_pose = Pose2D(
        position=Vector2(x=0.0, y=0.0),
        heading=0.0,
        velocity=Vector2(x=observer_velocity[0], y=observer_velocity[1]),
    )
    delivery_pose = Pose2D(
        position=Vector2(x=observer_velocity[0] * 0.1, y=observer_velocity[1] * 0.1),
        heading=0.0,
        velocity=capture_pose.velocity,
    )
    obs = range_observation(
        "delayed",
        distance=10.0,
        bearing=bearing,
        range_rate=range_rate,
        capture_time=0.0,
        delivery_time=0.05,
    )
    obs.observer_pose = capture_pose
    z = np.array([10.0, bearing, range_rate])
    r = obs.get_measurement_cov()

    tracker.process_observations([obs], 0.0)
    assert tracker.pending_count() == 1  # queued, not dropped
    tracker.process_observations([], 0.1)
    assert tracker.pending_count() == 0

    ekf = ExtendedKalmanFilter(dt=0.1)

    def update(state, cov, pose):
        return ekf.update(
            state,
            cov,
            z,
            ekf.jacobian_range_bearing(state, pose),
            r,
            ekf.measurement_range_bearing(state, pose),
            angle_indices=(1,),
        )

    x_pred, p_pred = ekf.predict(x0, p0)
    current_state, _ = update(x_pred, p_pred, capture_pose)
    rewind_replay, _ = ekf.predict(*update(x0, p0, capture_pose))
    wrong_pose, _ = update(x_pred, p_pred, delivery_pose)
    return tracker, obs, track, current_state, rewind_replay, wrong_pose


def test_delayed_observation_is_applied_to_delivery_time_state_not_rewound():
    """Stationary observer, target at 5 m/s: age 0.1 s -> ~0.5 m state mismatch."""
    tracker, obs, track, current, rewind, _ = _delay_scenario(
        (0.0, 0.0), (5.0, 0.0), range_rate=5.0
    )

    assert obs.associated_track_id == track.track_id
    assert (track.hits, track.misses) == (1, 0)
    stats = tracker.statistics()
    assert stats.age_samples == 1
    assert stats.mean_age_of_information == pytest.approx(0.1)

    final = track.state_array()
    # Policy: update the delivery-time (t=0.1) prediction with the capture-time measurement.
    np.testing.assert_allclose(final, current, atol=1e-9)
    # Pinned: predicted x=10.5 is pulled halfway back toward the stale range of 10.
    assert final[0] == pytest.approx(10.249975, abs=1e-5)
    assert final[2] == pytest.approx(4.9995, abs=1e-4)
    # Capture-time rewind/replay would give x=10.5 (measurement agrees with the t=0 state).
    assert rewind[0] == pytest.approx(10.5, abs=1e-9)
    # Applied-state mismatch vs. replay is 0.250 m; the pre-update state/measurement
    # inconsistency is speed x age = 0.5 m (a scale, not a strict bound).
    assert final[0] - rewind[0] == pytest.approx(-0.250025, abs=1e-5)


def test_delayed_observation_with_moving_observer_uses_capture_time_pose():
    """Observer velocity (0, 2) and target velocity (0, 3): distinguishes three policies."""
    tracker, obs, track, current, rewind, wrong_pose = _delay_scenario((0.0, 2.0), (0.0, 3.0))

    assert obs.associated_track_id == track.track_id
    assert tracker.statistics().mean_age_of_information == pytest.approx(0.1)

    final = track.state_array()
    # Documented approximation: capture-time observer pose + delivery-time target state.
    np.testing.assert_allclose(final, current, atol=1e-9)
    # Pinned y: predicted 0.3 m is pulled to ~0.0115 m by the capture-time bearing of 0.
    assert final[1] == pytest.approx(0.011513, abs=1e-5)
    # Rewind/replay keeps y=0.3 (measurement is consistent with the t=0 state).
    assert rewind[1] == pytest.approx(0.3, abs=1e-9)
    # Using the delivery-time observer pose instead would give y~0.2038 (observer moved 0.2 m).
    assert wrong_pose[1] == pytest.approx(0.203829, abs=1e-5)


@pytest.mark.parametrize("acceleration", [0.0, 4.0, 20.0, 100.0])
def test_delayed_observation_of_accelerating_target_state_error(acceleration):
    """Delayed capture-time range measurement of a target accelerating laterally.

    Truth: starts at (10, 0) with velocity (5, 0) and acceleration (0, a). The
    observation is captured at t=0 (truth range 10, bearing 0, range rate 5) and
    processed at t=0.1 (age tau=0.1 s). The tracker is constant-velocity and
    unaware of the acceleration, so it predicts (10.5, 0) and then applies the
    capture-time measurement to that delivery-time state.

    Measured against truth at the processing epoch:
    - along-track error is -0.25 m for every acceleration: the stale measurement
      pulls the estimate back by about half of speed x age (0.5 m);
    - lateral position error is -a*tau^2/2 and lateral velocity error is -a*tau,
      i.e. the unmodelled acceleration adds to, and does not replace, the
      speed x age term. Neither is a strict bound.
    """
    tau = 0.1
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    track = make_track(velocity=(5.0, 0.0), status=TrackStatus.CONFIRMED)
    track.covariance = np.diag([0.25, 0.25, 0.01, 0.01]).tolist()
    tracker.tracks[track.track_id] = track
    obs = range_observation(
        "accelerating",
        distance=10.0,
        bearing=0.0,
        range_rate=5.0,
        capture_time=0.0,
        delivery_time=0.05,
    )

    tracker.process_observations([obs], 0.0)
    tracker.process_observations([], 0.1)

    assert obs.associated_track_id == track.track_id
    assert tracker.statistics().mean_age_of_information == pytest.approx(tau)
    truth = np.array([10.0 + 5.0 * tau, 0.5 * acceleration * tau**2, 5.0, acceleration * tau])
    error = track.state_array() - truth

    assert error[0] == pytest.approx(-0.25, abs=1e-4)
    assert error[1] == pytest.approx(-0.5 * acceleration * tau**2, abs=1e-6)
    assert error[3] == pytest.approx(-acceleration * tau, abs=1e-6)
    # Lateral position error a*tau^2/2 equals the 0.25 m along-track error at
    # a = 50 m/s^2, so acceleration only dominates beyond that for this age.
    assert (abs(error[1]) < abs(error[0])) == (acceleration < 50.0)
