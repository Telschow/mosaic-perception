"""Tests for tracking."""

import numpy as np
from mosaic_perception.simulation.world import SyntheticWorld
from mosaic_perception.sensors import RangeBearingSensor
from mosaic_perception.domain.models import SensorConfig
from mosaic_perception.tracking import MultiSensorTracker


def test_range_only_tracking():
    w = SyntheticWorld(seed=42, duration=2.0, dt=0.1, num_objects=2)
    config = SensorConfig(
        sensor_id="range1",
        sensor_type="range_bearing",
        frame_rate=10.0,
        noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
        detection_probability=1.0,
    )
    rng = np.random.RandomState(123)
    sensor = RangeBearingSensor(config, rng)
    
    tracker = MultiSensorTracker(dt=0.1, use_vision=False)
    
    states = w.get_all_states()
    for i, world_state in enumerate(states):
        obs = sensor.generate_observations(world_state, world_state.time)
        # Strip true object ids
        for o in obs:
            o._true_object_id = None
        tracks = tracker.process_observations(obs, world_state.time)
    
    # Should have some tracks
    assert len(tracks) > 0
