#!/usr/bin/env python3
"""Plan and render the 4:5 Hook video (``make video``).

Beats: an illustrated ghost-witness opener (no numbers, tagged as an illustration), a bridge
line, then two real runs drawn from one development seed each, with the paired benchmark
values printed. The framing is about this simulated tracker, not fusion in general: the
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
ILLUSTRATION_LABEL = "ILLUSTRATION, NOT DATA"
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


def build_plan(payload: dict[str, Any]) -> dict[str, Any]:
    """Beats, captions and the numbers to print, all read from the development artifact."""
    manifest = make_hero.build_manifest(payload)
    seeds = payload["protocol"]["seeds"]
    stills = manifest["stills"]
    beats: list[dict[str, Any]] = [
        {
            "id": "opener",
            "duration_s": 6.5,
            "label": ILLUSTRATION_LABEL,
            "text": [
                "A person leaves the room.",
                "One witness crosses them off the list.",
                "The other keeps saying: still here.",
            ],
        },
        {
            "id": "bridge",
            "duration_s": 2.5,
            "text": ["In my simulation, the extra camera kept ghost tracks alive."],
        },
    ]
    captions = {
        "hurts": ["In my simulation,", "adding a camera made tracking worse."],
        "recovers": ["Estimate the camera's bias,", "and part of the loss comes back."],
    }
    durations = {"hurts": 10.0, "recovers": 10.0}
    for beat_id in ("hurts", "recovers"):
        still = stills[beat_id]
        beats.append(
            {
                "id": beat_id,
                "duration_s": durations[beat_id],
                "text": captions[beat_id],
                "scenario": still["scenario"],
                "seed": still["seed"],
                "comparison": still["comparison"],
                "precision": still["precision"],
            }
        )
    return {
        "label": LABEL,
        "commit": payload["code"]["git_commit"],
        "seed_label": f"development seeds {seeds[0]}-{seeds[-1]}",
        "n_seeds": len(seeds),
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
