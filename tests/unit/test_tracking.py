"""Basic tracker tests."""

from __future__ import annotations

import numpy as np

from mosaic_perception.domain.models import (
    Pose2D,
    SensorConfig,
    SensorObservation,
    TrackStatus,
)
from mosaic_perception.sensors import RangeBearingSensor
from mosaic_perception.simulation.world import SyntheticWorld
from mosaic_perception.tracking import MultiSensorTracker


def test_range_only_tracking_confirms_tracks_and_records_snapshots():
    world = SyntheticWorld(seed=42, duration=2.0, dt=0.1, num_objects=2)
    config = SensorConfig(
        sensor_id="range1",
        sensor_type="range_bearing",
        frame_rate=10.0,
        noise_std={"range": 0.2, "bearing": 0.005, "range_rate": 0.05},
        detection_probability=1.0,
        false_alarm_rate=0.0,
    )
    sensor = RangeBearingSensor(config, np.random.RandomState(123))
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)

    returned = {}
    for world_state in world.get_all_states():
        observations = sensor.generate_observations(world_state, world_state.time)
        for observation in observations:
            observation._true_object_id = None
        returned = tracker.process_observations(observations, world_state.time)

    confirmed = [track for track in returned.values() if track.status == TrackStatus.CONFIRMED]
    assert confirmed
    assert tracker.snapshots
    assert len({snapshot.time for snapshot in tracker.snapshots}) == 21
    assert all(
        len(snapshot.state) == 4 and len(snapshot.covariance) == 4 for snapshot in tracker.snapshots
    )
    assert tracker.statistics().delivered_observations > 0


def _vision_obs(obs_id, class_probs, t=0.1):
    return SensorObservation(
        observation_id=obs_id,
        sensor_id="cam1",
        sensor_type="vision_bearing",
        capture_time=t,
        delivery_time=t,
        measurement_model="vision_bearing",
        measurements={"bearing": 0.1},
        measurement_covariance=[[0.01]],
        class_probs=class_probs,
        observer_pose=Pose2D(),
    )


def test_unknown_class_name_is_rejected_and_epoch_finishes():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    tracker.process_observations([], 0.0)
    tracker.process_observations([_vision_obs("v1", {"bogus": 1.0})], 0.1)

    stats = tracker.statistics()
    assert stats.rejected_invalid == 1
    assert stats.rejected_observations == 1
    assert tracker.rejection_log[-1][0] == "v1"
    assert tracker._last_time == 0.1


def test_duplicate_observation_id_mid_batch_is_rejected_not_raised():
    tracker = MultiSensorTracker(dt=0.1, use_vision=True)
    tracker.process_observations([], 0.0)
    batch = [_vision_obs("a", None), _vision_obs("b", None), _vision_obs("a", None)]
    tracker.process_observations(batch, 0.1)

    stats = tracker.statistics()
    assert stats.rejected_invalid == 1
    assert tracker.rejection_log[-1][0] == "a"
    assert stats.delivered_observations == 3
    assert tracker._last_time == 0.1


def _range_obs(obs_id, capture, delivery, rng=5.0):
    return SensorObservation(
        observation_id=obs_id,
        sensor_id="r1",
        sensor_type="range_bearing",
        capture_time=capture,
        delivery_time=delivery,
        measurement_model="range_bearing",
        measurements={"range": rng, "bearing": 0.1, "range_rate": 0.0},
        measurement_covariance=[[0.04, 0, 0], [0, 0.0001, 0], [0, 0, 0.01]],
        observer_pose=Pose2D(),
    )


def test_age_of_information_is_measured_from_capture_to_delivery():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    tracker.process_observations([], 0.0)
    tracker.process_observations([_range_obs("a", 0.0, 0.01)], 0.1)

    assert abs(tracker.statistics().mean_age_of_information - 0.01) < 1e-9


def test_staleness_uses_delivery_latency_not_processing_time():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    tracker.process_observations([], 1.0)
    tracker.process_observations([_range_obs("a", 0.99, 1.01)], 1.1)

    stats = tracker.statistics()
    assert stats.rejected_out_of_sequence == 0
    assert tracker.rejection_log == []


def test_genuinely_late_delivery_is_still_stale():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    tracker.process_observations([], 1.0)
    tracker.process_observations([_range_obs("a", 0.5, 1.1)], 1.1)

    assert tracker.statistics().rejected_out_of_sequence == 1


def _tracker_snapshot(tracker):
    return (
        {tid: (list(t.state), list(t.covariance), t.time) for tid, t in tracker.tracks.items()},
        tracker._last_time,
        dict(tracker._epoch_applied),
        list(tracker._pending),
        set(tracker._seen_observation_ids),
    )


def test_rejected_batch_leaves_tracker_unchanged_and_retry_succeeds():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    for step in range(4):
        tracker.process_observations([_range_obs(f"w{step}", 0.1 * step, 0.1 * step)], 0.1 * step)
    before = _tracker_snapshot(tracker)

    bad = _range_obs("z", 0.4, float("nan"))
    batch = [_range_obs("x", 0.4, 0.5), _range_obs("y", 0.4, 0.5), bad]
    try:
        tracker.process_observations(batch, 0.5)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
    assert _tracker_snapshot(tracker) == before

    batch[2] = _range_obs("z", 0.4, 0.5)
    tracker.process_observations(batch, 0.5)
    assert tracker.statistics().rejected_invalid == 0
    assert tracker._last_time == 0.5


def test_non_observation_item_rejects_whole_batch_atomically():
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    tracker.process_observations([], 0.0)
    before = _tracker_snapshot(tracker)
    try:
        tracker.process_observations([_range_obs("x", 0.1, 0.1), "oops"], 0.1)  # type: ignore[list-item]
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError")
    assert _tracker_snapshot(tracker) == before


def test_repeated_call_time_does_not_rerun_an_epoch():
    # A-F2 regression: replaying the same batch at a repeated time must not double-apply.
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    tracker.process_observations([], 0.0)
    tracker.process_observations([_range_obs("a", 0.1, 0.1)], 0.1)
    first = _tracker_snapshot(tracker)[0]
    tracker.process_observations([], 0.1)
    assert _tracker_snapshot(tracker)[0] == first
