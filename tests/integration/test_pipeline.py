"""Integration tests for full pipeline."""

import numpy as np

from mosaic_perception.domain.models import SensorConfig
from mosaic_perception.evaluation.metrics import TrackingEvaluator
from mosaic_perception.sensors import RangeBearingSensor, VisionBearingSensor
from mosaic_perception.simulation.world import SyntheticWorld
from mosaic_perception.tracking import MultiSensorTracker


def test_nominal_deterministic_run():
    seed = 42
    world = SyntheticWorld(seed=seed, duration=5.0, dt=0.1, num_objects=3)
    rng_sensor = np.random.RandomState(seed + 1000)
    range_config = SensorConfig(
        sensor_id="range1",
        sensor_type="range_bearing",
        frame_rate=10.0,
        noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
        detection_probability=0.95,
        false_alarm_rate=0.01,
    )
    range_sensor = RangeBearingSensor(range_config, rng_sensor)
    vision_config = SensorConfig(
        sensor_id="vision1",
        sensor_type="vision_bearing",
        frame_rate=10.0,
        noise_std={"bearing": 0.005},
        detection_probability=0.9,
        false_alarm_rate=0.02,
    )
    VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))

    states = world.get_all_states()
    evaluator = TrackingEvaluator()

    # Range only
    tracker_range = MultiSensorTracker(dt=0.1, use_vision=False)
    for world_state in states:
        obs = range_sensor.generate_observations(world_state, world_state.time)
        for o in obs:
            o._true_object_id = None
        obs_pos = world_state.observer_pose.position.to_array()
        tracker_range.process_observations(obs, world_state.time, sensor_pos=obs_pos)
    result_range = evaluator.evaluate(tracker_range.tracks, states, "nominal", seed, "range_only")
    assert result_range.scenario_name == "nominal"
    assert result_range.method_name == "range_only"

    # Fused
    tracker_fused = MultiSensorTracker(dt=0.1, use_vision=True)
    rng_sensor2 = np.random.RandomState(seed + 1000)
    range_sensor2 = RangeBearingSensor(range_config, rng_sensor2)
    vision_sensor2 = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))
    for world_state in states:
        obs_range = range_sensor2.generate_observations(world_state, world_state.time)
        obs_vision = vision_sensor2.generate_observations(world_state, world_state.time)
        obs = obs_range + obs_vision
        for o in obs:
            o._true_object_id = None
        obs_pos = world_state.observer_pose.position.to_array()
        tracker_fused.process_observations(obs, world_state.time, sensor_pos=obs_pos)
    result_fused = evaluator.evaluate(tracker_fused.tracks, states, "nominal", seed, "fused")
    assert result_fused.method_name == "fused"


def test_repeatability_same_seed():
    seed = 7

    def run_once():
        world = SyntheticWorld(seed=seed, duration=3.0, dt=0.1, num_objects=2)
        rng_sensor = np.random.RandomState(seed + 1000)
        range_config = SensorConfig(
            sensor_id="range1",
            sensor_type="range_bearing",
            frame_rate=10.0,
            noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
            detection_probability=0.95,
            false_alarm_rate=0.01,
        )
        range_sensor = RangeBearingSensor(range_config, rng_sensor)
        states = world.get_all_states()
        tracker = MultiSensorTracker(dt=0.1, use_vision=False)
        for world_state in states:
            obs = range_sensor.generate_observations(world_state, world_state.time)
            for o in obs:
                o._true_object_id = None
            obs_pos = world_state.observer_pose.position.to_array()
            tracker.process_observations(obs, world_state.time, sensor_pos=obs_pos)
        evaluator = TrackingEvaluator()
        return evaluator.evaluate(tracker.tracks, states, "nominal", seed, "range_only")

    r1 = run_once()
    r2 = run_once()
    # Metrics should be consistent (allowing for float precision)
    if r1.position_rmse is not None and r2.position_rmse is not None:
        assert abs(r1.position_rmse - r2.position_rmse) < 1e-6
