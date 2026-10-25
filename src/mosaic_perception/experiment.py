"""
Shared experiment runner used by the CLI, Streamlit app and tests.

Both methods are evaluated on the **same** world states. Sensor random streams
are seeded independently of the method, so range observations are identical
for range-only and fused runs of the same scenario/seed; the fused run only
adds vision observations.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from .domain.models import EvaluationResult, ScenarioConfig, TrackSnapshot, WorldState
from .evaluation.metrics import TrackingEvaluator
from .sensors import RangeBearingSensor, VisionBearingSensor
from .simulation.world import SyntheticWorld
from .tracking import MultiSensorTracker

Method = Literal["range_only", "fused"]
METHODS: tuple[Method, Method] = ("range_only", "fused")


@dataclass
class RunRecord:
    """One method run: tracker snapshots plus evaluated metrics."""

    scenario_name: str
    seed: int
    method: str
    snapshots: list[TrackSnapshot]
    tracker: MultiSensorTracker
    result: EvaluationResult


@dataclass
class PairedRun:
    """Paired range-only and fused runs on identical worlds and range streams."""

    scenario: ScenarioConfig
    states: list[WorldState]
    range_only: RunRecord
    fused: RunRecord

    def record(self, method: str) -> RunRecord:
        if method == "range_only":
            return self.range_only
        if method == "fused":
            return self.fused
        raise ValueError(f"unknown method {method!r}")


def current_git_commit() -> str | None:
    """Return the current repository commit, or None outside a Git checkout."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[2],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    commit = completed.stdout.strip()
    return commit or None


def _build_sensors(
    scenario: ScenarioConfig, method: Method
) -> tuple[list[RangeBearingSensor], list[VisionBearingSensor]]:
    range_sensors: list[RangeBearingSensor] = []
    vision_sensors: list[VisionBearingSensor] = []
    for index, config in enumerate(scenario.sensors.values()):
        if config.sensor_type == "range_bearing":
            range_sensors.append(
                RangeBearingSensor(
                    config,
                    np.random.RandomState(scenario.seed + 1000 + index),
                )
            )
        elif config.sensor_type == "vision_bearing":
            if method == "fused":
                vision_sensors.append(
                    VisionBearingSensor(
                        config,
                        np.random.RandomState(scenario.seed + 2000 + index),
                    )
                )
        else:
            raise ValueError(f"unsupported sensor_type {config.sensor_type!r}")
    if not range_sensors:
        raise ValueError("scenario has no range-bearing sensor")
    return range_sensors, vision_sensors


def run_method(
    scenario: ScenarioConfig,
    method: Method,
    states: list[WorldState] | None = None,
    *,
    git_commit: str | None = None,
    evaluator: TrackingEvaluator | None = None,
) -> RunRecord:
    """Run one method on a scenario, optionally reusing shared world states."""
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}")
    if states is None:
        states = SyntheticWorld(
            seed=scenario.seed,
            duration=scenario.duration,
            dt=scenario.dt,
            num_objects=scenario.num_objects,
            observer_trajectory=scenario.observer_trajectory,
        ).get_all_states()

    range_sensors, vision_sensors = _build_sensors(scenario, method)
    tracker = MultiSensorTracker(
        dt=scenario.dt,
        use_vision=method == "fused",
    )

    for world_state in states:
        observations = []
        for sensor in range_sensors:
            observations.extend(sensor.generate_observations(world_state, world_state.time))
        for sensor in vision_sensors:
            observations.extend(sensor.generate_observations(world_state, world_state.time))
        # Evaluator-only metadata is deliberately removed before estimation.
        for observation in observations:
            observation._true_object_id = None
        tracker.process_observations(observations, world_state.time)

    evaluator = evaluator or TrackingEvaluator()
    commit = git_commit if git_commit is not None else current_git_commit()
    result = evaluator.evaluate(
        tracker.snapshots,
        states,
        scenario_name=scenario.name,
        seed=scenario.seed,
        method_name=method,
        statistics=tracker.statistics(),
        config=scenario.model_dump(mode="json"),
        git_commit=commit,
    )
    return RunRecord(
        scenario_name=scenario.name,
        seed=scenario.seed,
        method=method,
        snapshots=list(tracker.snapshots),
        tracker=tracker,
        result=result,
    )


def run_pair(
    scenario: ScenarioConfig,
    *,
    git_commit: str | None = None,
    evaluator: TrackingEvaluator | None = None,
) -> PairedRun:
    """Run range-only and fused methods on identical worlds and range streams."""
    states = SyntheticWorld(
        seed=scenario.seed,
        duration=scenario.duration,
        dt=scenario.dt,
        num_objects=scenario.num_objects,
        observer_trajectory=scenario.observer_trajectory,
    ).get_all_states()
    commit = git_commit if git_commit is not None else current_git_commit()
    range_only = run_method(
        scenario,
        "range_only",
        states,
        git_commit=commit,
        evaluator=evaluator,
    )
    fused = run_method(
        scenario,
        "fused",
        states,
        git_commit=commit,
        evaluator=evaluator,
    )
    return PairedRun(scenario, states, range_only, fused)
