"""Asset pipeline: the generated SVG is deterministic and matches the benchmark artifact."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_assets.py"
FIGURE = ROOT / "docs-site/src/assets/generated/position_rmse_paired.svg"


def _load():
    spec = importlib.util.spec_from_file_location("make_assets", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_is_byte_identical_across_runs():
    ma = _load()
    data = ma.load_figure_data(ma.BENCHMARK, ma.PER_SEED)
    assert ma.render_svg(data) == ma.render_svg(data)


def test_svg_carries_label_and_artifact_commit():
    ma = _load()
    data = ma.load_figure_data(ma.BENCHMARK, ma.PER_SEED)
    svg = ma.render_svg(data).decode()
    commit = json.loads(ma.BENCHMARK.read_text())["code"]["git_commit"]
    assert "Synthetic world, development seeds 0-24" in svg
    assert commit[:12] in svg


def test_committed_svg_data_matches_artifact():
    """Drift check: regenerate with `make assets` when this fails."""
    ma = _load()
    expected = ma.load_figure_data(ma.BENCHMARK, ma.PER_SEED)
    svg = FIGURE.read_text()
    match = re.search(r"<desc>(.*?)</desc>", svg, re.DOTALL)
    assert match, "figure has no embedded data"
    assert json.loads(match.group(1)) == expected


def test_script_never_reads_held_out():
    assert "held-out" not in SCRIPT.read_text()


def test_rejects_non_development_seed_group(tmp_path):
    ma = _load()
    payload = json.loads(ma.BENCHMARK.read_text())
    payload["protocol"]["seed_group"] = "held-out"
    bad = tmp_path / "benchmark.json"
    bad.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="development"):
        ma.load_figure_data(bad, ma.PER_SEED)
