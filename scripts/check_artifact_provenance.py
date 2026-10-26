#!/usr/bin/env python3
"""Check that the committed benchmark artifact was produced from this source tree.

Reads ``artifacts/benchmark/benchmark.json`` and verifies:

1. the recorded source commit exists in the repository,
2. it is an ancestor of ``HEAD`` (the artifact was generated from this line of
   development, not from a divergent branch or an uncommitted tree),
3. no artifact-producing source has changed since that commit — the set is
   ``src/`` (the package), which is what generates the numbers. Tests,
   documentation, workflows and dependency manifests are deliberately not in
   the set: they cannot change generated values, and a dependency change that
   does change values is caught by ``scripts/check_benchmark_golden.py``,
4. the recorded package version still equals the version in ``pyproject.toml``
   (a version bump without regenerating artifacts is stale provenance).

Exit code 0 when everything holds, 1 otherwise. Runs in CI on every push and
pull request; see docs/evaluation-protocol.md.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ARTIFACT = Path("artifacts/benchmark/benchmark.json")
SOURCE_PATHS = ("src/",)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def main() -> int:
    if not ARTIFACT.exists():
        print(f"missing {ARTIFACT}", file=sys.stderr)
        return 1
    artifact = json.loads(ARTIFACT.read_text())
    commit = artifact.get("code", {}).get("git_commit")
    version = artifact.get("code", {}).get("package_version")
    if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
        print(f"artifact records no valid source commit: {commit!r}", file=sys.stderr)
        return 1

    failures: list[str] = []

    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        failures.append(f"recorded commit {commit[:12]} does not exist in this repository")
    else:
        if _git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            failures.append(
                f"recorded commit {commit[:12]} is not an ancestor of HEAD "
                "(artifact generated outside this branch's history)"
            )
        changed = _git("diff", "--name-only", commit, "HEAD", "--", *SOURCE_PATHS).stdout.split()
        if changed:
            failures.append(
                "artifact-producing source changed since the recorded commit: "
                + ", ".join(changed[:10])
                + (" ..." if len(changed) > 10 else "")
                + " — regenerate the benchmark (make benchmark)"
            )

    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    declared = pyproject["project"]["version"]
    if version != declared:
        failures.append(
            f"artifact records package version {version!r} but pyproject.toml declares {declared!r}"
        )

    if failures:
        for line in failures:
            print(f"FAIL {line}", file=sys.stderr)
        return 1
    print(f"provenance OK: artifact from {commit[:12]}, package {version}, source unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
