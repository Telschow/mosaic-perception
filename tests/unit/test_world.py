"""Tests for synthetic world."""

from mosaic_perception.simulation.world import SyntheticWorld


def test_world_deterministic():
    w1 = SyntheticWorld(seed=42, duration=2.0, dt=0.1, num_objects=2)
    w2 = SyntheticWorld(seed=42, duration=2.0, dt=0.1, num_objects=2)
    states1 = w1.get_all_states()
    states2 = w2.get_all_states()
    assert len(states1) == len(states2)
    # Check first object position
    for s1, s2 in zip(states1, states2):
        for obj_id in s1.objects:
            assert s1.objects[obj_id].position.x == s2.objects[obj_id].position.x
            assert s1.objects[obj_id].position.y == s2.objects[obj_id].position.y


def test_world_has_ground_truth():
    w = SyntheticWorld(seed=123, duration=1.0, dt=0.1, num_objects=3)
    states = w.get_all_states()
    assert len(states[0].objects) == 3
    for obj in states[0].objects.values():
        assert obj.object_id is not None
        assert hasattr(obj, 'position')
        assert hasattr(obj, 'velocity')
