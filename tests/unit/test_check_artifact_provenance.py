"""Tests for the report.md consistency part of the artifact provenance check."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_artifact_provenance", _ROOT / "scripts" / "check_artifact_provenance.py"
)
assert _spec is not None and _spec.loader is not None
provenance = importlib.util.module_from_spec(_spec)
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
