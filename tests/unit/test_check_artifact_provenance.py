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


def _ablation_payload(commit: str = COMMIT) -> dict:
    return {"code": {"git_commit": commit}, "rows": []}


def test_ablation_report_with_matching_commit_and_render_passes() -> None:
    report = f"Commit: `{COMMIT}`\n"
    assert provenance.check_ablation_report(report, _ablation_payload(), report) == []


def test_ablation_report_with_mismatched_commit_fails() -> None:
    report = f"Commit: `{OTHER}`\n"
    failures = provenance.check_ablation_report(report, _ablation_payload(), report)
    assert failures and "vision_refresh.md" in failures[0]


def test_ablation_report_without_commit_fails() -> None:
    assert provenance.check_ablation_report("nothing\n", _ablation_payload(), "nothing\n") != []


def test_ablation_report_differing_from_render_fails() -> None:
    report = f"Commit: `{COMMIT}`\n"
    assert provenance.check_ablation_report(report, _ablation_payload(), report + "x") != []


def test_missing_recorded_commit_cannot_be_diffed() -> None:
    failures, changed = provenance.check_recorded_commit(COMMIT)
    assert failures and changed is None


def test_head_is_its_own_ancestor_with_no_source_change() -> None:
    head = provenance._git("rev-parse", "HEAD").stdout.strip()
    assert provenance.check_recorded_commit(head) == ([], [])


def test_ablation_directory_is_discovered(tmp_path: Path) -> None:
    (tmp_path / "ablation").mkdir()
    (tmp_path / "ablation" / "vision_refresh.json").write_text("{}")
    (tmp_path / "other").mkdir()
    assert provenance.ablation_directories(tmp_path) == [tmp_path / "ablation"]


def test_ablation_with_invalid_commit_fails(tmp_path: Path) -> None:
    (tmp_path / "vision_refresh.json").write_text(json.dumps(_ablation_payload("short")))
    assert provenance.check_ablation_directory(tmp_path).failures


_FREEZE = "8baa778e86826ddbdcb4b27ef07d7ca9b993e354"
_ABLATION_SCRIPT = "scripts/ablate_vision_refresh.py"


def test_source_changed_since_an_older_commit_is_listed() -> None:
    failures, changed = provenance.check_recorded_commit(_FREEZE)
    assert failures == []
    assert changed and all(path.startswith("src/") for path in changed)


def test_recorded_commit_diff_honours_the_given_source_paths() -> None:
    # The ablation script was added in 4a49ca1, so it differs from that commit's parent.
    parent = provenance._git("rev-parse", "4a49ca1^").stdout.strip()
    _, changed = provenance.check_recorded_commit(parent, (_ABLATION_SCRIPT,))
    assert changed == [_ABLATION_SCRIPT]


def test_ablation_check_watches_its_generating_script(tmp_path: Path, monkeypatch) -> None:
    seen: list[tuple[str, ...]] = []

    def fake(_commit: str, source_paths: tuple[str, ...] = provenance.SOURCE_PATHS):
        seen.append(tuple(source_paths))
        return [], [_ABLATION_SCRIPT]

    monkeypatch.setattr(provenance, "check_recorded_commit", fake)
    (tmp_path / "vision_refresh.json").write_text(json.dumps(_ablation_payload()))
    result = provenance.check_ablation_directory(tmp_path)
    assert seen and _ABLATION_SCRIPT in seen[0] and "src/" in seen[0]
    assert any("make ablation" in failure for failure in result.failures)


def test_non_frozen_benchmark_with_changed_source_fails(tmp_path: Path) -> None:
    payload = {"code": {"git_commit": _FREEZE, "package_version": "0.1.0"}}
    (tmp_path / "benchmark.json").write_text(json.dumps(payload))
    (tmp_path / "report.md").write_text(f"- Git commit: `{_FREEZE}`\n")
    failures = provenance.check_directory(tmp_path).failures
    assert any("source changed since the recorded commit" in f for f in failures)


def test_benchmark_without_a_report_fails(tmp_path: Path) -> None:
    head = provenance._git("rev-parse", "HEAD").stdout.strip()
    payload = {"code": {"git_commit": head, "package_version": "0.1.0"}}
    (tmp_path / "benchmark.json").write_text(json.dumps(payload))
    failures = provenance.check_directory(tmp_path).failures
    assert any("missing" in f and "report.md" in f for f in failures)


def test_benchmark_without_a_commit_fails(tmp_path: Path) -> None:
    (tmp_path / "benchmark.json").write_text(json.dumps({"code": {}}))
    assert provenance.check_directory(tmp_path).failures


def test_frozen_directory_with_unknown_commit_fails(tmp_path: Path) -> None:
    import hashlib

    payload = json.dumps({"code": {"git_commit": COMMIT, "package_version": "0.1.0"}})
    (tmp_path / "benchmark.json").write_text(payload)
    (tmp_path / "report.md").write_text(f"- Git commit: `{COMMIT}`\n")
    digest = hashlib.sha256(payload.encode()).hexdigest()
    (tmp_path / "FROZEN").write_text(f"{COMMIT}\nsha256 {digest}\n")
    failures = provenance.check_directory(tmp_path).failures
    assert any("does not exist" in f for f in failures)
