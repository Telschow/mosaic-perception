"""
Per-frame matching: the seam between tracker output and every metric.

``match_frames`` pairs evaluated track snapshots with ground-truth objects once
per frame (one-to-one Hungarian assignment inside a Euclidean gate) and returns
one :class:`FrameMatch` per world state. Metrics are functions of that list, so
each can be tested on hand-built frames without simulating a world.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linear_sum_assignment

from ..domain.models import ObjectState, TrackSnapshot, TrackStatus, WorldState

EVALUATED_STATUSES = {TrackStatus.CONFIRMED, TrackStatus.COASTING}


@dataclass(frozen=True)
class FrameMatch:
    """Matching result for one evaluated frame."""

    index: int
    time: float
    tracks: list[TrackSnapshot]
    objects: list[ObjectState]
    matched_pairs: list[tuple[TrackSnapshot, ObjectState]]
    unmatched_tracks: int
    unmatched_objects: int
    # Unmatched evaluated tracks that had a ground-truth object inside the
    # matching gate while that object was matched to another track.
    duplicate_tracks: list[TrackSnapshot] = field(default_factory=list)


def index_snapshots(snapshots: list[TrackSnapshot]) -> dict[float, dict[str, TrackSnapshot]]:
    """Group snapshots by (rounded) time, then track ID."""
    by_time: dict[float, dict[str, TrackSnapshot]] = {}
    for snapshot in snapshots:
        key = round(float(snapshot.time), 9)
        frame = by_time.setdefault(key, {})
        if snapshot.track_id in frame:
            raise ValueError(f"duplicate snapshot for track {snapshot.track_id!r} at time {key}")
        frame[snapshot.track_id] = snapshot
    return by_time


# Score bonus for re-using last frame's pairing. Larger than any in-gate similarity sum, so a
# still-valid previous pairing always beats a closer alternative (as in TrackEval's CLEAR).
_CONTINUITY_BONUS = 1_000.0


def match_frames(
    snapshots_by_time: dict[float, dict[str, TrackSnapshot]],
    world_states: list[WorldState],
    gate_m: float,
    continuity: bool = True,
) -> list[FrameMatch]:
    """Match evaluated tracks to ground truth in every frame.

    With ``continuity`` (the headline setting, as in TrackEval's CLEAR matching) the
    matcher prefers each object's track from the immediately preceding frame while
    that pairing remains inside the gate, even when that costs another object its
    match (continuity outranks match count); an object that was unmatched in the
    preceding frame has no preference. Otherwise matching is distance-only.
    """
    world_times = {round(float(world_state.time), 9) for world_state in world_states}
    stray = sorted(set(snapshots_by_time) - world_times)
    if stray:
        raise ValueError(f"snapshots at {stray[:3]} match no world-state time (within 1e-9 s)")
    frames: list[FrameMatch] = []
    previous: dict[str, str] = {}
    for index, world_state in enumerate(world_states):
        key = round(float(world_state.time), 9)
        tracks = [
            snapshot
            for snapshot in snapshots_by_time.get(key, {}).values()
            if snapshot.status in EVALUATED_STATUSES
        ]
        objects = list(world_state.objects.values())
        frame = match_frame(
            index,
            float(world_state.time),
            tracks,
            objects,
            gate_m,
            previous if continuity else None,
        )
        frames.append(frame)
        # Only the immediately preceding frame's pairing carries a preference.
        previous = {obj.object_id: snapshot.track_id for snapshot, obj in frame.matched_pairs}
    return frames


def match_frame(
    index: int,
    time: float,
    tracks: list[TrackSnapshot],
    objects: list[ObjectState],
    gate_m: float,
    previous: dict[str, str] | None = None,
) -> FrameMatch:
    """One-to-one gated Hungarian matching for a single frame."""
    if not tracks or not objects:
        return FrameMatch(index, time, tracks, objects, [], len(tracks), len(objects))

    track_positions = np.array([track.position() for track in tracks])
    object_positions = np.array([obj.position.to_array() for obj in objects])
    distances = np.linalg.norm(track_positions[:, None, :] - object_positions[None, :, :], axis=2)
    finite = distances <= gate_m
    if not np.any(finite):
        return FrameMatch(index, time, tracks, objects, [], len(tracks), len(objects))

    if previous is None:
        # Distance-only: maximise in-gate matches, then minimise total distance.
        assignment_cost = np.where(finite, distances, 1e9)
    else:
        # Continuity-first, as TrackEval's CLEAR matching: maximise
        # 1000 * previous_pairing + similarity over in-gate pairs only (similarity is
        # zero outside the gate), so a still-valid previous pairing outranks match count.
        score = np.where(finite, 1.0 - distances / gate_m, 0.0)
        for track_index, track in enumerate(tracks):
            for object_index, obj in enumerate(objects):
                if finite[track_index, object_index] and (
                    previous.get(obj.object_id) == track.track_id
                ):
                    score[track_index, object_index] += _CONTINUITY_BONUS
        assignment_cost = -score
    rows, columns = linear_sum_assignment(assignment_cost)
    paired_rows: set[int] = set()
    paired_columns: set[int] = set()
    matched_pairs: list[tuple[TrackSnapshot, ObjectState]] = []
    for row, column in zip(rows, columns, strict=True):
        if finite[row, column]:
            paired_rows.add(int(row))
            paired_columns.add(int(column))
            matched_pairs.append((tracks[row], objects[column]))
    claimed_columns = np.zeros(len(objects), dtype=bool)
    claimed_columns[list(paired_columns)] = True
    duplicates = [
        tracks[row]
        for row in range(len(tracks))
        if row not in paired_rows and bool(np.any(finite[row] & claimed_columns))
    ]
    return FrameMatch(
        index,
        time,
        tracks,
        objects,
        matched_pairs,
        len(tracks) - len(paired_rows),
        len(objects) - len(paired_columns),
        duplicates,
    )
