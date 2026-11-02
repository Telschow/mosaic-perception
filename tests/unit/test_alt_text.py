"""Every published image has alt text generated from its manifest, and the pages use it."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_alt_text.py"
GENERATED = ROOT / "docs-site" / "src" / "assets" / "generated"
IMAGE_SUFFIXES = {".svg", ".gif", ".png"}


def _load():
    spec = importlib.util.spec_from_file_location("make_alt_text", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _committed():
    return json.loads((GENERATED / "alt_text.json").read_text())


def test_committed_alt_text_matches_a_fresh_build():
    """Drift check: regenerate with `make assets` when this fails."""
    assert _load().build_alt_text() == _committed()


def test_every_published_image_has_alt_text():
    images = {p.stem for p in GENERATED.iterdir() if p.suffix in IMAGE_SUFFIXES}
    # The poster frame is a video thumbnail; the clip's own alt text covers it.
    assert images - {"summary_clip_poster"} == set(_committed())


def test_every_alt_text_says_it_is_synthetic_and_is_a_plain_sentence_or_two():
    for name, alt in _committed().items():
        assert re.search(r"synthetic", alt, re.I), name
        assert 40 <= len(alt) <= 700, name
        assert "\n" not in alt, name


def test_scenario_assets_name_the_scenario_their_manifest_records():
    alts = _committed()
    hero = json.loads((GENERATED / "hero.json").read_text())
    for key, still in hero["stills"].items():
        assert still["scenario"] in alts[f"hero_{key}"], key
    summary = json.loads((GENERATED / "summary_clip.json").read_text())
    recovery = next(b["scenario"] for b in summary["beats"] if b["id"] == "recovery")
    assert recovery in alts["summary_clip"] and recovery in alts["bias_recovery"]
    clip = json.loads((GENERATED / "scenario_clip.json").read_text())
    assert clip["scenario"] in alts["scenario_clip"]


def test_the_scoreboard_alt_text_quotes_the_artifacts_tally():
    ma = _load().make_assets
    rows = ma.load_scoreboard_data(ma.BENCHMARK)["rows"]
    row = next(
        r for r in rows if (r["comparison"], r["metric"]) == ("fused_vs_range_only", "precision")
    )
    alt = _committed()["scoreboard"]
    assert f"worse in {row['worse']}" in alt and f"better in {row['better']}" in alt


def test_readme_hero_and_landing_page_use_the_generated_alt_text():
    alts = _committed()
    readme = (ROOT / "README.md").read_text()
    assert f'alt="{alts["hero_recovers"]}"' in readme
    assert "docs-site/src/assets/generated/hero_recovers.png" in readme
    landing = (ROOT / "docs-site" / "src" / "content" / "docs" / "index.mdx").read_text()
    assert f'alt="{alts["summary_clip"]}"' in landing
    first_screen = readme.split("### Status")[0]
    assert "hero_recovers.png" in first_screen
