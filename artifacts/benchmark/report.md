# Mosaic Benchmark Report

## Experiment
- Scenario: nominal
- Seeds: [1, 2, 3, 4, 5]
- Duration: 5.0 s
- Methods: range_only, fused
- Synthetic 2D simulation with simplified sensor models

## Per-seed results
| Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused - Range) |
|---|---|---|---|
| 1 | 1.012 | 0.893 | -0.119 |
| 2 | 1.144 | 1.132 | -0.012 |
| 3 | 0.651 | 0.698 | +0.046 |
| 4 | 0.721 | 0.928 | +0.207 |
| 5 | 0.820 | 0.910 | +0.090 |

## Aggregate (mean ± std)
- Range-only position RMSE: 0.870 ± 0.183
- Fused position RMSE: 0.912 ± 0.138

## Interpretation
Fusion does not universally improve performance. Results depend on scenario, seed, data association, timing, and calibration. This is a synthetic educational benchmark.

## Limitations
- Synthetic 2D only; simplified sensor models (no raw images/waveforms)
- Vision-only track initiation not performed (bearing alone insufficient)
- Observer pose handled via context; timing/out-of-sequence handling limited in v0.1
- Results do not imply real-world or hardware performance
