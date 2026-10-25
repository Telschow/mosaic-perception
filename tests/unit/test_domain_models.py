"""Tests for domain models."""

from mosaic_perception.domain.models import (
    CoordinateFrame,
    ObjectState,
    SensorObservation,
    Vector2,
    WorldState,
)


def test_sensor_observation_creation():
    obs = SensorObservation(
        observation_id="test1",
        sensor_id="range1",
        sensor_type="range_bearing",
        capture_time=1.0,
        delivery_time=1.05,
        measurement_model="range_bearing_nonlinear",
        measurements={"range": 10.0, "bearing": 0.5},
    )
    assert obs.observation_id == "test1"
    assert abs(obs.age_of_information() - 0.05) < 1e-10
    assert obs.coordinate_frame == CoordinateFrame.SENSOR


def test_world_state_separation():
    """Ground truth must be separate from estimator inputs."""
    obj = ObjectState(
        object_id="obj1",
        position=Vector2(x=1.0, y=2.0),
        velocity=Vector2(x=0.5, y=0.0),
    )
    ws = WorldState(time=1.0, objects={"obj1": obj})
    assert ws.objects["obj1"].object_id == "obj1"
    # Ground truth should not be accessible via observation
    obs = SensorObservation(
        observation_id="test1",
        sensor_id="s1",
        sensor_type="test",
        capture_time=1.0,
        delivery_time=1.0,
        measurement_model="test",
        measurements={},
    )
    assert obs._true_object_id is None
