# Scenarios

Mosaic has 15 implemented presets. A scenario changes sensor parameters and/or
the observer trajectory; world generation, tracker management and evaluation
logic stay identical so that comparisons between scenarios and methods remain
meaningful. Every preset has a stated hypothesis and a list of metrics that can
reveal its failure mode; hypotheses are not automatically confirmed.

All presets resolve to two sensor groups:

- `range_bearing`: frame rate 10 Hz, detection probability 0.95, false-alarm
  rate 0.01, noise standard deviations range 0.5 m, bearing 0.01 rad,
  range rate 0.1 m/s;
- `vision_bearing`: frame rate 10 Hz, detection probability 0.90, false-alarm
  rate 0.02, bearing noise 0.005 rad.

## Implemented presets

| Name | What changes | Stated hypothesis / expected failure mode |
|---|---|---|
| `nominal` | Baseline noise and occasional misses | Vision bearings may reduce position error relative to the range-bearing baseline. |
| `vision_dropout` | Vision detection probability 0.45 | Sparse vision updates reduce any fusion benefit; fused may approach the baseline. |
| `range_dropout` | Range detection probability 0.55 | Vision cannot initiate tracks, so the fused method may not recover the missing range detections. |
| `measurement_bias` | Range bias +1.5 m, range-rate bias +0.3 m/s | Bias degrades the baseline and is only partially corrected by bearings; errors remain biased. |
| `delivery_delay` | Delivery delay 0.05 ± 0.02 s | A bounded one-epoch delay is queued and applied at delivery; AoI rises instead of observations being dropped. |
| `out_of_sequence` | Delivery delay 0.25 ± 0.05 s, older than one epoch | Stale observations are rejected and counted; accuracy becomes `N/A`, not silently computed from stale data. |
| `false_observations` | Range false-alarm rate 1.0, vision 3.0 per step | False alarms create spurious tentative tracks and can steal associations; precision and false tracks should worsen. |
| `uncertainty_miscalibration` | Reported covariance 20× too small (scale 0.05) | Overconfident measurements are over-trusted; empirical 95% coverage falls below nominal. |
| `sensor_disagreement_large_bias` | Vision bearing bias 0.12 rad (well outside 1-DOF gate), range unbiased | A sufficiently large bias should be rejected by the gate rather than corrupting the fused estimate. |
| `sensor_disagreement_within_gate_low` | Preregistered sweep value: vision bearing bias 0.010 rad (within 1-DOF gate), range unbiased | A bias that passes the gate will be fused and may degrade accuracy; measures the acceptance/degradation trade-off. |
| `sensor_disagreement_within_gate` | Vision bearing bias 0.015 rad (within 1-DOF gate), range unbiased | A bias that passes the gate will be fused and may degrade accuracy; measures the acceptance/degradation trade-off. |
| `sensor_disagreement_within_gate_high` | Preregistered sweep value: vision bearing bias 0.020 rad (within 1-DOF gate), range unbiased | A bias that passes the gate will be fused and may degrade accuracy; measures the acceptance/degradation trade-off. |
| `crossing_targets` | Constant-velocity targets at 2 m/s on distinct headings crossing at mid-run; adjacent targets 0.5 m apart at the crossing | Near-coincident targets make association ambiguous: identity switches, unmatched confirmed tracks and fragmentation can rise. Applies to a single crossing of a few targets under GNN association. |
| `dense_clutter` | Poisson false alarms per frame: 4.0 (range-bearing, 4x `false_observations`), 8.0 (vision, about 2.7x `false_observations`) | Clutter inside the gates produces spurious candidates; gate rejection is not a defence against clutter that falls inside the gate. |
| `moving_observer` | Observer follows a circular trajectory with changing heading and velocity | Correct sensor-frame models and observer-velocity handling keep error comparable to the static case. |

Random seed, duration, step size and object count are supplied by the caller;
they are not part of the preset identity.

## Usage

```bash
uv run mosaic run --scenario nominal --seed 42
uv run mosaic compare --scenario nominal --seeds 1,2,3
uv run mosaic benchmark --scenario all --seeds 0-24 --duration 10.0
```

In the Streamlit app, scenarios are selected from the sidebar. The checked-in
benchmark covers all 15 presets with all development seeds 0–24; held-out seeds
25–49 are reserved and were not run.
