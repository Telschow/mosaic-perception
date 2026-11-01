"""Copy the repository Markdown into the Starlight content tree.

``docs/`` stays the single source. Pages are generated into
``docs-site/src/content/docs/`` (git-ignored) with a title taken from the H1 and
relative links rewritten to site routes or GitHub URLs. Nothing is hand-copied.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_URL = "https://github.com/Telschow/mosaic-perception"
BASE = "/mosaic-perception"  # must match `base` in docs-site/astro.config.mjs
OUTPUT = Path("docs-site/src/content/docs")

# slug -> source path relative to the repository root
PAGES = {
    "architecture": "docs/architecture.md",
    "scenarios": "docs/scenarios.md",
    "metrics": "docs/metrics.md",
    "evaluation-protocol": "docs/evaluation-protocol.md",
    "limitations": "docs/limitations.md",
    "roadmap": "docs/roadmap.md",
    "implementation-status": "docs/implementation-status.md",
    "demos": "docs/demos.md",
    "audit": "docs/audits/mosaic-perception-comprehensive-audit.md",
}

_LINK = re.compile(r"\]\((?!https?://|#|mailto:)([^)#\s]+)(#[^)\s]*)?\)")
_ROUTES = {src: slug for slug, src in PAGES.items()}


def rewrite_links(text: str, source_dir: str) -> str:
    """Point links at site routes for published pages, else at GitHub."""

    def repl(match: re.Match[str]) -> str:
        target, anchor = match.group(1), match.group(2) or ""
        resolved = Path(source_dir, target).as_posix()
        parts: list[str] = []
        for part in resolved.split("/"):
            if part == "..":
                parts.pop()
            elif part != ".":
                parts.append(part)
        repo_path = "/".join(parts)
        if repo_path in _ROUTES:
            return f"]({BASE}/{_ROUTES[repo_path]}/{anchor})"
        return f"]({REPO_URL}/blob/main/{repo_path}{anchor})"

    return _LINK.sub(repl, text)


def split_title(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return line[2:].strip(), "\n".join(lines[:i] + lines[i + 1 :]).lstrip("\n")
    raise ValueError("document has no H1 title")


def _page(title: str, body: str, source: str) -> str:
    note = f"> Generated from [`{source}`]({REPO_URL}/blob/main/{source}); edit the source, not this page.\n\n"
    return f'---\ntitle: "{title}"\n---\n\n{note}{body.rstrip()}\n'


def sync(root: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for slug, source in PAGES.items():
        title, body = split_title((root / source).read_text())
        body = rewrite_links(body, str(Path(source).parent))
        (out / f"{slug}.md").write_text(_page(title, body, source))
    cff = (root / "CITATION.cff").read_text().rstrip()
    body = (
        "To cite this software, use the metadata below "
        f"([`CITATION.cff`]({REPO_URL}/blob/main/CITATION.cff)).\n\n```yaml\n{cff}\n```"
    )
    (out / "citation.md").write_text(_page("Citation", body, "CITATION.cff"))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    sync(root, Path(sys.argv[1]) if len(sys.argv) > 1 else root / OUTPUT)
