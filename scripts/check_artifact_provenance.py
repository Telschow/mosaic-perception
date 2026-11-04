#!/usr/bin/env python3
"""Check that the committed benchmark artifact was produced from this source tree.

Checks every ``artifacts/*/benchmark.json``. A directory containing a ``FROZEN``
file (line 1: the commit; optional line 2: ``sha256 <hex>`` of ``benchmark.json``) is a deliberately frozen run, such as the held-out
evaluation: instead of failing on later ``src/`` changes it reports the delta
since the frozen commit, and skips the version and re-render checks (the
renderer may legitimately have moved on). The frozen commit must equal the one
in ``benchmark.json`` and ``report.md``. For every other directory:

1. the recorded source commit exists in the repository,
2. it is an ancestor of ``HEAD`` (the artifact was generated from this line of
   development, not from a divergent branch or an uncommitted tree),
3. no artifact-producing source has changed since that commit — the set is
   ``src/`` (the package), which is what generates the numbers. Tests,
   documentation, workflows and dependency manifests are deliberately not in
   the set: they cannot change generated values, and a dependency change that
   does change values is caught by ``scripts/check_benchmark_golden.py``,
4. the recorded package version still equals the version in ``pyproject.toml``
   (a version bump without regenerating artifacts is stale provenance),
5. ``report.md`` records the same commit as ``benchmark.json`` and equals
   ``render_report(benchmark.json)`` (the render is a pure function, so a stale
   report is detectable). ``per_seed.csv`` records no commit and is not checked.

Exit code 0 when everything holds, 1 otherwise. Runs in CI on every push and
pull request; see docs/evaluation-protocol.md.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ARTIFACTS = Path("artifacts")
SOURCE_PATHS = ("src/",)
FROZEN_FILE = "FROZEN"


@dataclass
class DirectoryResult:
    failures: list[str] = field(default_factory=list)
    summary: str = ""
    frozen_at: str | None = None


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def check_report_commit(report: str, commit: str) -> list[str]:
    match = re.search(r"^- Git commit: `([^`]*)`", report, re.MULTILINE)
    if match is None:
        return ["report.md records no git commit"]
    if match.group(1) != commit:
        return [
            f"report.md records commit {match.group(1)[:12]} but benchmark.json records "
            f"{commit[:12]}; regenerate the benchmark (make benchmark)"
        ]
    return []


def check_report_render(report: str, payload: dict[str, Any]) -> list[str]:
    from mosaic_perception.reporting import render_report

    if report != render_report(payload):
        return ["report.md differs from render_report(benchmark.json); regenerate the report"]
    return []


def read_frozen(directory: Path) -> str | None:
    """The frozen commit: the first line of ``FROZEN``."""
    path = directory / FROZEN_FILE
    if not path.exists():
        return None
    lines = path.read_text().strip().splitlines()
    return lines[0].strip() if lines else ""


def read_frozen_sha256(directory: Path) -> str | None:
    """The optional ``sha256 <hex>`` line of ``FROZEN``: the hash of ``benchmark.json``."""
    path = directory / FROZEN_FILE
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        match = re.fullmatch(r"sha256\s+([0-9a-f]{64})", line.strip())
        if match:
            return match.group(1)
    return None


def check_frozen_hash(declared: str, artifact_path: Path) -> list[str]:
    actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    if declared != actual:
        return [
            f"{FROZEN_FILE} declares benchmark.json sha256 {declared[:12]} but it is {actual[:12]}"
        ]
    return []


def check_frozen_declaration(declared: str, commit: str) -> list[str]:
    if declared != commit:
        return [f"{FROZEN_FILE} declares {declared[:12]} but benchmark.json records {commit[:12]}"]
    return []


def artifact_directories(root: Path) -> list[Path]:
    return sorted(p.parent for p in root.glob("*/benchmark.json"))


def check_directory(directory: Path) -> DirectoryResult:
    result = DirectoryResult()
    failures = result.failures
    artifact_path = directory / "benchmark.json"
    report_path = directory / "report.md"
    artifact = json.loads(artifact_path.read_text())
    commit = artifact.get("code", {}).get("git_commit")
    version = artifact.get("code", {}).get("package_version")
    if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
        failures.append(f"artifact records no valid source commit: {commit!r}")
        return result

    declared = read_frozen(directory)
    frozen = declared is not None
    if declared is not None:
        failures += check_frozen_declaration(declared, commit)
        result.frozen_at = declared
        declared_hash = read_frozen_sha256(directory)
        if declared_hash is None:
            failures.append(f"{FROZEN_FILE} has no `sha256 <hex>` line for benchmark.json")
        else:
            failures += check_frozen_hash(declared_hash, artifact_path)

    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        failures.append(f"recorded commit {commit[:12]} does not exist in this repository")
    else:
        if _git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            failures.append(
                f"recorded commit {commit[:12]} is not an ancestor of HEAD "
                "(artifact generated outside this branch's history)"
            )
        changed = _git("diff", "--name-only", commit, "HEAD", "--", *SOURCE_PATHS).stdout.split()
        if frozen:
            commits = _git("log", "--oneline", f"{commit}..HEAD", "--", *SOURCE_PATHS)
            n = len(commits.stdout.splitlines())
            result.summary = (
                f"frozen at {commit[:12]}; {n} src/ commit(s) and {len(changed)} src/ file(s) "
                "changed since (not regenerated by design)"
            )
        elif changed:
            failures.append(
                "artifact-producing source changed since the recorded commit: "
                + ", ".join(changed[:10])
                + (" ..." if len(changed) > 10 else "")
                + "; regenerate the benchmark (make benchmark)"
            )

    if not frozen:
        declared_version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
        if version != declared_version:
            failures.append(
                f"artifact records package version {version!r} but pyproject.toml "
                f"declares {declared_version!r}"
            )

    if not report_path.exists():
        failures.append(f"missing {report_path}")
    else:
        report = report_path.read_text()
        failures += check_report_commit(report, commit)
        if not frozen:
            failures += check_report_render(report, artifact)

    if not result.summary:
        result.summary = f"artifact from {commit[:12]}, package {version}, source unchanged"
    return result


def main() -> int:
    directories = artifact_directories(ARTIFACTS)
    if not directories:
        print(f"no artifacts found under {ARTIFACTS}/", file=sys.stderr)
        return 1
    status = 0
    for directory in directories:
        result = check_directory(directory)
        for line in result.failures:
            print(f"FAIL {directory}: {line}", file=sys.stderr)
        if result.failures:
            status = 1
        else:
            print(f"provenance OK {directory}: {result.summary}")
    return status


if __name__ == "__main__":
    sys.exit(main())
