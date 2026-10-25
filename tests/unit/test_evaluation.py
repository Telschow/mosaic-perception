"""Hand-constructed evaluation tests with exactly computable expected values."""

from __future__ import annotations

import numpy as np
import pytest

from mosaic_perception.domain.models import ObjectClass, ObservationStatistics, TrackStatus
from mosaic_perception.evaluation.metrics import TrackingEvaluator
from tests.helpers import make_snapshot, make_world_state


def test_exact_rmse_matching_and_coverage():
    world = make_world_state(
        1.0,
        {
            "a": ((0.0, 0.0), (1.0, 0.0)),
            "b": ((10.0, 0.0), (0.0, 1.0)),
        },
    )
    snapshots = [
        make_snapshot(1.0, "track_a", (0.3, 0.4), (1.1, 0.0)),
        make_snapshot(1.0, "track_b", (9.5, 0.5), (0.0, 0.9)),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(
        snapshots, [world], scenario_name="hand", seed=1, method_name="fused"
    )

    assert result.matched_samples == 2
    assert result.ground_truth_samples == 2
    assert result.confirmed_track_samples == 2
    assert result.unmatched_ground_truth_samples == 0
    assert result.unmatched_track_samples == 0
    assert result.recall == pytest.approx(1.0)
    assert result.precision == pytest.approx(1.0)
    assert result.position_rmse == pytest.approx(np.sqrt(0.375))
    assert result.velocity_rmse == pytest.approx(0.1)
    assert result.position_coverage_95 == pytest.approx(1.0)
    assert result.coverage_samples == 2
    assert result.identity_switches == 0
    assert result.num_tracks == 2
    assert result.num_confirmed_tracks == 2
    assert result.num_unmatched_confirmed_tracks == 0
    assert result.track_fragmentation == 0
    assert result.per_frame_metrics[0]["matched"] == 2


def test_missed_object_lowers_recall():
    world = make_world_state(
        0.0,
        {
            "a": ((0.0, 0.0), (0.0, 0.0)),
            "b": ((10.0, 0.0), (0.0, 0.0)),
        },
    )
    snapshots = [make_snapshot(0.0, "track_a", (0.2, 0.0))]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.matched_samples == 1
    assert result.ground_truth_samples == 2
    assert result.recall == pytest.approx(0.5)
    assert result.precision == pytest.approx(1.0)
    assert result.unmatched_ground_truth_samples == 1
    assert result.unmatched_track_samples == 0
    assert result.position_rmse == pytest.approx(0.2)


def test_false_track_is_reported_without_inflating_recall():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_true", (0.1, 0.0)),
        make_snapshot(0.0, "track_false", (50.0, 50.0)),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.matched_samples == 1
    assert result.confirmed_track_samples == 2
    assert result.precision == pytest.approx(0.5)
    assert result.recall == pytest.approx(1.0)
    assert result.num_unmatched_confirmed_tracks == 1
    assert result.unmatched_track_samples == 1
    assert result.identity_switches == 0


def test_duplicate_tracks_are_matched_one_to_one():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_a", (0.1, 0.0)),
        make_snapshot(0.0, "track_b", (0.2, 0.0)),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.matched_samples == 1
    assert result.confirmed_track_samples == 2
    assert result.precision == pytest.approx(0.5)
    assert result.recall == pytest.approx(1.0)
    assert result.num_unmatched_confirmed_tracks == 1
    assert result.unmatched_track_samples == 1


def test_no_valid_matches_reports_none_for_undefined_rmse_and_coverage():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [make_snapshot(0.0, "track_far", (10.0, 0.0))]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.matched_samples == 0
    assert result.position_rmse is None
    assert result.velocity_rmse is None
    assert result.position_coverage_95 is None
    assert result.position_coverage_68 is None
    assert result.coverage_samples == 0
    assert result.recall == pytest.approx(0.0)
    assert result.precision == pytest.approx(0.0)
    assert result.identity_switches is None
    assert result.num_unmatched_confirmed_tracks == 1


def test_coverage_uses_chi_square_threshold_not_fixed_value():
    world = make_world_state(
        0.0,
        {
            "a": ((0.0, 0.0), (0.0, 0.0)),
            "b": ((10.0, 0.0), (0.0, 0.0)),
        },
    )
    # Isotropic covariance I: squared error 1 is inside chi2(2, 0.95)=5.991,
    # squared error 9 is outside.
    snapshots = [
        make_snapshot(0.0, "track_a", (1.0, 0.0)),
        make_snapshot(0.0, "track_b", (13.0, 0.0)),
    ]
    result = TrackingEvaluator(match_gate_m=10.0).evaluate(snapshots, [world])
    assert result.matched_samples == 2
    assert result.coverage_samples == 2
    assert result.position_coverage_95 == pytest.approx(0.5)
    assert result.position_coverage_68 == pytest.approx(0.5)
    assert result.position_rmse == pytest.approx(np.sqrt(5.0))


def test_identity_switch_is_counted_when_track_id_changes_for_same_object():
    states = [
        make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))}),
        make_world_state(1.0, {"a": ((0.0, 0.0), (0.0, 0.0))}),
    ]
    snapshots = [
        make_snapshot(0.0, "track_a", (0.1, 0.0)),
        make_snapshot(1.0, "track_b", (0.1, 0.0)),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, states)
    assert result.matched_samples == 2
    assert result.identity_switches == 1


def test_tentative_tracks_are_not_scored():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [make_snapshot(0.0, "track_tentative", (0.1, 0.0), status=TrackStatus.TENTATIVE)]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.matched_samples == 0
    assert result.confirmed_track_samples == 0
    assert result.precision is None
    assert result.recall == pytest.approx(0.0)
    assert result.num_confirmed_tracks == 0
    assert result.num_tracks == 1


def test_observation_statistics_are_propagated():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    statistics = ObservationStatistics(
        delivered_observations=5,
        rejected_observations=2,
        rejected_out_of_sequence=1,
        rejected_invalid=1,
        pending_observations=3,
        age_samples=7,
        mean_age_of_information=0.05,
    )
    result = TrackingEvaluator().evaluate(
        [make_snapshot(0.0, "track_a", (0.1, 0.0))],
        [world],
        statistics=statistics,
    )
    assert result.delivered_observations == 5
    assert result.rejected_observations == 2
    assert result.rejected_out_of_sequence == 1
    assert result.rejected_invalid == 1
    assert result.pending_observations == 3
    assert result.age_samples == 7
    assert result.mean_age_of_information == pytest.approx(0.05)


def test_duplicate_track_is_unmatched_track_near_a_claimed_object():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_main", (0.1, 0.0)),
        make_snapshot(0.0, "track_dup", (0.9, 0.0)),  # within 2 m gate, object already claimed
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.matched_samples == 1
    assert result.num_unmatched_confirmed_tracks == 1
    assert result.num_duplicate_tracks == 1
    assert result.duplicate_track_samples == 1


def test_distant_spurious_track_is_not_a_duplicate():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_main", (0.1, 0.0)),
        make_snapshot(0.0, "track_far", (30.0, 0.0)),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.num_unmatched_confirmed_tracks == 1
    assert result.num_duplicate_tracks == 0
    assert result.duplicate_track_samples == 0


def test_correctly_matched_tracks_have_no_duplicates():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0)), "b": ((10.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_a", (0.1, 0.0)),
        make_snapshot(0.0, "track_b", (10.1, 0.0)),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.num_unmatched_confirmed_tracks == 0
    assert result.num_duplicate_tracks == 0
    assert result.duplicate_track_samples == 0


def test_track_matched_in_another_frame_is_not_counted_as_duplicate_track():
    world0 = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    world1 = make_world_state(0.1, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_x", (0.1, 0.0)),
        make_snapshot(0.0, "track_y", (0.5, 0.0)),  # duplicate sample in frame 0
        make_snapshot(0.1, "track_y", (0.1, 0.0)),  # but matched in frame 1
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world0, world1])
    assert result.duplicate_track_samples == 1
    assert result.num_duplicate_tracks == 0


def _frames(matched_flags, track_ids=None):
    """One object at the origin over len(flags) frames; track present only when flagged."""
    worlds = [
        make_world_state(round(0.1 * i, 6), {"a": ((0.0, 0.0), (0.0, 0.0))})
        for i in range(len(matched_flags))
    ]
    snapshots = []
    for i, present in enumerate(matched_flags):
        if present:
            track_id = track_ids[i] if track_ids else "track_a"
            snapshots.append(make_snapshot(round(0.1 * i, 6), track_id, (0.1, 0.0)))
    return snapshots, worlds


def test_uninterrupted_track_has_zero_fragmentation():
    snapshots, worlds = _frames([True, True, True, True])
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.track_fragmentation == 0


def test_dropout_and_resume_counts_one_interruption():
    snapshots, worlds = _frames([True, True, False, False, True, True])
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.track_fragmentation == 1


def test_two_gaps_count_two_interruptions():
    snapshots, worlds = _frames([True, False, True, False, True])
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.track_fragmentation == 2


def test_late_start_and_early_end_are_not_interruptions():
    snapshots, worlds = _frames([False, False, True, True, False])
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.track_fragmentation == 0


def test_never_matched_object_has_undefined_fragmentation():
    snapshots, worlds = _frames([False, False, False])
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.track_fragmentation is None


def test_identity_switch_without_gap_is_not_fragmentation():
    snapshots, worlds = _frames(
        [True, True, True, True], ["track_a", "track_a", "track_b", "track_b"]
    )
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.identity_switches == 1
    assert result.track_fragmentation == 0


def test_fragmentation_sums_over_objects():
    worlds = [
        make_world_state(
            round(0.1 * i, 6),
            {"a": ((0.0, 0.0), (0.0, 0.0)), "b": ((10.0, 0.0), (0.0, 0.0))},
        )
        for i in range(4)
    ]
    snapshots = [make_snapshot(round(0.1 * i, 6), "track_a", (0.1, 0.0)) for i in (0, 1, 2, 3)] + [
        make_snapshot(round(0.1 * i, 6), "track_b", (10.1, 0.0)) for i in (0, 3)
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.track_fragmentation == 1


def test_duplicate_counts_depend_on_matching_gate():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_main", (0.1, 0.0)),
        make_snapshot(0.0, "track_near_dup", (0.0, 1.5)),  # inside 2 m and 3 m, not 1 m
        make_snapshot(0.0, "track_far_dup", (2.5, 0.0)),  # inside 3 m only
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.num_duplicate_tracks_by_gate["1m"] == 0
    assert result.num_duplicate_tracks_by_gate["2m"] == 1
    assert result.num_duplicate_tracks_by_gate["3m"] == 2
    assert result.num_duplicate_tracks == result.num_duplicate_tracks_by_gate["2m"]


def test_sensitivity_fields_are_independent_of_the_headline_gate():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "track_main", (0.1, 0.0)),
        make_snapshot(0.0, "track_dup", (0.0, 1.5)),
    ]
    headline_1m = TrackingEvaluator(match_gate_m=1.0).evaluate(snapshots, [world])
    headline_3m = TrackingEvaluator(match_gate_m=3.0).evaluate(snapshots, [world])
    for result in (headline_1m, headline_3m):
        assert result.num_duplicate_tracks_by_gate["1m"] == 0
        assert result.num_duplicate_tracks_by_gate["2m"] == 1
        assert result.num_duplicate_tracks_by_gate["3m"] == 1


def _class_world(true_classes):
    return make_world_state(
        0.0,
        {"a": ((0.0, 0.0), (0.0, 0.0)), "b": ((10.0, 0.0), (0.0, 0.0))},
        true_classes=true_classes,
    )


def test_class_accuracy_counts_correct_and_incorrect_estimates():
    world = _class_world({"a": ObjectClass.VEHICLE, "b": ObjectClass.PEDESTRIAN})
    snapshots = [
        make_snapshot(0.0, "t_a", (0.1, 0.0), class_estimate=ObjectClass.VEHICLE),
        make_snapshot(0.0, "t_b", (10.1, 0.0), class_estimate=ObjectClass.CYCLIST),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.class_classified_samples == 2
    assert result.class_correct_samples == 1
    assert result.class_accuracy == pytest.approx(0.5)


def test_unknown_class_estimates_are_excluded_from_the_denominator():
    world = _class_world({"a": ObjectClass.VEHICLE, "b": ObjectClass.PEDESTRIAN})
    snapshots = [
        make_snapshot(0.0, "t_a", (0.1, 0.0), class_estimate=ObjectClass.VEHICLE),
        make_snapshot(0.0, "t_b", (10.1, 0.0)),  # estimate stays UNKNOWN
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.matched_samples == 2
    assert result.class_classified_samples == 1
    assert result.class_correct_samples == 1
    assert result.class_accuracy == pytest.approx(1.0)


def test_class_accuracy_is_undefined_without_any_classified_sample():
    world = _class_world({"a": ObjectClass.VEHICLE, "b": ObjectClass.PEDESTRIAN})
    snapshots = [make_snapshot(0.0, "t_a", (0.1, 0.0)), make_snapshot(0.0, "t_b", (10.1, 0.0))]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.class_classified_samples == 0
    assert result.class_accuracy is None


def test_objects_with_unknown_true_class_are_not_scored():
    world = _class_world({"a": ObjectClass.VEHICLE})  # b has UNKNOWN true class
    snapshots = [
        make_snapshot(0.0, "t_a", (0.1, 0.0), class_estimate=ObjectClass.VEHICLE),
        make_snapshot(0.0, "t_b", (10.1, 0.0), class_estimate=ObjectClass.VEHICLE),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.class_classified_samples == 1
    assert result.class_accuracy == pytest.approx(1.0)


def test_aggregate_pools_class_accuracy_across_seeds():
    from mosaic_perception.cli.main import _aggregate
    from mosaic_perception.domain.models import EvaluationResult

    lucky = EvaluationResult(
        scenario_name="x",
        seed=1,
        method_name="fused",
        class_classified_samples=1,
        class_correct_samples=1,
        class_accuracy=1.0,
        matched_samples=10,
    )
    broad = EvaluationResult(
        scenario_name="x",
        seed=2,
        method_name="fused",
        class_classified_samples=500,
        class_correct_samples=300,
        class_accuracy=0.6,
        matched_samples=500,
    )
    aggregate = _aggregate([lucky, broad])
    assert aggregate["class_accuracy"] == pytest.approx(0.8)  # unweighted mean of seeds
    assert aggregate["class_accuracy_pooled"] == pytest.approx(301 / 501)
    assert aggregate["class_classified_fraction_pooled"] == pytest.approx(501 / 510)


def test_aggregate_pooled_class_accuracy_is_undefined_without_classified_samples():
    from mosaic_perception.cli.main import _aggregate
    from mosaic_perception.domain.models import EvaluationResult

    aggregate = _aggregate(
        [EvaluationResult(scenario_name="x", seed=1, method_name="fused", matched_samples=5)]
    )
    assert aggregate["class_accuracy_pooled"] is None
    assert aggregate["class_classified_fraction_pooled"] == 0.0


def test_evaluate_reports_perfect_scores_for_exact_tracking():
    worlds = [
        make_world_state(round(0.1 * i, 6), {"a": ((float(i), 0.0), (1.0, 0.0))}) for i in range(4)
    ]
    snapshots = [
        make_snapshot(round(0.1 * i, 6), "t1", (float(i), 0.0), (1.0, 0.0)) for i in range(4)
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, worlds)
    assert result.mota == pytest.approx(1.0)
    assert result.idf1 == pytest.approx(1.0)
    assert result.idp == pytest.approx(1.0) and result.idr == pytest.approx(1.0)
    assert result.gospa_p1 == pytest.approx(0.0)
    assert result.gospa_p2 == pytest.approx(0.0)


def test_evaluate_scores_a_duplicate_track_in_idf1_and_mota():
    world = make_world_state(0.0, {"a": ((0.0, 0.0), (0.0, 0.0))})
    snapshots = [
        make_snapshot(0.0, "t_main", (0.1, 0.0)),
        make_snapshot(0.0, "t_dup", (0.9, 0.0)),
    ]
    result = TrackingEvaluator(match_gate_m=2.0).evaluate(snapshots, [world])
    assert result.mota == pytest.approx(0.0)  # 1 - (0 + 1 FP + 0)/1
    assert result.idp == pytest.approx(0.5)
    assert result.idr == pytest.approx(1.0)
    assert result.idf1 == pytest.approx(2 / 3)
