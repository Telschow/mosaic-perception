"""Tests for delivery timing, frame-rate honoring and lifecycle transitions."""

from __future__ import annotations

import numpy as np
import pytest

from mosaic_perception.domain.models import SensorConfig
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
