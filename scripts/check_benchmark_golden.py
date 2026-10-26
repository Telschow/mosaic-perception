#!/usr/bin/env python3
"""Compare a freshly generated small benchmark against the committed goldens.

The golden files in ``artifacts/benchmark-golden/`` are byte-for-byte copies of
the three canonical benchmark outputs for one fixed, small configuration. This
script regenerates the same configuration into a temporary directory and
requires the outputs to match byte for byte, so any nondeterminism or silent
behaviour change fails the build.

The one exception is the recorded source commit: every artifact records the
commit it was generated from, which changes on every commit by design. Both
sides are normalised (any 40-hex commit hash replaced by a placeholder) before
comparison. Commit provenance itself is checked by
``scripts/check_artifact_provenance.py``.

Update the golden files (one command, documented in docs/evaluation-protocol.md):

    make benchmark-golden

Run the check:

    make benchmark-golden-check
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GOLDEN_DIR = Path("artifacts/benchmark-golden")
OUTPUT_FILES = ("benchmark.json", "per_seed.csv", "report.md")
BENCHMARK_ARGS = [
    "benchmark",
    "--scenario",
    "nominal,sensor_disagreement_within_gate",
    "--seeds",
    "0,1",
    "--duration",
    "2.0",
    "--num-objects",
    "2",
]
_COMMIT = re.compile(rb"\b[0-9a-f]{40}\b")


def _normalise(data: bytes) -> bytes:
    """Replace recorded commit hashes so only behaviour differences show up."""
    return _COMMIT.sub(b"<recorded-commit>", data)


def _run_benchmark(output_dir: Path) -> None:
    # Prefer the installed console script; fall back to -m (runpy warns there).
    console_script = Path(sys.executable).with_name("mosaic")
    command = (
        [str(console_script)]
        if console_script.exists()
        else [sys.executable, "-m", "mosaic_perception.cli.main"]
    )
    subprocess.run(
        [*command, *BENCHMARK_ARGS, "--output", str(output_dir)],
        check=True,
    )


def check() -> int:
    if not GOLDEN_DIR.is_dir():
        print(
            f"missing golden directory {GOLDEN_DIR}; run `make benchmark-golden`", file=sys.stderr
        )
        return 1
    with tempfile.TemporaryDirectory(prefix="mosaic-golden-") as tmp:
        output_dir = Path(tmp)
        _run_benchmark(output_dir)
        failures = []
        for name in OUTPUT_FILES:
            golden = GOLDEN_DIR / name
            fresh = output_dir / name
            if not golden.exists():
                failures.append(f"{name}: no golden copy (run `make benchmark-golden`)")
                continue
            if not fresh.exists():
                failures.append(f"{name}: regeneration produced no file")
                continue
            if _normalise(golden.read_bytes()) != _normalise(fresh.read_bytes()):
                failures.append(f"{name}: differs from golden copy")
    if failures:
        for line in failures:
            print(f"FAIL {line}", file=sys.stderr)
        print(
            "\nIf the change in output is intended, refresh the goldens with `make benchmark-golden`.",
            file=sys.stderr,
        )
        return 1
    print(f"golden benchmark matches ({', '.join(OUTPUT_FILES)})")
    return 0


def update() -> int:
    with tempfile.TemporaryDirectory(prefix="mosaic-golden-") as tmp:
        output_dir = Path(tmp)
        _run_benchmark(output_dir)
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        for name in OUTPUT_FILES:
            shutil.copyfile(output_dir / name, GOLDEN_DIR / name)
    print(f"wrote golden files to {GOLDEN_DIR}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="rewrite the golden files")
    args = parser.parse_args()
    return update() if args.update else check()


if __name__ == "__main__":
    sys.exit(main())
