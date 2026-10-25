"""Regenerate ``trackeval_reference.json`` from the pinned TrackEval reference.

Dev-only. Run from the repository root:

    uv run python -m tests.crosscheck.regenerate_reference

Requires the development dependency group (where TrackEval is pinned). The
committed JSON is what the unit test compares against, so the test itself runs
offline without TrackEval installed (for example under ``pip install -e .``).
"""

from __future__ import annotations

import json
from pathlib import Path

from .sequences import fixed_sequences
from .trackeval_harness import (
    CLEAR_THRESHOLD,
    TRACKEVAL_COMMIT,
    TRACKEVAL_REPOSITORY,
    run_trackeval,
    trackeval_version,
)

REFERENCE_PATH = Path(__file__).with_name("trackeval_reference.json")


def build_reference() -> dict:
    return {
        "tool": "TrackEval",
        "repository": TRACKEVAL_REPOSITORY,
        "commit": TRACKEVAL_COMMIT,
        "installed_version": trackeval_version(),
        "clear_threshold": CLEAR_THRESHOLD,
        "sequences": {seq.name: run_trackeval(seq) for seq in fixed_sequences()},
    }


def main() -> None:
    reference = build_reference()
    REFERENCE_PATH.write_text(json.dumps(reference, indent=2, sort_keys=True) + "\n")
    print(f"wrote {REFERENCE_PATH} ({reference['installed_version']} @ {reference['commit'][:12]})")


if __name__ == "__main__":
    main()
