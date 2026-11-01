"""Docs-site content sync: pages come from docs/, links resolve, no copied content is committed."""

from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "sync_docs_site.py"


def _load():
    spec = importlib.util.spec_from_file_location("sync_docs_site", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rewrite_links_maps_known_pages_to_site_routes():
    s = _load()
    assert s.rewrite_links("[m](metrics.md#x)", "docs") == "[m](/mosaic-perception/metrics/#x)"
    assert s.rewrite_links("[a](audits/mosaic-perception-comprehensive-audit.md)", "docs") == (
        "[a](/mosaic-perception/audit/)"
    )


def test_rewrite_links_sends_other_repo_paths_to_github():
    s = _load()
    out = s.rewrite_links("[r](../artifacts/benchmark/report.md)", "docs")
    assert out == f"[r]({s.REPO_URL}/blob/main/artifacts/benchmark/report.md)"
    out = s.rewrite_links("[d](demo-script.md)", "docs")
    assert out == f"[d]({s.REPO_URL}/blob/main/docs/demo-script.md)"


def test_rewrite_links_leaves_external_and_anchor_links():
    s = _load()
    text = "[a](https://example.org/x.md) [b](#sec)"
    assert s.rewrite_links(text, "docs") == text


def test_split_title_moves_h1_to_frontmatter():
    s = _load()
    title, body = s.split_title("# Evaluation Metrics\n\ntext\n")
    assert title == "Evaluation Metrics"
    assert body.strip() == "text"


def test_sync_writes_every_navigation_page(tmp_path):
    s = _load()
    s.sync(ROOT, tmp_path)
    for slug in [
        "architecture",
        "scenarios",
        "metrics",
        "evaluation-protocol",
        "limitations",
        "roadmap",
        "implementation-status",
        "demos",
        "audit",
        "citation",
    ]:
        page = tmp_path / f"{slug}.md"
        assert page.read_text().startswith("---\ntitle: "), slug
    assert "Generated" in (tmp_path / "metrics.md").read_text()


def test_no_relative_markdown_links_survive_sync(tmp_path):
    s = _load()
    s.sync(ROOT, tmp_path)
    for page in tmp_path.glob("*.md"):
        assert not re.search(r"\]\((?!https?:)[^)]*\.md[)#]", page.read_text()), page.name


def test_generated_pages_are_git_ignored():
    for name in ("metrics.md", "audit.md"):
        path = f"docs-site/src/content/docs/{name}"
        res = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT)
        assert res.returncode == 0, name
