#!/usr/bin/env python3
"""Write ``alt_text.json``: one alt text per published image, built from its manifest.

Every number and scenario name comes from the benchmark artifact or from the asset's own
JSON manifest, so the text cannot drift from the picture. The landing page and the README
embed these strings (``tests/unit/test_alt_text.py`` checks they do). Each text starts with
what the picture is, says it is a synthetic world, then states the finding in a sentence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import make_assets  # noqa: E402

GENERATED = Path("docs-site/src/assets/generated")
OUTPUT = GENERATED / "alt_text.json"


def _manifest(name: str) -> dict[str, Any]:
    return json.loads((GENERATED / f"{name}.json").read_text())


def _tally(rows: list[dict[str, Any]], comparison: str, metric: str) -> str:
    row = next(r for r in rows if (r["comparison"], r["metric"]) == (comparison, metric))
    return (
        f"{metric} worse in {row['worse']}, better in {row['better']} "
        f"and unclear in {row['inconclusive']} scenarios"
    )


def build_alt_text() -> dict[str, str]:
    payload = json.loads(make_assets.BENCHMARK.read_text())
    seeds = payload["protocol"]["seeds"]
    group = f"development seeds {seeds[0]}-{seeds[-1]}"
    rows = make_assets.load_scoreboard_data(make_assets.BENCHMARK)["rows"]
    recovery = make_assets.load_recovery_data(make_assets.BENCHMARK)
    verdict = make_assets.recovery_verdict(recovery["metrics"]["precision"])
    share = recovery["metrics"]["precision"]["recovered_share"]
    clip = _manifest("scenario_clip")
    hero = _manifest("hero")
    return {
        "position_rmse_paired": (
            f"Dot-and-interval chart of the paired change in position error, fused against "
            f"range-only, with a 95% interval for each of {len(payload['scenarios'])} scenarios "
            f"of a synthetic world ({group})."
        ),
        "scoreboard": (
            "Bar chart tallying, across the scenarios of a synthetic world, whether adding a camera "
            f"helped. Fused against range-only: {_tally(rows, 'fused_vs_range_only', 'precision')}. "
            f"Bias-estimated against fused: {_tally(rows, 'bias_estimated_vs_fused', 'precision')}."
        ),
        "bias_recovery": (
            f"Two bar charts for the {recovery['scenario']} scenario of a synthetic world: "
            f"precision and MOTA for range-only, fused and bias-estimated tracking. Bias estimation "
            f"{verdict} {share:.0%} of the precision fused tracking lost."
        ),
        "scenario_clip": (
            f"Animation of one target in the {clip['scenario']} scenario of a synthetic world "
            f"(seed {clip['seed']}). A range-only track is drawn first, then the fused track is "
            "added, both against the dashed ground-truth path."
        ),
        "summary_clip": (
            "Animated summary of a simulated, synthetic world, in five beats. One: a moving target "
            "is tracked by a range sensor alone. Two: a camera is added and the track looks better. "
            "Three: a scoreboard shows the fused tracker is worse than range-only on precision and "
            f"MOTA in most scenarios. Four: in the {recovery['scenario']} scenario, where the camera "
            f"has a small bearing bias, estimating the bias {verdict} part of fusion's loss. Five: "
            "an end card reading Synthetic world, full results and limits, with this site's address."
        ),
        **{f"hero_{key}": still["alt"] for key, still in hero["stills"].items()},
    }


def main() -> int:
    OUTPUT.write_text(json.dumps(build_alt_text(), indent=1) + "\n")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
