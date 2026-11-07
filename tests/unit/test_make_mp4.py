"""Feed-ready MP4 plan: sizes, captions, SRT, ffmpeg command and the missing-ffmpeg path."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_mp4.py"


def _load():
    spec = importlib.util.spec_from_file_location("make_mp4", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _summary_manifest():
    path = ROOT / "docs-site" / "src" / "assets" / "generated" / "summary_clip.json"
    return json.loads(path.read_text())


def test_both_formats_are_the_feed_sizes():
    mm = _load()
    assert mm.FORMATS == {"9x16": (1080, 1920), "16x9": (1920, 1080)}


def test_each_cut_is_between_30_and_45_seconds():
    mm = _load()
    plan = mm.build_plan(_summary_manifest(), commit="abcdef123456789")
    assert 30_000 <= plan["total_ms"] <= 45_000


def test_every_beat_has_a_caption_without_numbers_and_the_end_card_carries_the_url():
    mm = _load()
    plan = mm.build_plan(_summary_manifest(), commit="abcdef123456789")
    assert [c["id"] for c in plan["cues"]] == [b["id"] for b in _summary_manifest()["beats"]]
    for cue in plan["cues"]:
        assert cue["text"] and not re.search(r"\d", cue["text"]), cue["id"]
    assert mm.URL in plan["cues"][-1]["text"]


def test_captions_stay_readable_at_360_px_wide():
    mm = _load()
    assert mm.CAPTION_PX >= 48 and mm.LABEL_PX >= 48
    assert mm.CAPTION_PX * 360 / 1080 >= 16


def test_srt_has_one_cue_per_beat_in_order_with_srt_timestamps():
    mm = _load()
    plan = mm.build_plan(_summary_manifest(), commit="abcdef123456789")
    srt = mm.to_srt(plan["cues"])
    blocks = srt.strip().split("\n\n")
    assert len(blocks) == len(plan["cues"])
    stamp = r"\d\d:\d\d:\d\d,\d\d\d"
    last_end = ""
    for index, (block, cue) in enumerate(zip(blocks, plan["cues"], strict=True), start=1):
        lines = block.split("\n")
        assert lines[0] == str(index)
        match = re.fullmatch(rf"({stamp}) --> ({stamp})", lines[1])
        assert match and match.group(1) >= last_end
        last_end = match.group(2)
        assert "\n".join(lines[2:]) == "\n".join([cue["text"], *cue["facts"]])
    assert mm.srt_time(31_800) == "00:00:31,800" and mm.srt_time(3_723_004) == "01:02:03,004"


def test_ffmpeg_command_makes_h264_at_the_requested_size():
    mm = _load()
    command = mm.ffmpeg_command(Path("frames.txt"), Path("out.mp4"), (1080, 1920))
    assert command[0] == "ffmpeg"
    joined = " ".join(command)
    assert "libx264" in joined and "yuv420p" in joined and "+faststart" in joined
    assert "scale=1080:1920" in joined
    assert command[-1] == "out.mp4"


def test_without_ffmpeg_it_stops_with_a_clear_message_and_renders_nothing(capsys):
    mm = _load()
    with (
        mock.patch.object(mm.shutil, "which", return_value=None),
        mock.patch.object(mm.subprocess, "run") as run,
    ):
        assert mm.main() == 1
    run.assert_not_called()
    err = capsys.readouterr().err
    assert "ffmpeg" in err and "brew install ffmpeg" in err


def test_manifest_records_the_artifact_commit_sources_and_outputs():
    mm = _load()
    commit = json.loads((ROOT / "artifacts" / "benchmark" / "benchmark.json").read_text())["code"][
        "git_commit"
    ]
    plan = mm.build_plan(_summary_manifest(), commit=commit)
    manifest = mm.build_manifest(plan)
    assert manifest["source_commit"] == commit
    assert manifest["label"] == "Synthetic world"
    assert set(manifest["outputs"]) == {"9x16", "16x9"}
    assert manifest["srt"].endswith(".srt") and manifest["poster"].endswith(".png")
    for source in manifest["sources"]:
        assert (ROOT / source).exists(), source


def test_script_reads_only_the_development_artifact():
    text = SCRIPT.read_text()
    assert "held-out" not in text and "held_out" not in text


def test_burned_in_facts_are_the_artifacts_numbers():
    mm = _load()
    ma = mm.make_assets
    plan = mm.build_plan(_summary_manifest(), commit="abcdef123456789")
    facts = {c["id"]: c["facts"] for c in plan["cues"]}
    rows = {
        (r["comparison"], r["metric"]): r for r in ma.load_scoreboard_data(ma.BENCHMARK)["rows"]
    }
    row = rows[("fused_vs_range_only", "precision")]
    assert facts["scoreboard"] == [
        f"Precision: worse in {row['worse']} scenarios, better in {row['better']}, unclear in {row['inconclusive']}."
    ]
    recovery = ma.load_recovery_data(ma.BENCHMARK)
    precision = recovery["metrics"]["precision"]
    assert recovery["scenario"] in facts["recovery"][0]
    assert f"{precision['recovered_share']:.0%}" in facts["recovery"][1]
    assert facts["range_only"] == facts["fused"] == facts["end_card"] == []


def test_the_manifest_labels_the_seed_group_and_the_footer_says_it():
    mm = _load()
    plan = mm.build_plan(_summary_manifest(), commit="abcdef123456789")
    assert plan["seed_label"] == "development seeds 0-24"
    assert mm.build_manifest(plan)["seed_label"] == "development seeds 0-24"


def test_footer_and_captions_fit_inside_both_frames():
    from PIL import Image, ImageDraw

    mm = _load()
    plan = mm.build_plan(_summary_manifest(), commit="abcdef123456789")
    for size in mm.FORMATS.values():
        draw = ImageDraw.Draw(Image.new("RGB", size))
        for line in (
            mm.LABEL.upper(),
            plan["seed_label"],
            f"artifact commit {plan['commit'][:12]}",
        ):
            font = mm._draw.font(mm.LABEL_PX, bold=True)
            assert draw.textlength(line, font=font) <= size[0] - 80, (size, line)


def test_recovery_caption_does_not_claim_recovery_the_rule_rejects(monkeypatch):
    mm = _load()
    real = mm.make_assets.load_recovery_data(mm.make_assets.BENCHMARK)
    rejected = json.loads(json.dumps(real))
    rejected["metrics"]["precision"]["verdict"] = "does not recover"
    monkeypatch.setattr(mm.make_assets, "load_recovery_data", lambda *_a, **_k: rejected)
    facts = mm._facts("recovery")
    assert not any("recovers" in line for line in facts)
