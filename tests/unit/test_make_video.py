"""Hook video plan: one idea, plain words, numbers from the artifact, optional Manim."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_video.py"


def _load():
    spec = importlib.util.spec_from_file_location("make_video", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(mv):
    return json.loads(mv.make_assets.BENCHMARK.read_text())


def test_one_idea_in_five_beats():
    mv = _load()
    plan = mv.build_plan(_payload(mv))
    assert [b["id"] for b in plan["beats"]] == [
        "question",
        "one_sensor",
        "two_sensors",
        "numbers",
        "close",
    ]


def test_only_the_numbers_beat_carries_figures_and_captions_have_no_digits():
    mv = _load()
    for beat in mv.build_plan(_payload(mv))["beats"]:
        for line in [*beat["text"], beat.get("note", "")]:
            assert not re.search(r"\d", line), (beat["id"], line)
        assert ("real_of_100" in beat) == (beat["id"] == "numbers")


def test_the_framing_is_about_this_simulation_not_fusion_in_general():
    mv = _load()
    plan = mv.build_plan(_payload(mv))
    text = " ".join(" ".join([*b["text"], b.get("note", "")]) for b in plan["beats"]).lower()
    assert "simulation" in text
    assert "fusion is" not in text and "always" not in text


def test_the_two_figures_are_the_artifacts_scenario_means():
    mv = _load()
    payload = _payload(mv)
    plan = mv.build_plan(payload)
    entry = next(s for s in payload["scenarios"] if s["scenario"]["name"] == plan["scenario"])
    shown = next(b for b in plan["beats"] if b["id"] == "numbers")["real_of_100"]
    assert shown == {
        "range_only": round(100 * entry["aggregate"]["range_only"]["precision"]),
        "fused": round(100 * entry["aggregate"]["fused"]["precision"]),
    }
    assert shown["fused"] < shown["range_only"]
    assert plan["scenario"] == mv.make_hero.choose_hurt_scenario(payload)


def test_label_seed_group_and_commit_are_carried():
    mv = _load()
    payload = _payload(mv)
    plan = mv.build_plan(payload)
    assert plan["label"] == "SYNTHETIC WORLD"
    assert plan["seed_label"] == "development seeds 0-24"
    assert plan["commit"] == payload["code"]["git_commit"]
    assert plan["seed"] == 0


def test_every_caption_is_held_long_enough_to_read():
    mv = _load()
    for beat in mv.build_plan(_payload(mv))["beats"]:
        words = sum(len(line.split()) for line in [*beat["text"], beat.get("note", "")])
        assert beat["duration_s"] >= 4.0 and beat["duration_s"] >= words * 0.35, beat["id"]


def test_length_is_a_feed_length():
    mv = _load()
    assert 35 <= mv.build_plan(_payload(mv))["total_s"] <= 45


def test_format_is_four_by_five():
    mv = _load()
    assert mv.SIZE == (1080, 1350)


def test_script_reads_only_the_development_artifact():
    text = SCRIPT.read_text() + (ROOT / "scripts" / "video_scene.py").read_text()
    assert "held-out" not in text and "held_out" not in text


def test_committed_manifest_matches_the_artifact():
    mv = _load()
    committed = json.loads((ROOT / "docs-site/src/assets/generated/hook_video.json").read_text())
    assert mv.build_manifest(mv.build_plan(_payload(mv))) == committed


def test_without_manim_it_stops_with_a_clear_message_and_renders_nothing(capsys):
    mv = _load()
    with (
        mock.patch.object(mv.importlib.util, "find_spec", return_value=None),
        mock.patch.object(mv.subprocess, "run") as run,
    ):
        assert mv.main(render=True) == 1
    run.assert_not_called()
    assert "manim" in capsys.readouterr().err.lower()


def test_poster_is_taken_where_the_ghosts_are_on_screen():
    mv = _load()
    plan = mv.build_plan(_payload(mv))
    start = 0.0
    for beat in plan["beats"]:
        if beat["id"] == "two_sensors":
            assert start < plan["poster_s"] < start + beat["duration_s"]
        start += beat["duration_s"]


def test_poster_command_extracts_one_frame_at_that_time():
    mv = _load()
    command = mv.poster_command(Path("v.mp4"), Path("p.png"), 23.3)
    assert command[0] == "ffmpeg" and "-frames:v" in command
    assert command[command.index("-ss") + 1] == "23.30" and command[-1] == "p.png"
