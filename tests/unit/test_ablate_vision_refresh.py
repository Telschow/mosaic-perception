"""Ablation script: development seeds only, both policies reported per metric."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ablate_vision_refresh.py"


def _load():
    spec = importlib.util.spec_from_file_location("ablate_vision_refresh", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_refuses_held_out_seeds():
    with pytest.raises(ValueError):
        _load().run(seeds=[25, 26])


def test_reports_both_policies_for_every_metric():
    mod = _load()
    payload = mod.run(seeds=[0, 1], scenarios=("nominal",))
    keys = {(r["policy"], r["metric"]) for r in payload["rows"]}
    assert keys == {(p, m) for p in mod.POLICIES for m, _ in mod.METRICS}
    assert "range_supported" in mod.render(payload)
