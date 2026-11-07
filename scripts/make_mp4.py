#!/usr/bin/env python3
"""Render the feed-ready MP4 cuts of the summary clip (``make mp4``).

Re-lays the five beats of ``summary_clip`` (same panels, same order) at 1080x1920 (9:16)
and 1920x1080 (16:9) with captions of at least 48 px, so they stay readable at 360 px
wide. Burned-in captions carry no numbers of their own; the numbers on the scoreboard and
recovery panels come from ``artifacts/benchmark/benchmark.json``. Also writes an ``.srt``,
a poster frame and a manifest of the plan (commit, sources, cue timings). ffmpeg is an
optional tool: without it ``main`` says so and renders nothing. Tests check the plan and
the ffmpeg command, never the encoded bytes.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _draw  # noqa: E402
import make_assets  # noqa: E402
import make_summary_clip  # noqa: E402

OUTPUT_DIR = Path("docs-site/src/assets/generated")
SUMMARY_MANIFEST = OUTPUT_DIR / "summary_clip.json"
MANIFEST = OUTPUT_DIR / "summary_clip_mp4.json"
SRT = OUTPUT_DIR / "summary_clip.srt"
POSTER = OUTPUT_DIR / "summary_clip_poster.png"
FORMATS = {"9x16": (1080, 1920), "16x9": (1920, 1080)}
URL = make_summary_clip.URL
LABEL = make_summary_clip.LABEL
CAPTION_PX = 56
LABEL_PX = 48
FPS = 30
CHARTS = ("scoreboard", "recovery")
HOLD_MS = {"scoreboard": 8000, "recovery": 8000, "end_card": 5000}
CAPTIONS = {
    "fused": "Add a camera. The track looks better.",
    "scoreboard": "Scored across many runs, it is mostly worse.",
    "recovery": "A small camera bias can be estimated and partly fixed.",
}
END_URL_LINES = ("telschow.github.io", "/mosaic-perception/")
SOURCES = [
    "artifacts/benchmark/benchmark.json",
    "docs/demos.md",
    "docs-site/src/assets/generated/summary_clip.json",
    "docs-site/src/assets/generated/scenario_clip.json",
    "docs-site/src/assets/generated/scoreboard.svg",
    "docs-site/src/assets/generated/bias_recovery.svg",
    "scripts/make_mp4.py",
]
MISSING_FFMPEG = (
    "ffmpeg not found: `make mp4` needs it to encode. Install it (macOS: brew install ffmpeg) "
    "and run it again. Nothing was rendered; the GIF and stills do not need ffmpeg."
)


def _caption(beat_id: str) -> str:
    if beat_id == "range_only":
        return make_summary_clip.read_captions()[0]
    if beat_id == "end_card":
        return f"{make_summary_clip.END_CARD} {URL}"
    return CAPTIONS[beat_id]


def _facts(beat_id: str) -> list[str]:
    """On-screen figures, read from the benchmark artifact (never typed here)."""
    if beat_id == "scoreboard":
        rows = make_assets.load_scoreboard_data(make_assets.BENCHMARK)["rows"]
        row = next(
            r
            for r in rows
            if (r["comparison"], r["metric"]) == ("fused_vs_range_only", "precision")
        )
        return [
            f"Precision: worse in {row['worse']} scenarios, better in {row['better']}, "
            f"unclear in {row['inconclusive']}."
        ]
    if beat_id == "recovery":
        data = make_assets.load_recovery_data(make_assets.BENCHMARK)
        precision = data["metrics"]["precision"]
        if make_assets.recovery_verdict(precision) != "recovers":
            return [
                f"Scenario: {data['scenario']}",
                "Bias estimation does not recover fused's precision loss.",
            ]
        return [
            f"Scenario: {data['scenario']}",
            f"Bias estimation recovers {precision['recovered_share']:.0%} of fused's precision loss.",
        ]
    return []


def build_plan(summary: dict[str, Any], commit: str) -> dict[str, Any]:
    """Cue timings for the MP4: animated beats keep their length, still beats are held."""
    cues = []
    start = 0
    for beat in summary["beats"]:
        duration = HOLD_MS.get(beat["id"], beat["duration_ms"])
        cues.append(
            {
                "id": beat["id"],
                "start_ms": start,
                "end_ms": start + duration,
                "text": _caption(beat["id"]),
                "facts": _facts(beat["id"]),
            }
        )
        start += duration
    seeds = json.loads(make_assets.BENCHMARK.read_text())["protocol"]["seeds"]
    return {
        "commit": commit,
        "seed_label": f"development seeds {seeds[0]}-{seeds[-1]}",
        "total_ms": start,
        "cues": cues,
        "sources": SOURCES,
    }


def srt_time(ms: int) -> str:
    hours, rest = divmod(ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    seconds, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def to_srt(cues: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"{i}\n{srt_time(c['start_ms'])} --> {srt_time(c['end_ms'])}\n"
        + "\n".join([c["text"], *c["facts"]])
        + "\n"
        for i, c in enumerate(cues, start=1)
    )


def ffmpeg_command(
    concat_file: Path, output: Path, size: tuple[int, int], duration_ms: int | None = None
) -> list[str]:
    """The concat demuxer repeats the last file once, so ``duration_ms`` trims the cut."""
    width, height = size
    limit = [] if duration_ms is None else ["-t", f"{duration_ms / 1000:.3f}"]
    return [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-vf",
        f"scale={width}:{height}:flags=lanczos,fps={FPS},format=yuv420p",
        "-c:v",
        "libx264",
        "-crf",
        "20",
        "-preset",
        "medium",
        "-movflags",
        "+faststart",
        *limit,
        str(output),
    ]


def build_manifest(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": LABEL,
        "source_commit": plan["commit"],
        "seed_label": plan["seed_label"],
        "total_ms": plan["total_ms"],
        "min_text_px": CAPTION_PX,
        "outputs": {
            name: {"file": f"summary_clip_{name}.mp4", "size": list(size)}
            for name, size in FORMATS.items()
        },
        "srt": SRT.name,
        "poster": POSTER.name,
        "cues": plan["cues"],
        "sources": plan["sources"],
    }


def _compose(
    panel: Any, lines: list[str], facts: list[str], size: tuple[int, int], footer: list[str]
) -> Any:
    """Caption band on top, the beat's panel scaled to fit, the evidence label below."""
    from PIL import Image, ImageDraw

    width, height = size
    image = Image.new("RGB", size, make_summary_clip.WHITE)
    draw = ImageDraw.Draw(image)
    body = _draw.font(CAPTION_PX, bold=True)
    wrapped: list[str] = []
    for line in lines:
        wrapped += _draw.wrap(draw, line, body, width - 80)
    y = 60
    for line in wrapped:
        draw.text((40, y), line, fill=make_summary_clip.INK, font=body)
        y += CAPTION_PX + 14
    fact_font = _draw.font(LABEL_PX)
    for fact in facts:
        for line in _draw.wrap(draw, fact, fact_font, width - 80):
            draw.text((40, y + 10), line, fill=make_summary_clip.INK, font=fact_font)
            y += LABEL_PX + 10
        y += 10
    bottom = height - 40 - len(footer) * (LABEL_PX + 8)
    if panel is not None:
        room = (width - 80, bottom - (y + 30))
        scale = min(room[0] / panel.width, room[1] / panel.height)
        panel = panel.resize(
            (round(panel.width * scale), round(panel.height * scale)), Image.Resampling.LANCZOS
        )
        image.paste(panel, ((width - panel.width) // 2, y + 30))
    for row, line in enumerate(footer):
        draw.text(
            (40, height - 30 - (len(footer) - row) * (LABEL_PX + 8)),
            line,
            fill=make_summary_clip.INK,
            font=_draw.font(LABEL_PX, bold=row == 0),
        )
    return image


def _chart(beat_id: str) -> Any:
    """The beat's chart, rasterised sharply and cropped to its content."""
    import io

    from PIL import Image, ImageChops

    build, data = {
        "scoreboard": (
            make_assets.scoreboard_figure,
            make_assets.load_scoreboard_data(make_assets.BENCHMARK),
        ),
        "recovery": (
            make_assets.recovery_figure,
            make_assets.load_recovery_data(make_assets.BENCHMARK),
        ),
    }[beat_id]
    image = Image.open(io.BytesIO(make_assets.to_png(build, data, dpi=220))).convert("RGB")
    box = ImageChops.difference(image, Image.new("RGB", image.size, (255, 255, 255))).getbbox()
    return image.crop(box) if box else image


def render_timeline(plan: dict[str, Any], size: tuple[int, int]) -> list[tuple[Any, int, str]]:
    """(image, duration_ms, beat id) for every frame of one cut."""
    beats = {b["id"]: b for b in make_summary_clip.build_beats()}
    footer = [
        LABEL.upper(),
        plan["seed_label"],
        f"artifact commit {plan['commit'][:12]}",
    ]
    timeline: list[tuple[Any, int, str]] = []
    for cue in plan["cues"]:
        beat = beats[cue["id"]]
        text = [cue["text"]]
        if cue["id"] == "end_card":
            text = [make_summary_clip.END_CARD, *END_URL_LINES]
        panels = [None] if cue["id"] == "end_card" else beat["panels"]
        if cue["id"] in CHARTS:
            panels = [_chart(cue["id"])]
        durations = (
            beat["durations"]
            if cue["id"] in ("range_only", "fused")
            else [cue["end_ms"] - cue["start_ms"]]
        )
        for panel, duration in zip(panels, durations, strict=True):
            timeline.append(
                (_compose(panel, text, cue["facts"], size, footer), duration, cue["id"])
            )
    return timeline


def _encode(timeline: list[tuple[Any, int, str]], output: Path, size: tuple[int, int]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        lines = []
        for index, (image, duration, _beat) in enumerate(timeline):
            path = Path(tmp) / f"{index:04d}.png"
            image.save(path)
            lines += [f"file '{path}'", f"duration {duration / 1000:.3f}"]
        lines.append(
            f"file '{Path(tmp) / f'{len(timeline) - 1:04d}.png'}'"
        )  # concat needs a last file
        concat = Path(tmp) / "frames.txt"
        concat.write_text("\n".join(lines) + "\n")
        total = sum(duration for _, duration, _ in timeline)
        subprocess.run(ffmpeg_command(concat, output, size, total), check=True)


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print(MISSING_FFMPEG, file=sys.stderr)
        return 1
    commit = json.loads(make_assets.BENCHMARK.read_text())["code"]["git_commit"]
    plan = build_plan(json.loads(SUMMARY_MANIFEST.read_text()), commit)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, size in FORMATS.items():
        timeline = render_timeline(plan, size)
        if name == "9x16":
            next(image for image, _, beat in timeline if beat == "scoreboard").save(POSTER)
        _encode(timeline, OUTPUT_DIR / f"summary_clip_{name}.mp4", size)
    SRT.write_text(to_srt(plan["cues"]))
    MANIFEST.write_text(json.dumps(build_manifest(plan), indent=1) + "\n")
    print(f"wrote {MANIFEST}, {SRT}, {POSTER} and {len(FORMATS)} MP4 files in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
