"""Tests for scenario presets and effective configuration."""

from __future__ import annotations

import pytest

from mosaic_perception.scenarios import (
    DEFAULT_SCENARIO,
    PRESETS,
    available_scenarios,
    resolve_scenario,
)


def test_all_presets_resolve_with_two_sensor_groups():
    for name in available_scenarios():
        scenario = resolve_scenario(name, seed=3, duration=2.0)
        assert scenario.name == name
        assert set(scenario.sensors) == {"range_bearing", "vision_bearing"}
        assert scenario.sensors["range_bearing"].sensor_type == "range_bearing"
        assert scenario.sensors["vision_bearing"].sensor_type == "vision_bearing"
        assert scenario.seed == 3


def test_default_scenario_exists():
    assert DEFAULT_SCENARIO in PRESETS


def test_scenario_overrides_are_real_and_isolated():
    nominal = resolve_scenario("nominal", seed=1, duration=2.0)
    biased = resolve_scenario("measurement_bias", seed=1, duration=2.0)
    assert nominal.sensors["range_bearing"].noise_std == biased.sensors["range_bearing"].noise_std
    assert nominal.sensors["range_bearing"].bias == {}
    assert biased.sensors["range_bearing"].bias["range"] == pytest.approx(1.5)


def test_moving_observer_preset_uses_circle():
    scenario = resolve_scenario("moving_observer", seed=1, duration=2.0)
    assert scenario.observer_trajectory == "circle"


def test_out_of_sequence_preset_exceeds_one_epoch_delay():
    scenario = resolve_scenario("out_of_sequence", seed=1, duration=2.0)
    assert scenario.sensors["range_bearing"].delivery_delay_mean == pytest.approx(0.25)


def test_unknown_scenario_raises_with_available_names():
    with pytest.raises(ValueError, match="unknown scenario"):
        resolve_scenario("does_not_exist", seed=1, duration=2.0)


def test_resolved_scenario_is_independent_of_module_defaults():
    first = resolve_scenario("nominal", seed=1, duration=2.0)
    second = resolve_scenario("measurement_bias", seed=2, duration=2.0)
    first.sensors["range_bearing"].noise_std["range"] = 999.0
    third = resolve_scenario("nominal", seed=3, duration=2.0)
    assert third.sensors["range_bearing"].noise_std["range"] == pytest.approx(0.5)
    assert second.sensors["range_bearing"].noise_std["range"] == pytest.approx(0.5)
