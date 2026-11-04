"""Manim scene for the 4:5 Hook video. Rendered by ``make_video.py``; draws ``build_plan``.

Run only through Manim (``uv run --with manim``). The lines are the tracker's real tracks from
one development run; the two figures come from the plan, which reads
``artifacts/benchmark/benchmark.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from manim import (
    BOLD,
    DOWN,
    NORMAL,
    UP,
    DashedVMobject,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStartMap,
    Scene,
    Text,
    ValueTracker,
    VGroup,
    VMobject,
    always_redraw,
    config,
    linear,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_assets  # noqa: E402
import make_hero  # noqa: E402
import make_video  # noqa: E402

from mosaic_perception.domain.models import TrackStatus  # noqa: E402
from mosaic_perception.experiment import run_pair  # noqa: E402
from mosaic_perception.scenarios import resolve_scenario  # noqa: E402

config.pixel_width, config.pixel_height = make_video.SIZE
config.frame_height, config.frame_width = 12.5, 10.0
config.background_color = "#0E1116"
config.frame_rate = 30

FONT = "Helvetica Neue"
INK, MUTED, RED, BLUE, GREY = "#F2F4F7", "#9AA3B2", "#FF6B6B", "#4DA3F0", "#B7BDC8"
LIVE = {TrackStatus.CONFIRMED, TrackStatus.COASTING}
PAYLOAD = json.loads(make_assets.BENCHMARK.read_text())
PLAN = make_video.build_plan(PAYLOAD)
BEATS = {b["id"]: b for b in PLAN["beats"]}
PLOT = (8.6, 6.2, 0.0, -0.4)  # width, height, centre x, centre y


def label(s, size=40, color=INK, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def simulate_tracks():
    """The true path and every live track (id -> [(frame index, x, y)]) for both methods."""
    config_ = resolve_scenario(
        PLAN["scenario"],
        seed=PLAN["seed"],
        duration=make_hero.DURATION,
        num_objects=make_hero.NUM_OBJECTS,
    )
    pair = run_pair(config_)
    index = {state.time: i for i, state in enumerate(pair.states)}
    object_id = next(iter(pair.states[0].objects))
    truth = [
        (s.objects[object_id].position.x, s.objects[object_id].position.y) for s in pair.states
    ]
    tracks = {}
    for method in ("range_only", "fused"):
        by_id: dict[str, list[tuple[int, float, float]]] = {}
        for snap in pair.record(method).snapshots:
            if snap.status in LIVE and snap.time in index:
                by_id.setdefault(snap.track_id, []).append(
                    (index[snap.time], snap.state[0], snap.state[1])
                )
        tracks[method] = by_id
    return truth, tracks


TRUTH, TRACKS = simulate_tracks()


def _mapper():
    """Scale from the true path, padded so nearby ghosts fit; farther points are clipped."""
    xs, ys = [q[0] for q in TRUTH], [q[1] for q in TRUTH]
    pad_x, pad_y = 1.0 * (max(xs) - min(xs)), 0.45 * (max(ys) - min(ys))
    lo_x, hi_x, lo_y, hi_y = min(xs) - pad_x, max(xs) + pad_x, min(ys) - pad_y, max(ys) + pad_y
    w, h, cx, cy = PLOT
    scale = min(w / ((hi_x - lo_x) or 1), h / ((hi_y - lo_y) or 1))
    mx, my = (hi_x + lo_x) / 2, (hi_y + lo_y) / 2
    return lambda x, y: np.array([cx + (x - mx) * scale, cy + (y - my) * scale, 0.0])


TO = _mapper()


def _inside(point) -> bool:
    w, h, cx, cy = PLOT
    return abs(point[0] - cx) <= w / 2 and abs(point[1] - cy) <= h / 2


def _runs(points):
    """Split a polyline into the runs that stay inside the frame."""
    run, runs = [], []
    for point in points:
        if _inside(point):
            run.append(point)
        else:
            runs.append(run)
            run = []
    runs.append(run)
    return [r for r in runs if len(r) > 1]


class Hook(Scene):
    def construct(self):
        self.add(
            label(
                f"{PLAN['label']}  ·  {PLAN['seed_label']}  ·  artifact commit {PLAN['commit'][:7]}",
                18,
                MUTED,
            ).to_edge(DOWN, buff=0.35)
        )
        self._question(BEATS["question"])
        self._world(BEATS["one_sensor"], "range_only", GREY)
        self._world(BEATS["two_sensors"], "fused", BLUE)
        self._numbers(BEATS["numbers"])
        self._close(BEATS["close"])

    def _clear(self, *mobs, run_time=0.6):
        self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def _question(self, beat):
        title = (
            label("\n".join(beat["text"]), 54, INK, BOLD, line_spacing=1.2)
            .scale_to_fit_width(8.8)
            .move_to([0, 1.2, 0])
        )
        note = label(beat["note"], 28, MUTED).move_to([0, -1.2, 0]).scale_to_fit_width(8.6)
        self.play(FadeIn(title, shift=UP * 0.3), run_time=1.0)
        self.play(FadeIn(note), run_time=0.8)
        self.wait(beat["duration_s"] - 2.8)
        self._clear(title, note)

    def _world(self, beat, method, color):
        head = label(beat["text"][0], 46, INK, BOLD).move_to([0, 5.1, 0])
        sub = label(beat["text"][1], 30, MUTED).move_to([0, 4.3, 0]).scale_to_fit_width(9.0)
        note = label(beat["note"], 32, INK, BOLD).move_to([0, -4.3, 0]).scale_to_fit_width(9.0)
        u = ValueTracker(0)
        n = len(TRUTH)
        truth_path = VMobject().set_points_as_corners([TO(*q) for q in TRUTH])
        truth_dash = DashedVMobject(truth_path, num_dashes=70).set_stroke("#E6E9EF", 3)

        def frame():
            return int(u.get_value() * (n - 1))

        def lines():
            k = frame()
            group = VGroup()
            for pts_ in TRACKS[method].values():
                seen = [TO(x, y) for i, x, y in pts_ if i <= k]
                for run in _runs(seen):
                    group.add(VMobject().set_points_as_corners(run).set_stroke(color, 4, 0.85))
            return group

        mover = always_redraw(lambda: Dot(TO(*TRUTH[frame()]), radius=0.13, color=INK))
        live = always_redraw(lines)
        self.play(FadeIn(head), FadeIn(sub), FadeIn(truth_dash), run_time=0.8)
        self.add(live, mover)
        self.play(u.animate.set_value(1), run_time=beat["duration_s"] * 0.5, rate_func=linear)
        self.play(FadeIn(note), run_time=0.6)
        self.wait(beat["duration_s"] - 0.8 - beat["duration_s"] * 0.5 - 0.6 - 0.6)
        self._clear(head, sub, note, truth_dash, live, mover)

    def _numbers(self, beat):
        shown = beat["real_of_100"]
        head = label(beat["text"][0], 40, INK, BOLD).move_to([0, 5.2, 0])
        sub = label(beat["text"][1], 40, INK, BOLD).move_to([0, 4.5, 0])
        self.play(FadeIn(head), FadeIn(sub), run_time=0.8)
        groups, texts = [], []
        for x, method, name in zip(
            (-2.45, 2.45), ("range_only", "fused"), beat["columns"], strict=True
        ):
            real = shown[method]
            dots = VGroup(
                *[
                    Dot(
                        [x + (c - 4.5) * 0.34, 2.5 - r * 0.34 - 0.2, 0],
                        radius=0.12,
                        color=INK if r * 10 + c < real else RED,
                    )
                    for r in range(10)
                    for c in range(10)
                ]
            )
            groups.append(dots)
            texts.append(
                label(name, 28, GREY if method == "range_only" else BLUE, BOLD).move_to([x, 3.5, 0])
            )
            texts.append(
                label(str(real), 96, INK if method == "range_only" else RED, BOLD).move_to(
                    [x, -1.7, 0]
                )
            )
            texts.append(label("of 100 were real", 24, MUTED).move_to([x, -2.7, 0]))
        self.play(*[FadeIn(t) for t in texts[0::3]], run_time=0.5)
        self.play(*[LaggedStartMap(FadeIn, g, lag_ratio=0.02, run_time=2.2) for g in groups])
        self.play(*[FadeIn(t) for i, t in enumerate(texts) if i % 3], run_time=0.8)
        avg = (
            label(
                f"white: the real object   red: a ghost   ·   average over {PLAN['n_seeds']} runs",
                20,
                MUTED,
            )
            .move_to([0, -3.6, 0])
            .scale_to_fit_width(9.0)
        )
        self.play(FadeIn(avg), run_time=0.5)
        self.wait(beat["duration_s"] - 0.8 - 0.5 - 2.2 - 0.8 - 0.5 - 0.6)
        self._clear(head, sub, avg, *groups, *texts)

    def _close(self, beat):
        text = label("\n".join(beat["text"]), 46, INK, BOLD, line_spacing=1.2).move_to([0, 1.0, 0])
        text.scale_to_fit_width(8.8)
        note = label(beat["note"], 26, MUTED).move_to([0, -1.6, 0]).scale_to_fit_width(8.8)
        self.play(FadeIn(text, shift=UP * 0.3), run_time=1.0)
        self.play(FadeIn(note), run_time=0.8)
        self.wait(beat["duration_s"] - 1.8)
