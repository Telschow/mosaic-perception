"""Regression tests for per-group association, sequential fusion and gating."""

from __future__ import annotations

import numpy as np

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
