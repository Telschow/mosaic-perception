#!/usr/bin/env python3
"""Assemble the sixty-second summary clip (demo 1 in ``docs/demos.md``).

Beats 1 and 2 are the frames of the scenario clip (``make_clips.py``), beats 3 and 4
are the scoreboard and measurement-bias recovery panels (``make_assets.py``, rasterised
from the same benchmark data), beat 5 is an end card. The headline and subline are read
from ``docs/demos.md``; the clip adds no number of its own. Every frame carries the
"Synthetic world" label in its footer. Writes a GIF and a manifest of the beat order,
source files and timings (checked by ``tests/unit/test_make_summary_clip.py``). GIF only:
ffmpeg is not a documented dependency.
"""

from __future__ import annotations

import argparse
import functools
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import make_assets  # noqa: E402
import make_clips  # noqa: E402

DEMOS = Path("docs/demos.md")
OUTPUT = Path("docs-site/src/assets/generated/summary_clip.gif")
MANIFEST = OUTPUT.with_suffix(".json")
GENERATED = "docs-site/src/assets/generated"
URL = "https://telschow.github.io/mosaic-perception/"
END_CARD = "Synthetic world. Full results and limits:"
LABEL = "Synthetic world"
PANEL_SIZE = (640, 480)
SIZE = (640, 620)
FOOTER_BOX = (0, 590, 640, 620)  # holds only the label, identical in every frame
FRAME_MS = make_clips.FRAME_MS
HOLD_MS = {"range_only": 2000, "fused": 3000, "scoreboard": 14000, "recovery": 14000}
END_CARD_MS = 8000
BEAT_SOURCES = {
    "range_only": [f"{GENERATED}/scenario_clip.json", "scripts/make_clips.py"],
    "fused": [f"{GENERATED}/scenario_clip.json", "scripts/make_clips.py"],
    "scoreboard": [f"{GENERATED}/scoreboard.svg", "artifacts/benchmark/benchmark.json"],
    "recovery": [
        f"{GENERATED}/bias_recovery.svg",
        "artifacts/benchmark/benchmark.json",
    ],
    "end_card": ["docs/demos.md"],
}
PANEL_HEADERS = {
    "scoreboard": "Adding the camera: the scoreboard",
    "recovery": "Where bias estimation helps",
}
INK = (40, 40, 40)
WHITE = (255, 255, 255)


def read_captions(demos: Path = DEMOS) -> tuple[str, str]:
    text = demos.read_text()
    headline = re.search(r"^> \*\*(.+)\*\*\s*$", text, re.M)
    subline = re.search(r"^> \*(?!\*)(.+)\*\s*$", text, re.M)
    if headline is None or subline is None:
        raise ValueError("docs/demos.md has no headline blockquote")
    return headline.group(1), subline.group(1)


def _font(size: int, bold: bool = False):
    import matplotlib
    from PIL import ImageFont

    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / name), size)


def _wrap(draw: Any, text: str, font: Any, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=font) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return [*lines, line]


def _canvas(panel: Any) -> Any:
    """Place a 640x480 panel above the caption band: headline, subline, label."""
    from PIL import Image, ImageDraw

    headline, subline = read_captions()
    image = Image.new("RGB", SIZE, WHITE)
    image.paste(panel, (0, 0))
    draw = ImageDraw.Draw(image)
    draw.line((0, PANEL_SIZE[1], SIZE[0], PANEL_SIZE[1]), fill=(200, 200, 200), width=1)
    draw.text((10, 488), headline, fill=INK, font=_font(16, bold=True))
    small = _font(13)
    for row, line in enumerate(_wrap(draw, subline, small, SIZE[0] - 20)[:3]):
        draw.text((10, 514 + 19 * row), line, fill=INK, font=small)
    draw.text((10, FOOTER_BOX[1] + 4), LABEL, fill=INK, font=_font(15, bold=True))
    return image


def _panel_frame(build: Any, data: dict[str, Any], header: str) -> Any:
    from PIL import Image, ImageDraw

    png = Image.open(io.BytesIO(make_assets.to_png(build, data))).convert("RGB")
    width = PANEL_SIZE[0]
    png = png.resize((width, round(png.height * width / png.width)), Image.Resampling.LANCZOS)
    panel = Image.new("RGB", PANEL_SIZE, WHITE)
    ImageDraw.Draw(panel).text((10, 8), header, fill=INK, font=_font(18))
    panel.paste(png, (0, 40 + (PANEL_SIZE[1] - 40 - png.height) // 2))
    return panel


def _end_card() -> Any:
    from PIL import Image, ImageDraw

    panel = Image.new("RGB", PANEL_SIZE, WHITE)
    draw = ImageDraw.Draw(panel)
    for y, (text, size) in zip((200, 250), ((END_CARD, 20), (URL, 17)), strict=True):
        font = _font(size, bold=y == 200)
        x = (PANEL_SIZE[0] - draw.textlength(text, font=font)) / 2
        draw.text((x, y), text, fill=INK, font=font)
    return panel


@functools.cache
def build_beats() -> list[dict[str, Any]]:
    scenario = make_clips.render_frames(make_clips.simulate())
    split = make_clips.RANGE_ONLY_FRAMES
    scoreboard = make_assets.load_scoreboard_data(make_assets.BENCHMARK)
    recovery = make_assets.load_recovery_data(make_assets.BENCHMARK)
    frames = {
        "range_only": scenario[:split],
        "fused": scenario[split:],
        "scoreboard": [
            _panel_frame(make_assets.scoreboard_figure, scoreboard, PANEL_HEADERS["scoreboard"])
        ],
        "recovery": [
            _panel_frame(make_assets.recovery_figure, recovery, PANEL_HEADERS["recovery"])
        ],
        "end_card": [_end_card()],
    }
    beats = []
    for beat_id, images in frames.items():
        hold = HOLD_MS.get(beat_id, END_CARD_MS)
        durations = (
            [FRAME_MS] * (len(images) - 1) + [hold]
            if beat_id in ("range_only", "fused")
            else [hold]
        )
        beats.append(
            {
                "id": beat_id,
                "sources": BEAT_SOURCES[beat_id],
                "frames": [_canvas(image) for image in images],
                "panels": images,
                "durations": durations,
                **({"scenario": recovery["scenario"]} if beat_id == "recovery" else {}),
            }
        )
    return beats


def build_manifest(beats: list[dict[str, Any]]) -> dict[str, Any]:
    headline, subline = read_captions()
    entries = []
    start = 0
    for beat in beats:
        duration = sum(beat["durations"])
        entries.append(
            {
                "id": beat["id"],
                **({"scenario": beat["scenario"]} if "scenario" in beat else {}),
                "sources": beat["sources"],
                "frame_count": len(beat["frames"]),
                "start_ms": start,
                "duration_ms": duration,
            }
        )
        start += duration
    return {
        "label": LABEL,
        "headline": headline,
        "subline": subline,
        "end_card": END_CARD,
        "url": URL,
        "size": list(SIZE),
        "frame_count": sum(len(b["frames"]) for b in beats),
        "total_ms": start,
        "beats": entries,
    }


def render_gif(beats: list[dict[str, Any]]) -> bytes:
    from PIL import Image

    frames = [f for beat in beats for f in beat["frames"]]
    durations = [d for beat in beats for d in beat["durations"]]
    quantized = [
        f.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        for f in frames
    ]
    buffer = io.BytesIO()
    quantized[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    return buffer.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--format",
        choices=("gif", "mp4"),
        default="gif",
        help="gif (default) or mp4: the 9:16 and 16:9 cuts, which need ffmpeg (see make_mp4.py)",
    )
    if parser.parse_args(argv).format == "mp4":
        import make_mp4

        return make_mp4.main()
    beats = build_beats()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render_gif(beats))
    MANIFEST.write_text(json.dumps(build_manifest(beats), indent=1) + "\n")
    print(f"wrote {OUTPUT} and {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
