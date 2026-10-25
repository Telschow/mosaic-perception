"""
Markdown rendering of a benchmark payload.

``render_report`` is a pure function: the payload produced by the experiment
runner goes in, Markdown comes out. It has no dependency on the command-line
layer and no wall-clock input, so equal payloads render byte-identical reports.
"""

from __future__ import annotations

from typing import Any


def format_number(value: float | None, digits: int = 3) -> str:
    """Format a metric; undefined values are ``N/A``, never a fabricated zero."""
    return "N/A" if value is None else f"{value:.{digits}f}"


def _tally(payload: dict[str, Any], metric: str, lower_is_better: bool) -> tuple[int, int, int]:
    """Count scenarios where the paired interval favours, opposes or does not settle fusion."""
    better = worse = inconclusive = 0
    for scenario_report in payload["scenarios"]:
        row = scenario_report.get("paired_differences", {}).get(metric)
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


def render_report(payload: dict[str, Any]) -> str:
    protocol = payload["protocol"]
    methods = tuple(protocol["methods"])
    paired_comparison = protocol.get("paired_comparison", {})
    paired_baseline = str(paired_comparison.get("baseline", "range_only")).replace("_", "-")
    paired_treatment = str(paired_comparison.get("treatment", "fused")).replace("_", "-")
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
        "- Methods: range-only (range-bearing sensor only) and fused "
        "(range-bearing + vision bearing)",
        "- Paired: same world states and the same range-sensor random stream per seed; "
        "the fused run only adds vision observations.",
        f"- Evaluation matching gate: {protocol['matching_gate_m']:.2f} m, "
        "one-to-one Hungarian assignment per timestamp.",
        "- Accuracy denominators: matched sample pairs. Recall denominator: all "
        "ground-truth object samples. Precision denominator: all confirmed/coasting "
        "track samples.",
        "- 95% position coverage threshold: chi-square(2, 0.95) = 5.991.",
        "",
        "## Aggregate results",
        "",
        "Values are mean ± sample standard deviation across seeds. `N/A` means the",
        "metric was not defined for any seed (for example, no matched tracks); it is",
        "never a fabricated zero.",
        "",
        "| Scenario | Method | Pos RMSE (m) | Vel RMSE (m/s) | Recall | Precision | Cov95 | Matched/GT (mean) | Unmatched confirmed tracks | Duplicate tracks | Fragmentation |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for scenario_report in payload["scenarios"]:
        scenario_name = scenario_report["scenario"]["name"]
        for method in methods:
            aggregate = scenario_report["aggregate"][method]
            rmse = aggregate.get("position_rmse")
            rmse_std = aggregate.get("position_rmse_std")
            rmse_text = (
                "N/A"
                if rmse is None
                else f"{rmse:.3f} ± {rmse_std:.3f}"
                if rmse_std is not None
                else f"{rmse:.3f}"
            )
            lines.append(
                "| {scenario} | {method} | {rmse} | {vel} | {recall} | {precision} | "
                "{coverage} | {matched}/{gt} | {unmatched} | {duplicates} | {fragmentation} |".format(
                    scenario=scenario_name,
                    method=method,
                    rmse=rmse_text,
                    vel=format_number(aggregate.get("velocity_rmse")),
                    recall=format_number(aggregate.get("recall")),
                    precision=format_number(aggregate.get("precision")),
                    coverage=format_number(aggregate.get("position_coverage_95")),
                    matched=format_number(aggregate.get("matched_samples"), 0),
                    gt=format_number(aggregate.get("ground_truth_samples"), 0),
                    unmatched=format_number(aggregate.get("num_unmatched_confirmed_tracks"), 1),
                    duplicates=format_number(aggregate.get("num_duplicate_tracks"), 1),
                    fragmentation=format_number(aggregate.get("track_fragmentation"), 1),
                )
            )

    lines.extend(
        [
            "",
            f"## Paired differences ({paired_treatment} minus {paired_baseline})",
            "",
            "Mean per-seed difference with a two-sided 95% t interval over seeds. Seeds with",
            "an undefined value on either side are dropped (`n` is the number kept). A",
            "negative RMSE difference favours fusion; for recall, precision and coverage a",
            "positive one does. The interval describes seed-to-seed variation in this",
            "synthetic setup and is not a claim about other worlds.",
            "",
            "| Scenario | Metric | n | Mean diff | 95% interval |",
            "|---|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        for metric, row in scenario_report.get("paired_differences", {}).items():
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

    lines.extend(
        [
            "",
            "## Class estimate accuracy",
            "",
            "Correct / classified over matched samples where both the track's class estimate",
            "and the ground-truth class are known. Range-only runs carry no class",
            "information, so their accuracy is `N/A`, not zero. `Classified` is the mean",
            "number of such samples per seed, out of the matched samples in the results table.",
            "`Class accuracy` is an unweighted mean of per-seed accuracies (seeds with no",
            "classified sample are excluded). `Pooled` is total correct / total classified",
            "over all seeds, and `Classified fraction` is classified / matched samples, so a",
            "method that classifies rarely cannot look accurate on its own: read the three",
            "together.",
            "",
            "| Scenario | Method | Class accuracy | Pooled | Classified fraction | Classified (mean) |",
            "|---|---|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        for method in methods:
            aggregate = scenario_report["aggregate"][method]
            lines.append(
                "| {name} | {method} | {accuracy} | {pooled} | {fraction} | {classified} |".format(
                    name=scenario_report["scenario"]["name"],
                    method=method,
                    accuracy=format_number(aggregate.get("class_accuracy")),
                    pooled=format_number(aggregate.get("class_accuracy_pooled")),
                    fraction=format_number(aggregate.get("class_classified_fraction_pooled")),
                    classified=format_number(aggregate.get("class_classified_samples"), 1),
                )
            )

    lines.extend(
        [
            "",
            "## Duplicate-track sensitivity to the matching gate",
            "",
            "Mean number of duplicate tracks per seed when the evaluation matching gate is",
            "1.0, 2.0 or 3.0 m. The three gates were chosen before running (see the project issue",
            "tracker). The 2.0 m column is the headline gate used everywhere else in this",
            "report when it is the evaluator gate; the others show how much the",
            "duplicate count depends on that choice, not which gate is correct.",
            "",
            "| Scenario | Method | 1.0 m | 2.0 m | 3.0 m |",
            "|---|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        for method in methods:
            aggregate = scenario_report["aggregate"][method]
            lines.append(
                "| {name} | {method} | {g1} | {g2} | {g3} |".format(
                    name=scenario_report["scenario"]["name"],
                    method=method,
                    g1=format_number(aggregate.get("num_duplicate_tracks_gate_1m"), 1),
                    g2=format_number(aggregate.get("num_duplicate_tracks_gate_2m"), 1),
                    g3=format_number(aggregate.get("num_duplicate_tracks_gate_3m"), 1),
                )
            )

    lines.extend(
        [
            "",
            "## Vision observation acceptance (fused method)",
            "",
            "Mean per seed. `Generated` = produced by vision sensors; `Delivered` = left the",
            "pending queue (generated minus those still pending at the end); `Gate-rejected` =",
            "at least one track was evaluated and none passed the chi-square gate;",
            "`Lost competition` = passed the gate for some track but lost the one-to-one",
            "assignment; `Other unassigned` = no evaluable candidate track; `Stale/invalid` =",
            "rejected outside association; `Applied` = used in a track update.",
            "",
            "| Scenario | Generated | Delivered | Gate-rejected | Lost competition | Other unassigned | Stale/invalid | Applied |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        aggregate = scenario_report["aggregate"]["fused"]
        lines.append(
            "| {name} | {g} | {d} | {r} | {c} | {o} | {i} | {a} |".format(
                name=scenario_report["scenario"]["name"],
                g=format_number(aggregate.get("vision_generated"), 1),
                d=format_number(aggregate.get("vision_delivered"), 1),
                r=format_number(aggregate.get("vision_gate_rejected"), 1),
                c=format_number(aggregate.get("vision_lost_competition"), 1),
                o=format_number(aggregate.get("vision_unassigned_other"), 1),
                i=format_number(aggregate.get("vision_invalid_or_stale"), 1),
                a=format_number(aggregate.get("vision_applied"), 1),
            )
        )

    lines.extend(
        [
            "",
            "## Delivery statistics",
            "",
            "Means across seeds where applicable. `Delivered` counts observations removed",
            "from the pending queue, including those subsequently rejected. `Rejected`",
            "includes stale and invalid observations; gate-unmatched detections are not",
            "counted as rejected because range detections may initiate tracks. Unused",
            "vision detections are broken down in the vision acceptance table above.",
            "`AoI n` is the mean number of admitted",
            "observations behind each mean age of information.",
            "",
            "| Scenario | Method | Delivered | Rejected | Out of sequence | Pending at end | Mean AoI (s) | AoI n |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        scenario_name = scenario_report["scenario"]["name"]
        for method in methods:
            aggregate = scenario_report["aggregate"][method]
            lines.append(
                "| {scenario} | {method} | {delivered} | {rejected} | {oos} | "
                "{pending} | {aoi} | {aoi_n} |".format(
                    scenario=scenario_name,
                    method=method,
                    delivered=format_number(aggregate.get("delivered_observations"), 1),
                    rejected=format_number(aggregate.get("rejected_observations"), 1),
                    oos=format_number(aggregate.get("rejected_out_of_sequence"), 1),
                    pending=format_number(aggregate.get("pending_observations"), 1),
                    aoi=format_number(aggregate.get("mean_age_of_information"), 3),
                    aoi_n=format_number(aggregate.get("age_samples"), 1),
                )
            )

    lines.extend(
        [
            "",
            "## Per-seed results",
            "",
            "| Scenario | Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused − Range) |",
            "|---|---|---|---|---|",
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
            lines.append(
                f"| {scenario_name} | {run['seed']} | {format_number(range_rmse)} | "
                f"{format_number(fused_rmse)} | {delta} |"
            )

    def mean_metric(scenario_report: dict[str, Any], method: str, field: str) -> float | None:
        value = scenario_report["aggregate"][method].get(field)
        return None if value is None else float(value)

    rmse_better, rmse_worse, rmse_inconclusive = _tally(payload, "position_rmse", True)
    precision_better, precision_worse, _ = _tally(payload, "precision", False)
    coverage_better, coverage_worse, _ = _tally(payload, "position_coverage_95", False)
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
            "- Scenarios with no matched samples (for example `out_of_sequence`)",
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
