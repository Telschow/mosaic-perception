"""Manim scene for the 4:5 Hook video. Rendered by ``make_video.py``; draws ``build_plan``.

Run only through Manim (``uv run --with manim``). Every printed number comes from the plan,
which reads ``artifacts/benchmark/benchmark.json``; the opener is an illustration and prints
none.
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
    RIGHT,
    UP,
    Create,
    DashedVMobject,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Scene,
    Text,
    ValueTracker,
    VMobject,
    always_redraw,
    config,
    linear,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_assets  # noqa: E402
import make_hero  # noqa: E402
import make_video  # noqa: E402

config.pixel_width, config.pixel_height = make_video.SIZE
config.frame_height, config.frame_width = 12.5, 10.0
config.background_color = "#0E1116"
config.frame_rate = 30

FONT = "Helvetica Neue"
INK, MUTED, RED, AMBER = "#F2F4F7", "#8B94A3", "#FF6B6B", "#F0A24D"
COL = {"range_only": "#B7BDC8", "fused": "#4DA3F0", "fused_bias_estimated": AMBER}
PAYLOAD = json.loads(make_assets.BENCHMARK.read_text())
PLAN = make_video.build_plan(PAYLOAD)
BEATS = {b["id"]: b for b in PLAN["beats"]}


def label(s, size=40, color=INK, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def _fill(track):
    out, last = [], None
    for t in track:
        last = t if t else last
        out.append(last)
    first = next(t for t in out if t)
    return [t or first for t in out]


class _Panel:
    """Truth dashed, live track, and the 95% ring that follows the head."""

    def __init__(self, data, method, cx, cy, w, h, pts, u):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        self.s = min(w / ((max(xs) - min(xs)) or 1), h / ((max(ys) - min(ys)) or 1))
        self.to = lambda q: np.array([cx + (q[0] - mx) * self.s, cy + (q[1] - my) * self.s, 0.0])
        track = _fill(data[method])
        self.pos = [self.to(t[0]) for t in track]
        self.cov = [t[1] for t in track]
        n, color = len(self.pos), COL[method]
        truth = VMobject().set_points_as_corners([self.to(q) for q in data["ground_truth"]])
        self.truth = DashedVMobject(truth, num_dashes=60).set_stroke("#566070", 2)

        def head():
            k = u.get_value() * (n - 1)
            i, f = int(k), k - int(k)
            return i, f, min(i + 1, n - 1)

        def line():
            i, f, j = head()
            pts_ = self.pos[: i + 1] + [self.pos[i] * (1 - f) + self.pos[j] * f]
            return VMobject().set_points_as_corners(pts_).set_stroke(color, 8)

        def ring():
            i, f, j = head()
            c = self.pos[i] * (1 - f) + self.pos[j] * f
            ring_pts = make_hero.ellipse((0.0, 0.0), self.cov[i], self.s)
            corners = [c + np.array([x, -y, 0]) for x, y in ring_pts]
            return (
                VMobject()
                .set_points_as_corners([*corners, corners[0]])
                .set_stroke(color, 5)
                .set_fill(color, 0.2)
            )

        def dot():
            i, f, j = head()
            return Dot(self.pos[i] * (1 - f) + self.pos[j] * f, radius=0.09, color=color)

        self.line, self.ring, self.dot = (
            always_redraw(line),
            always_redraw(ring),
            always_redraw(dot),
        )

    def mobs(self):
        return [self.truth, self.ring, self.line, self.dot]


class Hook(Scene):
    def construct(self):
        self.add(
            label(
                f"{PLAN['label']}  ·  {PLAN['seed_label']}  ·  artifact commit {PLAN['commit'][:7]}",
                18,
                MUTED,
            ).to_edge(DOWN, buff=0.35)
        )
        self._opener(BEATS["opener"])
        self._bridge(BEATS["bridge"])
        self._real_run(
            BEATS["hurts"], ("range_only", "fused"), ("range sensor only", "plus camera"), RED
        )
        self._real_run(
            BEATS["recovers"],
            ("fused", "fused_bias_estimated"),
            ("camera, bias ignored", "bias estimated"),
            AMBER,
        )

    def _opener(self, beat):
        tag = label(beat["label"], 22, AMBER, BOLD).to_corner(UP + RIGHT, buff=0.4)
        room = Rectangle(width=3.6, height=3.0, color="#566070").move_to([-2.9, 1.2, 0])
        door = Line([-1.1, 0.5, 0], [-1.1, 1.9, 0], color="#0E1116", stroke_width=10)
        person = Dot([-3.1, 1.2, 0], radius=0.22, color=INK)
        names = ("range sensor", "camera")
        w1 = label(names[0], 24, COL["range_only"]).move_to([1.6, 3.4, 0])
        w2 = label(names[1], 24, COL["fused"]).move_to([3.7, 3.4, 0])
        listing = label("track list", 24, MUTED).move_to([2.7, 1.9, 0])
        entry = label("person", 34, INK).move_to([2.7, 1.1, 0])
        self.play(FadeIn(tag), Create(room), Create(door), FadeIn(person), run_time=0.8)
        self.play(FadeIn(w1), FadeIn(w2), FadeIn(listing), FadeIn(entry), run_time=0.6)
        line1 = label(beat["text"][0], 36, INK, BOLD).move_to([0, -1.6, 0])
        self.play(FadeIn(line1), person.animate.move_to([-0.2, 1.2, 0]), run_time=1.2)
        self.play(FadeOut(person), run_time=0.4)
        line2 = label(beat["text"][1], 30, COL["range_only"], BOLD).move_to([0, -2.6, 0])
        strike = Line([2.0, 1.1, 0], [3.4, 1.1, 0], color=COL["range_only"], stroke_width=6)
        self.play(FadeIn(line2), Create(strike), run_time=1.0)
        line3 = label(beat["text"][2], 30, COL["fused"], BOLD).move_to([0, -3.6, 0])
        ghost = label("person", 34, RED).move_to([2.7, 1.1, 0])
        self.play(FadeIn(line3), strike.animate.set_opacity(0), FadeIn(ghost), run_time=1.0)
        self.wait(max(beat["duration_s"] - 5.4, 0.3))
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.mobjects[0]], run_time=0.4)

    def _bridge(self, beat):
        head, tail = beat["text"][0].split(", ", 1)
        text = label(f"{head},\n{tail}", 46, INK, BOLD, line_spacing=1.2).scale_to_fit_width(8.8)
        self.play(FadeIn(text, shift=UP * 0.3), run_time=0.6)
        self.wait(beat["duration_s"] - 1.2)
        self.play(FadeOut(text), run_time=0.6)

    def _real_run(self, beat, methods, names, accent):
        n = PLAN["n_seeds"]
        p = beat["precision"]
        data = make_hero.simulate(beat["scenario"], beat["seed"])
        u = ValueTracker(0)
        pts = list(data["ground_truth"]) + [t[0] for m in methods for t in data[m] if t]
        xs = (-2.45, 2.45)
        panels = [
            _Panel(data, m, x, -1.0, 4.4, 6.4, pts, u) for m, x in zip(methods, xs, strict=True)
        ]
        l1 = label(beat["text"][0], 50, INK, BOLD).move_to([0, 5.0, 0])
        l2 = label(beat["text"][1], 50, accent, BOLD).move_to([0, 4.2, 0]).scale_to_fit_width(9.0)
        caps = [
            label(name, 28, COL[m]).move_to([x, 2.75, 0])
            for name, m, x in zip(names, methods, xs, strict=True)
        ]
        run_s = beat["duration_s"] - 4.9
        self.play(
            FadeIn(l1, shift=UP * 0.3), FadeIn(l2, shift=UP * 0.3), *map(FadeIn, caps), run_time=0.7
        )
        self.add(*[m for panel in panels for m in panel.mobs()])
        self.play(*[FadeIn(panel.truth) for panel in panels], run_time=0.3)
        self.play(u.animate.set_value(1), run_time=run_s, rate_func=linear)
        sentence = (
            "precision vs range-only"
            if beat["id"] == "hurts"
            else "precision vs camera, bias ignored"
        )
        cap = label(f"{beat['scenario']}, seed {beat['seed']}, one drawn run", 20, MUTED).move_to(
            [0, 1.3, 0]
        )
        k = ValueTracker(0)
        big = always_redraw(
            lambda: label(f"{k.get_value():+.3f}", 96, accent, BOLD).move_to([0, -0.2, 0])
        )
        sub = label(
            f"{sentence}, paired over {n} seeds   95% CI [{p['ci95_low']:+.3f}, {p['ci95_high']:+.3f}]",
            20,
            MUTED,
        ).move_to([0, -1.1, 0])
        gone = [m for panel in panels for m in panel.mobs()] + caps
        self.play(*map(FadeOut, gone), FadeIn(cap), run_time=0.5)
        self.add(big)
        self.play(k.animate.set_value(p["mean"]), FadeIn(sub), run_time=1.4)
        self.wait(1.5)
        self.play(*map(FadeOut, [big, sub, cap, l1, l2]), run_time=0.5)
