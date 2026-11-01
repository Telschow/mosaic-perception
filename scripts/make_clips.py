#!/usr/bin/env python3
"""Generate the animated scenario clip for demo 1 (beats 1 and 2 in ``docs/demos.md``).

Simulates the ``nominal`` scenario at seed 1 with one target through the public
``run_pair`` API (the path ``mosaic run`` uses), then draws a GIF: ground-truth path,
the range-only track, then the fused track on the same world. Writes a JSON manifest
of the plotted data next to the GIF so a test can detect drift without comparing GIF
bytes across platforms. Fixed frame count, size, palette and the font bundled with
matplotlib make the GIF byte-deterministic on one platform. Nothing is read from disk
besides that font; every plotted number comes from the simulation.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any

from mosaic_perception.domain.models import TrackStatus
from mosaic_perception.experiment import RunRecord, run_pair
from mosaic_perception.scenarios import resolve_scenario

SCENARIO = "nominal"
SEED = 1
DURATION = 10.0
NUM_OBJECTS = 1
LABEL = "Synthetic world, seed 1"
FRAME_COUNT = 60
RANGE_ONLY_FRAMES = 25  # frames showing ground truth plus the range-only track alone
SIZE = (640, 480)
MARGIN = 40
FRAME_MS = 100
LAST_FRAME_MS = 2000
OUTPUT = Path("docs-site/src/assets/generated/scenario_clip.gif")
MANIFEST = OUTPUT.with_suffix(".json")
COLORS = {
    "background": (255, 255, 255),
    "text": (40, 40, 40),
    "ground_truth": (150, 150, 150),
    "range_only": (77, 77, 77),
    "fused": (27, 108, 168),
}
LIVE_STATUSES = {TrackStatus.CONFIRMED, TrackStatus.COASTING}


def _track_path(record: RunRecord, times: list[float]) -> list[list[float] | None]:
    """Position of the longest-lived confirmed/coasting track at each world time."""
    by_track: dict[str, dict[float, list[float]]] = {}
    for snap in record.snapshots:
        if snap.status in LIVE_STATUSES:
            by_track.setdefault(snap.track_id, {})[snap.time] = snap.state[:2]
    if not by_track:
        return [None] * len(times)
    best = max(by_track.values(), key=len)
    return [best.get(t) for t in times]


def simulate() -> dict[str, Any]:
    config = resolve_scenario(SCENARIO, seed=SEED, duration=DURATION, num_objects=NUM_OBJECTS)
    pair = run_pair(config)
    times = [state.time for state in pair.states]
    object_id = next(iter(pair.states[0].objects))
    truth = [
        [state.objects[object_id].position.x, state.objects[object_id].position.y]
        for state in pair.states
    ]
    return {
        "times": times,
        "ground_truth": truth,
        "range_only": _track_path(pair.range_only, times),
        "fused": _track_path(pair.fused, times),
    }


def _round(path: list[list[float] | None]) -> list[list[float] | None]:
    return [None if p is None else [round(p[0], 2), round(p[1], 2)] for p in path]


def build_manifest(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario": SCENARIO,
        "seed": SEED,
        "duration": DURATION,
        "num_objects": NUM_OBJECTS,
        "label": LABEL,
        "frame_count": FRAME_COUNT,
        "ground_truth": _round(data["ground_truth"]),
        "range_only": _round(data["range_only"]),
        "fused": _round(data["fused"]),
    }


def _font(size: int):
    import matplotlib
    from PIL import ImageFont

    path = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf"
    return ImageFont.truetype(str(path), size)


def _palette_image():
    """Fixed palette: the clip colors plus a grey ramp for anti-aliased text edges."""
    from PIL import Image

    colors = list(COLORS.values()) + [(v, v, v) for v in range(32, 256, 32)]
    flat = [channel for color in colors for channel in color]
    image = Image.new("P", (1, 1))
    image.putpalette(flat + [0] * (768 - len(flat)))
    return image


def render_gif(data: dict[str, Any]) -> bytes:
    from PIL import Image, ImageDraw

    paths = [p for key in ("ground_truth", "range_only", "fused") for p in data[key] if p]
    xs = [p[0] for p in paths]
    ys = [p[1] for p in paths]
    width, height = SIZE
    scale = min(
        (width - 2 * MARGIN) / (max(xs) - min(xs) or 1.0),
        (height - 2 * MARGIN - 20) / (max(ys) - min(ys) or 1.0),
    )

    def to_px(p: list[float]) -> tuple[float, float]:
        return (
            MARGIN + (p[0] - min(xs)) * scale,
            height - MARGIN - (p[1] - min(ys)) * scale,
        )

    n = len(data["times"])
    title, small = _font(18), _font(14)
    labels = {
        "ground_truth": "ground truth",
        "range_only": "range-only track",
        "fused": "fused track",
    }
    frames = []
    for i in range(FRAME_COUNT):
        upto = max(1, round((i + 1) * n / FRAME_COUNT))
        image = Image.new("RGB", SIZE, COLORS["background"])
        draw = ImageDraw.Draw(image)
        shown = ["ground_truth", "range_only"] + (["fused"] if i >= RANGE_ONLY_FRAMES else [])
        for row, key in enumerate(shown):
            pts = [to_px(p) for p in data[key][:upto] if p]
            if len(pts) > 1:
                draw.line(pts, fill=COLORS[key], width=3 if key != "ground_truth" else 1)
            if pts and key != "ground_truth":
                x, y = pts[-1]
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=COLORS[key])
            draw.line((10, 56 + 18 * row, 34, 56 + 18 * row), fill=COLORS[key], width=3)
            draw.text((40, 48 + 18 * row), labels[key], fill=COLORS["text"], font=small)
        caption = "Range sensor alone" if i < RANGE_ONLY_FRAMES else "Range sensor plus camera"
        draw.text((10, 8), caption, fill=COLORS["text"], font=title)
        draw.text((10, height - 24), LABEL, fill=COLORS["text"], font=small)
        frames.append(image.quantize(palette=_palette_image(), dither=Image.Dither.NONE))
    durations = [FRAME_MS] * (FRAME_COUNT - 1) + [LAST_FRAME_MS]
    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    return buffer.getvalue()


def main() -> int:
    data = simulate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render_gif(data))
    MANIFEST.write_text(json.dumps(build_manifest(data), indent=1) + "\n")
    print(f"wrote {OUTPUT} and {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
