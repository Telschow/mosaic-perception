"""Report rendering tested on a hand-built payload (no benchmark run)."""

from __future__ import annotations

from mosaic_perception.reporting import format_number, render_report


def _aggregate(rmse: float | None, **extra):
    base = {
        "num_seeds": 1,
        "position_rmse": rmse,
        "position_rmse_std": 0.0 if rmse is not None else None,
        "velocity_rmse": 0.1,
        "recall": 1.0,
        "precision": 0.9,
        "position_coverage_95": 0.8,
        "matched_samples": 10.0,
        "ground_truth_samples": 10.0,
        "num_unmatched_confirmed_tracks": 1.0,
        "num_duplicate_tracks": 1.0,
        "track_fragmentation": 0.0,
        "class_accuracy": None,
        "num_duplicate_tracks_gate_1m": 0.0,
        "num_duplicate_tracks_gate_2m": 1.0,
        "num_duplicate_tracks_gate_3m": 1.0,
    }
    base.update(extra)
    return base


def _payload():
    return {
        "schema_version": 2,
        "command": "benchmark",
        "code": {"package_version": "0.0.0", "git_commit": "abc123"},
        "protocol": {
            "matching_gate_m": 2.0,
            "seed_group": "development",
            "seeds": [1],
            "duration_s": 1.0,
            "dt_s": 0.1,
            "num_objects": 1,
            "methods": ["range_only", "fused"],
        },
        "scenarios": [
            {
                "scenario": {"name": "toy"},
                "runs": [
                    {
                        "seed": 1,
                        "range_only": {"position_rmse": 0.3},
                        "fused": {"position_rmse": 0.2},
                    }
                ],
                "paired_differences": {
                    "position_rmse": {"n": 5, "mean": -0.1, "ci95_low": -0.2, "ci95_high": 0.0},
                    "precision": {"n": 1, "mean": 0.05, "ci95_low": None, "ci95_high": None},
                    "recall": {"n": 0, "mean": None, "ci95_low": None, "ci95_high": None},
                },
                "aggregate": {
                    "range_only": _aggregate(0.3),
                    "fused": _aggregate(0.2, vision_generated=5.0, vision_applied=4.0),
                },
            }
        ],
    }


def test_render_report_contains_headers_provenance_and_rows():
    text = render_report(_payload())
    assert text.startswith("# Mosaic Benchmark Report")
    assert "- Git commit: `abc123`" in text
    assert "- Seed group: development" in text
    assert "| toy | range_only | 0.300 ± 0.000 |" in text
    assert "| toy | fused | 0.200 ± 0.000 |" in text
    assert "## Duplicate-track sensitivity to the matching gate" in text


def test_render_report_is_deterministic():
    assert render_report(_payload()) == render_report(_payload())


def test_undefined_values_render_as_na_not_zero():
    payload = _payload()
    payload["scenarios"][0]["aggregate"]["fused"]["position_rmse"] = None
    payload["scenarios"][0]["aggregate"]["fused"]["position_rmse_std"] = None
    text = render_report(payload)
    assert "| toy | fused | N/A |" in text
    assert format_number(None) == "N/A"
    assert format_number(0.5, 1) == "0.5"


def test_paired_difference_section_renders_intervals_and_na():
    text = render_report(_payload())
    assert "## Paired differences (fused minus range-only)" in text
    assert "| toy | position_rmse | 5 | -0.100 | [-0.200, +0.000] |" in text
    assert "| toy | precision | 1 | +0.050 | N/A |" in text
    assert "| toy | recall | 0 | N/A | N/A |" in text


def _with_paired(rmse_row, precision_row=None):
    payload = _payload()
    payload["protocol"]["paired_comparison"] = {"baseline": "range_only", "treatment": "fused"}
    paired = payload["scenarios"][0]["paired_differences"]
    paired["position_rmse"] = rmse_row
    if precision_row is not None:
        paired["precision"] = precision_row
    return payload


def _interval(mean, low, high, n=25):
    return {"n": n, "mean": mean, "ci95_low": low, "ci95_high": high}


def test_findings_count_a_win_only_when_the_paired_interval_excludes_zero():
    spanning = render_report(_with_paired(_interval(-0.05, -0.20, 0.10)))
    assert "paired interval excludes zero in favour of fusion in 0 scenario(s)" in spanning
    assert "includes zero (or has fewer than two seeds) in 1 scenario(s)" in spanning

    favourable = render_report(_with_paired(_interval(-0.05, -0.08, -0.02)))
    assert "in favour of fusion in 1 scenario(s)" in favourable


def test_findings_count_a_loss_when_the_interval_is_entirely_positive_rmse_difference():
    text = render_report(_with_paired(_interval(0.06, 0.04, 0.08)))
    assert "against fusion in 1 scenario(s)" in text


def test_precision_tally_uses_the_paired_interval_too():
    text = render_report(_with_paired(_interval(-0.05, -0.08, -0.02), _interval(-0.1, -0.2, -0.05)))
    assert "Fused precision is lower (interval excludes zero) in 1" in text


def test_seed_prose_follows_the_seed_group():
    development = render_report(_payload())
    assert "development seeds" in development
    assert "no held-out claim is made" in development

    other = _payload()
    other["protocol"]["seed_group"] = "custom_or_held_out"
    other["protocol"]["seeds"] = [30, 31]
    text = render_report(other)
    assert "includes seeds outside the development range" in text
    assert "no held-out claim is made" not in text


def test_consistency_table_shows_pooled_values_intervals_and_position():
    payload = _payload()
    fused = payload["scenarios"][0]["aggregate"]["fused"]
    fused.update(
        anees_position_per_dof_pooled=1.02,
        anees_position_per_dof_pooled_low=0.95,
        anees_position_per_dof_pooled_high=1.05,
        anees_velocity_per_dof_pooled=1.80,
        anees_velocity_per_dof_pooled_low=0.90,
        anees_velocity_per_dof_pooled_high=1.10,
        anis_pooled=0.70,
        anis_pooled_low=0.90,
        anis_pooled_high=1.10,
        nees_samples=40.0,
        nis_updates=55.0,
        unmatched_ground_truth_samples=3.0,
    )
    text = render_report(payload)
    assert "## Estimator consistency (NEES and NIS)" in text
    assert "1.020 [0.950, 1.050] within" in text
    assert "1.800 [0.900, 1.100] above" in text
    assert "0.700 [0.900, 1.100] below" in text
    # The range-only row has no pooled values: N/A, not zero.
    assert "| toy | range_only | N/A | N/A | N/A |" in text


def test_paired_section_states_which_direction_favours_fusion():
    text = render_report(_payload())
    assert "Lower is" in text and "better for the RMSE metrics and GOSPA" in text
    assert "MOTA, IDF1 and GOSPA (interval excludes zero)" in text
