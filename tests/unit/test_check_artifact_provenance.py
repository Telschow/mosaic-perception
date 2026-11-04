"""Tests for the report.md consistency part of the artifact provenance check."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_artifact_provenance", _ROOT / "scripts" / "check_artifact_provenance.py"
)
assert _spec is not None and _spec.loader is not None
provenance = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = provenance
_spec.loader.exec_module(provenance)

COMMIT = "a" * 40
OTHER = "b" * 40


def test_report_with_matching_commit_passes() -> None:
    assert provenance.check_report_commit(f"- Git commit: `{COMMIT}`\n", COMMIT) == []


def test_report_with_mismatched_commit_fails() -> None:
    failures = provenance.check_report_commit(f"- Git commit: `{OTHER}`\n", COMMIT)
    assert failures and "report.md" in failures[0]


def test_report_without_commit_fails() -> None:
    assert provenance.check_report_commit("no commit here\n", COMMIT) != []


def test_report_differing_from_render_fails() -> None:
    payload = json.loads((_ROOT / "artifacts/benchmark/benchmark.json").read_text())
    assert provenance.check_report_render("stale", payload) != []


def test_committed_artifacts_pass() -> None:
    directory = _ROOT / "artifacts" / "benchmark"
    payload = json.loads((directory / "benchmark.json").read_text())
    report = (directory / "report.md").read_text()
    assert provenance.check_report_commit(report, payload["code"]["git_commit"]) == []
    assert provenance.check_report_render(report, payload) == []


def test_frozen_declaration_matching_commit_passes(tmp_path: Path) -> None:
    (tmp_path / "FROZEN").write_text(f"{COMMIT}\n")
    declared = provenance.read_frozen(tmp_path)
    assert declared == COMMIT
    assert provenance.check_frozen_declaration(declared, COMMIT) == []


def test_frozen_declaration_mismatch_fails() -> None:
    assert provenance.check_frozen_declaration(OTHER, COMMIT) != []


def test_no_frozen_file_means_not_frozen(tmp_path: Path) -> None:
    assert provenance.read_frozen(tmp_path) is None


def test_artifact_directories_include_every_benchmark_json() -> None:
    names = {d.name for d in provenance.artifact_directories(_ROOT / "artifacts")}
    assert {"benchmark", "benchmark-golden", "held-out"} <= names


def test_frozen_held_out_directory_reports_delta_and_passes() -> None:
    result = provenance.check_directory(_ROOT / "artifacts" / "held-out")
    assert result.failures == []
    assert result.frozen_at is not None and result.frozen_at.startswith("8baa778")


def test_frozen_directory_with_disagreeing_report_fails(tmp_path: Path) -> None:
    payload = {"code": {"git_commit": COMMIT, "package_version": "0.1.0"}}
    (tmp_path / "benchmark.json").write_text(json.dumps(payload))
    (tmp_path / "report.md").write_text(f"- Git commit: `{OTHER}`\n")
    (tmp_path / "FROZEN").write_text(COMMIT)
    result = provenance.check_directory(tmp_path)
    assert any("report.md" in f for f in result.failures)


def test_frozen_file_may_carry_a_benchmark_hash(tmp_path: Path) -> None:
    (tmp_path / "FROZEN").write_text(f"{COMMIT}\nsha256 {'c' * 64}\n")
    assert provenance.read_frozen(tmp_path) == COMMIT
    assert provenance.read_frozen_sha256(tmp_path) == "c" * 64


def test_benchmark_hash_mismatch_fails(tmp_path: Path) -> None:
    (tmp_path / "benchmark.json").write_text("{}")
    assert provenance.check_frozen_hash("c" * 64, tmp_path / "benchmark.json") != []
    import hashlib

    good = hashlib.sha256(b"{}").hexdigest()
    assert provenance.check_frozen_hash(good, tmp_path / "benchmark.json") == []


def test_held_out_benchmark_hash_is_declared_and_matches() -> None:
    directory = _ROOT / "artifacts" / "held-out"
    declared = provenance.read_frozen_sha256(directory)
    assert declared is not None
    assert provenance.check_frozen_hash(declared, directory / "benchmark.json") == []


def test_frozen_directory_without_a_benchmark_hash_fails(tmp_path: Path) -> None:
    payload = {"code": {"git_commit": COMMIT, "package_version": "0.1.0"}}
    (tmp_path / "benchmark.json").write_text(json.dumps(payload))
    (tmp_path / "FROZEN").write_text(f"{COMMIT}\n")
    result = provenance.check_directory(tmp_path)
    assert any("sha256" in failure for failure in result.failures)
