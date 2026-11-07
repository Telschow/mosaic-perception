"""Asset pipeline: the generated SVG is deterministic and matches the benchmark artifact."""

from __future__ import annotations

import importlib.util
import json
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

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
    "recovery": ("bias_recovery.svg", "load_recovery_data", "render_recovery"),
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


def _structure(svg):
    """Platform-tolerant SVG fingerprint: tags, attribute names and text; no geometry."""
    root = ElementTree.fromstring(svg)
    elements = [(el.tag, tuple(sorted(el.attrib))) for el in root.iter()]
    texts = [(el.tag, el.text.strip()) for el in root.iter() if el.text and el.text.strip()]
    return Counter(elements), texts


def test_structure_ignores_coordinates():
    a = b'<svg><text x="1" y="2">hi</text></svg>'
    b = b'<svg><text x="1.5" y="2.5">hi</text></svg>'
    assert _structure(a) == _structure(b)


def test_structure_detects_changed_data_and_label():
    base = b'<svg><desc>{"v": 1}</desc><text x="1">hi</text></svg>'
    assert _structure(base) != _structure(base.replace(b'"v": 1', b'"v": 2'))
    assert _structure(base) != _structure(base.replace(b">hi<", b">ho<"))


@pytest.mark.parametrize("name", PANELS)
def test_committed_panel_data_matches_artifact(name):
    """Drift check: regenerate with `make assets` when this fails."""
    ma = _load()
    path, load, render = _panel(ma, name)
    match = re.search(r"<desc>(.*?)</desc>", path.read_text(), re.DOTALL)
    assert match, "panel has no embedded data"
    assert json.loads(match.group(1)) == load(ma.BENCHMARK)
    assert _structure(path.read_bytes()) == _structure(render(load(ma.BENCHMARK)))


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
    lines = [
        ln for ln in REPORT.read_text().splitlines() if ln.startswith(f"| {data['scenario']} |")
    ]
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


def test_recovery_scenario_is_chosen_by_rule_not_by_hand():
    ma = _load()
    payload = json.loads(ma.BENCHMARK.read_text())
    name = ma.choose_recovery_scenario(payload)
    assert name != "measurement_bias"
    assert ma.load_recovery_data(ma.BENCHMARK)["scenario"] == name
    gains = {
        s["scenario"]["name"]: s["paired_differences"]["bias_estimated_vs_fused"]["precision"]
        for s in payload["scenarios"]
    }
    assert gains[name]["ci95_low"] > 0
    qualifying = [s for s in payload["scenarios"] if ma.recovery_holds(s, "precision")]
    assert all(gains[s["scenario"]["name"]]["mean"] <= gains[name]["mean"] for s in qualifying)


def test_panel_verdict_is_the_shared_recovery_rule_for_every_scenario_and_metric():
    ma = _load()
    payload = json.loads(ma.BENCHMARK.read_text())
    for scenario in payload["scenarios"]:
        name = scenario["scenario"]["name"]
        data = ma.load_recovery_data(ma.BENCHMARK, name)
        for metric, values in data["metrics"].items():
            expected = "recovers" if ma.recovery_holds(scenario, metric) else "does not recover"
            assert ma.recovery_verdict(values) == expected, (name, metric)
    # the chosen scenario's panel says "recovers"; measurement_bias's must not
    chosen = ma.load_recovery_data(ma.BENCHMARK)["metrics"]["precision"]
    assert ma.recovery_verdict(chosen) == "recovers"
    biased = ma.load_recovery_data(ma.BENCHMARK, "measurement_bias")["metrics"]["precision"]
    assert ma.recovery_verdict(biased) == "does not recover"


def _rule_scenario(name, fused_vs_range, bias_vs_fused, means, metric="precision"):
    """Intervals are (mean, ci95_low, ci95_high); means are range_only, fused, bias-estimated."""
    keys = ("mean", "ci95_low", "ci95_high")
    return {
        "scenario": {"name": name},
        "paired_differences": {
            "fused_vs_range_only": {metric: dict(zip(keys, fused_vs_range, strict=True))},
            "bias_estimated_vs_fused": {metric: dict(zip(keys, bias_vs_fused, strict=True))},
        },
        "aggregate": {
            m: {metric: v}
            for m, v in zip(("range_only", "fused", "fused_bias_estimated"), means, strict=True)
        },
    }


LOSS = (-0.3, -0.4, -0.2)
GAIN = (0.1, 0.05, 0.15)


@pytest.mark.parametrize(
    ("case", "fused_vs_range", "bias_vs_fused", "means", "holds"),
    [
        ("gain without a prior loss", (0.0, -0.1, 0.1), GAIN, (0.8, 0.8, 0.9), False),
        ("gain after a fusion gain", (0.1, 0.05, 0.15), GAIN, (0.7, 0.8, 0.9), False),
        ("loss and gain", LOSS, GAIN, (0.9, 0.6, 0.7), True),
        ("zero recovered share", LOSS, GAIN, (0.9, 0.6, 0.6), False),
        ("negative recovered share", LOSS, GAIN, (0.9, 0.6, 0.55), False),
        ("gain interval spans zero", LOSS, (0.05, -0.01, 0.11), (0.9, 0.6, 0.65), False),
        ("loss interval spans zero", (-0.05, -0.1, 0.01), GAIN, (0.9, 0.85, 0.9), False),
        ("undefined interval", (None, None, None), GAIN, (0.9, 0.6, 0.7), False),
    ],
)
def test_recovery_rule(case, fused_vs_range, bias_vs_fused, means, holds):
    ma = _load()
    for metric in ("precision", "mota"):
        scenario = _rule_scenario(case, fused_vs_range, bias_vs_fused, means, metric)
        assert ma.recovery_holds(scenario, metric) is holds, (case, metric)


def test_exploratory_choice_ignores_a_larger_gain_that_recovers_no_loss():
    ma = _load()
    payload = {
        "scenarios": [
            _rule_scenario(
                "bigger_gain_no_loss", (0.0, -0.1, 0.1), (0.5, 0.4, 0.6), (0.8, 0.8, 1.0)
            ),
            _rule_scenario("small", LOSS, (0.05, 0.01, 0.09), (0.9, 0.6, 0.65)),
            _rule_scenario("large", LOSS, GAIN, (0.9, 0.6, 0.7)),
        ]
    }
    assert ma.choose_recovery_scenario(payload) == "large"
