"""End-to-end pipeline integration tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mosaic_perception.cli.main import app
from mosaic_perception.experiment import run_method, run_pair
from mosaic_perception.scenarios import resolve_scenario


def test_paired_run_is_deterministic_and_uses_same_world():
    scenario = resolve_scenario("nominal", seed=7, duration=3.0)
    first = run_pair(scenario)
    second = run_pair(scenario)

    assert first.range_only.result.model_dump() == second.range_only.result.model_dump()
    assert first.fused.result.model_dump() == second.fused.result.model_dump()
    assert [state.model_dump() for state in first.states] == [
        state.model_dump() for state in second.states
    ]
    assert first.range_only.result.matched_samples > 0
    assert first.fused.result.matched_samples > 0
    assert first.range_only.result.scenario_name == "nominal"
    assert first.fused.result.method_name == "fused"


def test_range_only_result_matches_standalone_method_run():
    scenario = resolve_scenario("nominal", seed=9, duration=2.0)
    pair = run_pair(scenario)
    standalone = run_method(scenario, "range_only")
    assert pair.range_only.result.model_dump() == standalone.result.model_dump()


def test_fused_pipeline_applies_vision_to_some_tracks():
    scenario = resolve_scenario("nominal", seed=1, duration=2.0)
    fused = run_method(scenario, "fused")
    associated = [
        observation_id
        for track in fused.tracker.tracks.values()
        for observation_id in track.associated_observations
    ]
    assert any(observation_id.startswith("vision1-") for observation_id in associated)
    assert any(
        any(
            observation_id.startswith("range1-") for observation_id in track.associated_observations
        )
        and any(
            observation_id.startswith("vision1-")
            for observation_id in track.associated_observations
        )
        for track in fused.tracker.tracks.values()
    )


def test_moving_observer_pipeline_has_measurable_accuracy():
    scenario = resolve_scenario("moving_observer", seed=3, duration=4.0)
    pair = run_pair(scenario)
    for record in (pair.range_only, pair.fused):
        result = record.result
        assert result.position_rmse is not None
        assert result.position_rmse < 1.0
        assert result.matched_samples > 50
        assert result.num_confirmed_tracks >= 1


def test_delivery_delay_is_processed_or_counted_not_dropped():
    scenario = resolve_scenario("delivery_delay", seed=2, duration=2.0)
    pair = run_pair(scenario)
    result = pair.range_only.result
    assert result.delivered_observations > 0
    assert result.mean_age_of_information is not None
    assert result.pending_observations >= 0


def test_stale_observations_are_explicitly_rejected():
    scenario = resolve_scenario("stale_rejection", seed=2, duration=2.0)
    pair = run_pair(scenario)
    result = pair.range_only.result
    assert result.rejected_out_of_sequence > 0
    assert result.matched_samples == 0
    assert result.position_rmse is None


def test_evaluate_cli_is_reproducible(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    runner = CliRunner()
    arguments = [
        "evaluate",
        "--scenario",
        "nominal",
        "--seeds",
        "1",
        "--duration",
        "1.0",
        "--num-objects",
        "1",
    ]
    result_one = runner.invoke(app, [*arguments, "--output", str(first)])
    result_two = runner.invoke(app, [*arguments, "--output", str(second)])
    assert result_one.exit_code == 0, result_one.output
    assert result_two.exit_code == 0, result_two.output

    assert (first / "benchmark.json").read_bytes() == (second / "benchmark.json").read_bytes()
    assert (first / "per_seed.csv").read_bytes() == (second / "per_seed.csv").read_bytes()
    assert (first / "report.md").read_bytes() == (second / "report.md").read_bytes()
    payload = json.loads((first / "benchmark.json").read_text())
    assert payload["scenario" if "scenario" in payload else "scenarios"]
    assert payload["protocol"]["seeds"] == [1]


def test_cli_rejects_unknown_scenario(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["evaluate", "--scenario", "nope", "--output", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "unknown scenario" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Mosaic version" in result.output


def test_retrodiction_scenario_runs_and_reports_the_same_delivery_statistics():
    from mosaic_perception.experiment import run_pair

    base = run_pair(resolve_scenario("delivery_delay", seed=2, duration=3.0)).fused.result
    retro = run_pair(
        resolve_scenario("delivery_delay_retrodiction", seed=2, duration=3.0)
    ).fused.result
    # Same sensors, same delays: the same observations are delivered and admitted.
    assert retro.delivered_observations == base.delivered_observations
    assert retro.rejected_out_of_sequence == base.rejected_out_of_sequence
    assert retro.age_samples == base.age_samples
    assert retro.position_rmse is not None
