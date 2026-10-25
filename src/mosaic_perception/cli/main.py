"""
CLI for Mosaic.
"""

import json
from pathlib import Path

import numpy as np
import typer
from rich.console import Console
from rich.table import Table

from ..domain.models import SensorConfig
from ..evaluation.metrics import TrackingEvaluator
from ..sensors import RangeBearingSensor, VisionBearingSensor
from ..simulation.world import SyntheticWorld
from ..tracking import MultiSensorTracker

app = typer.Typer(help="Mosaic: Multi-sensor perception tracking workbench")
console = Console()


@app.command()
def run(
    scenario: str = typer.Option("nominal", help="Scenario name"),
    seed: int = typer.Option(42, help="Random seed"),
    duration: float = typer.Option(10.0, help="Simulation duration"),
    output: Path | None = typer.Option(None, help="Output directory"),
):
    """Run a single scenario."""
    console.print(f"[bold blue]Running scenario: {scenario} (seed={seed})[/bold blue]")

    # Create world
    world = SyntheticWorld(seed=seed, duration=duration, dt=0.1, num_objects=3)

    # Configure sensors
    rng_sensor = np.random.RandomState(seed + 1000)
    range_config = SensorConfig(
        sensor_id="range1",
        sensor_type="range_bearing",
        frame_rate=10.0,
        noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
        detection_probability=0.95,
        false_alarm_rate=0.01,
    )
    range_sensor = RangeBearingSensor(range_config, rng_sensor)

    vision_config = SensorConfig(
        sensor_id="vision1",
        sensor_type="vision_bearing",
        frame_rate=10.0,
        noise_std={"bearing": 0.005},
        detection_probability=0.9,
        false_alarm_rate=0.02,
    )
    vision_sensor = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))

    # Run range-only tracking
    console.print("Running range-only tracking...")
    tracker_range = MultiSensorTracker(dt=0.1, use_vision=False)
    states = world.get_all_states()

    for world_state in states:
        obs = range_sensor.generate_observations(world_state, world_state.time)
        for o in obs:
            o._true_object_id = None
        obs_pos = world_state.observer_pose.position.to_array()
        tracker_range.process_observations(obs, world_state.time, sensor_pos=obs_pos)

    # Run fused tracking
    console.print("Running fused tracking...")
    tracker_fused = MultiSensorTracker(dt=0.1, use_vision=True)
    rng_sensor_f = np.random.RandomState(seed + 1000)
    range_sensor_f = RangeBearingSensor(range_config, rng_sensor_f)
    vision_sensor_f = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))

    for world_state in states:
        obs_range = range_sensor_f.generate_observations(world_state, world_state.time)
        obs_vision = vision_sensor_f.generate_observations(world_state, world_state.time)
        obs = obs_range + obs_vision
        for o in obs:
            o._true_object_id = None
        obs_pos = world_state.observer_pose.position.to_array()
        tracker_fused.process_observations(obs, world_state.time, sensor_pos=obs_pos)

    # Evaluate
    evaluator = TrackingEvaluator()
    result_range = evaluator.evaluate(tracker_range.tracks, states, scenario, seed, "range_only")
    result_fused = evaluator.evaluate(tracker_fused.tracks, states, scenario, seed, "fused")

    # Display results
    table = Table(title="Tracking Results")
    table.add_column("Method")
    table.add_column("Position RMSE (m)")
    table.add_column("Velocity RMSE (m/s)")
    table.add_column("Confirmed Tracks")
    table.add_column("Total Tracks")

    table.add_row(
        "Range-only",
        f"{result_range.position_rmse:.3f}" if result_range.position_rmse else "N/A",
        f"{result_range.velocity_rmse:.3f}" if result_range.velocity_rmse else "N/A",
        str(result_range.num_confirmed_tracks),
        str(result_range.num_tracks),
    )
    table.add_row(
        "Fused",
        f"{result_fused.position_rmse:.3f}" if result_fused.position_rmse else "N/A",
        f"{result_fused.velocity_rmse:.3f}" if result_fused.velocity_rmse else "N/A",
        str(result_fused.num_confirmed_tracks),
        str(result_fused.num_tracks),
    )

    console.print(table)

    if output:
        output.mkdir(parents=True, exist_ok=True)
        with open(output / "metrics.json", "w") as f:
            json.dump(
                {
                    "scenario": scenario,
                    "seed": seed,
                    "duration": duration,
                    "range_only": result_range.model_dump(),
                    "fused": result_fused.model_dump(),
                },
                f,
                indent=2,
                default=str,
            )
        console.print(f"[green]Results saved to {output}[/green]")

    console.print("[bold green]Done![/bold green]")


@app.command()
def compare(
    scenario: str = typer.Option("nominal", help="Scenario name"),
    seeds: str = typer.Option("1,2,3", help="Comma-separated seeds"),
    duration: float = typer.Option(10.0, help="Simulation duration"),
    output: Path | None = typer.Option(None, help="Output directory"),
):
    """Compare methods across multiple seeds."""
    seed_list = [int(s.strip()) for s in seeds.split(",")]
    console.print(f"[bold blue]Comparing across seeds: {seed_list}[/bold blue]")

    results = []
    for seed in seed_list:
        world = SyntheticWorld(seed=seed, duration=duration, dt=0.1, num_objects=3)
        rng_sensor = np.random.RandomState(seed + 1000)
        range_config = SensorConfig(
            sensor_id="range1",
            sensor_type="range_bearing",
            frame_rate=10.0,
            noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
            detection_probability=0.95,
            false_alarm_rate=0.01,
        )
        range_sensor = RangeBearingSensor(range_config, rng_sensor)
        vision_config = SensorConfig(
            sensor_id="vision1",
            sensor_type="vision_bearing",
            frame_rate=10.0,
            noise_std={"bearing": 0.005},
            detection_probability=0.9,
            false_alarm_rate=0.02,
        )
        vision_sensor = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))

        states = world.get_all_states()
        evaluator = TrackingEvaluator()

        # Range only
        tracker_range = MultiSensorTracker(dt=0.1, use_vision=False)
        for world_state in states:
            obs = range_sensor.generate_observations(world_state, world_state.time)
            for o in obs:
                o._true_object_id = None
            obs_pos = world_state.observer_pose.position.to_array()
            tracker_range.process_observations(obs, world_state.time, sensor_pos=obs_pos)
        result_range = evaluator.evaluate(
            tracker_range.tracks, states, scenario, seed, "range_only"
        )

        # Fused
        tracker_fused = MultiSensorTracker(dt=0.1, use_vision=True)
        rng_sensor_f = np.random.RandomState(seed + 1000)
        range_sensor_f = RangeBearingSensor(range_config, rng_sensor_f)
        vision_sensor_f = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))
        for world_state in states:
            obs_range = range_sensor_f.generate_observations(world_state, world_state.time)
            obs_vision = vision_sensor_f.generate_observations(world_state, world_state.time)
            obs = obs_range + obs_vision
            for o in obs:
                o._true_object_id = None
            obs_pos = world_state.observer_pose.position.to_array()
            tracker_fused.process_observations(obs, world_state.time, sensor_pos=obs_pos)
        result_fused = evaluator.evaluate(tracker_fused.tracks, states, scenario, seed, "fused")

        results.append((seed, result_range, result_fused))

    table = Table(title="Multi-seed Comparison")
    table.add_column("Seed")
    table.add_column("Range RMSE (m)")
    table.add_column("Fused RMSE (m)")
    table.add_column("Δ (Fused - Range)")

    for seed, rr, rf in results:
        r_rmse = rr.position_rmse if rr.position_rmse else float("nan")
        f_rmse = rf.position_rmse if rf.position_rmse else float("nan")
        delta = f_rmse - r_rmse
        table.add_row(str(seed), f"{r_rmse:.3f}", f"{f_rmse:.3f}", f"{delta:+.3f}")

    console.print(table)

    if output:
        output.mkdir(parents=True, exist_ok=True)
        summary = {
            "scenario": scenario,
            "seeds": seed_list,
            "duration": duration,
            "results": [
                {
                    "seed": seed,
                    "range_only": rr.model_dump(),
                    "fused": rf.model_dump(),
                }
                for seed, rr, rf in results
            ],
        }
        with open(output / "summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        with open(output / "per_seed.csv", "w") as f:
            f.write("seed,range_rmse,fused_rmse,delta,range_confirmed,fused_confirmed\n")
            for seed, rr, rf in results:
                r_rmse = rr.position_rmse if rr.position_rmse is not None else "nan"
                f_rmse = rf.position_rmse if rf.position_rmse is not None else "nan"
                if rr.position_rmse is not None and rf.position_rmse is not None:
                    delta = rf.position_rmse - rr.position_rmse
                else:
                    delta = "nan"
                f.write(
                    f"{seed},{r_rmse},{f_rmse},{delta},{rr.num_confirmed_tracks},{rf.num_confirmed_tracks}\n"
                )
        console.print(f"[green]Results saved to {output}[/green]")


@app.command()
def benchmark(
    scenario: str = typer.Option("nominal", help="Scenario name"),
    seeds: str = typer.Option("1,2,3,4,5", help="Comma-separated seeds"),
    duration: float = typer.Option(10.0, help="Simulation duration"),
    output: Path = typer.Option(Path("artifacts/benchmark"), help="Output directory"),
):
    """Run reproducible benchmark and generate report."""
    seed_list = [int(s.strip()) for s in seeds.split(",")]
    console.print(f"[bold blue]Benchmark: {scenario} seeds={seed_list}[/bold blue]")

    output.mkdir(parents=True, exist_ok=True)
    results = []
    for seed in seed_list:
        world = SyntheticWorld(seed=seed, duration=duration, dt=0.1, num_objects=3)
        rng_sensor = np.random.RandomState(seed + 1000)
        range_config = SensorConfig(
            sensor_id="range1",
            sensor_type="range_bearing",
            frame_rate=10.0,
            noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
            detection_probability=0.95,
            false_alarm_rate=0.01,
        )
        range_sensor = RangeBearingSensor(range_config, rng_sensor)
        vision_config = SensorConfig(
            sensor_id="vision1",
            sensor_type="vision_bearing",
            frame_rate=10.0,
            noise_std={"bearing": 0.005},
            detection_probability=0.9,
            false_alarm_rate=0.02,
        )
        vision_sensor = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))

        states = world.get_all_states()
        evaluator = TrackingEvaluator()

        # Range only
        tracker_range = MultiSensorTracker(dt=0.1, use_vision=False)
        for world_state in states:
            obs = range_sensor.generate_observations(world_state, world_state.time)
            for o in obs:
                o._true_object_id = None
            obs_pos = world_state.observer_pose.position.to_array()
            tracker_range.process_observations(obs, world_state.time, sensor_pos=obs_pos)
        result_range = evaluator.evaluate(
            tracker_range.tracks, states, scenario, seed, "range_only"
        )

        # Fused
        tracker_fused = MultiSensorTracker(dt=0.1, use_vision=True)
        rng_sensor_f = np.random.RandomState(seed + 1000)
        range_sensor_f = RangeBearingSensor(range_config, rng_sensor_f)
        vision_sensor_f = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))
        for world_state in states:
            obs_range = range_sensor_f.generate_observations(world_state, world_state.time)
            obs_vision = vision_sensor_f.generate_observations(world_state, world_state.time)
            obs = obs_range + obs_vision
            for o in obs:
                o._true_object_id = None
            obs_pos = world_state.observer_pose.position.to_array()
            tracker_fused.process_observations(obs, world_state.time, sensor_pos=obs_pos)
        result_fused = evaluator.evaluate(tracker_fused.tracks, states, scenario, seed, "fused")

        results.append((seed, result_range, result_fused))

    # Aggregate
    range_rmses = [rr.position_rmse for _, rr, _ in results if rr.position_rmse is not None]
    fused_rmses = [rf.position_rmse for _, _, rf in results if rf.position_rmse is not None]
    range_mean = float(np.mean(range_rmses)) if range_rmses else None
    range_std = float(np.std(range_rmses)) if range_rmses else None
    fused_mean = float(np.mean(fused_rmses)) if fused_rmses else None
    fused_std = float(np.std(fused_rmses)) if fused_rmses else None

    summary = {
        "scenario": scenario,
        "seeds": seed_list,
        "duration": duration,
        "methods": ["range_only", "fused"],
        "results": [
            {
                "seed": seed,
                "range_only": rr.model_dump(),
                "fused": rf.model_dump(),
            }
            for seed, rr, rf in results
        ],
        "aggregate": {
            "range_only": {"position_rmse_mean": range_mean, "position_rmse_std": range_std},
            "fused": {"position_rmse_mean": fused_mean, "position_rmse_std": fused_std},
        },
    }
    with open(output / "benchmark.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    with open(output / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    with open(output / "per_seed.csv", "w") as f:
        f.write("seed,range_rmse,fused_rmse,delta,range_confirmed,fused_confirmed\n")
        for seed, rr, rf in results:
            r_rmse = rr.position_rmse if rr.position_rmse is not None else "nan"
            f_rmse = rf.position_rmse if rf.position_rmse is not None else "nan"
            if rr.position_rmse is not None and rf.position_rmse is not None:
                delta = rf.position_rmse - rr.position_rmse
            else:
                delta = "nan"
            f.write(
                f"{seed},{r_rmse},{f_rmse},{delta},{rr.num_confirmed_tracks},{rf.num_confirmed_tracks}\n"
            )

    report = f"""# Mosaic Benchmark Report

## Experiment
- Scenario: {scenario}
- Seeds: {seed_list}
- Duration: {duration} s
- Methods: range_only, fused
- Synthetic 2D simulation with simplified sensor models

## Per-seed results
| Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused - Range) |
|---|---|---|---|
"""
    for seed, rr, rf in results:
        r_rmse = f"{rr.position_rmse:.3f}" if rr.position_rmse is not None else "N/A"
        f_rmse = f"{rf.position_rmse:.3f}" if rf.position_rmse is not None else "N/A"
        if rr.position_rmse is not None and rf.position_rmse is not None:
            delta = f"{rf.position_rmse - rr.position_rmse:+.3f}"
        else:
            delta = "N/A"
        report += f"| {seed} | {r_rmse} | {f_rmse} | {delta} |\n"

    report += f"""
## Aggregate (mean ± std)
- Range-only position RMSE: {f"{range_mean:.3f} ± {range_std:.3f}" if range_mean is not None else "N/A"}
- Fused position RMSE: {f"{fused_mean:.3f} ± {fused_std:.3f}" if fused_mean is not None else "N/A"}

## Interpretation
Fusion does not universally improve performance. Results depend on scenario, seed, data association, timing, and calibration. This is a synthetic educational benchmark.

## Limitations
- Synthetic 2D only; simplified sensor models (no raw images/waveforms)
- Vision-only track initiation not performed (bearing alone insufficient)
- Observer pose handled via context; timing/out-of-sequence handling limited in v0.1
- Results do not imply real-world or hardware performance
"""
    with open(output / "report.md", "w") as f:
        f.write(report)
    with open(output / "benchmark_report.md", "w") as f:
        f.write(report)

    # Print summary table
    summary_table = Table(title="Benchmark Summary")
    summary_table.add_column("Seed")
    summary_table.add_column("Range RMSE (m)")
    summary_table.add_column("Fused RMSE (m)")
    summary_table.add_column("Δ (Fused - Range)")
    for seed, rr, rf in results:
        r_rmse = f"{rr.position_rmse:.3f}" if rr.position_rmse is not None else "N/A"
        f_rmse = f"{rf.position_rmse:.3f}" if rf.position_rmse is not None else "N/A"
        if rr.position_rmse is not None and rf.position_rmse is not None:
            delta = f"{rf.position_rmse - rr.position_rmse:+.3f}"
        else:
            delta = "N/A"
        summary_table.add_row(str(seed), r_rmse, f_rmse, delta)
    console.print(summary_table)
    console.print(f"[green]Benchmark artifacts saved to {output}[/green]")


@app.command()
def version():
    """Show version."""
    from .. import __version__

    console.print(f"Mosaic version {__version__}")


if __name__ == "__main__":
    app()
