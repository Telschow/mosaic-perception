"""
The single declaration of every per-run metric.

Each metric is declared once here with its name and display precision. The CSV
columns, the cross-seed aggregates and the report columns are all derived from
these declarations, so adding a metric means adding one line (plus the code
that computes it). ``docs/metrics.md`` documents each declared name and a test
checks that none is missing.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

# Matching gates at which duplicate-track counts are also reported. Fixed before
# any run (issue #11); the canonical headline gate stays 2.0 m.
DUPLICATE_SENSITIVITY_GATES_M = (1.0, 2.0, 3.0)


def gate_label(gate_m: float) -> str:
    """Stable label for a gate in field names: 1.0 -> '1m', 1.5 -> '1p5m'."""
    return f"{gate_m:g}".replace(".", "p") + "m"


def duplicate_gate_metric(gate_m: float) -> str:
    return f"num_duplicate_tracks_gate_{gate_label(gate_m)}"


@dataclass(frozen=True)
class MetricSpec:
    """A scalar per-run metric aggregated as mean and sample std over seeds."""

    name: str
    digits: int = 3


@dataclass(frozen=True)
class PooledRatio:
    """A ratio pooled over seeds (sum of numerators over sum of denominators)."""

    name: str
    numerator: str
    denominator: str
    digits: int = 3


@dataclass(frozen=True)
class PooledChiSquare:
    """A chi-square consistency statistic pooled over seeds, with a 95% interval.

    ``total`` is summed over seeds; the degrees of freedom are either
    ``dof_per_sample`` times the summed ``samples`` metric or the summed
    ``dof_metric``. The pooled value is ``total / dof``, i.e. the statistic per
    degree of freedom (nominally 1.0), with the two-sided 95% interval from the
    chi-square quantiles at ``dof`` degrees of freedom divided by ``dof``. Samples are treated as independent, which they are not within a
    track, so the interval is optimistic.
    """

    name: str
    total: str
    samples: str | None = None
    dof_per_sample: int = 1
    dof_metric: str | None = None
    digits: int = 3


# CSV column order follows this tuple.
RESULT_METRICS: tuple[MetricSpec, ...] = (
    MetricSpec("position_rmse"),
    MetricSpec("velocity_rmse"),
    MetricSpec("precision"),
    MetricSpec("recall"),
    MetricSpec("identity_switches", 1),
    MetricSpec("identity_switches_distance_only", 1),
    MetricSpec("mota"),
    MetricSpec("idf1"),
    MetricSpec("idp"),
    MetricSpec("idr"),
    MetricSpec("gospa_p1"),
    MetricSpec("gospa_p2"),
    MetricSpec("track_fragmentation", 1),
    MetricSpec("matched_samples", 0),
    MetricSpec("ground_truth_samples", 0),
    MetricSpec("confirmed_track_samples", 0),
    MetricSpec("unmatched_ground_truth_samples", 0),
    MetricSpec("unmatched_track_samples", 0),
    MetricSpec("coverage_samples", 0),
    MetricSpec("position_coverage_95"),
    MetricSpec("position_coverage_68"),
    MetricSpec("num_tracks", 1),
    MetricSpec("num_confirmed_tracks", 1),
    MetricSpec("num_unmatched_confirmed_tracks", 1),
    MetricSpec("num_duplicate_tracks", 1),
    MetricSpec("class_classified_samples", 1),
    MetricSpec("class_correct_samples", 1),
    MetricSpec("class_accuracy"),
    *(MetricSpec(duplicate_gate_metric(g), 1) for g in DUPLICATE_SENSITIVITY_GATES_M),
    MetricSpec("duplicate_track_samples", 1),
    MetricSpec("nees_samples", 0),
    MetricSpec("nees_position_sum", 1),
    MetricSpec("nees_velocity_sum", 1),
    MetricSpec("anees_position"),
    MetricSpec("anees_velocity"),
    MetricSpec("nis_updates", 1),
    MetricSpec("nis_sum", 1),
    MetricSpec("nis_dof_sum", 1),
    MetricSpec("anis"),
    MetricSpec("mean_age_of_information"),
    MetricSpec("rejected_observations", 1),
    MetricSpec("rejected_out_of_sequence", 1),
    MetricSpec("rejected_invalid", 1),
    MetricSpec("delivered_observations", 1),
    MetricSpec("pending_observations", 1),
    MetricSpec("age_samples", 1),
    MetricSpec("vision_generated", 1),
    MetricSpec("vision_delivered", 1),
    MetricSpec("vision_gate_rejected", 1),
    MetricSpec("vision_lost_competition", 1),
    MetricSpec("vision_unassigned_other", 1),
    MetricSpec("vision_invalid_or_stale", 1),
    MetricSpec("vision_applied", 1),
)

POOLED_RATIOS: tuple[PooledRatio, ...] = (
    PooledRatio("class_accuracy_pooled", "class_correct_samples", "class_classified_samples"),
    PooledRatio("class_classified_fraction_pooled", "class_classified_samples", "matched_samples"),
)

POOLED_CHI_SQUARES: tuple[PooledChiSquare, ...] = (
    PooledChiSquare("anees_position_per_dof_pooled", "nees_position_sum", "nees_samples", 2),
    PooledChiSquare("anees_velocity_per_dof_pooled", "nees_velocity_sum", "nees_samples", 2),
    PooledChiSquare("anis_pooled", "nis_sum", dof_metric="nis_dof_sum"),
)

METRIC_DIGITS: dict[str, int] = {
    **{spec.name: spec.digits for spec in RESULT_METRICS},
    **{ratio.name: ratio.digits for ratio in POOLED_RATIOS},
    **{stat.name: stat.digits for stat in POOLED_CHI_SQUARES},
}


def metric_names(metrics: Sequence[MetricSpec] = RESULT_METRICS) -> list[str]:
    return [spec.name for spec in metrics]


def metric_value(result: Any, name: str) -> float | None:
    """Read a declared metric from an evaluation result.

    Duplicate-gate metrics live in ``num_duplicate_tracks_by_gate``; every other
    metric is a plain attribute.
    """
    for gate in DUPLICATE_SENSITIVITY_GATES_M:
        if name == duplicate_gate_metric(gate):
            counts = getattr(result, "num_duplicate_tracks_by_gate", {})
            value = counts.get(gate_label(gate))
            return None if value is None else float(value)
    value = getattr(result, name)
    return None if value is None else float(value)
