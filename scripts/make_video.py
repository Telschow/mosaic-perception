#!/usr/bin/env python3
"""Plan and render the 4:5 Hook video (``make video``).

One idea for a non-expert: one real object followed with one sensor, then with a camera added.
Both are drawn from one real development run (the lines are the tracker's actual tracks), then
a 100-dot pictogram of the share of reported tracks that were the real object, read from the
benchmark artifact. The framing is about this simulated tracker, not fusion in general: the
vision-refresh ablation (``artifacts/ablation/``) shows most of the loss goes away when vision
cannot refresh tracks the range sensor missed. ``build_plan`` is pure and tested; the Manim
scene (``video_scene.py``) only draws it. Manim is optional (``uv run --with manim``): without
it ``main`` says so and renders nothing. Tests check the plan and manifest, never the bytes.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import make_assets  # noqa: E402
import make_hero  # noqa: E402

OUTPUT_DIR = Path("docs-site/src/assets/generated")
MANIFEST = OUTPUT_DIR / "hook_video.json"
VIDEO = OUTPUT_DIR / "hook_video_4x5.mp4"
SCENE = Path(__file__).resolve().parent / "video_scene.py"
SIZE = (1080, 1350)
LABEL = make_hero.LABEL
SOURCES = [
    "artifacts/benchmark/benchmark.json",
    "artifacts/ablation/vision_refresh.md",
    "docs-site/src/assets/generated/hero.json",
    "scripts/make_video.py",
    "scripts/video_scene.py",
]
MISSING_MANIM = (
    "manim not found: `make video` needs it to render. It is an optional tool, run through "
    "`uv run --with manim` (macOS also needs: brew install cairo pango ffmpeg). "
    "Nothing was rendered; the manifest was still written."
)


def _real_share(payload: dict[str, Any], scenario: str) -> dict[str, int]:
    """Share of reported tracks that were the real object, per 100, from the artifact."""
    entry = next(s for s in payload["scenarios"] if s["scenario"]["name"] == scenario)
    return {
        method: round(100 * entry["aggregate"][method]["precision"])
        for method in ("range_only", "fused")
    }


def build_plan(payload: dict[str, Any]) -> dict[str, Any]:
    """Beats, captions and the two figures to print, all read from the development artifact."""
    seeds = payload["protocol"]["seeds"]
    scenario = make_hero.choose_hurt_scenario(payload)
    beats: list[dict[str, Any]] = [
        {
            "id": "question",
            "duration_s": 7.0,
            "text": ["Does adding a second sensor", "make tracking better?"],
            "note": "A computer simulation: one object, two ways to follow it.",
        },
        {
            "id": "one_sensor",
            "duration_s": 10.0,
            "text": [
                "One sensor follows the object.",
                "Each line is something the tracker thinks is there.",
            ],
            "note": "There is really only one object: the dashed path.",
        },
        {
            "id": "two_sensors",
            "duration_s": 11.0,
            "text": ["Now add a camera.", "Same object. Many more lines."],
            "note": "Most of the new lines are ghosts.",
        },
        {
            "id": "numbers",
            "duration_s": 9.0,
            "text": ["Of everything the tracker reported,", "how much was the real object?"],
            "real_of_100": _real_share(payload, scenario),
            "columns": ["one sensor", "plus camera"],
        },
        {
            "id": "close",
            "duration_s": 7.0,
            "text": ["In this simulation,", "the second sensor added ghost tracks."],
            "note": "Details and limits: telschow.github.io/mosaic-perception",
        },
    ]
    return {
        "label": LABEL,
        "commit": payload["code"]["git_commit"],
        "seed_label": f"development seeds {seeds[0]}-{seeds[-1]}",
        "n_seeds": len(seeds),
        "scenario": scenario,
        "seed": min(seeds),
        "size": list(SIZE),
        "total_s": sum(b["duration_s"] for b in beats),
        "beats": beats,
    }


def build_manifest(plan: dict[str, Any]) -> dict[str, Any]:
    return {**plan, "sources": SOURCES, "output": VIDEO.name}


def main(render: bool = False) -> int:
    payload = json.loads(make_assets.BENCHMARK.read_text())
    plan = build_plan(payload)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(build_manifest(plan), indent=1) + "\n")
    print(f"wrote {MANIFEST}")
    if not render:
        return 0
    if importlib.util.find_spec("manim") is None:
        print(MISSING_MANIM, file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "manim",
                "render",
                str(SCENE),
                "Hook",
                "--media_dir",
                tmp,
                "--disable_caching",
            ],
            check=True,
        )
        shutil.copy(next(Path(tmp).rglob("Hook.mp4")), VIDEO)
    print(f"wrote {VIDEO}")
    return 0


if __name__ == "__main__":
    sys.exit(main(render="--manifest-only" not in sys.argv))
