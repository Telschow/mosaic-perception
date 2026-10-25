# Mosaic Benchmark Report

This report is generated from the code in this repository. It contains no
hand-edited numbers and no wall-clock timestamps, so repeated runs with the
same seeds and commit are byte-identical.

## Code and protocol

- Package version: `0.1.0`
- Git commit: `6859fbdd3cf0538ceabdd22a99ad9185ebe30505`
- Seeds: 1, 2, 3, 4, 5
- Seed group: development
- Duration: 10.0 s at dt=0.1 s
- Objects per world: 3
- Methods: range-only (range-bearing sensor only) and fused (range-bearing + vision bearing)
- Paired: same world states and the same range-sensor random stream per seed; the fused run only adds vision observations.
- Evaluation matching gate: 2.00 m, one-to-one Hungarian assignment per timestamp.
- Accuracy denominators: matched sample pairs. Recall denominator: all ground-truth object samples. Precision denominator: all confirmed/coasting track samples.
- 95% position coverage threshold: chi-square(2, 0.95) = 5.991.

## Aggregate results

Values are mean ± sample standard deviation across seeds. `N/A` means the
metric was not defined for any seed (for example, no matched tracks); it is
never a fabricated zero.

| Scenario | Method | Pos RMSE (m) | Vel RMSE (m/s) | Recall | Precision | Cov95 | Matched/GT (mean) | Unmatched confirmed tracks | Duplicate tracks | Fragmentation |
|---|---|---|---|---|---|---|---|---|---|---|
| delivery_delay | range_only | 0.279 ± 0.050 | 0.341 | 0.969 | 0.808 | 0.502 | 294/303 | 2.6 | 2.6 | 0.0 |
| delivery_delay | fused | 0.235 ± 0.015 | 0.278 | 0.970 | 0.671 | 0.463 | 294/303 | 4.0 | 4.0 | 0.0 |
| false_observations | range_only | 0.223 ± 0.051 | 0.311 | 0.979 | 0.840 | 0.865 | 297/303 | 2.0 | 2.0 | 0.2 |
| false_observations | fused | 0.195 ± 0.038 | 0.252 | 0.980 | 0.613 | 0.830 | 297/303 | 13.0 | 5.8 | 0.0 |
| measurement_bias | range_only | 1.579 ± 0.027 | 0.550 | 0.908 | 0.730 | 0.004 | 275/303 | 1.6 | 0.6 | 4.8 |
| measurement_bias | fused | 1.539 ± 0.027 | 0.575 | 0.931 | 0.593 | 0.021 | 282/303 | 2.2 | 0.8 | 3.8 |
| moving_observer | range_only | 0.231 ± 0.046 | 0.334 | 0.974 | 0.811 | 0.831 | 295/303 | 3.4 | 3.4 | 0.2 |
| moving_observer | fused | 0.206 ± 0.072 | 0.272 | 0.978 | 0.707 | 0.786 | 296/303 | 4.8 | 4.8 | 0.0 |
| nominal | range_only | 0.229 ± 0.024 | 0.317 | 0.977 | 0.804 | 0.836 | 296/303 | 2.4 | 2.4 | 0.2 |
| nominal | fused | 0.220 ± 0.019 | 0.270 | 0.980 | 0.669 | 0.802 | 297/303 | 4.8 | 4.8 | 0.0 |
| out_of_sequence | range_only | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A |
| out_of_sequence | fused | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A |
| range_dropout | range_only | 0.262 ± 0.043 | 0.380 | 0.867 | 0.963 | 0.906 | 263/303 | 0.4 | 0.4 | 5.2 |
| range_dropout | fused | 0.246 ± 0.074 | 0.312 | 0.970 | 0.782 | 0.876 | 294/303 | 2.4 | 2.2 | 0.4 |
| sensor_disagreement_large_bias | range_only | 0.229 ± 0.024 | 0.317 | 0.977 | 0.804 | 0.836 | 296/303 | 2.4 | 2.4 | 0.2 |
| sensor_disagreement_large_bias | fused | 0.230 ± 0.041 | 0.316 | 0.978 | 0.750 | 0.824 | 296/303 | 3.4 | 3.2 | 0.2 |
| sensor_disagreement_within_gate | range_only | 0.229 ± 0.024 | 0.317 | 0.977 | 0.804 | 0.836 | 296/303 | 2.4 | 2.4 | 0.2 |
| sensor_disagreement_within_gate | fused | 0.285 ± 0.043 | 0.427 | 0.980 | 0.524 | 0.497 | 297/303 | 3.6 | 3.6 | 0.0 |
| sensor_disagreement_within_gate_high | range_only | 0.229 ± 0.024 | 0.317 | 0.977 | 0.804 | 0.836 | 296/303 | 2.4 | 2.4 | 0.2 |
| sensor_disagreement_within_gate_high | fused | 0.293 ± 0.053 | 0.475 | 0.979 | 0.518 | 0.534 | 297/303 | 5.4 | 5.4 | 0.0 |
| sensor_disagreement_within_gate_low | range_only | 0.229 ± 0.024 | 0.317 | 0.977 | 0.804 | 0.836 | 296/303 | 2.4 | 2.4 | 0.2 |
| sensor_disagreement_within_gate_low | fused | 0.268 ± 0.049 | 0.360 | 0.980 | 0.550 | 0.440 | 297/303 | 5.2 | 5.2 | 0.0 |
| uncertainty_miscalibration | range_only | 0.432 ± 0.056 | 0.573 | 0.488 | 0.845 | 0.124 | 148/303 | 1.8 | 1.8 | 15.6 |
| uncertainty_miscalibration | fused | 0.407 ± 0.045 | 0.637 | 0.940 | 0.432 | 0.139 | 285/303 | 30.6 | 30.0 | 3.4 |
| vision_dropout | range_only | 0.229 ± 0.024 | 0.317 | 0.977 | 0.804 | 0.836 | 296/303 | 2.4 | 2.4 | 0.2 |
| vision_dropout | fused | 0.223 ± 0.032 | 0.301 | 0.979 | 0.685 | 0.804 | 297/303 | 5.8 | 5.8 | 0.0 |

## Class estimate accuracy

Correct / classified over matched samples where both the track's class estimate
and the ground-truth class are known. Range-only runs carry no class
information, so their accuracy is `N/A`, not zero. `Classified` is the mean
number of such samples per seed, out of the matched samples in the results table.
`Class accuracy` is an unweighted mean of per-seed accuracies (seeds with no
classified sample are excluded). `Pooled` is total correct / total classified
over all seeds, and `Classified fraction` is classified / matched samples, so a
method that classifies rarely cannot look accurate on its own: read the three
together.

| Scenario | Method | Class accuracy | Pooled | Classified fraction | Classified (mean) |
|---|---|---|---|---|---|
| delivery_delay | range_only | N/A | N/A | 0.000 | 0.0 |
| delivery_delay | fused | 1.000 | 1.000 | 0.728 | 214.0 |
| false_observations | range_only | N/A | N/A | 0.000 | 0.0 |
| false_observations | fused | 1.000 | 1.000 | 0.719 | 213.6 |
| measurement_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| measurement_bias | fused | 0.996 | 0.995 | 0.717 | 202.4 |
| moving_observer | range_only | N/A | N/A | 0.000 | 0.0 |
| moving_observer | fused | 0.999 | 0.999 | 0.735 | 217.8 |
| nominal | range_only | N/A | N/A | 0.000 | 0.0 |
| nominal | fused | 1.000 | 1.000 | 0.723 | 214.8 |
| out_of_sequence | range_only | N/A | N/A | N/A | 0.0 |
| out_of_sequence | fused | N/A | N/A | N/A | 0.0 |
| range_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| range_dropout | fused | 1.000 | 1.000 | 0.733 | 215.4 |
| sensor_disagreement_large_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_large_bias | fused | 0.333 | 0.043 | 0.047 | 13.8 |
| sensor_disagreement_within_gate | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate | fused | 0.981 | 0.973 | 0.668 | 198.2 |
| sensor_disagreement_within_gate_high | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_high | fused | 0.972 | 0.961 | 0.599 | 177.8 |
| sensor_disagreement_within_gate_low | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_low | fused | 0.979 | 0.971 | 0.708 | 210.2 |
| uncertainty_miscalibration | range_only | N/A | N/A | 0.000 | 0.0 |
| uncertainty_miscalibration | fused | 1.000 | 1.000 | 0.703 | 200.2 |
| vision_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| vision_dropout | fused | 1.000 | 1.000 | 0.719 | 213.2 |

## Duplicate-track sensitivity to the matching gate

Mean number of duplicate tracks per seed when the evaluation matching gate is
1.0, 2.0 or 3.0 m. The three gates were chosen before running (see the project issue
tracker). The 2.0 m column is the headline gate used everywhere else in this
report when it is the evaluator gate; the others show how much the
duplicate count depends on that choice, not which gate is correct.

| Scenario | Method | 1.0 m | 2.0 m | 3.0 m |
|---|---|---|---|---|
| delivery_delay | range_only | 2.6 | 2.6 | 2.6 |
| delivery_delay | fused | 3.6 | 4.0 | 4.0 |
| false_observations | range_only | 2.0 | 2.0 | 2.0 |
| false_observations | fused | 4.8 | 5.8 | 6.2 |
| measurement_bias | range_only | 0.0 | 0.6 | 1.2 |
| measurement_bias | fused | 0.0 | 0.8 | 2.0 |
| moving_observer | range_only | 3.4 | 3.4 | 3.4 |
| moving_observer | fused | 3.8 | 4.8 | 4.8 |
| nominal | range_only | 2.4 | 2.4 | 2.4 |
| nominal | fused | 4.4 | 4.8 | 4.8 |
| out_of_sequence | range_only | 0.0 | 0.0 | 0.0 |
| out_of_sequence | fused | 0.0 | 0.0 | 0.0 |
| range_dropout | range_only | 0.4 | 0.4 | 0.4 |
| range_dropout | fused | 1.8 | 2.2 | 2.2 |
| sensor_disagreement_large_bias | range_only | 2.4 | 2.4 | 2.4 |
| sensor_disagreement_large_bias | fused | 3.0 | 3.2 | 3.2 |
| sensor_disagreement_within_gate | range_only | 2.4 | 2.4 | 2.4 |
| sensor_disagreement_within_gate | fused | 3.6 | 3.6 | 3.6 |
| sensor_disagreement_within_gate_high | range_only | 2.4 | 2.4 | 2.4 |
| sensor_disagreement_within_gate_high | fused | 4.2 | 5.4 | 5.4 |
| sensor_disagreement_within_gate_low | range_only | 2.4 | 2.4 | 2.4 |
| sensor_disagreement_within_gate_low | fused | 4.4 | 5.2 | 5.2 |
| uncertainty_miscalibration | range_only | 1.8 | 1.8 | 1.8 |
| uncertainty_miscalibration | fused | 26.8 | 30.0 | 30.6 |
| vision_dropout | range_only | 2.4 | 2.4 | 2.4 |
| vision_dropout | fused | 5.0 | 5.8 | 5.8 |

## Vision observation acceptance (fused method)

Mean per seed. `Generated` = produced by vision sensors; `Delivered` = left the
pending queue (generated minus those still pending at the end); `Gate-rejected` =
at least one track was evaluated and none passed the chi-square gate;
`Lost competition` = passed the gate for some track but lost the one-to-one
assignment; `Other unassigned` = no evaluable candidate track; `Stale/invalid` =
rejected outside association; `Applied` = used in a track update.

| Scenario | Generated | Delivered | Gate-rejected | Lost competition | Other unassigned | Stale/invalid | Applied |
|---|---|---|---|---|---|---|---|
| delivery_delay | 275.4 | 272.6 | 14.0 | 0.6 | 0.0 | 1.0 | 257.0 |
| false_observations | 572.6 | 572.6 | 276.0 | 3.2 | 0.0 | 0.0 | 293.4 |
| measurement_bias | 276.4 | 276.4 | 16.0 | 0.0 | 0.0 | 0.0 | 260.4 |
| moving_observer | 276.4 | 276.4 | 17.6 | 0.2 | 0.0 | 0.0 | 258.6 |
| nominal | 276.4 | 276.4 | 14.2 | 0.0 | 0.0 | 0.0 | 262.2 |
| out_of_sequence | 275.4 | 267.2 | 0.0 | 0.0 | 0.0 | 267.0 | 0.2 |
| range_dropout | 276.4 | 276.4 | 19.4 | 0.2 | 0.4 | 0.0 | 256.4 |
| sensor_disagreement_large_bias | 276.4 | 276.4 | 253.8 | 0.4 | 0.0 | 0.0 | 22.2 |
| sensor_disagreement_within_gate | 276.4 | 276.4 | 24.2 | 0.2 | 0.0 | 0.0 | 252.0 |
| sensor_disagreement_within_gate_high | 276.4 | 276.4 | 50.8 | 0.2 | 0.0 | 0.0 | 225.4 |
| sensor_disagreement_within_gate_low | 276.4 | 276.4 | 17.8 | 0.0 | 0.0 | 0.0 | 258.6 |
| uncertainty_miscalibration | 276.4 | 276.4 | 35.2 | 0.0 | 0.0 | 0.0 | 241.2 |
| vision_dropout | 137.2 | 137.2 | 5.4 | 0.0 | 0.0 | 0.0 | 131.8 |

## Delivery statistics

Means across seeds where applicable. `Delivered` counts observations removed
from the pending queue, including those subsequently rejected. `Rejected`
includes stale and invalid observations; gate-unmatched detections are not
counted as rejected because range detections may initiate tracks. Unused
vision detections are broken down in the vision acceptance table above.
`AoI n` is the mean number of admitted
observations behind each mean age of information.

| Scenario | Method | Delivered | Rejected | Out of sequence | Pending at end | Mean AoI (s) | AoI n |
|---|---|---|---|---|---|---|---|
| delivery_delay | range_only | 286.0 | 1.2 | 1.2 | 2.4 | 0.099 | 284.8 |
| delivery_delay | fused | 558.6 | 2.2 | 2.2 | 5.2 | 0.099 | 556.4 |
| false_observations | range_only | 387.8 | 0.0 | 0.0 | 0.0 | 0.000 | 387.8 |
| false_observations | fused | 960.4 | 0.0 | 0.0 | 0.0 | 0.000 | 960.4 |
| measurement_bias | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| measurement_bias | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| moving_observer | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| moving_observer | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| nominal | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| nominal | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| out_of_sequence | range_only | 280.0 | 278.6 | 278.6 | 8.4 | 0.100 | 1.4 |
| out_of_sequence | fused | 547.2 | 545.6 | 545.6 | 16.6 | 0.100 | 1.6 |
| range_dropout | range_only | 165.2 | 0.0 | 0.0 | 0.0 | 0.000 | 165.2 |
| range_dropout | fused | 441.6 | 0.0 | 0.0 | 0.0 | 0.000 | 441.6 |
| sensor_disagreement_large_bias | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| sensor_disagreement_large_bias | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| sensor_disagreement_within_gate | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| sensor_disagreement_within_gate | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| sensor_disagreement_within_gate_high | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| sensor_disagreement_within_gate_high | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| sensor_disagreement_within_gate_low | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| sensor_disagreement_within_gate_low | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| uncertainty_miscalibration | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| uncertainty_miscalibration | fused | 566.0 | 0.0 | 0.0 | 0.0 | 0.000 | 566.0 |
| vision_dropout | range_only | 289.6 | 0.0 | 0.0 | 0.0 | 0.000 | 289.6 |
| vision_dropout | fused | 426.8 | 0.0 | 0.0 | 0.0 | 0.000 | 426.8 |

## Per-seed results

| Scenario | Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused − Range) |
|---|---|---|---|---|
| delivery_delay | 1 | 0.274 | 0.234 | -0.040 |
| delivery_delay | 2 | 0.264 | 0.226 | -0.038 |
| delivery_delay | 3 | 0.253 | 0.245 | -0.008 |
| delivery_delay | 4 | 0.240 | 0.216 | -0.024 |
| delivery_delay | 5 | 0.366 | 0.254 | -0.112 |
| false_observations | 1 | 0.206 | 0.186 | -0.020 |
| false_observations | 2 | 0.187 | 0.171 | -0.016 |
| false_observations | 3 | 0.286 | 0.226 | -0.060 |
| false_observations | 4 | 0.168 | 0.150 | -0.018 |
| false_observations | 5 | 0.267 | 0.240 | -0.027 |
| measurement_bias | 1 | 1.601 | 1.556 | -0.045 |
| measurement_bias | 2 | 1.558 | 1.498 | -0.060 |
| measurement_bias | 3 | 1.602 | 1.567 | -0.035 |
| measurement_bias | 4 | 1.543 | 1.533 | -0.010 |
| measurement_bias | 5 | 1.589 | 1.542 | -0.048 |
| moving_observer | 1 | 0.181 | 0.147 | -0.035 |
| moving_observer | 2 | 0.184 | 0.229 | +0.045 |
| moving_observer | 3 | 0.285 | 0.320 | +0.035 |
| moving_observer | 4 | 0.256 | 0.153 | -0.103 |
| moving_observer | 5 | 0.249 | 0.181 | -0.068 |
| nominal | 1 | 0.226 | 0.221 | -0.005 |
| nominal | 2 | 0.200 | 0.190 | -0.010 |
| nominal | 3 | 0.268 | 0.239 | -0.028 |
| nominal | 4 | 0.225 | 0.216 | -0.009 |
| nominal | 5 | 0.224 | 0.232 | +0.008 |
| out_of_sequence | 1 | N/A | N/A | N/A |
| out_of_sequence | 2 | N/A | N/A | N/A |
| out_of_sequence | 3 | N/A | N/A | N/A |
| out_of_sequence | 4 | N/A | N/A | N/A |
| out_of_sequence | 5 | N/A | N/A | N/A |
| range_dropout | 1 | 0.333 | 0.372 | +0.039 |
| range_dropout | 2 | 0.247 | 0.218 | -0.029 |
| range_dropout | 3 | 0.268 | 0.225 | -0.043 |
| range_dropout | 4 | 0.225 | 0.180 | -0.045 |
| range_dropout | 5 | 0.237 | 0.235 | -0.002 |
| sensor_disagreement_large_bias | 1 | 0.226 | 0.202 | -0.024 |
| sensor_disagreement_large_bias | 2 | 0.200 | 0.198 | -0.002 |
| sensor_disagreement_large_bias | 3 | 0.268 | 0.300 | +0.033 |
| sensor_disagreement_large_bias | 4 | 0.225 | 0.225 | +0.000 |
| sensor_disagreement_large_bias | 5 | 0.224 | 0.224 | +0.000 |
| sensor_disagreement_within_gate | 1 | 0.226 | 0.263 | +0.037 |
| sensor_disagreement_within_gate | 2 | 0.200 | 0.274 | +0.074 |
| sensor_disagreement_within_gate | 3 | 0.268 | 0.320 | +0.052 |
| sensor_disagreement_within_gate | 4 | 0.225 | 0.337 | +0.111 |
| sensor_disagreement_within_gate | 5 | 0.224 | 0.231 | +0.007 |
| sensor_disagreement_within_gate_high | 1 | 0.226 | 0.259 | +0.033 |
| sensor_disagreement_within_gate_high | 2 | 0.200 | 0.216 | +0.016 |
| sensor_disagreement_within_gate_high | 3 | 0.268 | 0.333 | +0.065 |
| sensor_disagreement_within_gate_high | 4 | 0.225 | 0.326 | +0.100 |
| sensor_disagreement_within_gate_high | 5 | 0.224 | 0.330 | +0.106 |
| sensor_disagreement_within_gate_low | 1 | 0.226 | 0.216 | -0.010 |
| sensor_disagreement_within_gate_low | 2 | 0.200 | 0.218 | +0.018 |
| sensor_disagreement_within_gate_low | 3 | 0.268 | 0.302 | +0.035 |
| sensor_disagreement_within_gate_low | 4 | 0.225 | 0.322 | +0.097 |
| sensor_disagreement_within_gate_low | 5 | 0.224 | 0.282 | +0.057 |
| uncertainty_miscalibration | 1 | 0.370 | 0.346 | -0.024 |
| uncertainty_miscalibration | 2 | 0.385 | 0.410 | +0.025 |
| uncertainty_miscalibration | 3 | 0.432 | 0.463 | +0.031 |
| uncertainty_miscalibration | 4 | 0.501 | 0.383 | -0.118 |
| uncertainty_miscalibration | 5 | 0.472 | 0.430 | -0.042 |
| vision_dropout | 1 | 0.226 | 0.187 | -0.038 |
| vision_dropout | 2 | 0.200 | 0.195 | -0.005 |
| vision_dropout | 3 | 0.268 | 0.255 | -0.013 |
| vision_dropout | 4 | 0.225 | 0.253 | +0.027 |
| vision_dropout | 5 | 0.224 | 0.225 | +0.001 |

## Findings

- On the aggregate position RMSE, fused was better in 6 scenario(s),
  worse in 3 scenario(s), and within 0.01 m in 3 scenario(s).
- Fused precision was higher in 0 scenario(s) and lower
  in 12. Fused 95% coverage was higher in 2
  scenario(s) and lower in 10. Accuracy alone does not
  establish that fusion improved association or calibration.
- Fusion is not guaranteed to improve accuracy. Systematic sensor bias,
  miscalibrated uncertainty, missed detections, false observations and
  association errors can all reverse the comparison.
- Precision is sample-based: matched samples over all confirmed/coasting
  track samples. `Unmatched confirmed tracks` are confirmed track IDs never
  matched to a ground-truth object. `Duplicate tracks` is the subset that, in
  at least one frame, was left unmatched while a ground-truth object lay
  within the matching gate (the object had been claimed by another track).
  The rest were never near an unclaimed object under that gate.
- `sensor_disagreement_large_bias` (0.12 rad) is a gate-rejection
  experiment: see the vision acceptance table for how many biased
  observations the gate rejected versus applied. It does not measure the
  cost of fusing biased data.
- `sensor_disagreement_within_gate` (0.015 rad) applies a bias small
  enough to pass the gate often, so it measures what happens when biased
  vision data is actually fused. Neither scenario establishes real-world
  sensor-fusion performance; both are descriptive synthetic results on
  development seeds, not statistical or held-out claims.
- `track_fragmentation` counts interruptions in an object's matched frames, summed
  over objects; it is independent of identity switches.
- `identity_switches` counts changes of matched track ID for the same
  ground-truth object across consecutive matched frames.
- Coverage is empirical and only defined over matched samples; its
  denominator is reported in `per_seed.csv` and `benchmark.json`.
- Scenarios with no matched samples (for example `out_of_sequence`)
  report `N/A` accuracy because their observations are rejected as stale;
  that is an explicit non-result, not a zero-error result.
- This report uses the seeds shown above. The reserved held-out range
  (25-49) is not included here and no held-out claim is made.

## Limitations

- Synthetic 2-D world; simplified sensor models, not hardware validation.
- Vision-only track initiation is not supported (bearing alone cannot
  determine range).
- Out-of-sequence observations older than one tracker epoch are explicitly
  rejected and counted, not silently dropped. Their accuracy impact is
  therefore not represented as a successful fusion result.
- Development seeds are used for debugging. The documented held-out seed
  range (25-49) is only a held-out evaluation when those seeds are actually
  present in the `Seeds` line above.
