#!/usr/bin/env python3
"""Generate the README hero stills: range-only, fused and bias-estimated on one seed.

Two stills of three stacked panels each, drawn from one simulated seed of a scenario
that a rule picks from ``artifacts/benchmark/benchmark.json`` (development seeds 0-24):
``hurts`` is the scenario with the largest paired precision loss of fused against
range-only whose 95% interval excludes zero; ``recovers`` is the scenario
``make_assets.choose_recovery_scenario`` picks. The seed is the first development seed.
The drawing is a single seed, so every number printed on a still is the paired benchmark
value from the artifact (never read off the drawn seed). Ground truth is dashed, the
95% position ellipse is drawn at the last point of each track. Writes the PNGs and a
JSON manifest of the choices, numbers and alt text; a test checks the manifest, not the
PNG bytes.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _draw  # noqa: E402
import make_assets  # noqa: E402

from mosaic_perception.domain.models import TrackStatus  # noqa: E402
from mosaic_perception.experiment import run_pair  # noqa: E402
from mosaic_perception.scenarios import resolve_scenario  # noqa: E402

OUTPUT_DIR = Path("docs-site/src/assets/generated")
MANIFEST = OUTPUT_DIR / "hero.json"
LABEL = "SYNTHETIC WORLD"
SIZE = (1080, 1350)
HEADER_H = 190
FOOTER_H = 84
COLUMN_HEAD_H = 190
DURATION = 10.0
NUM_OBJECTS = 1
CHI2_95_2DOF = 5.991
METHODS = ("range_only", "fused", "fused_bias_estimated")
METHOD_NAMES = {
    "range_only": "range sensor only",
    "fused": "range sensor plus camera",
    "fused_bias_estimated": "plus camera, bias estimated",
}
COLORS = {
    "background": (255, 255, 255),
    "text": (40, 40, 40),
    "ground_truth": (120, 120, 120),
    "range_only": (77, 77, 77),
    "fused": (27, 108, 168),
    "fused_bias_estimated": (217, 130, 43),
}
STILLS = {
    "hurts": {
        "comparison": "fused_vs_range_only",
        "file": "hero_hurts.png",
        "title": "More sensors, worse tracking?",
    },
    "recovers": {
        "comparison": "bias_estimated_vs_fused",
        "file": "hero_recovers.png",
        "title": "A camera that is slightly off, and a fix",
    },
}
SHORT = {"fused_vs_range_only": "fused vs range-only", "bias_estimated_vs_fused": "bias vs fused"}
LIVE = {TrackStatus.CONFIRMED, TrackStatus.COASTING}


def _interval(scenario: dict[str, Any], comparison: str) -> dict[str, float]:
    paired = scenario["paired_differences"][comparison]["precision"]
    return {k: round(paired[k], 3) for k in ("mean", "ci95_low", "ci95_high")}


def choose_hurt_scenario(payload: dict[str, Any]) -> str:
    """The scenario with the largest paired precision loss of fused vs range-only whose
    95% interval excludes zero."""
    best: tuple[float, str] | None = None
    for scenario in payload["scenarios"]:
        paired = scenario["paired_differences"]["fused_vs_range_only"]["precision"]
        high = paired["ci95_high"]
        if high is not None and high < 0 and (best is None or paired["mean"] < best[0]):
            best = (paired["mean"], scenario["scenario"]["name"])
    if best is None:
        raise ValueError("no scenario where fusion reliably lowers precision")
    return best[1]


def _verdict(interval: dict[str, float]) -> int:
    if interval["ci95_high"] < 0:
        return -1
    if interval["ci95_low"] > 0:
        return 1
    return 0


def panel_labels(hurts_fused: dict[str, float], bias_vs_fused: dict[str, float]) -> dict[str, str]:
    """Plain-language panel labels, each decided by the sign of a paired interval."""
    camera = {-1: "worse here", 0: "no clear change here", 1: "better here"}[_verdict(hurts_fused)]
    bias = {
        -1: "bias estimated: made it worse",
        0: "bias estimated: no clear change",
        1: "bias corrected: partly recovered",
    }[_verdict(bias_vs_fused)]
    return {
        "range_only": "baseline",
        "fused": f"camera added: {camera}",
        "fused_bias_estimated": bias,
    }


def build_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["protocol"]["seed_group"] != "development":
        raise ValueError("artifact is not the development run")
    seed = min(payload["protocol"]["seeds"])
    commit = payload["code"]["git_commit"]
    names = {
        "hurts": choose_hurt_scenario(payload),
        "recovers": make_assets.choose_recovery_scenario(payload),
    }
    stills = {}
    for key, spec in STILLS.items():
        scenario = next(s for s in payload["scenarios"] if s["scenario"]["name"] == names[key])
        interval = _interval(scenario, spec["comparison"])
        labels = panel_labels(
            _interval(scenario, "fused_vs_range_only"),
            _interval(scenario, "bias_estimated_vs_fused"),
        )
        stills[key] = {
            "file": spec["file"],
            "title": spec["title"],
            "scenario": names[key],
            "seed": seed,
            "n_seeds": len(payload["protocol"]["seeds"]),
            "comparison": spec["comparison"],
            "precision": interval,
            "panel_labels": labels,
            "source_commit": commit[:12],
            "alt": _alt(names[key], labels, interval, spec["comparison"]),
        }
    return {"label": LABEL, "commit": commit, "stills": stills}


def _alt(scenario: str, labels: dict[str, str], interval: dict[str, float], comparison: str) -> str:
    what = (
        "fused against range-only"
        if comparison == "fused_vs_range_only"
        else "bias-estimated against fused"
    )
    return (
        f"Three panels of one simulated target in the {scenario} scenario of a synthetic world: "
        f"range sensor only ({labels['range_only']}), {labels['fused']}, and {labels['fused_bias_estimated']}. "
        f"Ground truth is dashed; each panel marks the 95% position uncertainty at the end of the track. "
        f"Paired precision difference, {what}: {interval['mean']:+.3f}, "
        f"95% interval [{interval['ci95_low']:+.3f}, {interval['ci95_high']:+.3f}]."
    )


def _track(record: Any, times: list[float]) -> list[tuple[list[float], list[list[float]]] | None]:
    """Position and covariance of the longest-lived confirmed/coasting track per world time."""
    by_track: dict[str, dict[float, Any]] = {}
    for snap in record.snapshots:
        if snap.status in LIVE:
            by_track.setdefault(snap.track_id, {})[snap.time] = snap
    if not by_track:
        return [None] * len(times)
    best = max(by_track.values(), key=len)
    return [(best[t].state[:2], best[t].covariance) if t in best else None for t in times]


def simulate(name: str, seed: int) -> dict[str, Any]:
    config = resolve_scenario(name, seed=seed, duration=DURATION, num_objects=NUM_OBJECTS)
    pair = run_pair(config, include_bias_estimation=True)
    times = [state.time for state in pair.states]
    object_id = next(iter(pair.states[0].objects))
    return {
        "times": times,
        "ground_truth": [
            [s.objects[object_id].position.x, s.objects[object_id].position.y] for s in pair.states
        ],
        **{m: _track(pair.record(m), times) for m in METHODS},
    }


def ellipse(
    center: tuple[float, float], cov: list[list[float]], scale: float
) -> list[tuple[float, float]]:
    a, b, c = cov[0][0], cov[0][1], cov[1][1]
    mid, diff = (a + c) / 2, math.hypot((a - c) / 2, b)
    l1, l2 = max(mid + diff, 0.0), max(mid - diff, 0.0)
    angle = 0.5 * math.atan2(2 * b, a - c)
    r1, r2 = math.sqrt(CHI2_95_2DOF * l1) * scale, math.sqrt(CHI2_95_2DOF * l2) * scale
    points = []
    for k in range(48):
        t = 2 * math.pi * k / 48
        x, y = r1 * math.cos(t), r2 * math.sin(t)
        points.append(
            (
                center[0] + x * math.cos(angle) - y * math.sin(angle),
                center[1] - (x * math.sin(angle) + y * math.cos(angle)),
            )
        )
    return points


def render_still(data: dict[str, Any], still: dict[str, Any]) -> Any:
    """Three columns (the tracks are tall and narrow), caption band above, label below."""
    from PIL import Image, ImageDraw

    width, height = SIZE
    image = Image.new("RGB", SIZE, COLORS["background"])
    draw = ImageDraw.Draw(image)
    title, body, small = _draw.font(40), _draw.font(30), _draw.font(26)
    p = still["precision"]
    draw.text((30, 24), still["title"], fill=COLORS["text"], font=title)
    draw.text(
        (30, 84),
        f"{still['scenario']}, seed {still['seed']}, one drawn run.",
        fill=COLORS["text"],
        font=body,
    )
    draw.text(
        (30, 128),
        f"Over {still['n_seeds']} seeds: {SHORT[still['comparison']]} precision "
        f"{p['mean']:+.3f} [{p['ci95_low']:+.3f}, {p['ci95_high']:+.3f}]",
        fill=COLORS["text"],
        font=body,
    )
    col_w = width // 3
    plot_top = HEADER_H + COLUMN_HEAD_H
    plot_h = height - FOOTER_H - plot_top
    pts = list(data["ground_truth"])
    for m in METHODS:
        pts += [t[0] for t in data[m] if t]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    margin = 40
    scale = min(
        (col_w - 2 * margin) / (max(xs) - min(xs) or 1.0),
        (plot_h - 2 * margin) / (max(ys) - min(ys) or 1.0),
    )
    for col, method in enumerate(METHODS):
        left = col * col_w
        if col:
            draw.line((left, HEADER_H, left, height - FOOTER_H), fill=(210, 210, 210), width=2)
        color = COLORS["text"] if method == "range_only" else COLORS[method]
        y = HEADER_H + 10
        for line in _draw.wrap(draw, still["panel_labels"][method], body, col_w - 30)[:3]:
            draw.text((left + 15, y), line, fill=color, font=body)
            y += 36
        y = HEADER_H + 10 + 3 * 36 + 4
        for line in _draw.wrap(draw, METHOD_NAMES[method], small, col_w - 30)[:2]:
            draw.text((left + 15, y), line, fill=COLORS["text"], font=small)
            y += 30

        def to_px(q: list[float], left: int = left) -> tuple[float, float]:
            return (
                left + margin + (q[0] - min(xs)) * scale,
                plot_top + plot_h - margin - (q[1] - min(ys)) * scale,
            )

        truth = [to_px(q) for q in data["ground_truth"]]
        for a, b in zip(truth[::6], truth[3::6], strict=False):
            draw.line((a, b), fill=COLORS["ground_truth"], width=2)
        track = [t for t in data[method] if t]
        track_px = [to_px(t[0]) for t in track]
        if len(track_px) > 1:
            draw.line(track_px, fill=COLORS[method], width=4)
        if track:
            draw.polygon(
                ellipse(track_px[-1], track[-1][1], scale), outline=COLORS[method], width=3
            )
    draw.text(
        (30, height - FOOTER_H + 6),
        f"{LABEL}   artifact commit {still['source_commit']}",
        fill=COLORS["text"],
        font=small,
    )
    draw.text(
        (30, height - FOOTER_H + 38),
        "dashed = ground truth, ring = 95% position uncertainty",
        fill=COLORS["text"],
        font=small,
    )
    return image


def main() -> int:
    payload = json.loads(make_assets.BENCHMARK.read_text())
    manifest = build_manifest(payload)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for still in manifest["stills"].values():
        data = simulate(still["scenario"], still["seed"])
        render_still(data, still).save(OUTPUT_DIR / still["file"], optimize=False)
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"wrote {MANIFEST} and {len(manifest['stills'])} stills in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
