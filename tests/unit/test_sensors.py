"""Tests for sensor models and their reported metadata."""

from __future__ import annotations

import numpy as np

from mosaic_perception.domain.models import CoordinateFrame, SensorConfig, wrap_angle
from mosaic_perception.sensors import RangeBearingSensor, VisionBearingSensor
from mosaic_perception.simulation.world import SyntheticWorld


def range_config(**overrides) -> SensorConfig:
    values = {
        "sensor_id": "range1",
        "sensor_type": "range_bearing",
        "frame_rate": 10.0,
        "noise_std": {"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
        "detection_probability": 1.0,
        "false_alarm_rate": 0.0,
    }
    values.update(overrides)
    return SensorConfig(**values)


def vision_config(**overrides) -> SensorConfig:
    values = {
        "sensor_id": "vision1",
        "sensor_type": "vision_bearing",
        "frame_rate": 10.0,
        "noise_std": {"bearing": 0.005},
        "detection_probability": 1.0,
        "false_alarm_rate": 0.0,
    }
    values.update(overrides)
    return SensorConfig(**values)


def test_range_bearing_sensor_reports_sensor_frame_and_covariance():
    world = SyntheticWorld(seed=42, duration=0.5, dt=0.1, num_objects=1)
    sensor = RangeBearingSensor(range_config(), np.random.RandomState(123))
    state = world.get_world_state(0)
    observations = sensor.generate_observations(state, state.time)
    assert len(observations) == 1
    observation = observations[0]
    assert observation.coordinate_frame == CoordinateFrame.SENSOR
    assert set(observation.measurements) == {"range", "bearing", "range_rate"}
    assert observation.measurement_covariance is not None
    assert observation.observer_pose is not None
    covariance = np.array(observation.measurement_covariance)
    assert np.allclose(covariance, np.diag([0.25, 1e-4, 0.01]))


def test_vision_bearing_sensor_reports_bearing_and_class_scores():
    world = SyntheticWorld(seed=42, duration=0.5, dt=0.1, num_objects=1)
    sensor = VisionBearingSensor(vision_config(), np.random.RandomState(123))
    state = world.get_world_state(0)
    observations = sensor.generate_observations(state, state.time)
    assert len(observations) == 1
    observation = observations[0]
    assert "bearing" in observation.measurements
    assert "range" not in observation.measurements
    assert observation.class_probs is not None
    assert abs(sum(observation.class_probs.values()) - 1.0) < 1e-9
    assert observation.detection_confidence is not None
    assert observation.observer_pose is not None


def test_reported_covariance_scale_does_not_change_measurement_noise():
    world = SyntheticWorld(seed=42, duration=0.5, dt=0.1, num_objects=1)
    state = world.get_world_state(0)
    normal = RangeBearingSensor(range_config(), np.random.RandomState(7))
    miscalibrated = RangeBearingSensor(
        range_config(reported_cov_scale=0.25), np.random.RandomState(7)
    )
    normal_observation = normal.generate_observations(state, 0.0)[0]
    miscalibrated_observation = miscalibrated.generate_observations(state, 0.0)[0]
    assert normal_observation.measurements == miscalibrated_observation.measurements
    normal_covariance = np.array(normal_observation.measurement_covariance)
    scaled_covariance = np.array(miscalibrated_observation.measurement_covariance)
    assert np.allclose(scaled_covariance, normal_covariance * 0.25)


def test_sensor_bias_is_applied_in_sensor_units():
    world = SyntheticWorld(seed=42, duration=0.0, dt=0.1, num_objects=1)
    state = world.get_world_state(0)
    unbiased = RangeBearingSensor(
        range_config(noise_std={"range": 0.0, "bearing": 0.0, "range_rate": 0.0}),
        np.random.RandomState(1),
    )
    biased = RangeBearingSensor(
        range_config(
            noise_std={"range": 0.0, "bearing": 0.0, "range_rate": 0.0},
            bias={"range": 1.5, "bearing": 0.1, "range_rate": 0.3},
        ),
        np.random.RandomState(1),
    )
    clean = unbiased.generate_observations(state, 0.0)[0].measurements
    offset = biased.generate_observations(state, 0.0)[0].measurements
    assert np.isclose(offset["range"], clean["range"] + 1.5)
    assert np.isclose(wrap_angle(offset["bearing"] - clean["bearing"]), 0.1)
    assert np.isclose(offset["range_rate"], clean["range_rate"] + 0.3)


def test_sensor_observation_ids_are_deterministic():
    world = SyntheticWorld(seed=5, duration=1.0, dt=0.1, num_objects=2)
    first = RangeBearingSensor(range_config(), np.random.RandomState(10))
    second = RangeBearingSensor(range_config(), np.random.RandomState(10))
    for state in world.get_all_states():
        first_ids = [
            observation.observation_id
            for observation in first.generate_observations(state, state.time)
        ]
        second_ids = [
            observation.observation_id
            for observation in second.generate_observations(state, state.time)
        ]
        assert first_ids == second_ids


def test_false_alarms_are_emitted_and_use_sensor_frame_metadata():
    world = SyntheticWorld(seed=9, duration=0.0, dt=0.1, num_objects=1)
    state = world.get_world_state(0)
    sensor = RangeBearingSensor(
        range_config(detection_probability=0.0, false_alarm_rate=3.0),
        np.random.RandomState(3),
    )
    observations = sensor.generate_observations(state, 0.0)
    assert observations
    for observation in observations:
        assert observation._true_object_id is None
        assert observation.observer_pose is not None
        assert observation.coordinate_frame == CoordinateFrame.SENSOR
