#!/usr/bin/env python3
"""Ablation: may vision keep a track alive that the range sensor missed? (``make ablation``)

Runs ``fused`` twice on the development seeds (0-24): with the benchmark default
(``vision_updates="all"``) and with ``"range_supported"`` (vision only updates tracks a
range observation updated in the same epoch), each paired against ``range_only``.
Writes ``artifacts/ablation/vision_refresh.json`` and ``.md``. It reads only the
development seeds, never the held-out range, and is not part of the benchmark artifact.
The finding says nothing beyond this tracker and these gates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from mosaic_perception.evaluation.registry import metric_value
from mosaic_perception.evaluation.statistics import paired_difference
from mosaic_perception.experiment import current_git_commit, run_method
from mosaic_perception.scenarios import resolve_scenario

OUTPUT = Path("artifacts/ablation")
SEEDS = list(range(0, 25))
SCENARIOS = ("nominal", "dense_clutter", "vision_dropout", "sensor_disagreement_within_gate")
METRICS = (("precision", False), ("mota", False), ("gospa_p1", True))
POLICIES = ("all", "range_supported")
DURATION = 10.0
NUM_OBJECTS = 3


def run(seeds: list[int] = SEEDS, scenarios: tuple[str, ...] = SCENARIOS) -> dict[str, Any]:
    if max(seeds) > 24:
        raise ValueError("the ablation uses development seeds only (0-24)")
    commit = current_git_commit()
    rows: list[dict[str, Any]] = []
    for name in scenarios:
        values: dict[str, dict[str, list[float | None]]] = {
            key: {m: [] for m, _ in METRICS} for key in ("range_only", *POLICIES)
        }
        for seed in seeds:
            config = resolve_scenario(name, seed=seed, duration=DURATION, num_objects=NUM_OBJECTS)
            base = run_method(config, "range_only", git_commit=commit)
            for metric, _ in METRICS:
                values["range_only"][metric].append(metric_value(base.result, metric))
            for policy in POLICIES:
                record = run_method(config, "fused", git_commit=commit, vision_updates=policy)
                for metric, _ in METRICS:
                    values[policy][metric].append(metric_value(record.result, metric))
        for policy in POLICIES:
            for metric, lower_is_better in METRICS:
                diff = paired_difference(values["range_only"][metric], values[policy][metric])
                rows.append(
                    {
                        "scenario": name,
                        "policy": policy,
                        "metric": metric,
                        "lower_is_better": lower_is_better,
                        "n": diff.n,
                        "mean": diff.mean,
                        "ci95_low": diff.low,
                        "ci95_high": diff.high,
                    }
                )
    return {
        "code": {"git_commit": commit},
        "protocol": {
            "seeds": seeds,
            "seed_group": "development",
            "duration_s": DURATION,
            "num_objects": NUM_OBJECTS,
            "comparison": "fused (policy) minus range_only, paired per seed",
        },
        "rows": rows,
    }


def render(payload: dict[str, Any]) -> str:
    lines = [
        "# Ablation: vision refreshing range-missed tracks",
        "",
        "Fused minus range-only, paired over development seeds 0-24 (95% t interval).",
        "`all` is the benchmark default; `range_supported` lets vision update only tracks a",
        "range observation updated in the same epoch. Claims are limited to this tracker and",
        "these gates.",
        f"Commit: `{payload['code']['git_commit']}`",
        "",
        "| Scenario | Policy | Metric | Mean difference | 95% interval |",
        "|---|---|---|---|---|",
    ]
    for r in payload["rows"]:
        interval = (
            "N/A" if r["ci95_low"] is None else f"[{r['ci95_low']:+.3f}, {r['ci95_high']:+.3f}]"
        )
        mean = "N/A" if r["mean"] is None else f"{r['mean']:+.3f}"
        lines.append(f"| {r['scenario']} | {r['policy']} | {r['metric']} | {mean} | {interval} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = run()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "vision_refresh.json").write_text(json.dumps(payload, indent=1) + "\n")
    (OUTPUT / "vision_refresh.md").write_text(render(payload))
    print(f"wrote {OUTPUT}/vision_refresh.json and .md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
