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
from ..reporting import format_number as _fmt
from ..reporting import render_report
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
    classified = sum(result.class_classified_samples for result in results)
    matched = sum(result.matched_samples for result in results)
    correct = sum(result.class_correct_samples for result in results)
    # Pooled over seeds so a seed with very few classified samples cannot dominate.
    aggregate["class_accuracy_pooled"] = correct / classified if classified else None
    aggregate["class_classified_fraction_pooled"] = classified / matched if matched else None
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
        (output / "report.md").write_text(render_report(payload))
        console.print(f"[green]Canonical artifacts written to {output}[/green]")
    return payload


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
