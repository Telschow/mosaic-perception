"""Fixed sequences for the TrackEval cross-check (issue #30).

Every sequence is hand-built and deterministic: no RNG, no simulator. The same
sequences are evaluated twice — by this project's evaluation pipeline and by
TrackEval's reference CLEAR/ID metrics — so any disagreement is a definition
difference, not sampling noise.

Positions are chosen so the two matchers cannot disagree about association:

- intended matches sit well inside both gates (offset <= 0.2 m; unit boxes give
  IoU >= 0.667 at that offset, the CLEAR threshold is 0.5, our gate is 2 m),
- distinct objects sit far apart (>= 10 m), outside both gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mosaic_perception.domain.models import (
    ObjectClass,
    ObjectState,
    TrackSnapshot,
    TrackStatus,
    Vector2,
    WorldState,
)

DT = 0.1
FRAMES = 6
BOX_SIZE = 1.0


def frame_time(index: int) -> float:
    return round(index * DT, 9)


def make_state(index: int, objects: dict[str, tuple[float, float]]) -> WorldState:
    return WorldState(
        time=frame_time(index),
        objects={
            object_id: ObjectState(
                object_id=object_id,
                position=Vector2(x=position[0], y=position[1]),
                velocity=Vector2(x=0.0, y=0.0),
                true_class=ObjectClass.VEHICLE,
            )
            for object_id, position in objects.items()
        },
    )


def make_snapshot(index: int, track_id: str, position: tuple[float, float]) -> TrackSnapshot:
    return TrackSnapshot(
        time=frame_time(index),
        track_id=track_id,
        status=TrackStatus.CONFIRMED,
        state=[position[0], position[1], 0.0, 0.0],
        covariance=[
            [0.01, 0.0, 0.0, 0.0],
            [0.0, 0.01, 0.0, 0.0],
            [0.0, 0.0, 0.01, 0.0],
            [0.0, 0.0, 0.0, 0.01],
        ],
        hits=6,
        misses=0,
        age=6,
    )


@dataclass(frozen=True)
class FixedSequence:
    """One sequence: ground-truth world states plus tracker snapshots."""

    name: str
    states: list[WorldState]
    snapshots: list[TrackSnapshot]
    description: str = field(default="")


def _clean_two_objects() -> FixedSequence:
    """Two well-separated objects, tracks tracking with a 0.1 m offset."""
    states = [make_state(i, {"obj_a": (0.0, 0.0), "obj_b": (10.0, 0.0)}) for i in range(FRAMES)]
    snapshots = []
    for i in range(FRAMES):
        snapshots.append(make_snapshot(i, "track_a", (0.1, 0.0)))
        snapshots.append(make_snapshot(i, "track_b", (10.1, 0.0)))
    return FixedSequence(
        name="clean_two_objects",
        states=states,
        snapshots=snapshots,
        description="Perfect tracking of two objects; both matchers must score a perfect run.",
    )


def _duplicate_track() -> FixedSequence:
    """One object covered by two tracks in every frame: the duplicate case."""
    states = [make_state(i, {"obj_a": (0.0, 0.0)}) for i in range(FRAMES)]
    snapshots = []
    for i in range(FRAMES):
        snapshots.append(make_snapshot(i, "track_main", (0.0, 0.0)))
        snapshots.append(make_snapshot(i, "track_dup", (0.2, 0.0)))
    return FixedSequence(
        name="duplicate_track",
        states=states,
        snapshots=snapshots,
        description="A second track shadows one object in every frame (false positives).",
    )


def _identity_switch() -> FixedSequence:
    """A track leaves object A and picks up object B: one identity switch."""
    states = [make_state(i, {"obj_a": (0.0, 0.0), "obj_b": (10.0, 0.0)}) for i in range(FRAMES)]
    snapshots = []
    for i in range(FRAMES):
        if i < 3:
            snapshots.append(make_snapshot(i, "track_1", (0.0, 0.0)))
            snapshots.append(make_snapshot(i, "track_2", (10.0, 0.0)))
        else:
            snapshots.append(make_snapshot(i, "track_1", (10.0, 0.0)))
    return FixedSequence(
        name="identity_switch",
        states=states,
        snapshots=snapshots,
        description="track_1 switches from obj_a to obj_b at frame 3; obj_a is then missed.",
    )


def _miss_and_spurious() -> FixedSequence:
    """One object is missed late, plus a track that never matches anything."""
    states = [make_state(i, {"obj_a": (0.0, 0.0)}) for i in range(FRAMES)]
    snapshots = []
    for i in range(FRAMES):
        if i < 4:
            snapshots.append(make_snapshot(i, "track_a", (0.0, 0.0)))
        snapshots.append(make_snapshot(i, "track_spurious", (20.0, 0.0)))
    return FixedSequence(
        name="miss_and_spurious",
        states=states,
        snapshots=snapshots,
        description="track_a stops at frame 4 (misses) while a far-away track is all false positives.",
    )


def fixed_sequences() -> list[FixedSequence]:
    """The fixed cross-check sequences, at least three, one per corner case."""
    return [
        _clean_two_objects(),
        _duplicate_track(),
        _identity_switch(),
        _miss_and_spurious(),
    ]
