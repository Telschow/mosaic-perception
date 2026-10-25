"""
Scenario presets.

Each preset declares what changes, what stays constant, the expected failure
mode and the metrics that can reveal it. Presets only override sensor and
observer settings; world generation and tracker manage/estimation logic are
identical across scenarios so comparisons stay fair.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .domain.models import ScenarioConfig, SensorConfig


@dataclass(frozen=True)
class ScenarioPreset:
    name: str
    description: str
    hypothesis: str
    relevant_metrics: list[str] = field(default_factory=list)
    observer_trajectory: str = "static"
    range_overrides: dict[str, Any] = field(default_factory=dict)
    vision_overrides: dict[str, Any] = field(default_factory=dict)


_RANGE_DEFAULTS: dict[str, Any] = {
    "sensor_id": "range1",
    "sensor_type": "range_bearing",
    "frame_rate": 10.0,
    "noise_std": {"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
    "detection_probability": 0.95,
    "false_alarm_rate": 0.01,
}

_VISION_DEFAULTS: dict[str, Any] = {
    "sensor_id": "vision1",
    "sensor_type": "vision_bearing",
    "frame_rate": 10.0,
    "noise_std": {"bearing": 0.005},
    "detection_probability": 0.9,
    "false_alarm_rate": 0.02,
}

PRESETS: dict[str, ScenarioPreset] = {
    "nominal": ScenarioPreset(
        name="nominal",
        description="Baseline noise with occasional missed detections.",
        hypothesis=(
            "With clean timing and calibrated noise, vision bearings should "
            "reduce position error relative to the range-bearing baseline."
        ),
        relevant_metrics=["position_rmse", "velocity_rmse", "recall", "coverage"],
    ),
    "vision_dropout": ScenarioPreset(
        name="vision_dropout",
        description="Vision detection probability reduced to 0.45.",
        hypothesis=(
            "Sparse vision updates should reduce the benefit of fusion; the "
            "fused method may converge towards the baseline."
        ),
        relevant_metrics=["position_rmse", "recall", "coverage"],
        vision_overrides={"detection_probability": 0.45},
    ),
    "range_dropout": ScenarioPreset(
        name="range_dropout",
        description="Range-bearing detection probability reduced to 0.55.",
        hypothesis=(
            "With the baseline sensor sparse, vision bearings may help less "
            "than expected because tracks cannot be initiated from bearings."
        ),
        relevant_metrics=["position_rmse", "recall", "num_tracks"],
        range_overrides={"detection_probability": 0.55},
    ),
    "measurement_bias": ScenarioPreset(
        name="measurement_bias",
        description="Constant range bias of +1.5 m and range-rate bias of +0.3 m/s.",
        hypothesis=(
            "A systematic bias degrades the baseline and is only partially "
            "corrected by additional bearings; errors stay biased."
        ),
        relevant_metrics=["position_rmse", "coverage", "recall"],
        range_overrides={"bias": {"range": 1.5, "range_rate": 0.3}},
    ),
    "delivery_delay": ScenarioPreset(
        name="delivery_delay",
        description="Observations are delivered 0.05+-0.02 s after capture.",
        hypothesis=(
            "A bounded one-epoch delay is queued and applied at delivery; "
            "the run reports a small age of information rather than silently "
            "dropping observations."
        ),
        relevant_metrics=[
            "position_rmse",
            "mean_age_of_information",
            "rejected_out_of_sequence",
        ],
        range_overrides={"delivery_delay_mean": 0.05, "delivery_delay_std": 0.02},
        vision_overrides={"delivery_delay_mean": 0.05, "delivery_delay_std": 0.02},
    ),
    "out_of_sequence": ScenarioPreset(
        name="out_of_sequence",
        description="Observations arrive 0.25+-0.05 s after capture (older than one epoch).",
        hypothesis=(
            "Observations older than the bounded one-epoch staleness policy "
            "are explicitly rejected and counted; no track can be maintained "
            "from them, so accuracy metrics are unavailable rather than "
            "silently computed from stale data."
        ),
        relevant_metrics=[
            "rejected_out_of_sequence",
            "delivered_observations",
            "pending_observations",
        ],
        range_overrides={"delivery_delay_mean": 0.25, "delivery_delay_std": 0.05},
        vision_overrides={"delivery_delay_mean": 0.25, "delivery_delay_std": 0.05},
    ),
    "false_observations": ScenarioPreset(
        name="false_observations",
        description="Elevated false-alarm rates on both sensors.",
        hypothesis=(
            "False alarms create spurious tentative tracks and can steal "
            "associations; precision and false-track counts should worsen."
        ),
        relevant_metrics=["position_rmse", "precision", "num_false_tracks"],
        range_overrides={"false_alarm_rate": 1.0},
        vision_overrides={"false_alarm_rate": 3.0},
    ),
    "uncertainty_miscalibration": ScenarioPreset(
        name="uncertainty_miscalibration",
        description="Reported measurement covariance is 20x too small.",
        hypothesis=(
            "Overconfident measurements make the filter trust observations "
            "too much; empirical 95% coverage should fall below nominal."
        ),
        relevant_metrics=["position_coverage_95", "coverage_samples"],
        range_overrides={"reported_cov_scale": 0.05},
        vision_overrides={"reported_cov_scale": 0.05},
    ),
    "sensor_disagreement": ScenarioPreset(
        name="sensor_disagreement",
        description="Vision bearing bias of 0.12 rad while range-bearing is unbiased.",
        hypothesis=(
            "Conflicting bearings pull fused estimates away from truth when "
            "the filter treats them as unbiased."
        ),
        relevant_metrics=["position_rmse", "coverage"],
        vision_overrides={"bias": {"bearing": 0.12}},
    ),
    "moving_observer": ScenarioPreset(
        name="moving_observer",
        description="Observer follows a circular trajectory with changing heading.",
        hypothesis=(
            "Correct sensor-frame measurement models and observer velocity "
            "handling should keep error comparable to the static case."
        ),
        relevant_metrics=["position_rmse", "recall"],
        observer_trajectory="circle",
    ),
}

DEFAULT_SCENARIO = "nominal"


def available_scenarios() -> list[str]:
    return sorted(PRESETS)


def resolve_scenario(
    name: str,
    seed: int,
    duration: float,
    dt: float = 0.1,
    num_objects: int = 3,
) -> ScenarioConfig:
    """Expand a preset name into a fully resolved scenario configuration."""
    if name not in PRESETS:
        raise ValueError(
            f"unknown scenario {name!r}; available: {', '.join(available_scenarios())}"
        )
    preset = PRESETS[name]

    range_cfg = dict(_RANGE_DEFAULTS)
    range_cfg["noise_std"] = dict(_RANGE_DEFAULTS["noise_std"])
    range_cfg.update(preset.range_overrides)
    vision_cfg = dict(_VISION_DEFAULTS)
    vision_cfg["noise_std"] = dict(_VISION_DEFAULTS["noise_std"])
    vision_cfg.update(preset.vision_overrides)

    # Deep-copy nested noise/bias dictionaries from overrides.
    for cfg in (range_cfg, vision_cfg):
        for key in ("noise_std", "bias"):
            if key in cfg and isinstance(cfg[key], dict):
                cfg[key] = dict(cfg[key])

    return ScenarioConfig(
        name=preset.name,
        description=preset.description,
        hypothesis=preset.hypothesis,
        seed=seed,
        duration=duration,
        dt=dt,
        num_objects=num_objects,
        observer_trajectory=preset.observer_trajectory,
        sensors={
            "range_bearing": SensorConfig(**range_cfg),
            "vision_bearing": SensorConfig(**vision_cfg),
        },
    )
