"""One declaration per metric drives CSV, aggregates, report and docs."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from mosaic_perception.cli.main import _aggregate, _write_per_seed_csv
from mosaic_perception.domain.models import EvaluationResult
from mosaic_perception.evaluation.registry import (
    DUPLICATE_SENSITIVITY_GATES_M,
    METRIC_DIGITS,
    POOLED_RATIOS,
    RESULT_METRICS,
    MetricSpec,
    duplicate_gate_metric,
    gate_label,
    metric_value,
)
from mosaic_perception.reporting import render_report
from mosaic_perception.reporting.tables import RESULTS_TABLE, Column, TableSpec

DOCS = Path(__file__).resolve().parents[2] / "docs" / "metrics.md"


class _ResultWithDummy(EvaluationResult):
    dummy_metric: float | None = None


def _result(seed: int, dummy: float | None) -> _ResultWithDummy:
    return _ResultWithDummy(
        scenario_name="toy", seed=seed, method_name="fused", dummy_metric=dummy, position_rmse=0.1
    )


def test_every_declared_metric_exists_on_the_result_model():
    result = EvaluationResult(scenario_name="x", seed=1, method_name="fused")
    for spec in RESULT_METRICS:
        metric_value(result, spec.name)  # raises AttributeError if undeclared on the model


def test_metric_names_are_unique():
    names = [spec.name for spec in RESULT_METRICS]
    assert len(names) == len(set(names))


def test_every_declared_metric_is_documented():
    text = DOCS.read_text()
    gate_names = {duplicate_gate_metric(g) for g in DUPLICATE_SENSITIVITY_GATES_M}
    for spec in RESULT_METRICS:
        if spec.name in gate_names:
            continue  # documented together as num_duplicate_tracks_gate_*
        assert f"`{spec.name}`" in text, f"{spec.name} is not documented in docs/metrics.md"
    assert "num_duplicate_tracks_gate_" in text
    for ratio in POOLED_RATIOS:
        assert f"`{ratio.name}`" in text, f"{ratio.name} is not documented in docs/metrics.md"


def test_gate_labels_are_stable():
    assert gate_label(1.0) == "1m"
    assert gate_label(1.5) == "1p5m"
    assert duplicate_gate_metric(3.0) == "num_duplicate_tracks_gate_3m"


def test_a_new_declaration_appears_in_aggregate_csv_and_report(tmp_path):
    metrics = (*RESULT_METRICS, MetricSpec("dummy_metric", 2))
    results = [_result(1, 1.0), _result(2, 3.0)]

    aggregate = _aggregate(results, metrics)
    assert aggregate["dummy_metric"] == pytest.approx(2.0)
    assert aggregate["dummy_metric_std"] == pytest.approx(1.4142135623730951)

    rows = [
        {"scenario": "toy", "seed": r.seed, "method": "fused", "dummy_metric": r.dummy_metric}
        for r in results
    ]
    path = tmp_path / "per_seed.csv"
    _write_per_seed_csv(path, rows, metrics)
    with path.open() as handle:
        reader = csv.DictReader(handle)
        assert "dummy_metric" in reader.fieldnames
        assert [row["dummy_metric"] for row in reader] == ["1.0", "3.0"]

    table = TableSpec(
        heading="Extra",
        intro=("A dummy metric.",),
        columns=(*RESULTS_TABLE.columns, Column("Dummy", "dummy_metric", 2)),
        primary=True,
    )
    payload = {
        "code": {"package_version": "0", "git_commit": None},
        "protocol": {
            "methods": ["fused"],
            "seeds": [1, 2],
            "seed_group": "development",
            "matching_gate_m": 2.0,
            "duration_s": 1.0,
            "dt_s": 0.1,
            "num_objects": 1,
        },
        "scenarios": [{"scenario": {"name": "toy"}, "runs": [], "aggregate": {"fused": aggregate}}],
    }
    text = render_report(payload, tables=(table,))
    assert "| Dummy |" in text
    assert "| toy | fused |" in text and "| 2.00 |" in text


def test_metric_digits_cover_every_declared_metric_and_ratio():
    for spec in RESULT_METRICS:
        assert METRIC_DIGITS[spec.name] == spec.digits
    for ratio in POOLED_RATIOS:
        assert ratio.name in METRIC_DIGITS


def test_pooled_chi_square_interval_matches_the_chi_square_quantiles():
    from scipy.stats import chi2

    results = [
        EvaluationResult(
            scenario_name="x",
            seed=seed,
            method_name="fused",
            nees_samples=n,
            nees_position_sum=total,
            nees_velocity_sum=total,
        )
        for seed, (n, total) in enumerate([(10, 18.0), (30, 66.0)])
    ]
    aggregate = _aggregate(results)
    samples, total = 40, 84.0
    dof = 2 * samples
    assert aggregate["anees_position_per_dof_pooled"] == pytest.approx(total / dof)
    assert aggregate["anees_position_per_dof_pooled_low"] == pytest.approx(
        chi2.ppf(0.025, dof) / dof
    )
    assert aggregate["anees_position_per_dof_pooled_high"] == pytest.approx(
        chi2.ppf(0.975, dof) / dof
    )
    assert aggregate["anees_position_per_dof_pooled_dof"] == dof


def test_pooled_nis_uses_the_summed_degrees_of_freedom():
    from scipy.stats import chi2

    results = [
        EvaluationResult(
            scenario_name="x",
            seed=1,
            method_name="fused",
            nis_sum=30.0,
            nis_dof_sum=25,
            nis_updates=10,
        ),
        EvaluationResult(
            scenario_name="x",
            seed=2,
            method_name="fused",
            nis_sum=20.0,
            nis_dof_sum=15,
            nis_updates=8,
        ),
    ]
    aggregate = _aggregate(results)
    assert aggregate["anis_pooled"] == pytest.approx(50.0 / 40)
    assert aggregate["anis_pooled_low"] == pytest.approx(chi2.ppf(0.025, 40) / 40)
    assert aggregate["anis_pooled_high"] == pytest.approx(chi2.ppf(0.975, 40) / 40)


def test_pooled_chi_square_is_undefined_without_samples():
    result = EvaluationResult(scenario_name="x", seed=1, method_name="fused")
    aggregate = _aggregate([result])
    assert aggregate["anees_position_per_dof_pooled"] is None
    assert aggregate["anees_position_per_dof_pooled_low"] is None
    assert aggregate["anis_pooled"] is None
