"""
CLI for Mosaic.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
import numpy as np

from ..simulation.world import SyntheticWorld
from ..sensors import RangeBearingSensor, VisionBearingSensor
from ..domain.models import SensorConfig
from ..tracking import MultiSensorTracker
from ..evaluation.metrics import TrackingEvaluator

app = typer.Typer(help="Mosaic: Multi-sensor perception tracking workbench")
console = Console()


@app.command()
def run(
    scenario: str = typer.Option("nominal", help="Scenario name"),
    seed: int = typer.Option(42, help="Random seed"),
    duration: float = typer.Option(10.0, help="Simulation duration"),
    output: Optional[Path] = typer.Option(None, help="Output directory"),
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
        tracker_range.process_observations(obs, world_state.time)
    
    # Run fused tracking
    console.print("Running fused tracking...")
    tracker_fused = MultiSensorTracker(dt=0.1, use_vision=True)
    
    for world_state in states:
        obs_range = range_sensor.generate_observations(world_state, world_state.time)
        obs_vision = vision_sensor.generate_observations(world_state, world_state.time)
        obs = obs_range + obs_vision
        for o in obs:
            o._true_object_id = None
        tracker_fused.process_observations(obs, world_state.time)
    
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
            json.dump({
                "range_only": result_range.model_dump(),
                "fused": result_fused.model_dump(),
            }, f, indent=2, default=str)
        console.print(f"[green]Results saved to {output}[/green]")
    
    console.print("[bold green]Done![/bold green]")


@app.command()
def compare(
    scenario: str = typer.Option("nominal", help="Scenario name"),
    seeds: str = typer.Option("1,2,3", help="Comma-separated seeds"),
    duration: float = typer.Option(10.0, help="Simulation duration"),
):
    """Compare methods across multiple seeds."""
    seed_list = [int(s.strip()) for s in seeds.split(",")]
    console.print(f"[bold blue]Comparing across seeds: {seed_list}[/bold blue]")
    
    results = []
    for seed in seed_list:
        world = SyntheticWorld(seed=seed, duration=duration, dt=0.1, num_objects=3)
        rng_sensor = np.random.RandomState(seed + 1000)
        range_config = SensorConfig(
            sensor_id="range1", sensor_type="range_bearing", frame_rate=10.0,
            noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
            detection_probability=0.95, false_alarm_rate=0.01,
        )
        range_sensor = RangeBearingSensor(range_config, rng_sensor)
        vision_config = SensorConfig(
            sensor_id="vision1", sensor_type="vision_bearing", frame_rate=10.0,
            noise_std={"bearing": 0.005}, detection_probability=0.9, false_alarm_rate=0.02,
        )
        vision_sensor = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))
        
        states = world.get_all_states()
        evaluator = TrackingEvaluator()
        
        # Range only
        tracker_range = MultiSensorTracker(dt=0.1, use_vision=False)
        for world_state in states:
            obs = range_sensor.generate_observations(world_state, world_state.time)
            for o in obs: o._true_object_id = None
            tracker_range.process_observations(obs, world_state.time)
        result_range = evaluator.evaluate(tracker_range.tracks, states, scenario, seed, "range_only")
        
        # Fused
        tracker_fused = MultiSensorTracker(dt=0.1, use_vision=True)
        for world_state in states:
            obs_range = range_sensor.generate_observations(world_state, world_state.time)
            obs_vision = vision_sensor.generate_observations(world_state, world_state.time)
            obs = obs_range + obs_vision
            for o in obs: o._true_object_id = None
            tracker_fused.process_observations(obs, world_state.time)
        result_fused = evaluator.evaluate(tracker_fused.tracks, states, scenario, seed, "fused")
        
        results.append((seed, result_range, result_fused))
    
    table = Table(title="Multi-seed Comparison")
    table.add_column("Seed")
    table.add_column("Range RMSE (m)")
    table.add_column("Fused RMSE (m)")
    table.add_column("Δ (Fused - Range)")
    
    for seed, rr, rf in results:
        r_rmse = rr.position_rmse if rr.position_rmse else float('nan')
        f_rmse = rf.position_rmse if rf.position_rmse else float('nan')
        delta = f_rmse - r_rmse
        table.add_row(str(seed), f"{r_rmse:.3f}", f"{f_rmse:.3f}", f"{delta:+.3f}")
    
    console.print(table)


@app.command()
def version():
    """Show version."""
    from .. import __version__
    console.print(f"Mosaic version {__version__}")


if __name__ == "__main__":
    app()
