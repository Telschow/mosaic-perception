"""
Declarative description of the per-scenario metric tables in the report.

A table is a heading, an introduction and a list of columns. A column normally
names a declared metric (``evaluation.registry``) and inherits its display
precision; a few columns compose several metrics or show a standard deviation.
Adding a metric to a table is one ``Column`` line.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..evaluation.registry import (
    DUPLICATE_SENSITIVITY_GATES_M,
    METRIC_DIGITS,
    duplicate_gate_metric,
)


def format_number(value: float | None, digits: int = 3) -> str:
    """Format a metric; undefined values are ``N/A``, never a fabricated zero."""
    return "N/A" if value is None else f"{value:.{digits}f}"


@dataclass(frozen=True)
class Column:
    header: str
    key: str | None = None
    digits: int | None = None  # None: the metric's declared digits
    with_std: bool = False  # "mean ± std" using the aggregate's ``<key>_std``
    render: Callable[[dict[str, Any]], str] | None = None  # custom cell

    def cell(self, aggregate: dict[str, Any]) -> str:
        if self.render is not None:
            return self.render(aggregate)
        assert self.key is not None
        digits = self.digits if self.digits is not None else METRIC_DIGITS.get(self.key, 3)
        value = aggregate.get(self.key)
        if self.with_std:
            std = aggregate.get(f"{self.key}_std")
            if value is None:
                return "N/A"
            return (
                f"{value:.{digits}f} ± {std:.{digits}f}"
                if std is not None
                else f"{value:.{digits}f}"
            )
        return format_number(value, digits)


@dataclass(frozen=True)
class TableSpec:
    heading: str
    intro: tuple[str, ...]
    columns: tuple[Column, ...]
    methods: tuple[str, ...] | None = None  # None: every method, with a Method column
    primary: bool = False  # rendered before the paired-difference section


def _pooled_interval(name: str) -> Callable[[dict[str, Any]], str]:
    """Cell showing a pooled per-DOF statistic, its 95% interval and where it falls."""

    def render(aggregate: dict[str, Any]) -> str:
        value = aggregate.get(name)
        low = aggregate.get(f"{name}_low")
        high = aggregate.get(f"{name}_high")
        if value is None or low is None or high is None:
            return "N/A"
        position = "below" if value < low else "above" if value > high else "within"
        return f"{value:.3f} [{low:.3f}, {high:.3f}] {position}"

    return render


def _matched_over_ground_truth(aggregate: dict[str, Any]) -> str:
    matched = format_number(aggregate.get("matched_samples"), METRIC_DIGITS["matched_samples"])
    truth = format_number(
        aggregate.get("ground_truth_samples"), METRIC_DIGITS["ground_truth_samples"]
    )
    return f"{matched}/{truth}"


RESULTS_TABLE = TableSpec(
    heading="Aggregate results",
    intro=(
        "Values are mean ± sample standard deviation across seeds. `N/A` means the",
        "metric was not defined for any seed (for example, no matched tracks); it is",
        "never a fabricated zero.",
    ),
    columns=(
        Column("Pos RMSE (m)", "position_rmse", with_std=True),
        Column("Vel RMSE (m/s)", "velocity_rmse"),
        Column("Recall", "recall"),
        Column("Precision", "precision"),
        Column("Cov95", "position_coverage_95"),
        Column("Matched/GT (mean)", render=_matched_over_ground_truth),
        Column("Unmatched confirmed tracks", "num_unmatched_confirmed_tracks"),
        Column("Duplicate tracks", "num_duplicate_tracks"),
        Column("ID switches", "identity_switches"),
        Column("ID switches (distance-only)", "identity_switches_distance_only"),
        Column("Fragmentation", "track_fragmentation"),
        Column("MOTA", "mota"),
        Column("IDF1", "idf1"),
        Column("GOSPA (p=1, m)", "gospa_p1"),
    ),
    primary=True,
)

CLASS_TABLE = TableSpec(
    heading="Class estimate accuracy",
    intro=(
        "Correct / classified over matched samples where both the track's class estimate",
        "and the ground-truth class are known. Range-only runs carry no class",
        "information, so their accuracy is `N/A`, not zero. `Classified` is the mean",
        "number of such samples per seed, out of the matched samples in the results table.",
        "`Class accuracy` is an unweighted mean of per-seed accuracies (seeds with no",
        "classified sample are excluded). `Pooled` is total correct / total classified",
        "over all seeds, and `Classified fraction` is classified / matched samples, so a",
        "method that classifies rarely cannot look accurate on its own: read the three",
        "together.",
    ),
    columns=(
        Column("Class accuracy", "class_accuracy"),
        Column("Pooled", "class_accuracy_pooled"),
        Column("Classified fraction", "class_classified_fraction_pooled"),
        Column("Classified (mean)", "class_classified_samples"),
    ),
)

CONSISTENCY_TABLE = TableSpec(
    heading="Estimator consistency (NEES and NIS)",
    intro=(
        "Statistics per degree of freedom, pooled over seeds; the nominal value for a",
        "consistent filter is 1.0 and the bracket is the two-sided 95% chi-square interval",
        "for the pooled degrees of freedom. `within`, `above` or `below` says where the value",
        "falls: above means overconfident, below means underconfident.",
        "",
        "- NEES (position and velocity, 2 DOF each) uses only samples matched to a ground-truth",
        "  object inside the 2 m matching gate, so it is conditioned on that gate;",
        "  `GT samples outside gate` is the mean number of ground-truth samples excluded.",
        "- NIS uses the filter's own innovations for every applied update, with no ground",
        "  truth. Updates exist only after gating, so NIS is truncated and sits slightly",
        "  below 1.0 even for a correct filter.",
        "- Samples within one track are correlated and seeds share the scenario, so the",
        "  intervals assume more independence than there is and are optimistic.",
    ),
    columns=(
        Column("Position NEES per DOF", render=_pooled_interval("anees_position_per_dof_pooled")),
        Column("Velocity NEES per DOF", render=_pooled_interval("anees_velocity_per_dof_pooled")),
        Column("NIS per DOF", render=_pooled_interval("anis_pooled")),
        Column("NEES samples (mean)", "nees_samples"),
        Column("NIS updates (mean)", "nis_updates"),
        Column("GT samples outside gate", "unmatched_ground_truth_samples"),
    ),
)

DUPLICATE_GATE_TABLE = TableSpec(
    heading="Duplicate-track sensitivity to the matching gate",
    intro=(
        "Mean number of duplicate tracks per seed when the evaluation matching gate is",
        "1.0, 2.0 or 3.0 m. The three gates were chosen before running (see the project issue",
        "tracker). The 2.0 m column is the headline gate used everywhere else in this",
        "report when it is the evaluator gate; the others show how much the",
        "duplicate count depends on that choice, not which gate is correct.",
    ),
    columns=tuple(
        Column(f"{gate:.1f} m", duplicate_gate_metric(gate))
        for gate in DUPLICATE_SENSITIVITY_GATES_M
    ),
)

VISION_TABLE = TableSpec(
    heading="Vision observation acceptance (fused method)",
    intro=(
        "Mean per seed. `Generated` = produced by vision sensors; `Delivered` = left the",
        "pending queue (generated minus those still pending at the end); `Gate-rejected` =",
        "at least one track was evaluated and none passed the chi-square gate;",
        "`Lost competition` = passed the gate for some track but lost the one-to-one",
        "assignment; `Other unassigned` = no evaluable candidate track; `Stale/invalid` =",
        "rejected outside association; `Applied` = used in a track update.",
    ),
    columns=(
        Column("Generated", "vision_generated"),
        Column("Delivered", "vision_delivered"),
        Column("Gate-rejected", "vision_gate_rejected"),
        Column("Lost competition", "vision_lost_competition"),
        Column("Other unassigned", "vision_unassigned_other"),
        Column("Stale/invalid", "vision_invalid_or_stale"),
        Column("Applied", "vision_applied"),
    ),
    methods=("fused",),
)

DELIVERY_TABLE = TableSpec(
    heading="Delivery statistics",
    intro=(
        "Means across seeds where applicable. `Delivered` counts observations removed",
        "from the pending queue, including those subsequently rejected. `Rejected`",
        "includes stale and invalid observations; gate-unmatched detections are not",
        "counted as rejected because range detections may initiate tracks. Unused",
        "vision detections are broken down in the vision acceptance table above.",
        "`AoI n` is the mean number of admitted",
        "observations behind each mean age of information.",
    ),
    columns=(
        Column("Delivered", "delivered_observations"),
        Column("Rejected", "rejected_observations"),
        Column("Out of sequence", "rejected_out_of_sequence"),
        Column("Pending at end", "pending_observations"),
        Column("Mean AoI (s)", "mean_age_of_information"),
        Column("AoI n", "age_samples"),
    ),
)

TABLES: tuple[TableSpec, ...] = (
    RESULTS_TABLE,
    CLASS_TABLE,
    CONSISTENCY_TABLE,
    DUPLICATE_GATE_TABLE,
    VISION_TABLE,
    DELIVERY_TABLE,
)


def render_table(spec: TableSpec, payload: dict[str, Any], methods: tuple[str, ...]) -> list[str]:
    """Render one table as Markdown lines, starting with a blank line."""
    shown_methods = spec.methods if spec.methods is not None else methods
    with_method = spec.methods is None
    headers = ["Scenario", *(["Method"] if with_method else []), *(c.header for c in spec.columns)]
    lines = [
        "",
        f"## {spec.heading}",
        "",
        *spec.intro,
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "---|" * len(headers),
    ]
    for scenario_report in payload["scenarios"]:
        name = scenario_report["scenario"]["name"]
        for method in shown_methods:
            aggregate = scenario_report["aggregate"][method]
            cells = [
                name,
                *([method] if with_method else []),
                *(c.cell(aggregate) for c in spec.columns),
            ]
            lines.append("| " + " | ".join(cells) + " |")
    return lines
