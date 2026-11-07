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
    payload = json.loads(mh.make_assets.BENCHMARK.read_text())
    manifest = mh.build_manifest(payload)
    ma_choice = mh.make_assets.choose_recovery_scenario(payload)
    assert manifest["stills"]["hurts"]["scenario"] == mh.choose_hurt_scenario(payload)
    assert manifest["stills"]["recovers"]["scenario"] == ma_choice
    assert manifest["stills"]["hurts"]["seed"] == min(payload["protocol"]["seeds"])


def test_manifest_numbers_are_the_artifacts_numbers():
    mh = _load()
    payload = json.loads(mh.make_assets.BENCHMARK.read_text())
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
    payload = json.loads(mh.make_assets.BENCHMARK.read_text())
    manifest = mh.build_manifest(payload)
    hurts, recovers = manifest["stills"]["hurts"], manifest["stills"]["recovers"]
    assert hurts["precision"]["ci95_high"] < 0
    assert recovers["precision"]["ci95_low"] > 0
    assert "worse" in hurts["panel_labels"]["fused"]
    assert "recover" in recovers["panel_labels"]["fused_bias_estimated"]


def test_label_and_commit_are_burned_into_every_still():
    mh = _load()
    assert mh.LABEL == "SYNTHETIC WORLD"
    payload = json.loads(mh.make_assets.BENCHMARK.read_text())
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
    assert mh.build_manifest(json.loads(mh.make_assets.BENCHMARK.read_text())) == committed
    for still in committed["stills"].values():
        assert (ROOT / "docs-site/src/assets/generated" / still["file"]).exists()


def _recovery_payload(name, fused_vs_range, bias_vs_fused, precision):
    """precision: (range_only, fused, fused_bias_estimated) aggregate means."""
    keys = ("mean", "ci95_low", "ci95_high")
    return {
        "scenario": {"name": name},
        "paired_differences": {
            "fused_vs_range_only": {"precision": dict(zip(keys, fused_vs_range, strict=True))},
            "bias_estimated_vs_fused": {"precision": dict(zip(keys, bias_vs_fused, strict=True))},
        },
        "aggregate": {
            m: {"precision": v}
            for m, v in zip(("range_only", "fused", "fused_bias_estimated"), precision, strict=True)
        },
    }


def test_recovery_requires_a_reliable_fusion_loss_first():
    mh = _load()
    gain_only = _recovery_payload("gain_only", (0.0, -0.1, 0.1), (0.2, 0.1, 0.3), (0.8, 0.8, 0.9))
    real = _recovery_payload("real", (-0.3, -0.4, -0.2), (0.1, 0.05, 0.15), (0.9, 0.6, 0.7))
    payload = {"scenarios": [gain_only, real]}
    assert mh.make_assets.choose_recovery_scenario(payload) == "real"


def test_recovery_rule_refuses_when_nothing_recovers_a_loss():
    mh = _load()
    payload = {
        "scenarios": [
            _recovery_payload("gain_only", (0.0, -0.1, 0.1), (0.2, 0.1, 0.3), (0.8, 0.8, 0.9)),
            _recovery_payload(
                "worse_after", (-0.3, -0.4, -0.2), (0.1, 0.05, 0.15), (0.9, 0.6, 0.55)
            ),
        ]
    }
    try:
        mh.make_assets.choose_recovery_scenario(payload)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_recovered_label_needs_a_prior_loss():
    mh = _load()
    no_loss = mh.panel_labels(
        {"mean": 0.0, "ci95_low": -0.1, "ci95_high": 0.1},
        {"mean": 0.1, "ci95_low": 0.05, "ci95_high": 0.15},
    )
    lost = mh.panel_labels(
        {"mean": -0.3, "ci95_low": -0.4, "ci95_high": -0.2},
        {"mean": 0.1, "ci95_low": 0.05, "ci95_high": 0.15},
    )
    assert "recover" not in no_loss["fused_bias_estimated"]
    assert "recover" in lost["fused_bias_estimated"]
