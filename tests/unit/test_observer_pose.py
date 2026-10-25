"""Observer-frame convention and end-to-end moving-observer tests."""

from __future__ import annotations

import numpy as np

from mosaic_perception.domain.models import Pose2D, SensorConfig, Vector2, wrap_angle
from mosaic_perception.evaluation.metrics import TrackingEvaluator
from mosaic_perception.experiment import run_method
from mosaic_perception.scenarios import resolve_scenario
from mosaic_perception.sensors import RangeBearingSensor
from mosaic_perception.simulation.world import SyntheticWorld


def test_sensor_reports_sensor_frame_measurements_exactly():
    world = SyntheticWorld(
        seed=7, duration=1.0, dt=0.1, num_objects=2, observer_trajectory="circle"
    )
    config = SensorConfig(
        sensor_id="r1",
        sensor_type="range_bearing",
        frame_rate=100.0,
        noise_std={"range": 0.0, "bearing": 0.0, "range_rate": 0.0},
        detection_probability=1.0,
        false_alarm_rate=0.0,
    )
    sensor = RangeBearingSensor(config, np.random.RandomState(1))
    state = world.get_world_state(3)
    observations = sensor.generate_observations(state, state.time)
    assert len(observations) == len(state.objects)

    observer_position = state.observer_pose.position.to_array()
    observer_velocity = state.observer_pose.velocity.to_array()
    heading = float(state.observer_pose.heading)
    for observation in observations:
        object_id = observation._true_object_id
        assert object_id is not None
        truth = state.objects[object_id]
        relative_position = truth.position.to_array() - observer_position
        relative_velocity = truth.velocity.to_array() - observer_velocity
        distance = float(np.linalg.norm(relative_position))
        expected_bearing = wrap_angle(
            float(np.arctan2(relative_position[1], relative_position[0])) - heading
        )
        expected_range_rate = float(np.dot(relative_position / distance, relative_velocity))
        assert np.isclose(observation.measurements["range"], distance, atol=1e-12)
        assert np.isclose(
            wrap_angle(observation.measurements["bearing"]), expected_bearing, atol=1e-12
        )
        assert np.isclose(observation.measurements["range_rate"], expected_range_rate, atol=1e-12)
        assert np.isclose(observation.observer_pose.heading, heading)
        assert np.allclose(observation.observer_pose.velocity.to_array(), observer_velocity)


def test_stationary_observer_nonzero_heading_round_trip():
    world = SyntheticWorld(seed=3, duration=0.0, dt=0.1, num_objects=1)
    state = world.get_world_state(0)
    truth = next(iter(state.objects.values()))
    state.observer_pose = Pose2D(
        position=Vector2(x=0.0, y=0.0),
        heading=np.pi / 2.0,
        velocity=Vector2(x=0.0, y=0.0),
    )
    config = SensorConfig(
        sensor_id="r1",
        sensor_type="range_bearing",
        noise_std={"range": 0.0, "bearing": 0.0, "range_rate": 0.0},
        detection_probability=1.0,
    )
    sensor = RangeBearingSensor(config, np.random.RandomState(2))
    observation = sensor.generate_observations(state, 0.0)[0]
    world_bearing = float(np.arctan2(truth.position.y, truth.position.x))
    assert np.isclose(
        wrap_angle(observation.measurements["bearing"]),
        wrap_angle(world_bearing - np.pi / 2.0),
        atol=1e-12,
    )


def test_end_to_end_moving_observer_accuracy():
    scenario = resolve_scenario("moving_observer", seed=4, duration=5.0)
    # Lower measurement noise than the default preset so the assertion is
    # about geometric/motion consistency rather than noise magnitude.
    range_config = scenario.sensors["range_bearing"].model_copy(
        update={
            "noise_std": {"range": 0.1, "bearing": 0.001, "range_rate": 0.02},
            "false_alarm_rate": 0.0,
            "detection_probability": 1.0,
        }
    )
    scenario.sensors["range_bearing"] = range_config
    scenario.sensors["vision_bearing"] = scenario.sensors["vision_bearing"].model_copy(
        update={
            "noise_std": {"bearing": 0.001},
            "false_alarm_rate": 0.0,
            "detection_probability": 1.0,
        }
    )
    record = run_method(scenario, "range_only", evaluator=TrackingEvaluator(match_gate_m=2.0))
    result = record.result
    assert result.position_rmse is not None
    assert result.position_rmse < 0.5
    assert result.recall is not None and result.recall > 0.8
    assert result.num_confirmed_tracks >= 1
    assert result.matched_samples > 100

    states = SyntheticWorld(
        seed=4,
        duration=5.0,
        dt=0.1,
        num_objects=3,
        observer_trajectory="circle",
    ).get_all_states()
    headings = {round(float(state.observer_pose.heading), 6) for state in states}
    assert len(headings) > 5
