"""Tests for sensor models."""

import numpy as np
from mosaic_perception.simulation.world import SyntheticWorld
from mosaic_perception.sensors import RangeBearingSensor, VisionBearingSensor
from mosaic_perception.domain.models import SensorConfig


def test_range_bearing_sensor():
    w = SyntheticWorld(seed=42, duration=0.5, dt=0.1, num_objects=1)
    config = SensorConfig(
        sensor_id="range1",
        sensor_type="range_bearing",
        frame_rate=10.0,
        noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
        detection_probability=1.0,
    )
    rng = np.random.RandomState(123)
    sensor = RangeBearingSensor(config, rng)
    state = w.get_world_state(0)
    obs = sensor.generate_observations(state, state.time)
    assert len(obs) > 0
    assert "range" in obs[0].measurements
    assert "bearing" in obs[0].measurements
    assert obs[0].measurement_covariance is not None


def test_vision_bearing_sensor():
    w = SyntheticWorld(seed=42, duration=0.5, dt=0.1, num_objects=1)
    config = SensorConfig(
        sensor_id="vision1",
        sensor_type="vision_bearing",
        frame_rate=10.0,
        noise_std={"bearing": 0.005},
        detection_probability=1.0,
    )
    rng = np.random.RandomState(123)
    sensor = VisionBearingSensor(config, rng)
    state = w.get_world_state(0)
    obs = sensor.generate_observations(state, state.time)
    assert len(obs) > 0
    assert "bearing" in obs[0].measurements
    assert "range" not in obs[0].measurements
    assert obs[0].class_probs is not None
