"""Tests for domain contracts and validation."""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from mosaic_perception.domain.models import (
    CoordinateFrame,
    ObjectState,
    Pose2D,
    SensorConfig,
    SensorObservation,
    Vector2,
    WorldState,
    wrap_angle,
)


def test_sensor_observation_creation():
    obs = SensorObservation(
        observation_id="test1",
        sensor_id="range1",
        sensor_type="range_bearing",
        capture_time=1.0,
        delivery_time=1.05,
        measurement_model="range_bearing_sensor_frame",
        measurements={"range": 10.0, "bearing": 0.5},
    )
    assert obs.observation_id == "test1"
    assert abs(obs.age_of_information() - 0.05) < 1e-10
    assert obs.coordinate_frame == CoordinateFrame.SENSOR
    assert obs.measurement_group() == "range_bearing"


def test_measurement_group_distinguishes_vision():
    obs = SensorObservation(
        observation_id="test2",
        sensor_id="vision1",
        sensor_type="vision_bearing",
        capture_time=1.0,
        delivery_time=1.0,
        measurement_model="bearing_sensor_frame",
        measurements={"bearing": 0.1},
    )
    assert obs.measurement_group() == "vision_bearing"


def test_measurement_group_rejects_unknown_measurements():
    obs = SensorObservation(
        observation_id="test3",
        sensor_id="unknown",
        sensor_type="unknown",
        capture_time=1.0,
        delivery_time=1.0,
        measurement_model="unknown",
        measurements={"intensity": 1.0},
    )
    with pytest.raises(ValueError):
        obs.measurement_group()


def test_world_state_separation():
    """Ground truth must be separate from estimator inputs."""
    obj = ObjectState(
        object_id="obj1",
        position=Vector2(x=1.0, y=2.0),
        velocity=Vector2(x=0.5, y=0.0),
    )
    ws = WorldState(time=1.0, objects={"obj1": obj})
    assert ws.objects["obj1"].object_id == "obj1"
    obs = SensorObservation(
        observation_id="test1",
        sensor_id="s1",
        sensor_type="test",
        capture_time=1.0,
        delivery_time=1.0,
        measurement_model="test",
        measurements={"bearing": 0.0},
    )
    assert obs._true_object_id is None


def test_pose_carries_observer_velocity():
    pose = Pose2D(
        position=Vector2(x=1.0, y=2.0),
        heading=0.5,
        velocity=Vector2(x=3.0, y=-1.0),
    )
    assert np.allclose(pose.to_array(), [1.0, 2.0, 0.5])
    assert np.allclose(pose.velocity.to_array(), [3.0, -1.0])


def test_wrap_angle_is_bounded():
    for angle in (-10.0, -np.pi, -0.1, 0.0, 0.1, np.pi, 10.0):
        wrapped = wrap_angle(angle)
        assert -np.pi - 1e-12 <= wrapped <= np.pi + 1e-12
        assert abs(wrap_angle(wrapped) - wrapped) < 1e-12


def test_sensor_config_validates_frame_rate_and_covariance_scale():
    with pytest.raises(ValidationError):
        SensorConfig(sensor_id="s", sensor_type="t", frame_rate=0.0)
    with pytest.raises(ValidationError):
        SensorConfig(sensor_id="s", sensor_type="t", reported_cov_scale=0.0)
    with pytest.raises(ValidationError):
        SensorConfig(sensor_id="s", sensor_type="t", detection_probability=1.5)
