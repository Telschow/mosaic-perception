#!/usr/bin/env python3
"""Generate the paired position-RMSE figure and the demo 1 panels from the benchmark artifact.

Reads ``artifacts/benchmark/benchmark.json`` and ``per_seed.csv`` (development
seeds 0-24; nothing is re-simulated) and writes SVGs to
``docs-site/src/assets/generated/``: the paired-RMSE figure, the scoreboard
(paired tallies, counted by the report's own rule) and the measurement-bias
recovery panel. Every plotted value comes from the artifact.
The output is byte-deterministic: bundled font, no text-as-path variation, fixed
hash salt, no timestamps. The plotted data is embedded in the SVG ``<desc>`` so a
test can detect drift from the artifact. Refuses a stale artifact by running
``scripts/check_artifact_provenance.py`` first.
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from mosaic_perception.reporting.markdown import _tally

BENCHMARK = Path("artifacts/benchmark/benchmark.json")
PER_SEED = BENCHMARK.with_name("per_seed.csv")
OUTPUT = Path("docs-site/src/assets/generated/position_rmse_paired.svg")
SCOREBOARD_OUTPUT = OUTPUT.with_name("scoreboard.svg")
RECOVERY_OUTPUT = OUTPUT.with_name("measurement_bias_recovery.svg")
METRIC = "position_rmse"
# (comparison, metric, lower is better), as tallied in the report's Findings.
SCOREBOARD_ROWS = (
    ("fused_vs_range_only", "precision", False),
    ("fused_vs_range_only", "mota", False),
    ("bias_estimated_vs_fused", "precision", False),
    ("bias_estimated_vs_fused", "mota", False),
)
COMPARISON_LABELS = {
    "fused_vs_range_only": "fused vs range-only",
    "bias_estimated_vs_fused": "fused_bias_estimated vs fused",
}
RECOVERY_SCENARIO = "measurement_bias"
RECOVERY_METRICS = ("precision", "mota")
# (fill, text) pairs used on the panels; tests check WCAG AA (4.5:1) for each.
TALLY_COLORS = {
    "better": ("#1b6ca8", "#ffffff"),
    "worse": ("#a62a1f", "#ffffff"),
    "inconclusive": ("#d9d9d9", "#000000"),
}
LABEL = "Synthetic world, development seeds 0-24"
COLORS = {"range_only": "#4d4d4d", "fused": "#1b6ca8", "fused_bias_estimated": "#d9822b"}


def load_figure_data(benchmark: Path, per_seed: Path) -> dict[str, Any]:
    payload = json.loads(benchmark.read_text())
    protocol = payload["protocol"]
    if protocol["seed_group"] != "development" or protocol["seeds"] != list(range(25)):
        raise ValueError("artifact is not the development run on seeds 0-24")
    methods = protocol["methods"]
    spread: dict[tuple[str, str], list[float]] = {}
    with per_seed.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row[METRIC]:
                spread.setdefault((row["scenario"], row["method"]), []).append(float(row[METRIC]))
    scenarios = []
    for scenario in payload["scenarios"]:
        name = scenario["scenario"]["name"]
        values: dict[str, Any] = {}
        for method in methods:
            mean = scenario["aggregate"][method].get(METRIC)
            seeds = spread.get((name, method))
            values[method] = None if mean is None or not seeds else [mean, min(seeds), max(seeds)]
        scenarios.append({"scenario": name, "values": values})
    return {
        "commit": payload["code"]["git_commit"],
        "metric": METRIC,
        "methods": methods,
        "scenarios": scenarios,
    }


def _load_development(benchmark: Path) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(benchmark.read_text())
    protocol = payload["protocol"]
    if protocol["seed_group"] != "development" or protocol["seeds"] != list(range(25)):
        raise ValueError("artifact is not the development run on seeds 0-24")
    return payload


def load_scoreboard_data(benchmark: Path) -> dict[str, Any]:
    payload = _load_development(benchmark)
    rows = []
    for comparison, metric, lower in SCOREBOARD_ROWS:
        better, worse, inconclusive = _tally(payload, metric, lower, comparison)
        rows.append(
            {
                "comparison": comparison,
                "metric": metric,
                "better": better,
                "worse": worse,
                "inconclusive": inconclusive,
            }
        )
    return {"commit": payload["code"]["git_commit"], "rows": rows}


def load_recovery_data(benchmark: Path) -> dict[str, Any]:
    payload = _load_development(benchmark)
    scenario = next(s for s in payload["scenarios"] if s["scenario"]["name"] == RECOVERY_SCENARIO)
    metrics: dict[str, Any] = {}
    for metric in RECOVERY_METRICS:
        values = {m: scenario["aggregate"][m][metric] for m in payload["protocol"]["methods"]}
        loss = values["range_only"] - values["fused"]
        recovered = values["fused_bias_estimated"] - values["fused"]
        values["recovered_share"] = recovered / loss if loss else None
        metrics[metric] = values
    return {
        "commit": payload["code"]["git_commit"],
        "scenario": RECOVERY_SCENARIO,
        "metrics": metrics,
    }


RC_PARAMS = {
    "svg.hashsalt": "mosaic-perception",
    "svg.fonttype": "none",
    "font.family": "DejaVu Sans",
    "path.simplify": False,
}


def _to_svg(fig: Any, data: dict[str, Any], title: str) -> bytes:
    """Serialise ``fig`` with an accessible title and the plotted data in ``<desc>``."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="svg", metadata={"Date": None, "Creator": "make_assets"})
    svg = buffer.getvalue().decode()
    desc = json.dumps(data, sort_keys=True).replace("&", "&amp;").replace("<", "&lt;")
    block = f"\n <title>{title}</title>\n <desc>{desc}</desc>"
    svg = svg.replace("</metadata>", "</metadata>" + block, 1)
    return svg.replace("<svg ", '<svg role="img" ', 1).encode()


def render_scoreboard(data: dict[str, Any]) -> bytes:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with matplotlib.rc_context(RC_PARAMS):
        rows = data["rows"]
        fig, ax = plt.subplots(figsize=(8, 3.6))
        for y, row in enumerate(rows):
            left = 0
            for key in ("better", "worse", "inconclusive"):
                count = row[key]
                fill, ink = TALLY_COLORS[key]
                ax.barh(y, count, left=left, color=fill, height=0.6, label=key if y == 0 else None)
                if count:
                    ax.text(left + count / 2, y, str(count), ha="center", va="center", color=ink)
                left += count
        names = [f"{COMPARISON_LABELS[r['comparison']]}: {r['metric']}" for r in rows]
        ax.set_yticks(range(len(rows)), names, fontsize=8)
        ax.invert_yaxis()
        ax.set_xlabel("scenarios (paired 95% interval, treatment vs baseline)", fontsize=8)
        ax.set_title(f"Scoreboard: precision and MOTA\n{LABEL}", fontsize=10)
        ax.legend(fontsize=8, loc="lower right")
        fig.text(0.99, 0.005, f"artifact commit {data['commit'][:12]}", ha="right", fontsize=7)
        fig.tight_layout(rect=(0, 0.02, 1, 1))
        svg = _to_svg(fig, data, "Scoreboard: scenarios where the treatment is better or worse")
        plt.close(fig)
    return svg


def render_recovery(data: dict[str, Any]) -> bytes:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    methods = ("range_only", "fused", "fused_bias_estimated")
    with matplotlib.rc_context(RC_PARAMS):
        fig, axes = plt.subplots(1, len(RECOVERY_METRICS), figsize=(8, 3.8))
        for ax, metric in zip(axes, RECOVERY_METRICS, strict=True):
            values = data["metrics"][metric]
            for x, method in enumerate(methods):
                ax.bar(x, values[method], color=COLORS[method], width=0.6)
                ax.text(x, values[method] + 0.01, f"{values[method]:.3f}", ha="center", fontsize=8)
            share = values["recovered_share"]
            note = "no gap" if share is None else f"recovered {share * 100:.1f}% of fused's loss"
            ax.set_title(f"{metric}\n{note}", fontsize=9)
            ax.set_xticks(range(3), ["range-only", "fused", "fused_bias_\nestimated"], fontsize=8)
            ax.set_ylim(0, 1)
        fig.suptitle(f"{data['scenario']}: bias estimation vs fusion's loss\n{LABEL}", fontsize=10)
        fig.text(0.99, 0.005, f"artifact commit {data['commit'][:12]}", ha="right", fontsize=7)
        fig.tight_layout(rect=(0, 0.03, 1, 0.88))
        svg = _to_svg(fig, data, "Measurement-bias scenario: precision and MOTA by method")
        plt.close(fig)
    return svg


def render_svg(data: dict[str, Any]) -> bytes:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    params = {
        "svg.hashsalt": "mosaic-perception",
        "svg.fonttype": "none",
        "font.family": "DejaVu Sans",
        "path.simplify": False,
    }
    with matplotlib.rc_context(params):
        rows = data["scenarios"]
        fig, ax = plt.subplots(figsize=(8, 0.42 * len(rows) + 1.8))
        offsets = {m: (i - 1) * 0.22 for i, m in enumerate(data["methods"])}
        for y, row in enumerate(rows):
            for method, value in row["values"].items():
                if value is None:
                    continue
                mean, low, high = value
                ypos = y + offsets[method]
                ax.plot([low, high], [ypos, ypos], color=COLORS[method], alpha=0.35, lw=1.5)
                ax.plot(mean, ypos, "o", color=COLORS[method], ms=4)
            if all(v is None for v in row["values"].values()):
                ax.text(0.01, y, "no estimate", va="center", fontsize=7, color="#777777")
        for method in data["methods"]:
            ax.plot([], [], "o", color=COLORS[method], label=method)
        ax.set_yticks(range(len(rows)), [r["scenario"] for r in rows], fontsize=8)
        ax.invert_yaxis()
        ax.set_xlabel("position RMSE (m): seed mean, line = min-max over seeds 0-24", fontsize=8)
        ax.set_title(f"Paired position RMSE per scenario\n{LABEL}", fontsize=10)
        ax.legend(fontsize=8, loc="lower right")
        ax.grid(axis="x", alpha=0.3)
        fig.text(0.99, 0.005, f"artifact commit {data['commit'][:12]}", ha="right", fontsize=7)
        fig.tight_layout(rect=(0, 0.02, 1, 1))
        buffer = io.BytesIO()
        fig.savefig(buffer, format="svg", metadata={"Date": None, "Creator": "make_assets"})
        plt.close(fig)
    svg = buffer.getvalue().decode()
    desc = "<desc>" + json.dumps(data, sort_keys=True).replace("&", "&amp;").replace("<", "&lt;")
    svg = svg.replace("</metadata>", "</metadata>\n " + desc + "</desc>", 1)
    return svg.encode()


def main() -> int:
    check = subprocess.run([sys.executable, "scripts/check_artifact_provenance.py"])
    if check.returncode != 0:
        print("refusing to build assets from a stale artifact", file=sys.stderr)
        return 1
    data = load_figure_data(BENCHMARK, PER_SEED)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render_svg(data))
    SCOREBOARD_OUTPUT.write_bytes(render_scoreboard(load_scoreboard_data(BENCHMARK)))
    RECOVERY_OUTPUT.write_bytes(render_recovery(load_recovery_data(BENCHMARK)))
    print(f"wrote {OUTPUT}, {SCOREBOARD_OUTPUT}, {RECOVERY_OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
