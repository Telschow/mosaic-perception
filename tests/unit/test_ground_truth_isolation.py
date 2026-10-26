"""Ground truth must never reach the estimator.

Ground-truth-only fields exist for evaluation and debugging:

- ``SensorObservation._true_object_id`` (set by sensors, stripped by the
  experiment driver before estimation),
- ``ObjectState.object_id`` and ``ObjectState.true_class`` on world state.

The one legitimate use of ground truth during generation is the synthetic
vision confusion model: the sensor reads ``ObjectState.true_class`` to produce
the ``class_probs`` vector on the observation. That happens before estimation
and the true class itself must never cross into the tracker. These tests state
that boundary rather than silently skipping it: they poison every
evaluation-only field, rerun, and require the tracker's recorded snapshots to
be identical.

The method loop covers every method in ``METHODS``, so a method added to the
experiment runner is covered here automatically.
"""

from __future__ import annotations

from mosaic_perception.domain.models import (
    ObjectClass,
    SensorObservation,
    TrackStatus,
    WorldState,
)
from mosaic_perception.experiment import METHODS, run_method, run_pair
from mosaic_perception.scenarios import resolve_scenario
from mosaic_perception.tracking import MultiSensorTracker

from ..helpers import make_track, range_observation, vision_observation

POISON_ID = "poisoned_object"


def _poisoned_states(states: list[WorldState], *, poison_true_class: bool) -> list[WorldState]:
    """Deep-copy world states, renaming ground-truth identities consistently."""
    renamed: list[WorldState] = []
    for state in states:
        objects = {}
        for key, obj in state.objects.items():
            copy_obj = obj.model_copy(deep=True)
            new_id = f"{POISON_ID}_{key}"
            copy_obj.object_id = new_id
            if poison_true_class:
                copy_obj.true_class = (
                    ObjectClass.VEHICLE
                    if copy_obj.true_class is not ObjectClass.VEHICLE
                    else ObjectClass.PEDESTRIAN
                )
            objects[new_id] = copy_obj
        renamed.append(state.model_copy(deep=True, update={"objects": objects}))
    return renamed


def _snapshot_dicts(record) -> list[dict]:
    return [snap.model_dump(mode="json") for snap in record.snapshots]


def _epoch_observations(poison: str | None) -> list[tuple[float, list[SensorObservation]]]:
    """Fresh observation batches for three epochs, optionally poisoned."""
    epochs: list[tuple[float, list[SensorObservation]]] = []
    for step in range(3):
        time = step * 0.1
        obs = [
            range_observation(
                f"range-{step}",
                distance=10.0 - 0.1 * step,
                capture_time=time,
                delivery_time=time,
            ),
            vision_observation(
                f"vision-{step}", bearing=0.0, capture_time=time, delivery_time=time
            ),
        ]
        if poison is not None:
            for observation in obs:
                observation._true_object_id = poison
        epochs.append((time, obs))
    return epochs


def test_tracker_snapshots_ignore_poisoned_observation_identity() -> None:
    """The tracker must ignore the observation's ground-truth identity outright.

    This seam bypasses the experiment driver's stripping step, so the only way
    it passes is if no estimator, associator or track-management code path
    reads the private evaluation-only field.
    """

    def run(poison: str | None) -> tuple[list[dict], dict[str, list[str]]]:
        tracker = MultiSensorTracker(dt=0.1, use_vision=True)
        track = make_track(
            position=(10.0, 0.0),
            status=TrackStatus.CONFIRMED,
            hits=3,
        )
        tracker.tracks[track.track_id] = track
        for time, observations in _epoch_observations(poison):
            tracker.process_observations(observations, time)
        linked = {
            track_id: list(t.associated_observations)
            for track_id, t in sorted(tracker.tracks.items())
        }
        return [s.model_dump(mode="json") for s in tracker.snapshots], linked

    clean_snapshots, clean_linked = run(None)
    poisoned_snapshots, poisoned_linked = run(POISON_ID)

    assert clean_snapshots, "expected the tracker to record snapshots"
    assert poisoned_snapshots == clean_snapshots
    assert poisoned_linked == clean_linked


def test_run_method_snapshots_ignore_renamed_ground_truth_identities() -> None:
    """End-to-end: renaming every ground-truth identity changes nothing.

    Covers every method in ``METHODS``. ``true_class`` is left untouched here because the
    vision confusion model legitimately reads it during generation (see the
    module docstring); its estimator-side isolation is covered by the
    range-only case below, where no vision generation happens.
    """
    scenario = resolve_scenario("nominal", seed=7, duration=2.0, num_objects=3)
    reference = run_pair(scenario)
    poisoned = _poisoned_states(reference.states, poison_true_class=False)

    for method in METHODS:
        clean_record = run_method(scenario, method, reference.states)
        poison_record = run_method(scenario, method, poisoned)
        assert _snapshot_dicts(poison_record) == _snapshot_dicts(clean_record), method
        assert poison_record.result.position_rmse == clean_record.result.position_rmse, method
        assert poison_record.result.mota == clean_record.result.mota, method


def test_range_only_snapshots_ignore_poisoned_true_class() -> None:
    """Poisoning the true class must not move a run that generates no vision.

    If this ever fails, ground truth reached the estimator outside the
    documented class-probability path.
    """
    scenario = resolve_scenario("nominal", seed=7, duration=2.0, num_objects=3)
    reference = run_pair(scenario)
    poisoned = _poisoned_states(reference.states, poison_true_class=True)

    clean_record = run_method(scenario, "range_only", reference.states)
    poison_record = run_method(scenario, "range_only", poisoned)
    assert _snapshot_dicts(poison_record) == _snapshot_dicts(clean_record)
