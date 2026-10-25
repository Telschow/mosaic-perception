"""
Command-line interface for Mosaic.

All experiment commands use the shared runner in ``mosaic_perception.experiment``
so the CLI, the Streamlit app and the tests execute the same pipeline.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Annotated, Any

import numpy as np
import typer
from rich.console import Console
from rich.table import Table

from .. import __version__
from ..domain.models import EvaluationResult
from ..experiment import (
    METHODS,
    PairedRun,
    current_git_commit,
    run_pair,
)
from ..scenarios import available_scenarios, resolve_scenario

app = typer.Typer(help="Mosaic: multi-sensor perception tracking workbench")
console = Console()

_RESULT_FIELDS = [
    "position_rmse",
    "velocity_rmse",
    "precision",
    "recall",
    "identity_switches",
    "track_fragmentation",
    "matched_samples",
    "ground_truth_samples",
    "confirmed_track_samples",
    "unmatched_ground_truth_samples",
    "unmatched_track_samples",
    "coverage_samples",
    "position_coverage_95",
    "position_coverage_68",
    "num_tracks",
    "num_confirmed_tracks",
    "num_unmatched_confirmed_tracks",
    "num_duplicate_tracks",
    "class_classified_samples",
    "class_correct_samples",
    "class_accuracy",
    "num_duplicate_tracks_gate_1m",
    "num_duplicate_tracks_gate_2m",
    "num_duplicate_tracks_gate_3m",
    "duplicate_track_samples",
    "mean_age_of_information",
    "rejected_observations",
    "rejected_out_of_sequence",
    "rejected_invalid",
    "delivered_observations",
    "pending_observations",
    "age_samples",
    "vision_generated",
    "vision_delivered",
    "vision_gate_rejected",
    "vision_lost_competition",
    "vision_unassigned_other",
    "vision_invalid_or_stale",
    "vision_applied",
]


def _parse_seeds(value: str) -> list[int]:
    """Parse ``1,2,3`` or ``1-5`` (or a mix) into a deterministic seed list."""
    seeds: list[int] = []
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start, end = int(start_text), int(end_text)
            if end < start:
                raise typer.BadParameter(f"invalid seed range {token!r}")
            seeds.extend(range(start, end + 1))
        else:
            seeds.append(int(token))
    if not seeds:
        raise typer.BadParameter("at least one seed is required")
    if len(set(seeds)) != len(seeds):
        raise typer.BadParameter("seed list contains duplicates")
    return seeds


def _scenario_names(value: str) -> list[str]:
    if value.strip().lower() == "all":
        return available_scenarios()
    names = [name.strip() for name in value.split(",") if name.strip()]
    if not names:
        raise typer.BadParameter("at least one scenario is required")
    unknown = [name for name in names if name not in available_scenarios()]
    if unknown:
        raise typer.BadParameter(
            f"unknown scenario(s) {', '.join(unknown)}; "
            f"available: {', '.join(available_scenarios())}"
        )
    return names


def _result_payload(result: EvaluationResult, include_frames: bool = False) -> dict[str, Any]:
    """Serialise deterministic scalar metrics without volatile environment data."""
    payload = result.model_dump(mode="json")
    payload.pop("config", None)
    payload.pop("git_commit", None)
    if not include_frames:
        payload.pop("per_frame_metrics", None)
    return payload


def _fmt(value: float | None, digits: int = 3) -> str:
    return "N/A" if value is None else f"{value:.{digits}f}"


def _print_pair(pair: PairedRun) -> None:
    table = Table(title=f"{pair.scenario.name} (seed={pair.scenario.seed})")
    for column in (
        "Method",
        "Pos RMSE (m)",
        "Vel RMSE (m/s)",
        "Recall",
        "Precision",
        "Cov95",
        "Matched",
        "Tracks",
        "Unmatched confirmed tracks",
    ):
        table.add_column(column)
    for method in METHODS:
        result = pair.record(method).result
        table.add_row(
            method,
            _fmt(result.position_rmse),
            _fmt(result.velocity_rmse),
            _fmt(result.recall),
            _fmt(result.precision),
            _fmt(result.position_coverage_95),
            f"{result.matched_samples}/{result.ground_truth_samples}",
            f"{result.num_confirmed_tracks}/{result.num_tracks}",
            str(result.num_unmatched_confirmed_tracks),
        )
    console.print(table)


def _aggregate(results: list[EvaluationResult]) -> dict[str, Any]:
    """Aggregate deterministic metrics over seeds (mean and sample std)."""
    aggregate: dict[str, Any] = {"num_seeds": len(results)}
    for field in _RESULT_FIELDS:
        values = [
            float(value) for result in results if (value := getattr(result, field)) is not None
        ]
        if not values:
            aggregate[field] = None
            aggregate[f"{field}_std"] = None
            continue
        aggregate[field] = float(np.mean(values))
        aggregate[f"{field}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    return aggregate


def _write_per_seed_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = ["scenario", "seed", "method", *_RESULT_FIELDS]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})


def _run_experiment(
    scenarios: list[str],
    seeds: list[int],
    duration: float,
    dt: float,
    num_objects: int,
    output: Path | None,
    *,
    command: str,
) -> dict[str, Any]:
    commit = current_git_commit()
    scenario_reports: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for scenario_name in scenarios:
        runs: list[dict[str, Any]] = []
        results_by_method: dict[str, list[EvaluationResult]] = {method: [] for method in METHODS}
        first_config: dict[str, Any] | None = None
        for seed in seeds:
            scenario = resolve_scenario(
                scenario_name,
                seed=seed,
                duration=duration,
                dt=dt,
                num_objects=num_objects,
            )
            if first_config is None:
                first_config = scenario.model_dump(mode="json")
            pair = run_pair(scenario)
            console.print(
                f"  {scenario_name} seed={seed}: "
                f"range RMSE={_fmt(pair.range_only.result.position_rmse)} m, "
                f"fused RMSE={_fmt(pair.fused.result.position_rmse)} m"
            )
            run_payload: dict[str, Any] = {"seed": seed}
            for method in METHODS:
                record = pair.record(method)
                results_by_method[method].append(record.result)
                run_payload[method] = _result_payload(record.result)
                csv_rows.append(
                    {
                        "scenario": scenario_name,
                        "seed": seed,
                        "method": method,
                        **_result_payload(record.result),
                    }
                )
            runs.append(run_payload)
        scenario_reports.append(
            {
                "scenario": first_config,
                "runs": runs,
                "aggregate": {method: _aggregate(results_by_method[method]) for method in METHODS},
            }
        )

    payload: dict[str, Any] = {
        "schema_version": 2,
        "command": command,
        "code": {"package_version": __version__, "git_commit": commit},
        "protocol": {
            "matching_gate_m": 2.0,
            "position_coverage_95_threshold": 5.991,
            "seed_group": ("development" if max(seeds) <= 24 else "custom_or_held_out"),
            "seeds": seeds,
            "duration_s": duration,
            "dt_s": dt,
            "num_objects": num_objects,
            "methods": list(METHODS),
            "paired": "same world states and range-sensor random stream per seed",
            "metrics_document": "docs/metrics.md",
        },
        "scenarios": scenario_reports,
    }

    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        with (output / "benchmark.json").open("w") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
        _write_per_seed_csv(output / "per_seed.csv", csv_rows)
        (output / "report.md").write_text(_render_report(payload))
        console.print(f"[green]Canonical artifacts written to {output}[/green]")
    return payload


def _render_report(payload: dict[str, Any]) -> str:
    protocol = payload["protocol"]
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
        for method in METHODS:
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
                    vel=_fmt(aggregate.get("velocity_rmse")),
                    recall=_fmt(aggregate.get("recall")),
                    precision=_fmt(aggregate.get("precision")),
                    coverage=_fmt(aggregate.get("position_coverage_95")),
                    matched=_fmt(aggregate.get("matched_samples"), 0),
                    gt=_fmt(aggregate.get("ground_truth_samples"), 0),
                    unmatched=_fmt(aggregate.get("num_unmatched_confirmed_tracks"), 1),
                    duplicates=_fmt(aggregate.get("num_duplicate_tracks"), 1),
                    fragmentation=_fmt(aggregate.get("track_fragmentation"), 1),
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
            "",
            "| Scenario | Method | Class accuracy | Classified (mean) |",
            "|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        for method in METHODS:
            aggregate = scenario_report["aggregate"][method]
            lines.append(
                "| {name} | {method} | {accuracy} | {classified} |".format(
                    name=scenario_report["scenario"]["name"],
                    method=method,
                    accuracy=_fmt(aggregate.get("class_accuracy")),
                    classified=_fmt(aggregate.get("class_classified_samples"), 1),
                )
            )

    lines.extend(
        [
            "",
            "## Duplicate-track sensitivity to the matching gate",
            "",
            "Mean number of duplicate tracks per seed when the evaluation matching gate is",
            "1.0, 2.0 or 3.0 m. The gates were fixed before any run. The 2.0 m column is the",
            "headline gate used everywhere else in this report; the others show how much the",
            "duplicate count depends on that choice, not which gate is correct.",
            "",
            "| Scenario | Method | 1.0 m | 2.0 m | 3.0 m |",
            "|---|---|---|---|---|",
        ]
    )
    for scenario_report in payload["scenarios"]:
        for method in METHODS:
            aggregate = scenario_report["aggregate"][method]
            lines.append(
                "| {name} | {method} | {g1} | {g2} | {g3} |".format(
                    name=scenario_report["scenario"]["name"],
                    method=method,
                    g1=_fmt(aggregate.get("num_duplicate_tracks_gate_1m"), 1),
                    g2=_fmt(aggregate.get("num_duplicate_tracks_gate_2m"), 1),
                    g3=_fmt(aggregate.get("num_duplicate_tracks_gate_3m"), 1),
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
                g=_fmt(aggregate.get("vision_generated"), 1),
                d=_fmt(aggregate.get("vision_delivered"), 1),
                r=_fmt(aggregate.get("vision_gate_rejected"), 1),
                c=_fmt(aggregate.get("vision_lost_competition"), 1),
                o=_fmt(aggregate.get("vision_unassigned_other"), 1),
                i=_fmt(aggregate.get("vision_invalid_or_stale"), 1),
                a=_fmt(aggregate.get("vision_applied"), 1),
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
        for method in METHODS:
            aggregate = scenario_report["aggregate"][method]
            lines.append(
                "| {scenario} | {method} | {delivered} | {rejected} | {oos} | "
                "{pending} | {aoi} | {aoi_n} |".format(
                    scenario=scenario_name,
                    method=method,
                    delivered=_fmt(aggregate.get("delivered_observations"), 1),
                    rejected=_fmt(aggregate.get("rejected_observations"), 1),
                    oos=_fmt(aggregate.get("rejected_out_of_sequence"), 1),
                    pending=_fmt(aggregate.get("pending_observations"), 1),
                    aoi=_fmt(aggregate.get("mean_age_of_information"), 3),
                    aoi_n=_fmt(aggregate.get("age_samples"), 1),
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
                f"| {scenario_name} | {run['seed']} | {_fmt(range_rmse)} | "
                f"{_fmt(fused_rmse)} | {delta} |"
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


@app.command()
def run(
    scenario: Annotated[str, typer.Option(help="Scenario name")] = "nominal",
    seed: Annotated[int, typer.Option(help="Random seed")] = 42,
    duration: Annotated[float, typer.Option(help="Simulation duration in seconds")] = 10.0,
    num_objects: Annotated[int, typer.Option(help="Number of ground-truth objects")] = 3,
    output: Annotated[Path | None, typer.Option(help="Output directory")] = None,
):
    """Run one scenario with both methods."""
    if scenario not in available_scenarios():
        raise typer.BadParameter(
            f"unknown scenario {scenario!r}; available: {', '.join(available_scenarios())}"
        )
    console.print(f"[bold blue]Running scenario {scenario} (seed={seed})[/bold blue]")
    config = resolve_scenario(scenario, seed=seed, duration=duration, num_objects=num_objects)
    pair = run_pair(config)
    _print_pair(pair)

    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        payload = {
            "scenario": config.model_dump(mode="json"),
            "code": {"package_version": __version__, "git_commit": current_git_commit()},
            "range_only": _result_payload(pair.range_only.result, include_frames=True),
            "fused": _result_payload(pair.fused.result, include_frames=True),
        }
        with (output / "metrics.json").open("w") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
        console.print(f"[green]Results saved to {output / 'metrics.json'}[/green]")


@app.command()
def compare(
    scenario: Annotated[str, typer.Option(help="Scenario name")] = "nominal",
    seeds: Annotated[str, typer.Option(help="Seeds, e.g. 1,2,3 or 1-5")] = "1,2,3",
    duration: Annotated[float, typer.Option(help="Simulation duration in seconds")] = 10.0,
    num_objects: Annotated[int, typer.Option(help="Number of ground-truth objects")] = 3,
    output: Annotated[Path | None, typer.Option(help="Output directory")] = None,
):
    """Compare methods across multiple seeds and scenarios."""
    names = _scenario_names(scenario)
    seed_list = _parse_seeds(seeds)
    console.print(f"[bold blue]Comparing {names} across seeds {seed_list}[/bold blue]")
    payload = _run_experiment(
        names,
        seed_list,
        duration,
        0.1,
        num_objects,
        output,
        command="compare",
    )
    if output is None:
        for scenario_report in payload["scenarios"]:
            name = scenario_report["scenario"]["name"]
            table = Table(title=f"Comparison: {name}")
            table.add_column("Method")
            table.add_column("Pos RMSE (m)")
            table.add_column("Recall")
            table.add_column("Precision")
            table.add_column("Cov95")
            for method in METHODS:
                aggregate = scenario_report["aggregate"][method]
                table.add_row(
                    method,
                    _fmt(aggregate.get("position_rmse")),
                    _fmt(aggregate.get("recall")),
                    _fmt(aggregate.get("precision")),
                    _fmt(aggregate.get("position_coverage_95")),
                )
            console.print(table)


def _benchmark_impl(
    scenario: str,
    seeds: str,
    duration: float,
    num_objects: int,
    output: Path,
    command: str,
) -> None:
    names = _scenario_names(scenario)
    seed_list = _parse_seeds(seeds)
    console.print(f"[bold blue]Benchmark: {names} seeds={seed_list}[/bold blue]")
    _run_experiment(
        names,
        seed_list,
        duration,
        0.1,
        num_objects,
        output,
        command=command,
    )
    console.print(f"[green]Benchmark artifacts saved to {output}[/green]")


@app.command()
def benchmark(
    scenario: Annotated[
        str, typer.Option(help="Scenario name, comma-separated list, or 'all'")
    ] = "nominal",
    seeds: Annotated[str, typer.Option(help="Seeds, e.g. 1,2,3 or 1-5")] = "1-5",
    duration: Annotated[float, typer.Option(help="Simulation duration in seconds")] = 10.0,
    num_objects: Annotated[int, typer.Option(help="Number of ground-truth objects")] = 3,
    output: Annotated[Path, typer.Option(help="Output directory")] = Path("artifacts/benchmark"),
):
    """Run the reproducible benchmark and write canonical artifacts."""
    _benchmark_impl(scenario, seeds, duration, num_objects, output, "benchmark")


@app.command()
def evaluate(
    scenario: Annotated[
        str, typer.Option(help="Scenario name, comma-separated list, or 'all'")
    ] = "nominal",
    seeds: Annotated[str, typer.Option(help="Seeds, e.g. 1,2,3 or 1-5")] = "1-5",
    duration: Annotated[float, typer.Option(help="Simulation duration in seconds")] = 10.0,
    num_objects: Annotated[int, typer.Option(help="Number of ground-truth objects")] = 3,
    output: Annotated[Path, typer.Option(help="Output directory")] = Path("results"),
):
    """Generate an evaluation report (same canonical artifacts as benchmark)."""
    _benchmark_impl(scenario, seeds, duration, num_objects, output, "evaluate")


@app.command()
def version():
    """Show version."""
    console.print(f"Mosaic version {__version__}")


if __name__ == "__main__":
    app()
