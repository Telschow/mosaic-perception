"""
Markdown rendering of a benchmark payload.

``render_report`` is a pure function: the payload produced by the experiment
runner goes in, Markdown comes out. It has no dependency on the command-line
layer and no wall-clock input, so equal payloads render byte-identical reports.
"""

from __future__ import annotations

from typing import Any

from .tables import TABLES, TableSpec, format_number, render_table

_PRIMARY_COMPARISON = "fused_vs_range_only"
_DEFAULT_COMPARISONS = [
    {"name": _PRIMARY_COMPARISON, "baseline": "range_only", "treatment": "fused"}
]


def _tally(
    payload: dict[str, Any],
    metric: str,
    lower_is_better: bool,
    comparison: str = _PRIMARY_COMPARISON,
) -> tuple[int, int, int]:
    """Count scenarios where the paired interval favours, opposes or does not settle the treatment."""
    better = worse = inconclusive = 0
    for scenario_report in payload["scenarios"]:
        row = scenario_report.get("paired_differences", {}).get(comparison, {}).get(metric)
        if not row or row["n"] == 0:
            continue
        if row["ci95_low"] is None:
            inconclusive += 1
        elif row["ci95_high"] < 0:
            better, worse = (better + 1, worse) if lower_is_better else (better, worse + 1)
        elif row["ci95_low"] > 0:
            better, worse = (better, worse + 1) if lower_is_better else (better + 1, worse)
        else:
            inconclusive += 1
    return better, worse, inconclusive


def render_report(payload: dict[str, Any], tables: tuple[TableSpec, ...] = TABLES) -> str:
    protocol = payload["protocol"]
    methods = tuple(protocol["methods"])
    comparisons = protocol.get("paired_comparisons", _DEFAULT_COMPARISONS)
    code = payload["code"]
    lines = [
        "# Mosaic Benchmark Report",
        "",
        "This report is generated from the code in this repository. It contains no",
        "hand-edited numbers and no wall-clock timestamps, so repeated runs with the",
        "same seeds and commit are byte-identical.",
        "",
        "## Code and protocol",
        "",
        f"- Package version: `{code['package_version']}`",
        f"- Git commit: `{code['git_commit'] or 'not available'}`",
        f"- Seeds: {', '.join(str(seed) for seed in protocol['seeds'])}",
        f"- Seed group: {protocol['seed_group']}",
        f"- Duration: {protocol['duration_s']} s at dt={protocol['dt_s']} s",
        f"- Objects per world: {protocol['num_objects']}",
        "- Methods: range-only (range-bearing sensor only), fused (range-bearing + vision "
        "bearing) and, where present, fused-bias-estimated (fused plus an estimate of the "
        "vision bearing bias, subtracted before gating and updating)",
        "- Paired: same world states and the same sensor random streams per seed; "
        "the fused runs only add vision observations, and bias estimation changes only how "
        "they are used.",
        f"- Evaluation matching gate: {protocol['matching_gate_m']:.2f} m, "
        "one-to-one Hungarian assignment per timestamp"
        + (
            ", preferring each object's previous track while it stays inside the gate."
            if protocol.get("matching_continuity")
            else " (distance only)."
        ),
        "- Accuracy denominators: matched sample pairs. Recall denominator: all "
        "ground-truth object samples. Precision denominator: all confirmed/coasting "
        "track samples.",
        "- 95% position coverage threshold: chi-square(2, 0.95) = 5.991.",
    ]
    for table in (t for t in tables if t.primary):
        lines.extend(render_table(table, payload, methods))

    for index, comparison in enumerate(comparisons):
        treatment = str(comparison["treatment"]).replace("_", "-")
        baseline = str(comparison["baseline"]).replace("_", "-")
        intro = (
            [
                "Mean per-seed difference with a two-sided 95% t interval over seeds. Seeds with",
                "an undefined value on either side are dropped (`n` is the number kept). Lower is",
                "better for the RMSE metrics and GOSPA, so a negative difference favours the",
                "treatment; higher is better for recall, precision, coverage, MOTA and IDF1, so a",
                "positive one does. The interval describes seed-to-seed variation in this synthetic",
                "setup and is not a claim about other worlds.",
            ]
            if index == 0
            else ["Same conventions as the first comparison."]
        )
        lines.extend(
            [
                "",
                f"## Paired differences ({treatment} minus {baseline})",
                "",
                *intro,
                "",
                "| Scenario | Metric | n | Mean diff | 95% interval |",
                "|---|---|---|---|---|",
            ]
        )
        for scenario_report in payload["scenarios"]:
            rows = scenario_report.get("paired_differences", {}).get(comparison["name"], {})
            for metric, row in rows.items():
                interval = (
                    "N/A"
                    if row["ci95_low"] is None
                    else f"[{row['ci95_low']:+.3f}, {row['ci95_high']:+.3f}]"
                )
                mean = "N/A" if row["mean"] is None else f"{row['mean']:+.3f}"
                lines.append(
                    f"| {scenario_report['scenario']['name']} | {metric} | {row['n']} | "
                    f"{mean} | {interval} |"
                )

    for table in (t for t in tables if not t.primary):
        lines.extend(render_table(table, payload, methods))

    lines.extend(
        [
            "",
            "## Per-seed results",
            "",
            "| Scenario | Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused − Range) | Bias-estimated RMSE (m) |",
            "|---|---|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        scenario_name = scenario_report["scenario"]["name"]
        for run in scenario_report["runs"]:
            range_rmse = run["range_only"].get("position_rmse")
            fused_rmse = run["fused"].get("position_rmse")
            delta = (
                f"{fused_rmse - range_rmse:+.3f}"
                if range_rmse is not None and fused_rmse is not None
                else "N/A"
            )
            bias_rmse = run.get("fused_bias_estimated", {}).get("position_rmse")
            lines.append(
                f"| {scenario_name} | {run['seed']} | {format_number(range_rmse)} | "
                f"{format_number(fused_rmse)} | {delta} | {format_number(bias_rmse)} |"
            )

    def mean_metric(scenario_report: dict[str, Any], method: str, field: str) -> float | None:
        value = scenario_report["aggregate"][method].get(field)
        return None if value is None else float(value)

    rmse_better, rmse_worse, rmse_inconclusive = _tally(payload, "position_rmse", True)
    precision_better, precision_worse, _ = _tally(payload, "precision", False)
    coverage_better, coverage_worse, _ = _tally(payload, "position_coverage_95", False)
    plain_better, plain_worse, plain_inconclusive = _tally(
        payload, "position_rmse_distance_only", True
    )
    mota_better, mota_worse, _ = _tally(payload, "mota", False)
    idf1_better, idf1_worse, _ = _tally(payload, "idf1", False)
    gospa_better, gospa_worse, _ = _tally(payload, "gospa_p1", True)
    extra_comparison_lines: list[str] = []
    for comparison in comparisons[1:]:
        name = comparison["name"]
        treatment = str(comparison["treatment"]).replace("_", "-")
        baseline = str(comparison["baseline"]).replace("_", "-")
        parts = []
        for label, metric, lower in (
            ("position RMSE", "position_rmse", True),
            ("precision", "precision", False),
            ("MOTA", "mota", False),
            ("GOSPA", "gospa_p1", True),
        ):
            better, worse, inconclusive = _tally(payload, metric, lower, name)
            parts.append(
                f"{label}: better in {better}, worse in {worse}, inconclusive in {inconclusive}"
            )
        extra_comparison_lines.append(
            f"- {treatment} against {baseline} (interval excludes zero): " + "; ".join(parts) + "."
        )
    seed_group = protocol.get("seed_group", "unknown")
    if seed_group == "development":
        seed_note = (
            f"- This report uses {len(protocol['seeds'])} development seed(s). The reserved "
            "held-out range (25-49) is not included here and no held-out claim is made."
        )
        seed_limit = (
            "- Results on development seeds include choices made while building the "
            "workbench and are not confirmatory. A held-out evaluation exists only when the "
            "reserved seeds (25-49) appear in the `Seeds` line above."
        )
    else:
        seed_note = (
            f"- This run includes seeds outside the development range ({seed_group}); "
            "do not read it as the development benchmark. A held-out evaluation requires "
            "a single run on frozen code, reported separately."
        )
        seed_limit = (
            "- This run uses seeds outside the development range; whether it is a "
            "held-out evaluation depends on how the code was frozen before it."
        )
    if len(protocol["seeds"]) < 2:
        seed_note += " Intervals need at least two seeds, so they are `N/A` here."

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Position RMSE: the paired interval excludes zero in favour of fusion in {rmse_better} scenario(s) and against fusion in {rmse_worse} scenario(s); it includes zero (or has fewer than two seeds) in {rmse_inconclusive} scenario(s).",
            f"- The RMSE tally depends on the matcher: with a distance-only matcher the interval excludes zero in favour of fusion in {plain_better} scenario(s), against fusion in {plain_worse}, and includes zero in {plain_inconclusive}.",
            f"- MOTA, IDF1 and GOSPA (interval excludes zero): fusion better in {mota_better}, {idf1_better} and {gospa_better} scenario(s) and worse in {mota_worse}, {idf1_worse} and {gospa_worse}, respectively.",
            *extra_comparison_lines,
            f"- Fused precision is lower (interval excludes zero) in {precision_worse} scenario(s) and higher in {precision_better}; fused 95% coverage is lower in {coverage_worse} and higher in {coverage_better}. Accuracy alone does not establish that fusion improved association or calibration.",
            "- Fusion is not guaranteed to improve accuracy. Systematic sensor bias,",
            "  miscalibrated uncertainty, missed detections, false observations and",
            "  association errors can all reverse the comparison.",
            "- Precision is sample-based: matched samples over all confirmed/coasting",
            "  track samples. `Unmatched confirmed tracks` are confirmed track IDs never",
            "  matched to a ground-truth object. `Duplicate tracks` is the subset that, in",
            "  at least one frame, was left unmatched while a ground-truth object lay",
            "  within the matching gate (the object had been claimed by another track).",
            "  The rest were never near an unclaimed object under that gate.",
            "- `sensor_disagreement_large_bias` (0.12 rad) is a gate-rejection",
            "  experiment: see the vision acceptance table for how many biased",
            "  observations the gate rejected versus applied. It does not measure the",
            "  cost of fusing biased data.",
            "- `sensor_disagreement_within_gate` (0.015 rad) applies a bias small",
            "  enough to pass the gate often, so it measures what happens when biased",
            "  vision data is actually fused. Neither scenario establishes real-world",
            "  sensor-fusion performance; both are descriptive synthetic results on",
            "  results; intervals reflect seed-to-seed variation only.",
            "- `track_fragmentation` counts interruptions in an object's matched frames, summed",
            "  over objects; it is independent of identity switches.",
            "- `identity_switches` counts changes of matched track ID for the same",
            "  ground-truth object across consecutive matched frames.",
            "- Coverage is empirical and only defined over matched samples; its",
            "  denominator is reported in `per_seed.csv` and `benchmark.json`.",
            "- Scenarios with no matched samples (for example `stale_rejection`)",
            "  report `N/A` accuracy because their observations are rejected as stale;",
            "  that is an explicit non-result, not a zero-error result.",
            seed_note,
            "",
            "## Limitations",
            "",
            "- Synthetic 2-D world; simplified sensor models, not hardware validation.",
            "- Vision-only track initiation is not supported (bearing alone cannot",
            "  determine range).",
            "- Out-of-sequence observations older than one tracker epoch are explicitly",
            "  rejected and counted, not silently dropped. Their accuracy impact is",
            "  therefore not represented as a successful fusion result.",
            seed_limit,
            "",
        ]
    )
    return "\n".join(lines)
