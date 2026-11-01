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


# --- demo 1 panels: scoreboard and measurement-bias recovery ---

REPORT = ROOT / "artifacts/benchmark/report.md"
PANELS = {
    "scoreboard": ("scoreboard.svg", "load_scoreboard_data", "render_scoreboard"),
    "recovery": ("measurement_bias_recovery.svg", "load_recovery_data", "render_recovery"),
}


def _panel(ma, name):
    file, load, render = PANELS[name]
    return ROOT / "docs-site/src/assets/generated" / file, getattr(ma, load), getattr(ma, render)


@pytest.mark.parametrize("name", PANELS)
def test_panel_is_deterministic_labelled_and_accessible(name):
    ma = _load()
    _, load, render = _panel(ma, name)
    data = load(ma.BENCHMARK)
    svg = render(data)
    assert svg == render(data)
    text = svg.decode()
    assert "Synthetic world, development seeds 0-24" in text
    assert data["commit"][:12] in text
    assert re.search(r"<title>.+</title>", text) and "<desc>" in text
    assert 'role="img"' in text


@pytest.mark.parametrize("name", PANELS)
def test_committed_panel_data_matches_artifact(name):
    """Drift check: regenerate with `make assets` when this fails."""
    ma = _load()
    path, load, render = _panel(ma, name)
    match = re.search(r"<desc>(.*?)</desc>", path.read_text(), re.DOTALL)
    assert match, "panel has no embedded data"
    assert json.loads(match.group(1)) == load(ma.BENCHMARK)
    assert path.read_bytes() == render(load(ma.BENCHMARK))


def _luminance(color):
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def test_panel_text_contrast_passes_wcag_aa():
    ma = _load()
    for fill, ink in ma.TALLY_COLORS.values():
        light, dark = sorted((_luminance(fill), _luminance(ink)), reverse=True)
        assert (light + 0.05) / (dark + 0.05) >= 4.5


def _findings():
    text = REPORT.read_text()
    return text[text.index("## Findings") :]


def test_scoreboard_matches_report_findings():
    ma = _load()
    rows = {
        (r["comparison"], r["metric"]): r for r in ma.load_scoreboard_data(ma.BENCHMARK)["rows"]
    }
    findings = _findings()
    lower, higher = re.search(
        r"Fused precision is lower .*? in (\d+) scenario\(s\) and higher in (\d+)", findings
    ).groups()
    row = rows["fused_vs_range_only", "precision"]
    assert (row["worse"], row["better"]) == (int(lower), int(higher))
    better, worse = re.search(
        r"MOTA, IDF1 and GOSPA .*?better in (\d+), \d+ and \d+ scenario\(s\) and worse in (\d+),",
        findings,
    ).groups()
    row = rows["fused_vs_range_only", "mota"]
    assert (row["better"], row["worse"]) == (int(better), int(worse))
    line = re.search(r"- fused-bias-estimated against fused.*", findings).group(0)
    for metric, label in (("precision", "precision"), ("mota", "MOTA")):
        b, w, i = re.search(
            rf"{label}: better in (\d+), worse in (\d+), inconclusive in (\d+)", line
        ).groups()
        row = rows["bias_estimated_vs_fused", metric]
        assert (row["better"], row["worse"], row["inconclusive"]) == (int(b), int(w), int(i))


def test_recovery_values_match_report_table():
    ma = _load()
    data = ma.load_recovery_data(ma.BENCHMARK)
    lines = [ln for ln in REPORT.read_text().splitlines() if ln.startswith("| measurement_bias |")]
    header = next(
        ln
        for ln in REPORT.read_text().splitlines()
        if ln.startswith("| Scenario | Method | Pos RMSE")
    )
    columns = [c.strip() for c in header.strip("|").split("|")]
    for method in ("range_only", "fused", "fused_bias_estimated"):
        cells = next(
            [c.strip() for c in ln.strip("|").split("|")] for ln in lines if f"| {method} |" in ln
        )
        for metric, column in (("precision", "Precision"), ("mota", "MOTA")):
            assert f"{data['metrics'][metric][method]:.3f}" == cells[columns.index(column)]


def test_panels_refuse_non_development_artifact(tmp_path):
    ma = _load()
    payload = json.loads(ma.BENCHMARK.read_text())
    payload["protocol"]["seed_group"] = "held-out"
    bad = tmp_path / "benchmark.json"
    bad.write_text(json.dumps(payload))
    for load in (ma.load_scoreboard_data, ma.load_recovery_data):
        with pytest.raises(ValueError, match="development"):
            load(bad)
