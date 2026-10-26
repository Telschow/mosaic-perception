"""Data-preparation smoke test for the Streamlit workbench (issue #33).

Imports the browser-free app module and checks what it would render on one
short scenario: method coverage, both accuracy views, scene traces and the
simulated-data labelling. No browser and no Streamlit runtime involved.
"""

from __future__ import annotations

import pytest

from app.data_prep import (
    LIMITATIONS_NOTE,
    SIMULATED_LABEL,
    build_metrics_rows,
    build_scene_figure,
    format_metric,
    scenario_summary,
    visible_methods,
)
from mosaic_perception.experiment import METHODS, PairedRun, run_pair
from mosaic_perception.scenarios import resolve_scenario


@pytest.fixture(scope="module")
def pair() -> PairedRun:
    scenario = resolve_scenario("nominal", seed=3, duration=1.0, num_objects=2)
    return run_pair(scenario, include_bias_estimation=True)


def test_rows_cover_every_method_the_runner_exposes(pair: PairedRun) -> None:
    methods = visible_methods(pair)
    rows = build_metrics_rows(methods)
    assert [row["method"] for row in rows] == list(METHODS)
    assert {name for name, _ in methods} == set(METHODS)


def test_accuracy_rows_carry_headline_and_distance_only_rmse(pair: PairedRun) -> None:
    rows = build_metrics_rows(visible_methods(pair))
    for row in rows:
        assert row["position_rmse_m"] is not None, row["method"]
        assert row["position_rmse_distance_only_m"] is not None, row["method"]
        assert row["position_rmse_m"] >= 0.0
        assert row["mota"] is not None
        assert row["idf1"] is not None
        assert row["identity_switches"] is not None


def test_scene_figure_contains_ground_truth_and_method_tracks(pair: PairedRun) -> None:
    methods = visible_methods(pair)
    figure = build_scene_figure(pair, methods)
    names = [trace.name for trace in figure.data]
    assert sum(1 for name in names if name and name.startswith("GT ")) == pair.scenario.num_objects
    for method_name, _ in methods:
        assert any(name and name.startswith(f"{method_name} ") for name in names), method_name
    assert "simulated" in figure.layout.title.text.lower()


def test_views_are_labelled_as_simulated_and_link_limitations(pair: PairedRun) -> None:
    summary = scenario_summary(pair)
    assert SIMULATED_LABEL in summary
    assert "docs/limitations.md" in LIMITATIONS_NOTE
    assert "not evidence of real-world" in LIMITATIONS_NOTE


def test_format_metric_renders_undefined_as_na() -> None:
    assert format_metric(None) == "N/A"
    assert format_metric(0.12345) == "0.123"
    assert SIMULATED_LABEL.startswith("Simulated data")
