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


def _positions_at(world, step):
    state = world.get_world_state(step)
    return {object_id: obj.position.to_array() for object_id, obj in state.objects.items()}


def test_crossing_layout_brings_targets_within_the_matching_gate_at_mid_run():
    import numpy as np

    from mosaic_perception.simulation.world import SyntheticWorld

    world = SyntheticWorld(seed=3, duration=10.0, dt=0.1, num_objects=3, target_layout="crossing")
    positions = _positions_at(world, 50)  # t = 5.0 = duration / 2
    ids = sorted(positions)
    for i, first in enumerate(ids):
        for j, second in enumerate(ids):
            if j > i:
                separation = float(np.linalg.norm(positions[first] - positions[second]))
                assert separation == pytest.approx(0.5 * (j - i), abs=1e-9)
    # ... and the targets are far apart at the start and end of the run.
    start = _positions_at(world, 0)
    spread_start = max(
        float(np.linalg.norm(start[a] - start[b])) for a in ids for b in ids if a < b
    )
    assert spread_start > 8.0


def test_crossing_layout_uses_constant_velocity_with_distinct_headings():
    import numpy as np

    from mosaic_perception.simulation.world import SyntheticWorld

    world = SyntheticWorld(seed=3, duration=10.0, dt=0.1, num_objects=3, target_layout="crossing")
    headings = []
    for object_id in sorted(world.object_trajectories):
        states = world.object_trajectories[object_id]
        velocities = np.array([s.velocity.to_array() for s in states])
        assert np.allclose(velocities, velocities[0])  # constant velocity
        assert np.linalg.norm(velocities[0]) == pytest.approx(2.0)
        headings.append(float(np.arctan2(velocities[0][1], velocities[0][0])))
    assert len({round(h, 6) for h in headings}) == 3


def test_crossing_layout_is_deterministic_and_seed_dependent():
    from mosaic_perception.simulation.world import SyntheticWorld

    def first_position(seed):
        world = SyntheticWorld(
            seed=seed, duration=4.0, dt=0.1, num_objects=2, target_layout="crossing"
        )
        return tuple(_positions_at(world, 0)["obj_000"])

    assert first_position(1) == first_position(1)
    assert first_position(1) != first_position(2)


def test_random_layout_is_unchanged_by_the_layout_option():
    from mosaic_perception.simulation.world import SyntheticWorld

    default = SyntheticWorld(seed=5, duration=2.0, dt=0.1, num_objects=3)
    explicit = SyntheticWorld(seed=5, duration=2.0, dt=0.1, num_objects=3, target_layout="random")
    for step in (0, 10, 20):
        assert _positions_at(default, step).keys() == _positions_at(explicit, step).keys()
        for key, value in _positions_at(default, step).items():
            assert tuple(value) == tuple(_positions_at(explicit, step)[key])


def test_unknown_layout_is_rejected():
    from mosaic_perception.simulation.world import SyntheticWorld

    with pytest.raises(ValueError):
        SyntheticWorld(seed=1, target_layout="spiral")
