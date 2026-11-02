"""Mechanical guardrails: tracked README/landing images, and unfiltered required-check workflows."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
# Jobs whose names are required status checks on main.
REQUIRED_CHECK_JOBS = {"build", "test"}

_HTML_SRC = re.compile(r"""<img[^>]+src=["']([^"']+)["']""")
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
_MDX_IMPORT = re.compile(r"""import\s+\w+\s+from\s+['"]([^'"]+\.(?:png|gif|jpe?g|svg|webp))['"]""")


def _tracked() -> set[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return set(out.splitlines())


def referenced_images(path: Path) -> list[Path]:
    """Local image files referenced from a README or landing page, relative to the repo root."""
    text = path.read_text(encoding="utf-8")
    refs = _HTML_SRC.findall(text) + _MD_IMAGE.findall(text) + _MDX_IMPORT.findall(text)
    found = []
    for ref in refs:
        if re.match(r"^[a-z]+://|^data:|^/", ref):
            continue
        found.append((path.parent / ref.split("#")[0].split("?")[0]).resolve().relative_to(ROOT))
    return found


def untracked_images(pages: list[Path], tracked: set[str]) -> list[str]:
    return sorted(
        {f"{page.relative_to(ROOT)} -> {img}" for page in pages for img in referenced_images(page)
         if img.as_posix() not in tracked}
    )  # fmt: skip


def required_workflows_with_path_filter(workflows: Path, required: set[str]) -> list[str]:
    bad = []
    for wf in sorted(workflows.glob("*.y*ml")):
        doc = yaml.safe_load(wf.read_text(encoding="utf-8"))
        if not required & set(doc.get("jobs", {})):
            continue
        pr = (doc.get(True) or doc.get("on") or {}).get("pull_request") or {}
        if "paths" in pr or "paths-ignore" in pr:
            bad.append(wf.name)
    return bad


def test_readme_and_landing_images_are_tracked_by_git():
    pages = [ROOT / "README.md", ROOT / "docs-site" / "src" / "content" / "docs" / "index.mdx"]
    assert not untracked_images(pages, _tracked())


def test_untracked_image_is_detected():
    page = ROOT / "README.md"
    assert untracked_images([page], set()), "README references images; none tracked must fail"


def test_required_check_workflows_have_no_pull_request_path_filter():
    assert not required_workflows_with_path_filter(WORKFLOWS, REQUIRED_CHECK_JOBS)


def test_path_filter_on_required_check_is_detected(tmp_path):
    (tmp_path / "docs.yml").write_text(
        "on:\n  pull_request:\n    paths: ['docs/**']\njobs:\n  build:\n    runs-on: x\n"
    )
    assert required_workflows_with_path_filter(tmp_path, {"build"}) == ["docs.yml"]
