"""Metrics tested directly on hand-built frame matches (no world, no matching)."""

from __future__ import annotations

import pytest

from mosaic_perception.domain.models import ObjectClass, ObjectState, Vector2
from mosaic_perception.evaluation.frames import FrameMatch
from mosaic_perception.evaluation.metrics import (
    class_counts,
    duplicate_track_ids,
    duplicate_track_samples,
    identity_switches,
    interruptions,
    matched_errors,
    per_frame_metrics,
    sample_counts,
)
from tests.helpers import make_snapshot


def _object(object_id, position=(0.0, 0.0), true_class=ObjectClass.UNKNOWN):
    return ObjectState(
        object_id=object_id,
        position=Vector2(x=position[0], y=position[1]),
        true_class=true_class,
    )


def _frame(index, matched=(), unmatched_tracks=(), objects=(), duplicates=()):
    """matched: (track_id, position, object) triples; unmatched_tracks: track snapshots."""
    pairs = [
        (make_snapshot(0.1 * index, track_id, position), obj) for track_id, position, obj in matched
    ]
    tracks = [snapshot for snapshot, _ in pairs] + list(unmatched_tracks)
    all_objects = list(objects) or [obj for _, _, obj in matched]
    return FrameMatch(
        index=index,
        time=0.1 * index,
        tracks=tracks,
        objects=all_objects,
        matched_pairs=pairs,
        unmatched_tracks=len(unmatched_tracks),
        unmatched_objects=len(all_objects) - len(pairs),
        duplicate_tracks=list(duplicates),
    )


def test_identity_switches_count_track_changes_between_matched_frames():
    a = _object("a")
    frames = [
        _frame(0, [("t1", (0.0, 0.0), a)]),
        _frame(1, [("t1", (0.0, 0.0), a)]),
        _frame(2, [("t2", (0.0, 0.0), a)]),
        _frame(3, [("t1", (0.0, 0.0), a)]),
    ]
    assert identity_switches(frames) == 2


def test_identity_switches_are_undefined_without_matches():
    assert identity_switches([_frame(0, objects=[_object("a")])]) is None


def test_interruptions_count_gaps_between_matched_frames_per_object():
    a, b = _object("a"), _object("b")
    frames = [
        _frame(0, [("t1", (0, 0), a), ("t2", (0, 0), b)]),
        _frame(1, [("t2", (0, 0), b)], objects=[a, b]),  # a unmatched
        _frame(2, [("t1", (0, 0), a), ("t2", (0, 0), b)]),
        _frame(3, [("t1", (0, 0), a)], objects=[a, b]),  # b unmatched, trailing
    ]
    assert interruptions(frames) == 1.0  # only a's gap; b's trailing loss is not one


def test_class_counts_skip_unknown_estimate_and_unknown_truth():
    vehicle = _object("a", true_class=ObjectClass.VEHICLE)
    unknown_truth = _object("b")
    frame = FrameMatch(
        index=0,
        time=0.0,
        tracks=[],
        objects=[vehicle, unknown_truth],
        matched_pairs=[
            (make_snapshot(0.0, "t1", (0, 0), class_estimate=ObjectClass.VEHICLE), vehicle),
            (make_snapshot(0.0, "t2", (0, 0), class_estimate=ObjectClass.VEHICLE), unknown_truth),
            (make_snapshot(0.0, "t3", (0, 0)), vehicle),  # estimate UNKNOWN
        ],
        unmatched_tracks=0,
        unmatched_objects=0,
    )
    counts = class_counts([frame])
    assert (counts.classified, counts.correct) == (1, 1)


def test_duplicates_are_read_from_the_frame_matches():
    a = _object("a")
    dup = make_snapshot(0.0, "t_dup", (0.5, 0.0))
    frames = [
        _frame(0, [("t1", (0.0, 0.0), a)], unmatched_tracks=[dup], duplicates=[dup]),
        _frame(1, [("t1", (0.0, 0.0), a)], unmatched_tracks=[dup], duplicates=[dup]),
    ]
    assert duplicate_track_samples(frames) == 2
    assert duplicate_track_ids(frames) == {"t_dup"}


def test_sample_counts_sum_over_frames():
    a = _object("a")
    spurious = make_snapshot(0.0, "t_far", (30.0, 0.0))
    frames = [
        _frame(0, [("t1", (0.0, 0.0), a)], unmatched_tracks=[spurious]),
        _frame(1, objects=[a]),
    ]
    counts = sample_counts(frames)
    assert counts.ground_truth == 2
    assert counts.evaluated_tracks == 2
    assert counts.matched == 1
    assert counts.unmatched_ground_truth == 1
    assert counts.unmatched_tracks == 1


def test_matched_errors_and_per_frame_rows():
    a = _object("a", position=(0.0, 0.0))
    frames = [_frame(0, [("t1", (3.0, 4.0), a)])]
    errors = matched_errors(frames)
    assert errors.position_squared == [pytest.approx(25.0)]
    rows = per_frame_metrics(frames)
    assert rows[0]["mean_position_error_m"] == pytest.approx(5.0)
    assert rows[0]["matched"] == 1
