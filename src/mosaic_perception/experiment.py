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

Method = Literal["range_only", "fused", "fused_bias_estimated"]
METHODS: tuple[Method, Method, Method] = ("range_only", "fused", "fused_bias_estimated")
_VISION_METHODS = ("fused", "fused_bias_estimated")

# Paired comparisons reported in the benchmark: (name, baseline, treatment). The first is the
# headline fusion comparison; the second asks whether estimating the vision bias helps.
PAIRED_COMPARISONS: tuple[tuple[str, Method, Method], ...] = (
    ("fused_vs_range_only", "range_only", "fused"),
    ("bias_estimated_vs_fused", "fused", "fused_bias_estimated"),
)


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
    """Paired runs on identical worlds and sensor random streams.

    ``fused_bias_estimated`` is only present when requested (see ``run_pair``).
    """

    scenario: ScenarioConfig
    states: list[WorldState]
    range_only: RunRecord
    fused: RunRecord
    fused_bias_estimated: RunRecord | None = None

    def record(self, method: str) -> RunRecord:
        if method == "range_only":
            return self.range_only
        if method == "fused":
            return self.fused
        if method == "fused_bias_estimated" and self.fused_bias_estimated is not None:
            return self.fused_bias_estimated
        raise ValueError(f"unknown or missing method {method!r}")


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
            if method in _VISION_METHODS:
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
            target_layout=scenario.target_layout,
        ).get_all_states()

    range_sensors, vision_sensors = _build_sensors(scenario, method)
    tracker = MultiSensorTracker(
        dt=scenario.dt,
        use_vision=method in _VISION_METHODS,
        delayed_update=scenario.delayed_update,
        bias_estimation=method == "fused_bias_estimated",
    )

    for world_state in states:
        observations = []
        for sensor in range_sensors:
            observations.extend(sensor.generate_observations(world_state, world_state.time))
        vision_observations = []
        for vision_sensor in vision_sensors:
            vision_observations.extend(
                vision_sensor.generate_observations(world_state, world_state.time)
            )
        # Record vision observations generated
        tracker.record_vision_generated(len(vision_observations))
        observations.extend(vision_observations)
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
    vision_config = next(
        (c for c in scenario.sensors.values() if c.sensor_type == "vision_bearing"), None
    )
    # Reported next to the estimate for comparison only; never an estimator input.
    result.vision_bias_configured = (
        float((vision_config.bias or {}).get("bearing", 0.0))
        if vision_config is not None and method in _VISION_METHODS
        else None
    )
    result.vision_bias_estimate = tracker.vision_bias_estimate
    result.vision_bias_updates = tracker.vision_bias_updates
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
    include_bias_estimation: bool = False,
) -> PairedRun:
    """Run range-only and fused methods (optionally also bias-estimated fusion).

    All methods share the world states and the same per-sensor random streams.
    """
    states = SyntheticWorld(
        seed=scenario.seed,
        duration=scenario.duration,
        dt=scenario.dt,
        num_objects=scenario.num_objects,
        observer_trajectory=scenario.observer_trajectory,
        target_layout=scenario.target_layout,
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
    bias_estimated = (
        run_method(
            scenario,
            "fused_bias_estimated",
            states,
            git_commit=commit,
            evaluator=evaluator,
        )
        if include_bias_estimation
        else None
    )
    return PairedRun(scenario, states, range_only, fused, bias_estimated)
