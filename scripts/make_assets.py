#!/usr/bin/env python3
"""Generate the paired position-RMSE figure from the committed benchmark artifact.

Reads ``artifacts/benchmark/benchmark.json`` and ``per_seed.csv`` (development
seeds 0-24; nothing is re-simulated) and writes one SVG to
``docs-site/src/assets/generated/``. Every plotted value comes from the artifact.
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

BENCHMARK = Path("artifacts/benchmark/benchmark.json")
PER_SEED = BENCHMARK.with_name("per_seed.csv")
OUTPUT = Path("docs-site/src/assets/generated/position_rmse_paired.svg")
METRIC = "position_rmse"
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
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
