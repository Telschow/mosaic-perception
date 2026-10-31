"""Tests for the platform-tolerant golden benchmark comparison.

The comparison must tolerate last-digit floating-point/BLAS noise (which differs
between platforms for the same code) while still failing on any real change in
counts, identities, structure or values beyond the tolerance.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_benchmark_golden.py"
_spec = importlib.util.spec_from_file_location("check_benchmark_golden", _SCRIPT)
assert _spec is not None and _spec.loader is not None
golden = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(golden)


def test_json_last_digit_float_noise_passes() -> None:
    # The example from the issue: identical except in the last two digits.
    a = b'{"anees_position": 4.2417037447519625}'
    b = b'{"anees_position": 4.24170374475195}'
    assert golden.compare_json(a, b) == []


def test_json_real_float_change_fails() -> None:
    a = b'{"anees_position": 4.2417037447519625}'
    b = b'{"anees_position": 4.2517037447519625}'
    assert golden.compare_json(a, b) != []


def test_json_integer_change_fails() -> None:
    a = b'{"identity_switches": 2}'
    b = b'{"identity_switches": 3}'
    diffs = golden.compare_json(a, b)
    assert diffs and "identity_switches" in diffs[0]


def test_json_string_change_fails() -> None:
    a = b'{"method": "fused"}'
    b = b'{"method": "range_only"}'
    assert golden.compare_json(a, b) != []


def test_json_structural_change_fails() -> None:
    assert golden.compare_json(b'{"a": 1, "b": 2}', b'{"a": 1}') != []
    assert golden.compare_json(b"[1, 2, 3]", b"[1, 2]") != []


def test_json_boolean_change_fails() -> None:
    a = b'{"matching_continuity": true}'
    b = b'{"matching_continuity": false}'
    assert golden.compare_json(a, b) != []


def test_json_nested_noise_passes_and_change_fails() -> None:
    a = b'{"scenario": {"fused": {"x": 1.0000000001, "n": 80}}}'
    b = b'{"scenario": {"fused": {"x": 1.0000000002, "n": 80}}}'
    assert golden.compare_json(a, b) == []
    c = b'{"scenario": {"fused": {"x": 1.0000000001, "n": 81}}}'
    assert golden.compare_json(a, c) != []


def test_csv_last_digit_float_noise_passes() -> None:
    header = b"scenario,seed,position_rmse\n"
    a = header + b"nominal,0,0.34844266454764494\n"
    b = header + b"nominal,0,0.3484426645476449\n"
    assert golden.compare_csv(a, b) == []


def test_csv_real_float_change_fails() -> None:
    header = b"scenario,seed,position_rmse\n"
    a = header + b"nominal,0,0.34844266454764494\n"
    b = header + b"nominal,0,0.35844266454764494\n"
    diffs = golden.compare_csv(a, b)
    assert diffs and "position_rmse" in diffs[0]


def test_csv_integer_count_change_fails() -> None:
    header = b"scenario,seed,identity_switches\n"
    a = header + b"nominal,0,2\n"
    b = header + b"nominal,0,3\n"
    diffs = golden.compare_csv(a, b)
    assert diffs and "identity_switches" in diffs[0]


def test_csv_string_change_fails() -> None:
    header = b"scenario,seed,method\n"
    a = header + b"nominal,0,fused\n"
    b = header + b"nominal,0,range_only\n"
    assert golden.compare_csv(a, b) != []


def test_csv_header_change_fails() -> None:
    a = b"scenario,seed,position_rmse\nnominal,0,0.1\n"
    b = b"scenario,seed,velocity_rmse\nnominal,0,0.1\n"
    assert golden.compare_csv(a, b) != []


def test_csv_row_count_change_fails() -> None:
    header = b"scenario,seed,position_rmse\n"
    a = header + b"nominal,0,0.1\nnominal,1,0.2\n"
    b = header + b"nominal,0,0.1\n"
    assert golden.compare_csv(a, b) != []


def test_commit_hash_is_normalised() -> None:
    a = b'{"git_commit": "7e3c9360038bcabac57d6a6aaf414fbe3c8c47f2"}'
    b = b'{"git_commit": "0123456789abcdef0123456789abcdef01234567"}'
    assert golden._compare_file("benchmark.json", a, b) == []


def test_report_md_compared_byte_for_byte() -> None:
    assert golden._compare_file("report.md", b"# Report\n0.234\n", b"# Report\n0.234\n") == []
    assert golden._compare_file("report.md", b"# Report\n0.234\n", b"# Report\n0.235\n") != []
