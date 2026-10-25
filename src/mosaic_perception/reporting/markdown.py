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


def render_report(payload: dict[str, Any]) -> str:
    protocol = payload["protocol"]
    methods = tuple(protocol["methods"])
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

    wins = 0
    losses = 0
    ties = 0
    for scenario_report in payload["scenarios"]:
        range_rmse = mean_metric(scenario_report, "range_only", "position_rmse")
        fused_rmse = mean_metric(scenario_report, "fused", "position_rmse")
        if range_rmse is None or fused_rmse is None:
            continue
        if abs(fused_rmse - range_rmse) < 0.01:
            ties += 1
        elif fused_rmse < range_rmse:
            wins += 1
        else:
            losses += 1

    precision_wins = 0
    precision_losses = 0
    coverage_wins = 0
    coverage_losses = 0
    for scenario_report in payload["scenarios"]:
        range_precision = mean_metric(scenario_report, "range_only", "precision")
        fused_precision = mean_metric(scenario_report, "fused", "precision")
        if range_precision is not None and fused_precision is not None:
            if fused_precision > range_precision:
                precision_wins += 1
            elif fused_precision < range_precision:
                precision_losses += 1
        range_coverage = mean_metric(scenario_report, "range_only", "position_coverage_95")
        fused_coverage = mean_metric(scenario_report, "fused", "position_coverage_95")
        if range_coverage is not None and fused_coverage is not None:
            if fused_coverage > range_coverage:
                coverage_wins += 1
            elif fused_coverage < range_coverage:
                coverage_losses += 1

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- On the aggregate position RMSE, fused was better in {wins} scenario(s),",
            f"  worse in {losses} scenario(s), and within 0.01 m in {ties} scenario(s).",
            f"- Fused precision was higher in {precision_wins} scenario(s) and lower",
            f"  in {precision_losses}. Fused 95% coverage was higher in {coverage_wins}",
            f"  scenario(s) and lower in {coverage_losses}. Accuracy alone does not",
            "  establish that fusion improved association or calibration.",
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
            "  development seeds, not statistical or held-out claims.",
            "- `track_fragmentation` counts interruptions in an object's matched frames, summed",
            "  over objects; it is independent of identity switches.",
            "- `identity_switches` counts changes of matched track ID for the same",
            "  ground-truth object across consecutive matched frames.",
            "- Coverage is empirical and only defined over matched samples; its",
            "  denominator is reported in `per_seed.csv` and `benchmark.json`.",
            "- Scenarios with no matched samples (for example `out_of_sequence`)",
            "  report `N/A` accuracy because their observations are rejected as stale;",
            "  that is an explicit non-result, not a zero-error result.",
            "- This report uses the seeds shown above. The reserved held-out range",
            "  (25-49) is not included here and no held-out claim is made.",
            "",
            "## Limitations",
            "",
            "- Synthetic 2-D world; simplified sensor models, not hardware validation.",
            "- Vision-only track initiation is not supported (bearing alone cannot",
            "  determine range).",
            "- Out-of-sequence observations older than one tracker epoch are explicitly",
            "  rejected and counted, not silently dropped. Their accuracy impact is",
            "  therefore not represented as a successful fusion result.",
            "- Development seeds are used for debugging. The documented held-out seed",
            "  range (25-49) is only a held-out evaluation when those seeds are actually",
            "  present in the `Seeds` line above.",
            "",
        ]
    )
    return "\n".join(lines)
