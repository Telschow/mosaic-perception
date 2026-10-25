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


# --- MOTA, IDF1/IDP/IDR, GOSPA -------------------------------------------------

import math  # noqa: E402

from mosaic_perception.evaluation.metrics import gospa, idf1_scores, mota  # noqa: E402


def _near(track_id, object_id, index, offset=0.1):
    """A frame with one object at the origin and one track `offset` m away."""
    obj = _object(object_id)
    snapshot = make_snapshot(0.1 * index, track_id, (offset, 0.0))
    return FrameMatch(
        index=index,
        time=0.1 * index,
        tracks=[snapshot],
        objects=[obj],
        matched_pairs=[(snapshot, obj)],
        unmatched_tracks=0,
        unmatched_objects=0,
    )


def test_mota_is_one_minus_misses_false_positives_and_switches_over_ground_truth():
    a = _object("a")
    spurious = make_snapshot(0.0, "t_far", (30.0, 0.0))
    frames = [
        _frame(0, [("t1", (0.0, 0.0), a)]),  # 1 GT, matched
        _frame(1, [("t2", (0.0, 0.0), a)], unmatched_tracks=[spurious]),  # switch + 1 FP
        _frame(2, objects=[a]),  # 1 miss
        _frame(3, [("t2", (0.0, 0.0), a)]),
    ]
    # GT = 4, FN = 1, FP = 1, IDSW = 1  ->  1 - 3/4
    assert mota(frames) == pytest.approx(0.25)


def test_mota_can_be_negative_and_is_undefined_without_ground_truth():
    spurious = [make_snapshot(0.0, f"t{i}", (30.0 + i, 0.0)) for i in range(3)]
    noisy = _frame(0, objects=[_object("a")], unmatched_tracks=spurious)  # GT 1, FN 1, FP 3
    assert mota([noisy]) == pytest.approx(1 - 4 / 1)
    empty = FrameMatch(0, 0.0, [], [], [], 0, 0)
    assert mota([empty]) is None


def test_idf1_follows_the_longest_trajectory_pairing():
    # Object a is covered by t1 for 3 frames and by t2 for 1 frame.
    frames = [_near("t1", "a", 0), _near("t1", "a", 1), _near("t1", "a", 2), _near("t2", "a", 3)]
    scores = idf1_scores(frames, gate_m=2.0)
    # IDTP = 3, IDFN = 1, IDFP = 1
    assert scores.idtp == 3 and scores.idfn == 1 and scores.idfp == 1
    assert scores.idp == pytest.approx(0.75)
    assert scores.idr == pytest.approx(0.75)
    assert scores.idf1 == pytest.approx(6 / 8)


def test_idf1_is_perfect_for_one_track_per_object_and_undefined_when_empty():
    frames = [_near("t1", "a", i) for i in range(5)]
    assert idf1_scores(frames, 2.0).idf1 == pytest.approx(1.0)
    empty = FrameMatch(0, 0.0, [], [], [], 0, 0)
    assert idf1_scores([empty], 2.0).idf1 is None


def test_idf1_penalises_a_duplicate_track_that_a_per_frame_matcher_forgives():
    # Each frame: one object, a main track and a duplicate 0.5 m away.
    obj = _object("a")
    frames = []
    for index in range(4):
        main = make_snapshot(0.1 * index, "t_main", (0.1, 0.0))
        dup = make_snapshot(0.1 * index, "t_dup", (0.5, 0.0))
        frames.append(
            FrameMatch(index, 0.1 * index, [main, dup], [obj], [(main, obj)], 1, 0, [dup])
        )
    scores = idf1_scores(frames, 2.0)
    # IDTP = 4, IDFN = 0, IDFP = 4 (the duplicate's detections)
    assert (scores.idtp, scores.idfn, scores.idfp) == (4, 0, 4)
    assert scores.idp == pytest.approx(0.5)
    assert scores.idr == pytest.approx(1.0)
    assert scores.idf1 == pytest.approx(8 / 12)


def test_gospa_localisation_only():
    frame = _near("t1", "a", 0, offset=1.0)
    assert gospa([frame], cutoff_m=2.0, p=1) == pytest.approx(1.0)
    assert gospa([frame], cutoff_m=2.0, p=2) == pytest.approx(1.0)


def test_gospa_missed_object_and_false_track_cost_half_the_cutoff_power_each():
    missed = _frame(0, objects=[_object("a")])
    false = _frame(0, unmatched_tracks=[make_snapshot(0.0, "t", (30.0, 0.0))], objects=[])
    for frame in (missed, false):
        assert gospa([frame], cutoff_m=2.0, p=1) == pytest.approx(1.0)  # c^p / 2
        assert gospa([frame], cutoff_m=2.0, p=2) == pytest.approx(math.sqrt(2.0))


def test_gospa_caps_distant_pairs_at_the_cutoff_and_averages_over_frames():
    far = _near("t1", "a", 0, offset=5.0)  # capped at c = 2
    perfect = _near("t1", "a", 1, offset=0.0)
    assert gospa([far], cutoff_m=2.0, p=1) == pytest.approx(2.0)
    assert gospa([far, perfect], cutoff_m=2.0, p=1) == pytest.approx(1.0)


def test_gospa_of_an_empty_frame_is_zero_and_no_frames_is_undefined():
    empty = FrameMatch(0, 0.0, [], [], [], 0, 0)
    assert gospa([empty], 2.0, 1) == 0.0
    assert gospa([], 2.0, 1) is None
