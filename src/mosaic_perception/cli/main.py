"""
Command-line interface for Mosaic.

All experiment commands use the shared runner in ``mosaic_perception.experiment``
so the CLI, the Streamlit app and the tests execute the same pipeline.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Any

import numpy as np
import typer
from rich.console import Console
from rich.table import Table
from scipy.stats import chi2

from .. import __version__
from ..domain.models import EvaluationResult
from ..evaluation.registry import (
    DUPLICATE_SENSITIVITY_GATES_M,
    POOLED_CHI_SQUARES,
    POOLED_RATIOS,
    RESULT_METRICS,
    MetricSpec,
    PooledChiSquare,
    PooledRatio,
    duplicate_gate_metric,
    gate_label,
    metric_names,
    metric_value,
)
from ..evaluation.statistics import paired_difference
from ..experiment import (
    METHODS,
    PAIRED_COMPARISONS,
    PairedRun,
    current_git_commit,
    run_pair,
)
from ..reporting import format_number as _fmt
from ..reporting import render_report
from ..scenarios import available_scenarios, resolve_scenario

app = typer.Typer(help="Mosaic: multi-sensor perception tracking workbench")
console = Console()


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
    # Flatten the per-gate duplicate counts into the declared metric names.
    by_gate = payload.pop("num_duplicate_tracks_by_gate", {})
    for gate in DUPLICATE_SENSITIVITY_GATES_M:
        label = gate_label(gate)
        payload[duplicate_gate_metric(gate)] = by_gate.get(label)
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
        if method == "fused_bias_estimated" and pair.fused_bias_estimated is None:
            continue
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


def _aggregate(
    results: list[EvaluationResult],
    metrics: Sequence[MetricSpec] = RESULT_METRICS,
    pooled: Sequence[PooledRatio] = POOLED_RATIOS,
    chi_squares: Sequence[PooledChiSquare] = POOLED_CHI_SQUARES,
) -> dict[str, Any]:
    """Aggregate the declared metrics over seeds (mean and sample std, plus pooled ratios)."""
    aggregate: dict[str, Any] = {"num_seeds": len(results)}
    for spec in metrics:
        values = [
            value for result in results if (value := metric_value(result, spec.name)) is not None
        ]
        if not values:
            aggregate[spec.name] = None
            aggregate[f"{spec.name}_std"] = None
            continue
        aggregate[spec.name] = float(np.mean(values))
        aggregate[f"{spec.name}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    for ratio in pooled:
        # Pooled over seeds so a seed with very few samples cannot dominate.
        numerator = sum(metric_value(result, ratio.numerator) or 0.0 for result in results)
        denominator = sum(metric_value(result, ratio.denominator) or 0.0 for result in results)
        aggregate[ratio.name] = numerator / denominator if denominator else None
    for stat in chi_squares:
        total = sum(metric_value(result, stat.total) or 0.0 for result in results)
        if stat.dof_metric is not None:
            dof = int(sum(metric_value(result, stat.dof_metric) or 0.0 for result in results))
        else:
            assert stat.samples is not None
            samples = sum(metric_value(result, stat.samples) or 0.0 for result in results)
            dof = int(samples) * stat.dof_per_sample
        if dof > 0:
            aggregate[stat.name] = total / dof
            aggregate[f"{stat.name}_low"] = float(chi2.ppf(0.025, dof)) / dof
            aggregate[f"{stat.name}_high"] = float(chi2.ppf(0.975, dof)) / dof
            aggregate[f"{stat.name}_dof"] = dof
        else:
            for suffix in ("", "_low", "_high", "_dof"):
                aggregate[f"{stat.name}{suffix}"] = None
    return aggregate


_PAIRED_METRICS = (
    "position_rmse",
    "position_rmse_distance_only",
    "recall",
    "precision",
    "position_coverage_95",
    "mota",
    "idf1",
    "gospa_p1",
)


def _paired_differences(runs: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """Per comparison and metric: paired difference (treatment - baseline) over seeds."""
    summary: dict[str, dict[str, dict[str, Any]]] = {}
    for name, baseline, treatment in PAIRED_COMPARISONS:
        summary[name] = {}
        for metric in _PAIRED_METRICS:
            difference = paired_difference(
                [run[baseline].get(metric) for run in runs],
                [run[treatment].get(metric) for run in runs],
            )
            summary[name][metric] = {
                "n": difference.n,
                "mean": difference.mean,
                "ci95_low": difference.low,
                "ci95_high": difference.high,
            }
    return summary


def _write_per_seed_csv(
    path: Path, rows: list[dict[str, Any]], metrics: Sequence[MetricSpec] = RESULT_METRICS
) -> None:
    columns = ["scenario", "seed", "method", *metric_names(metrics)]
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
    all_results: list[list[EvaluationResult]] = []
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
            pair = run_pair(scenario, include_bias_estimation=True)
            bias_estimated = pair.record("fused_bias_estimated")
            console.print(
                f"  {scenario_name} seed={seed}: "
                f"range RMSE={_fmt(pair.range_only.result.position_rmse)} m, "
                f"fused RMSE={_fmt(pair.fused.result.position_rmse)} m, "
                f"bias-estimated RMSE={_fmt(bias_estimated.result.position_rmse)} m"
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
        all_results.extend(results_by_method.values())
        scenario_reports.append(
            {
                "scenario": first_config,
                "runs": runs,
                "aggregate": {method: _aggregate(results_by_method[method]) for method in METHODS},
                "paired_differences": _paired_differences(runs),
            }
        )

    gates = {r.matching_gate_m for rs in all_results for r in rs}
    continuities = {r.matching_continuity for rs in all_results for r in rs}
    if len(gates) != 1 or len(continuities) != 1:
        raise RuntimeError("results were evaluated with inconsistent matching settings")
    matching_gate_m = gates.pop()
    matching_continuity = continuities.pop()

    payload: dict[str, Any] = {
        "schema_version": 2,
        "command": command,
        "code": {"package_version": __version__, "git_commit": commit},
        "protocol": {
            "matching_gate_m": matching_gate_m,
            "matching_continuity": matching_continuity,
            "position_coverage_95_threshold": 5.991,
            "seed_group": ("development" if max(seeds) <= 24 else "custom_or_held_out"),
            "seeds": seeds,
            "duration_s": duration,
            "dt_s": dt,
            "num_objects": num_objects,
            "methods": list(METHODS),
            "paired": "same world states and range-sensor random stream per seed",
            "paired_comparisons": [
                {"name": name, "baseline": baseline, "treatment": treatment}
                for name, baseline, treatment in PAIRED_COMPARISONS
            ],
            "paired_difference_interval": (
                "two-sided 95% t interval over seeds of (treatment - baseline); "
                "descriptive seed-to-seed variation, not a generalisation claim"
            ),
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
