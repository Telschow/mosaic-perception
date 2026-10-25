"""Tests for the deterministic synthetic world."""

from __future__ import annotations

import numpy as np
import pytest

from mosaic_perception.simulation.world import SyntheticWorld


def test_world_deterministic():
    world_a = SyntheticWorld(seed=42, duration=2.0, dt=0.1, num_objects=2)
    world_b = SyntheticWorld(seed=42, duration=2.0, dt=0.1, num_objects=2)
    states_a = world_a.get_all_states()
    states_b = world_b.get_all_states()
    assert len(states_a) == len(states_b)
    for state_a, state_b in zip(states_a, states_b, strict=True):
        for object_id in state_a.objects:
            assert state_a.objects[object_id].position.x == state_b.objects[object_id].position.x
            assert state_a.objects[object_id].position.y == state_b.objects[object_id].position.y


def test_world_has_ground_truth():
    world = SyntheticWorld(seed=123, duration=1.0, dt=0.1, num_objects=3)
    states = world.get_all_states()
    assert len(states[0].objects) == 3
    for obj in states[0].objects.values():
        assert obj.object_id is not None
        assert hasattr(obj, "position")
        assert hasattr(obj, "velocity")


def test_world_time_grid_is_exact():
    world = SyntheticWorld(seed=1, duration=1.0, dt=0.1, num_objects=1)
    assert len(world.time_steps) == 11
    assert world.time_steps[0] == 0.0
    assert np.isclose(world.time_steps[-1], 1.0)


def test_zero_duration_has_one_state():
    world = SyntheticWorld(seed=1, duration=0.0, dt=0.1, num_objects=1)
    assert len(world.get_all_states()) == 1


def test_object_velocity_matches_position_derivative():
    world = SyntheticWorld(seed=8, duration=1.0, dt=0.001, num_objects=3)
    states = world.get_all_states()
    index = len(states) // 2
    for object_id in states[index].objects:
        previous = states[index - 1].objects[object_id]
        following = states[index + 1].objects[object_id]
        position_derivative = (following.position.to_array() - previous.position.to_array()) / (
            2.0 * world.dt
        )
        assert np.allclose(
            states[index].objects[object_id].velocity.to_array(),
            position_derivative,
            atol=2e-3,
        )


def test_circle_observer_velocity_and_heading():
    world = SyntheticWorld(
        seed=2, duration=1.0, dt=0.001, num_objects=1, observer_trajectory="circle"
    )
    states = world.get_all_states()
    index = len(states) // 2
    previous = states[index - 1].observer_pose
    following = states[index + 1].observer_pose
    position_derivative = (following.position.to_array() - previous.position.to_array()) / (
        2.0 * world.dt
    )
    assert np.allclose(
        states[index].observer_pose.velocity.to_array(),
        position_derivative,
        atol=2e-3,
    )
    expected_heading = 0.2 * states[index].time + np.pi / 2.0
    assert np.isclose(
        np.sin(states[index].observer_pose.heading),
        np.sin(expected_heading),
        atol=1e-9,
    )
    assert np.isclose(
        np.cos(states[index].observer_pose.heading),
        np.cos(expected_heading),
        atol=1e-9,
    )


def test_unknown_observer_trajectory_raises():
    with pytest.raises(ValueError):
        SyntheticWorld(seed=1, duration=1.0, observer_trajectory="teleport")
