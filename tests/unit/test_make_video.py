"""Hook video plan: honest framing, numbers from the artifact, optional Manim."""

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


def test_the_opener_is_labelled_an_illustration_and_shows_no_numbers():
    mv = _load()
    plan = mv.build_plan(_payload(mv))
    opener = plan["beats"][0]
    assert opener["id"] == "opener"
    assert "illustration, not data" in opener["label"].lower()
    for line in opener["text"]:
        assert not re.search(r"\d", line), line


def test_beats_run_opener_then_bridge_then_the_real_runs():
    mv = _load()
    plan = mv.build_plan(_payload(mv))
    assert [b["id"] for b in plan["beats"]] == ["opener", "bridge", "hurts", "recovers"]


def test_the_framing_is_about_this_simulation_not_fusion_in_general():
    mv = _load()
    plan = mv.build_plan(_payload(mv))
    text = " ".join(" ".join(b["text"]) for b in plan["beats"]).lower()
    assert "in my simulation" in text
    assert "i added a sensor" not in text
    assert "fusion is" not in text


def test_real_run_numbers_are_the_artifacts_paired_values():
    mv = _load()
    payload = _payload(mv)
    plan = mv.build_plan(payload)
    stills = mv.make_hero.build_manifest(payload)["stills"]
    by_id = {b["id"]: b for b in plan["beats"]}
    for beat_id in ("hurts", "recovers"):
        beat, still = by_id[beat_id], stills[beat_id]
        assert beat["scenario"] == still["scenario"]
        assert beat["seed"] == still["seed"]
        assert beat["precision"] == still["precision"]
    assert plan["n_seeds"] == len(payload["protocol"]["seeds"])


def test_label_seed_group_and_commit_are_carried():
    mv = _load()
    payload = _payload(mv)
    plan = mv.build_plan(payload)
    assert plan["label"] == "SYNTHETIC WORLD"
    assert plan["seed_label"] == "development seeds 0-24"
    assert plan["commit"] == payload["code"]["git_commit"]


def test_length_is_a_feed_length():
    mv = _load()
    assert 15 <= mv.build_plan(_payload(mv))["total_s"] <= 30


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
