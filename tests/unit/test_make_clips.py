"""Clip pipeline: the manifest of plotted data is reproducible and matches the committed one."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_clips.py"


def _load():
    spec = importlib.util.spec_from_file_location("make_clips", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_matches_committed_file():
    """Drift check: regenerate with `make assets` when this fails."""
    mc = _load()
    committed = json.loads(mc.MANIFEST.read_text())
    assert mc.build_manifest(mc.simulate()) == committed


def test_manifest_states_scenario_seed_and_frames():
    mc = _load()
    manifest = mc.build_manifest(mc.simulate())
    assert manifest["scenario"] == "nominal"
    assert manifest["seed"] == 1
    assert manifest["frame_count"] == mc.FRAME_COUNT
    assert manifest["ground_truth"] and manifest["range_only"] and manifest["fused"]


def test_render_is_byte_identical_and_small():
    mc = _load()
    data = mc.simulate()
    first = mc.render_gif(data)
    assert first == mc.render_gif(data)
    assert first[:6] == b"GIF89a"
    assert len(first) < 2_000_000


def test_committed_gif_is_under_two_megabytes():
    mc = _load()
    assert mc.OUTPUT.stat().st_size < 2_000_000


def test_script_never_reads_held_out():
    assert "held-out" not in SCRIPT.read_text()
