# Core Validity Audit (pre-fix baseline)

> **Status: historical.** This is a pre-fix record, not a description of the
> current code. For current state see
> [implementation-status.md](implementation-status.md). Statements below that
> are now out of date (for example the V10 row on `track_fragmentation`, which is
> implemented) are catalogued in the
> [comprehensive audit](audits/mosaic-perception-comprehensive-audit.md).

**Branch:** `fix/core-validity` (from published `main` @ `ae518f7`)
**Date:** 2026-10-25

This note records defects reproduced in the published v0.1.0 code before the
correctness repair. Findings were confirmed by reading the implementation and
running the existing tests/benchmark, not taken on trust.

| ID | Severity | Finding | Evidence | Files |
|---|---|---|---|---|
| V1 | P0 | One Hungarian assignment over a combined observation list allows at most **one** observation per track per epoch. Range-bearing and vision observations compete for the same slot, so sequential fusion is impossible in practice. | `associate()` returns `track_id -> [obs_id]` with one column per observation; assignment is one-to-one. | `tracking/association.py`, `tracking/tracker.py` |
| V2 | P0 | In baseline mode, vision observations still enter association and can consume the single assignment slot, then are skipped in the update loop. Baseline is influenced by a sensor it is supposed to ignore. | Update loop `continue`s on vision when `use_vision=False`, after association already assigned it. | `tracking/tracker.py` |
| V3 | P0 | Sensor bearings are **sensor-relative** (`bearing_world - heading`) but EKF measurement models predict **world** bearings. Latent because default observer heading is 0; wrong for any nonzero heading. | Sensor line `bearing_sensor = bearing_world - observer_heading`; `h_bearing` uses `atan2(dy, dx)` only. | `sensors/*`, `tracking/ekf.py` |
| V4 | P0 | Range rate ignores observer velocity, so moving observers produce a biased radial-velocity model. Observer velocity is not even represented. | `range_rate = unit . obj_vel`; `Pose2D` has no velocity. | `sensors/range_bearing.py`, `domain/models.py`, `simulation/world.py` |
| V5 | P0 | Evaluator reuses **final** track states for every historical timestamp, matches tracks independently (object can be credited to several tracks), and hard-codes 95% coverage to 0.85. | `evaluate()` receives final `tracks` dict; nested loop picks nearest object per track; `position_coverage_95 = 0.85`. | `evaluation/metrics.py` |
| V6 | P1 | Delayed observations are generated then silently discarded when `delivery_time > current_time`; no queue. | CLI generates per step and calls `process_observations` once; `valid_obs` filters future deliveries which are never revisited. | `cli/main.py`, `tracking/tracker.py` |
| V7 | P1 | `SensorConfig.frame_rate` is never used; sensors sample every simulation step. | No reference to `frame_rate` in sensor code. | `sensors/*` |
| V8 | P1 | `--scenario` is a label only; all scenario names run identical dynamics. | CLI ignores scenario except in metadata. | `cli/main.py` |
| V9 | P1 | Hit counting increments once per epoch even when **no** observation was applied; broad `except Exception: continue` silently swallows update failures. | Update loop increments `track.hits` outside per-observation success tracking. | `tracking/tracker.py` |
| V10 | P2 | Uncomputed metrics (`precision`, `recall`, `identity_switches`, `num_false_tracks`, `track_fragmentation`) default to `0`/`None` and are reported as if measured. | `EvaluationResult` defaults; evaluator never sets them. | `evaluation/metrics.py`, `domain/models.py` |
| V11 | P2 | CI runs `ruff check` and stops; tests never execute. Lock file absent; dependency resolution unpinned. | `.github/workflows/ci.yml`, no `uv.lock`. | CI, packaging |
| V12 | P2 | README documents `mosaic evaluate`, which is not implemented. | CLI has `run`, `compare`, `benchmark`, `version`. | `README.md` |

## Baseline commands

```
PYTHONPATH=src python3 -m pytest -q        -> 14 passed
PYTHONPATH=src ruff check src tests         -> 56 errors
PYTHONPATH=src ruff format --check src tests -> 20 files already formatted
benchmark (nominal, seeds 1-5, 5 s)         -> range 0.870 ± 0.183 m, fused 0.912 ± 0.138 m
```

The previous "fusion helps / hurts" numbers were produced with V1–V5 present and
are therefore not a valid multi-sensor fusion comparison. All benchmark values
are regenerated after the repair; no old number is preserved for continuity.

## Resolution status (local `fix/core-validity` branch, unreleased)

| ID | Status | Resolution and regression evidence |
|---|---|---|
| V1 | Resolved | Association is now performed independently per measurement group with a gated Hungarian assignment. One track may receive one range-bearing and one vision observation in the same epoch, applied sequentially. Tests: `test_one_track_receives_both_modalities_in_one_epoch`, `test_sequential_fusion_reduces_covariance_relative_to_range_only`, `test_one_observation_cannot_update_two_tracks`. |
| V2 | Resolved | `range_only` does not enqueue vision observations at all. Test: `test_range_only_mode_ignores_vision_completely` (state, covariance, hit/miss and delivery counts unchanged). |
| V3 | Resolved | One convention: sensor-frame bearing = wrapped world line-of-sight minus observer heading, used by sensors, EKF prediction/Jacobians, gating and initiation. Tests: `test_bearing_is_sensor_relative_with_nonzero_heading`, `test_sensor_reports_sensor_frame_measurements_exactly`, finite-difference Jacobian tests. |
| V4 | Resolved | `Pose2D` carries velocity; range rate uses object velocity minus observer velocity. Tests: `test_range_rate_is_relative_to_observer_velocity`, `test_range_rate_stationary_object_with_moving_observer`, `test_circle_observer_velocity_and_heading`, end-to-end moving-observer tests. |
| V5 | Resolved | Evaluation uses per-epoch `TrackSnapshot` records, one-to-one gated Hungarian matching per timestamp, confirmed/coasting only, and χ²(2, 0.95)=5.991 coverage. Tests: `test_exact_rmse_matching_and_coverage`, `test_duplicate_tracks_are_matched_one_to_one`, `test_coverage_uses_chi_square_threshold_not_fixed_value`, `test_false_track_is_reported_without_inflating_recall`, `test_identity_switch_is_counted_when_track_id_changes_for_same_object`. |
| V6 | Resolved as an explicit bounded-staleness policy | A pending queue holds observations until delivery. Those older than `dt + 1e-6` are rejected with a logged `stale` reason and counted in `rejected_out_of_sequence`; in-flight observations are reported as `pending_observations`. Full historical replay is explicitly not implemented. Tests: `test_future_delivery_is_queued_not_dropped`, `test_observation_older_than_one_epoch_is_rejected_and_counted`, `test_out_of_sequence_observations_are_explicitly_rejected`. |
| V7 | Resolved | Sensors honour `frame_rate` instead of emitting every simulation step. Test: `test_sensor_frame_rate_is_honored`. |
| V8 | Resolved | Scenario presets resolve real sensor/observer overrides; CLI validates names. There are 10 presets, including `delivery_delay`, `out_of_sequence` and `moving_observer`. Tests: `test_all_presets_resolve_with_two_sensor_groups`, `test_scenario_overrides_are_real_and_isolated`, `test_moving_observer_preset_uses_circle`. |
| V9 | Resolved | Hits increment only for tracks with at least one successfully applied observation in the epoch; otherwise misses increment. Rejected/failed updates do not count as hits or reset misses. Broad exception swallowing was removed; update failures are logged and counted. Tests: `test_rejected_observation_does_not_count_as_hit_or_reset_misses`, `test_failed_update_does_not_count_as_hit`, `test_track_lifecycle_confirm_coast_delete`. |
| V10 | Resolved | Recall, precision, identity switches and false tracks are computed with explicit denominators and sample counts. `track_fragmentation` is explicitly unsupported (`None`/`N/A`), not defaulted to zero. Tests: `test_exact_rmse_matching_and_coverage`, `test_missed_object_lowers_recall`, `test_no_valid_matches_reports_none_for_undefined_rmse_and_coverage`, `test_observation_statistics_are_propagated`. |
| V11 | Resolved | `uv.lock` is committed; CI uses `uv sync --locked --all-extras`, then Ruff check, format check and `pytest`. The workflow also runs a CLI smoke test. |
| V12 | Resolved | `mosaic evaluate` is implemented and writes the same canonical JSON/CSV/Markdown artifacts as `benchmark`. Test: `test_evaluate_cli_is_reproducible`; README now documents implemented behavior. |

## Current verification (local branch)

```
uv run ruff check src tests                  -> pass
uv run ruff format --check src tests         -> pass
uv run pytest                                -> 77 passed
uv run mosaic evaluate --scenario nominal --seeds 1 \
  --duration 1.0 --num-objects 1             -> writes benchmark.json, per_seed.csv, report.md
benchmark --scenario all --seeds 1-5 --duration 10.0
                                             -> 10 scenarios, development seeds only
```

The held-out seed range 25–49 was **not** run. The regenerated benchmark is a
development result and makes no held-out or real-world claim. Old v0.1.0
numbers are not preserved as a baseline.
