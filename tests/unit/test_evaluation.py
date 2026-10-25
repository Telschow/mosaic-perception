"""Hand-constructed evaluation tests with exactly computable expected values."""

from __future__ import annotations

import numpy as np
import pytest

from mosaic_perception.domain.models import ObservationStatistics, TrackStatus
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
    assert result.track_fragmentation is None
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
