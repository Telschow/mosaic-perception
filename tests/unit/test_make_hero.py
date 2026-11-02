"""README hero stills: scenarios are chosen by a rule, and every number comes from the artifact."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "make_hero.py"


def _load():
    spec = importlib.util.spec_from_file_location("make_hero", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(*rows):
    """A minimal artifact: (name, fused-vs-range precision [mean, low, high], bias-vs-fused likewise)."""
    scenarios = []
    for name, hurt, help_ in rows:
        scenarios.append(
            {
                "scenario": {"name": name},
                "paired_differences": {
                    "fused_vs_range_only": {
                        "precision": dict(zip(("mean", "ci95_low", "ci95_high"), hurt, strict=True))
                    },
                    "bias_estimated_vs_fused": {
                        "precision": dict(
                            zip(("mean", "ci95_low", "ci95_high"), help_, strict=True)
                        )
                    },
                },
            }
        )
    return {"scenarios": scenarios}


def test_hurt_scenario_is_the_largest_loss_whose_interval_excludes_zero():
    mh = _load()
    payload = _payload(
        ("small_loss", (-0.1, -0.2, -0.05), (0, -0.1, 0.1)),
        ("big_loss", (-0.5, -0.6, -0.4), (0, -0.1, 0.1)),
        ("huge_but_noisy", (-0.9, -1.2, 0.1), (0, -0.1, 0.1)),
        ("a_gain", (0.3, 0.2, 0.4), (0, -0.1, 0.1)),
    )
    assert mh.choose_hurt_scenario(payload) == "big_loss"


def test_hurt_scenario_rule_refuses_when_fusion_never_reliably_hurts():
    mh = _load()
    payload = _payload(("flat", (0.0, -0.1, 0.1), (0, -0.1, 0.1)))
    try:
        mh.choose_hurt_scenario(payload)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_stills_use_the_rule_not_a_hand_picked_scenario_or_seed():
    mh = _load()
    payload = json.loads(mh.BENCHMARK.read_text())
    manifest = mh.build_manifest(payload)
    ma_choice = mh.make_assets.choose_recovery_scenario(payload)
    assert manifest["stills"]["hurts"]["scenario"] == mh.choose_hurt_scenario(payload)
    assert manifest["stills"]["recovers"]["scenario"] == ma_choice
    assert manifest["stills"]["hurts"]["seed"] == min(payload["protocol"]["seeds"])


def test_manifest_numbers_are_the_artifacts_numbers():
    mh = _load()
    payload = json.loads(mh.BENCHMARK.read_text())
    manifest = mh.build_manifest(payload)
    assert manifest["commit"] == payload["code"]["git_commit"]
    for still in manifest["stills"].values():
        scenario = next(
            s for s in payload["scenarios"] if s["scenario"]["name"] == still["scenario"]
        )
        paired = scenario["paired_differences"][still["comparison"]]["precision"]
        assert still["precision"] == {
            k: round(paired[k], 3) for k in ("mean", "ci95_low", "ci95_high")
        }


def test_panel_labels_say_what_the_numbers_show():
    mh = _load()
    payload = json.loads(mh.BENCHMARK.read_text())
    manifest = mh.build_manifest(payload)
    hurts, recovers = manifest["stills"]["hurts"], manifest["stills"]["recovers"]
    assert hurts["precision"]["ci95_high"] < 0
    assert recovers["precision"]["ci95_low"] > 0
    assert "worse" in hurts["panel_labels"]["fused"]
    assert "recover" in recovers["panel_labels"]["fused_bias_estimated"]


def test_label_and_commit_are_burned_into_every_still():
    mh = _load()
    assert mh.LABEL == "SYNTHETIC WORLD"
    payload = json.loads(mh.BENCHMARK.read_text())
    manifest = mh.build_manifest(payload)
    assert manifest["label"] == mh.LABEL
    for still in manifest["stills"].values():
        assert re.fullmatch(r"[0-9a-f]{12}", still["source_commit"])
        assert still["source_commit"] == manifest["commit"][:12]


def test_script_reads_only_the_development_artifact():
    text = SCRIPT.read_text()
    assert "held-out" not in text and "held_out" not in text


def test_committed_manifest_matches_the_artifact():
    """Drift check: regenerate with `make assets` when this fails."""
    mh = _load()
    committed = json.loads((ROOT / "docs-site/src/assets/generated/hero.json").read_text())
    assert mh.build_manifest(json.loads(mh.BENCHMARK.read_text())) == committed
    for still in committed["stills"].values():
        assert (ROOT / "docs-site/src/assets/generated" / still["file"]).exists()
