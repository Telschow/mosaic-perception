"""Summary clip: the beat manifest is reproducible and the committed GIF follows it."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_summary_clip.py"
BEATS = ["range_only", "fused", "scoreboard", "recovery", "end_card"]


def _load():
    spec = importlib.util.spec_from_file_location("make_summary_clip", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_matches_committed_file():
    """Drift check: regenerate with `make assets` when this fails."""
    msc = _load()
    committed = json.loads(msc.MANIFEST.read_text())
    assert msc.build_manifest(msc.build_beats()) == committed


def test_manifest_lists_every_beat_in_storyboard_order_with_sources():
    msc = _load()
    manifest = json.loads(msc.MANIFEST.read_text())
    assert [b["id"] for b in manifest["beats"]] == BEATS
    for beat in manifest["beats"]:
        assert beat["sources"], beat["id"]
        for source in beat["sources"]:
            assert (ROOT / source).exists(), source
    starts = [b["start_ms"] for b in manifest["beats"]]
    assert starts == sorted(starts) and starts[0] == 0
    last = manifest["beats"][-1]
    assert manifest["total_ms"] == last["start_ms"] + last["duration_ms"]


def test_total_length_under_sixty_seconds():
    msc = _load()
    assert json.loads(msc.MANIFEST.read_text())["total_ms"] < 60_000


def test_captions_come_from_demos_page():
    msc = _load()
    manifest = json.loads(msc.MANIFEST.read_text())
    assert manifest["headline"] == "More sensors don't automatically mean better tracking."
    demos = (ROOT / "docs" / "demos.md").read_text()
    assert manifest["headline"] in demos and manifest["subline"] in demos
    assert manifest["end_card"] == "Synthetic world. Full results and limits:"
    assert manifest["url"] == "https://telschow.github.io/mosaic-perception/"


def test_text_added_by_the_clip_has_no_numbers():
    """Every number on screen comes from the pieces; the clip's own text adds none."""
    msc = _load()
    manifest = json.loads(msc.MANIFEST.read_text())
    for key in ("headline", "subline", "end_card", "label"):
        assert not re.search(r"\d", manifest[key]), key
    assert "held-out" not in SCRIPT.read_text()


def test_committed_gif_follows_manifest():
    msc = _load()
    manifest = json.loads(msc.MANIFEST.read_text())
    with Image.open(msc.OUTPUT) as gif:
        assert gif.n_frames == manifest["frame_count"]
        total = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            total += gif.info["duration"]
    assert total == manifest["total_ms"]
    assert msc.OUTPUT.stat().st_size < 5_000_000


def test_synthetic_label_is_in_every_frame():
    msc = _load()
    frames = [f for beat in msc.build_beats() for f in beat["frames"]]
    footer = [f.crop(msc.FOOTER_BOX).tobytes() for f in frames]
    assert len(set(footer)) == 1
    blank = Image.new("RGB", frames[0].size, (255, 255, 255)).crop(msc.FOOTER_BOX)
    assert footer[0] != blank.tobytes()


def test_render_is_byte_identical():
    msc = _load()
    beats = msc.build_beats()
    assert msc.render_gif(beats) == msc.render_gif(msc.build_beats())


def test_recovery_beat_names_the_scenario_the_docs_and_alt_text_name():
    manifest = json.loads((ROOT / "docs-site/src/assets/generated/summary_clip.json").read_text())
    scenario = next(b for b in manifest["beats"] if b["id"] == "recovery")["scenario"]
    assert scenario in (ROOT / "docs/demos.md").read_text()
    assert scenario in (ROOT / "docs-site/src/content/docs/index.mdx").read_text()
