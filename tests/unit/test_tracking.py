"""Basic tracker tests."""

from __future__ import annotations

import numpy as np

from mosaic_perception.domain.models import SensorConfig, TrackStatus
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
