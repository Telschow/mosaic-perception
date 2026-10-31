#!/usr/bin/env python3
"""Compare a freshly generated small benchmark against the committed goldens.

The golden files in ``artifacts/benchmark-golden/`` are the three canonical
benchmark outputs for one fixed, small configuration. This script regenerates
the same configuration into a temporary directory and requires the outputs to
match the committed copies, so any nondeterminism or silent behaviour change
fails the build.

Integer, string and structural fields are compared exactly. Float fields are
compared with a tight relative tolerance (``REL_TOL``) so that last-digit
floating-point/BLAS noise -- which differs between platforms such as Linux CI
and macOS arm64 even for the same code -- does not fail the check, while any
real change in a value stays far above the tolerance and still fails. Files
that are not structured data (``report.md``) are compared byte for byte; its
numbers are rounded for display and so are stable across platforms.

The recorded source commit is a further exception: every artifact records the
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
import csv
import io
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

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
_INT_TEXT = re.compile(r"^[+-]?\d+$")

# Relative tolerance for float comparisons. Last-digit floating-point/BLAS noise
# between platforms is on the order of 1e-15 (relative); a real change in any
# metric is orders of magnitude larger, so 1e-9 fails on behaviour changes while
# tolerating platform noise. ABS_TOL covers values at or near zero.
REL_TOL = 1e-9
ABS_TOL = 1e-12


def _normalise(data: bytes) -> bytes:
    """Replace recorded commit hashes so only behaviour differences show up."""
    return _COMMIT.sub(b"<recorded-commit>", data)


def _floats_match(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def compare_json(golden: bytes, fresh: bytes) -> list[str]:
    """Compare two JSON documents; floats within tolerance, everything else exact."""
    try:
        golden_obj = json.loads(golden)
        fresh_obj = json.loads(fresh)
    except json.JSONDecodeError as exc:  # pragma: no cover - corrupt input
        return [f"could not parse JSON: {exc}"]
    return _compare_json_values(golden_obj, fresh_obj, "$")


def _compare_json_values(golden: Any, fresh: Any, path: str) -> list[str]:
    if isinstance(golden, bool) or isinstance(fresh, bool):
        return [] if golden is fresh else [f"{path}: {golden!r} != {fresh!r}"]
    if _is_number(golden) and _is_number(fresh):
        if isinstance(golden, int) and isinstance(fresh, int):
            return [] if golden == fresh else [f"{path}: {golden} != {fresh}"]
        if _floats_match(float(golden), float(fresh)):
            return []
        return [f"{path}: {golden!r} != {fresh!r} (rel tol {REL_TOL})"]
    if isinstance(golden, dict) and isinstance(fresh, dict):
        diffs: list[str] = []
        if golden.keys() != fresh.keys():
            missing = sorted(golden.keys() - fresh.keys())
            extra = sorted(fresh.keys() - golden.keys())
            diffs.append(f"{path}: keys differ (missing={missing}, extra={extra})")
        for key in golden.keys() & fresh.keys():
            diffs.extend(_compare_json_values(golden[key], fresh[key], f"{path}.{key}"))
        return diffs
    if isinstance(golden, list) and isinstance(fresh, list):
        if len(golden) != len(fresh):
            return [f"{path}: length {len(golden)} != {len(fresh)}"]
        diffs = []
        for index, (g_item, f_item) in enumerate(zip(golden, fresh, strict=True)):
            diffs.extend(_compare_json_values(g_item, f_item, f"{path}[{index}]"))
        return diffs
    return (
        []
        if type(golden) is type(fresh) and golden == fresh
        else [f"{path}: {golden!r} != {fresh!r}"]
    )


def _cells_match(golden: str, fresh: str) -> bool:
    if golden == fresh:
        return True
    # Integer-valued cells (counts, sample sizes) must match exactly.
    if _INT_TEXT.match(golden) or _INT_TEXT.match(fresh):
        return False
    try:
        return _floats_match(float(golden), float(fresh))
    except ValueError:
        return False


def compare_csv(golden: bytes, fresh: bytes) -> list[str]:
    """Compare two CSV documents cell by cell; floats within tolerance, else exact."""
    golden_rows = list(csv.reader(io.StringIO(golden.decode())))
    fresh_rows = list(csv.reader(io.StringIO(fresh.decode())))
    if golden_rows[:1] != fresh_rows[:1]:
        return [f"header differs: {golden_rows[:1]} != {fresh_rows[:1]}"]
    if len(golden_rows) != len(fresh_rows):
        return [f"row count {len(golden_rows)} != {len(fresh_rows)}"]
    header = golden_rows[0] if golden_rows else []
    diffs: list[str] = []
    for row_index, (golden_row, fresh_row) in enumerate(
        zip(golden_rows[1:], fresh_rows[1:], strict=True), start=1
    ):
        if len(golden_row) != len(fresh_row):
            diffs.append(f"row {row_index}: field count {len(golden_row)} != {len(fresh_row)}")
            continue
        for col_index, (golden_cell, fresh_cell) in enumerate(
            zip(golden_row, fresh_row, strict=True)
        ):
            if not _cells_match(golden_cell, fresh_cell):
                column = header[col_index] if col_index < len(header) else f"col {col_index}"
                diffs.append(f"row {row_index}, {column}: {golden_cell!r} != {fresh_cell!r}")
    return diffs


def _compare_file(name: str, golden: bytes, fresh: bytes) -> list[str]:
    golden, fresh = _normalise(golden), _normalise(fresh)
    if name.endswith(".json"):
        return compare_json(golden, fresh)
    if name.endswith(".csv"):
        return compare_csv(golden, fresh)
    return [] if golden == fresh else ["differs from golden copy"]


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
            for diff in _compare_file(name, golden.read_bytes(), fresh.read_bytes()):
                failures.append(f"{name}: {diff}")
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
