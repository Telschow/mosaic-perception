# Mosaic Benchmark Report

This report is generated from the code in this repository. It contains no
hand-edited numbers and no wall-clock timestamps, so repeated runs with the
same seeds and commit are byte-identical.

## Code and protocol

- Package version: `0.1.0`
- Git commit: `9feac5eca754e67ffb5db0b95e0f48aa7984ab8a`
- Seeds: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24
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
| crossing_targets | range_only | 0.148 ± 0.033 | 0.184 | 0.977 | 0.856 | 0.923 | 296/303 | 3.2 | 3.2 | 0.0 |
| crossing_targets | fused | 0.146 ± 0.043 | 0.164 | 0.979 | 0.718 | 0.886 | 297/303 | 4.6 | 4.5 | 0.0 |
| delivery_delay | range_only | 0.285 ± 0.039 | 0.344 | 0.968 | 0.807 | 0.563 | 293/303 | 2.4 | 2.4 | 0.1 |
| delivery_delay | fused | 0.268 ± 0.045 | 0.301 | 0.970 | 0.660 | 0.402 | 294/303 | 4.5 | 4.5 | 0.0 |
| dense_clutter | range_only | 0.219 ± 0.042 | 0.326 | 0.979 | 0.816 | 0.850 | 297/303 | 2.6 | 2.6 | 0.0 |
| dense_clutter | fused | 0.206 ± 0.038 | 0.286 | 0.979 | 0.338 | 0.752 | 297/303 | 71.0 | 6.3 | 0.0 |
| false_observations | range_only | 0.208 ± 0.043 | 0.323 | 0.977 | 0.840 | 0.870 | 296/303 | 2.1 | 2.1 | 0.0 |
| false_observations | fused | 0.189 ± 0.043 | 0.276 | 0.979 | 0.639 | 0.810 | 297/303 | 11.0 | 4.6 | 0.0 |
| measurement_bias | range_only | 1.594 ± 0.031 | 0.563 | 0.889 | 0.715 | 0.002 | 269/303 | 0.9 | 0.3 | 5.3 |
| measurement_bias | fused | 1.556 ± 0.034 | 0.557 | 0.909 | 0.599 | 0.016 | 275/303 | 1.7 | 0.5 | 4.1 |
| moving_observer | range_only | 0.218 ± 0.053 | 0.369 | 0.975 | 0.833 | 0.863 | 296/303 | 2.8 | 2.8 | 0.1 |
| moving_observer | fused | 0.188 ± 0.053 | 0.282 | 0.978 | 0.714 | 0.820 | 296/303 | 4.8 | 4.7 | 0.0 |
| nominal | range_only | 0.213 ± 0.041 | 0.317 | 0.977 | 0.826 | 0.851 | 296/303 | 2.4 | 2.4 | 0.0 |
| nominal | fused | 0.195 ± 0.037 | 0.271 | 0.980 | 0.696 | 0.816 | 297/303 | 3.9 | 3.8 | 0.0 |
| out_of_sequence | range_only | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A |
| out_of_sequence | fused | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A |
| range_dropout | range_only | 0.248 ± 0.036 | 0.355 | 0.881 | 0.972 | 0.896 | 267/303 | 0.4 | 0.4 | 5.1 |
| range_dropout | fused | 0.219 ± 0.050 | 0.281 | 0.970 | 0.816 | 0.859 | 294/303 | 2.0 | 2.0 | 0.3 |
| sensor_disagreement_large_bias | range_only | 0.213 ± 0.041 | 0.317 | 0.977 | 0.826 | 0.851 | 296/303 | 2.4 | 2.4 | 0.0 |
| sensor_disagreement_large_bias | fused | 0.211 ± 0.046 | 0.320 | 0.977 | 0.807 | 0.848 | 296/303 | 3.5 | 3.1 | 0.0 |
| sensor_disagreement_within_gate | range_only | 0.213 ± 0.041 | 0.317 | 0.977 | 0.826 | 0.851 | 296/303 | 2.4 | 2.4 | 0.0 |
| sensor_disagreement_within_gate | fused | 0.273 ± 0.046 | 0.424 | 0.979 | 0.560 | 0.478 | 297/303 | 4.6 | 4.6 | 0.0 |
| sensor_disagreement_within_gate_high | range_only | 0.213 ± 0.041 | 0.317 | 0.977 | 0.826 | 0.851 | 296/303 | 2.4 | 2.4 | 0.0 |
| sensor_disagreement_within_gate_high | fused | 0.278 ± 0.041 | 0.476 | 0.978 | 0.535 | 0.597 | 296/303 | 4.2 | 4.2 | 0.0 |
| sensor_disagreement_within_gate_low | range_only | 0.213 ± 0.041 | 0.317 | 0.977 | 0.826 | 0.851 | 296/303 | 2.4 | 2.4 | 0.0 |
| sensor_disagreement_within_gate_low | fused | 0.256 ± 0.044 | 0.347 | 0.979 | 0.617 | 0.427 | 297/303 | 4.5 | 4.4 | 0.0 |
| uncertainty_miscalibration | range_only | 0.431 ± 0.061 | 0.613 | 0.521 | 0.832 | 0.107 | 158/303 | 1.6 | 1.6 | 15.6 |
| uncertainty_miscalibration | fused | 0.409 ± 0.051 | 0.648 | 0.932 | 0.445 | 0.151 | 282/303 | 26.5 | 26.1 | 3.6 |
| vision_dropout | range_only | 0.213 ± 0.041 | 0.317 | 0.977 | 0.826 | 0.851 | 296/303 | 2.4 | 2.4 | 0.0 |
| vision_dropout | fused | 0.208 ± 0.049 | 0.298 | 0.978 | 0.726 | 0.800 | 296/303 | 4.2 | 4.2 | 0.0 |

## Paired differences (fused minus range-only)

Mean per-seed difference with a two-sided 95% t interval over seeds. Seeds with
an undefined value on either side are dropped (`n` is the number kept). A
negative RMSE difference favours fusion; for recall, precision and coverage a
positive one does. The interval describes seed-to-seed variation in this
synthetic setup and is not a claim about other worlds.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| crossing_targets | position_rmse | 25 | -0.002 | [-0.015, +0.011] |
| crossing_targets | recall | 25 | +0.002 | [+0.000, +0.003] |
| crossing_targets | precision | 25 | -0.138 | [-0.171, -0.106] |
| crossing_targets | position_coverage_95 | 25 | -0.037 | [-0.071, -0.003] |
| delivery_delay | position_rmse | 25 | -0.017 | [-0.032, -0.003] |
| delivery_delay | recall | 25 | +0.001 | [+0.000, +0.002] |
| delivery_delay | precision | 25 | -0.147 | [-0.174, -0.120] |
| delivery_delay | position_coverage_95 | 25 | -0.160 | [-0.214, -0.107] |
| dense_clutter | position_rmse | 25 | -0.013 | [-0.024, -0.002] |
| dense_clutter | recall | 25 | +0.001 | [-0.000, +0.001] |
| dense_clutter | precision | 25 | -0.478 | [-0.499, -0.457] |
| dense_clutter | position_coverage_95 | 25 | -0.098 | [-0.127, -0.069] |
| false_observations | position_rmse | 25 | -0.018 | [-0.035, -0.002] |
| false_observations | recall | 25 | +0.002 | [+0.001, +0.004] |
| false_observations | precision | 25 | -0.202 | [-0.238, -0.165] |
| false_observations | position_coverage_95 | 25 | -0.059 | [-0.096, -0.023] |
| measurement_bias | position_rmse | 25 | -0.038 | [-0.053, -0.024] |
| measurement_bias | recall | 25 | +0.020 | [+0.007, +0.033] |
| measurement_bias | precision | 25 | -0.117 | [-0.137, -0.096] |
| measurement_bias | position_coverage_95 | 25 | +0.014 | [+0.010, +0.019] |
| moving_observer | position_rmse | 25 | -0.029 | [-0.044, -0.014] |
| moving_observer | recall | 25 | +0.002 | [+0.000, +0.004] |
| moving_observer | precision | 25 | -0.119 | [-0.150, -0.089] |
| moving_observer | position_coverage_95 | 25 | -0.043 | [-0.090, +0.004] |
| nominal | position_rmse | 25 | -0.018 | [-0.031, -0.005] |
| nominal | recall | 25 | +0.003 | [+0.001, +0.004] |
| nominal | precision | 25 | -0.130 | [-0.162, -0.099] |
| nominal | position_coverage_95 | 25 | -0.035 | [-0.077, +0.007] |
| out_of_sequence | position_rmse | 0 | N/A | N/A |
| out_of_sequence | recall | 25 | +0.000 | [+0.000, +0.000] |
| out_of_sequence | precision | 0 | N/A | N/A |
| out_of_sequence | position_coverage_95 | 0 | N/A | N/A |
| range_dropout | position_rmse | 25 | -0.029 | [-0.046, -0.012] |
| range_dropout | recall | 25 | +0.090 | [+0.074, +0.105] |
| range_dropout | precision | 25 | -0.156 | [-0.182, -0.129] |
| range_dropout | position_coverage_95 | 25 | -0.038 | [-0.069, -0.007] |
| sensor_disagreement_large_bias | position_rmse | 25 | -0.002 | [-0.007, +0.004] |
| sensor_disagreement_large_bias | recall | 25 | +0.000 | [-0.000, +0.000] |
| sensor_disagreement_large_bias | precision | 25 | -0.018 | [-0.038, +0.001] |
| sensor_disagreement_large_bias | position_coverage_95 | 25 | -0.004 | [-0.016, +0.009] |
| sensor_disagreement_within_gate | position_rmse | 25 | +0.060 | [+0.043, +0.078] |
| sensor_disagreement_within_gate | recall | 25 | +0.002 | [+0.001, +0.003] |
| sensor_disagreement_within_gate | precision | 25 | -0.265 | [-0.292, -0.239] |
| sensor_disagreement_within_gate | position_coverage_95 | 25 | -0.373 | [-0.421, -0.326] |
| sensor_disagreement_within_gate_high | position_rmse | 25 | +0.065 | [+0.048, +0.082] |
| sensor_disagreement_within_gate_high | recall | 25 | +0.001 | [-0.000, +0.002] |
| sensor_disagreement_within_gate_high | precision | 25 | -0.291 | [-0.314, -0.267] |
| sensor_disagreement_within_gate_high | position_coverage_95 | 25 | -0.255 | [-0.308, -0.201] |
| sensor_disagreement_within_gate_low | position_rmse | 25 | +0.042 | [+0.024, +0.061] |
| sensor_disagreement_within_gate_low | recall | 25 | +0.002 | [+0.001, +0.003] |
| sensor_disagreement_within_gate_low | precision | 25 | -0.209 | [-0.241, -0.177] |
| sensor_disagreement_within_gate_low | position_coverage_95 | 25 | -0.424 | [-0.472, -0.377] |
| uncertainty_miscalibration | position_rmse | 25 | -0.022 | [-0.048, +0.003] |
| uncertainty_miscalibration | recall | 25 | +0.411 | [+0.387, +0.435] |
| uncertainty_miscalibration | precision | 25 | -0.386 | [-0.405, -0.367] |
| uncertainty_miscalibration | position_coverage_95 | 25 | +0.044 | [+0.016, +0.072] |
| vision_dropout | position_rmse | 25 | -0.005 | [-0.018, +0.008] |
| vision_dropout | recall | 25 | +0.001 | [+0.000, +0.002] |
| vision_dropout | precision | 25 | -0.100 | [-0.124, -0.075] |
| vision_dropout | position_coverage_95 | 25 | -0.051 | [-0.091, -0.012] |

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
| crossing_targets | range_only | N/A | N/A | 0.000 | 0.0 |
| crossing_targets | fused | 0.990 | 0.990 | 0.657 | 194.8 |
| delivery_delay | range_only | N/A | N/A | 0.000 | 0.0 |
| delivery_delay | fused | 0.999 | 0.999 | 0.665 | 195.3 |
| dense_clutter | range_only | N/A | N/A | 0.000 | 0.0 |
| dense_clutter | fused | 0.999 | 0.999 | 0.637 | 189.1 |
| false_observations | range_only | N/A | N/A | 0.000 | 0.0 |
| false_observations | fused | 0.999 | 0.999 | 0.657 | 194.9 |
| measurement_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| measurement_bias | fused | 0.998 | 0.997 | 0.655 | 180.5 |
| moving_observer | range_only | N/A | N/A | 0.000 | 0.0 |
| moving_observer | fused | 0.999 | 0.999 | 0.664 | 196.8 |
| nominal | range_only | N/A | N/A | 0.000 | 0.0 |
| nominal | fused | 0.999 | 0.999 | 0.662 | 196.6 |
| out_of_sequence | range_only | N/A | N/A | N/A | 0.0 |
| out_of_sequence | fused | N/A | N/A | N/A | 0.0 |
| range_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| range_dropout | fused | 0.999 | 0.999 | 0.666 | 195.7 |
| sensor_disagreement_large_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_large_bias | fused | 0.429 | 0.298 | 0.040 | 12.0 |
| sensor_disagreement_within_gate | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate | fused | 0.992 | 0.989 | 0.596 | 176.8 |
| sensor_disagreement_within_gate_high | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_high | fused | 0.987 | 0.984 | 0.556 | 164.8 |
| sensor_disagreement_within_gate_low | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_low | fused | 0.995 | 0.993 | 0.650 | 193.0 |
| uncertainty_miscalibration | range_only | N/A | N/A | 0.000 | 0.0 |
| uncertainty_miscalibration | fused | 0.998 | 0.997 | 0.628 | 177.4 |
| vision_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| vision_dropout | fused | 0.999 | 0.999 | 0.652 | 193.4 |

## Duplicate-track sensitivity to the matching gate

Mean number of duplicate tracks per seed when the evaluation matching gate is
1.0, 2.0 or 3.0 m. The three gates were chosen before running (see the project issue
tracker). The 2.0 m column is the headline gate used everywhere else in this
report when it is the evaluator gate; the others show how much the
duplicate count depends on that choice, not which gate is correct.

| Scenario | Method | 1.0 m | 2.0 m | 3.0 m |
|---|---|---|---|---|
| crossing_targets | range_only | 3.2 | 3.2 | 3.2 |
| crossing_targets | fused | 4.1 | 4.5 | 4.6 |
| delivery_delay | range_only | 2.2 | 2.4 | 2.4 |
| delivery_delay | fused | 3.8 | 4.5 | 4.5 |
| dense_clutter | range_only | 2.6 | 2.6 | 2.6 |
| dense_clutter | fused | 4.6 | 6.3 | 7.9 |
| false_observations | range_only | 2.0 | 2.1 | 2.1 |
| false_observations | fused | 3.8 | 4.6 | 4.7 |
| measurement_bias | range_only | 0.0 | 0.3 | 0.7 |
| measurement_bias | fused | 0.0 | 0.5 | 1.4 |
| moving_observer | range_only | 2.8 | 2.8 | 2.8 |
| moving_observer | fused | 4.1 | 4.7 | 4.7 |
| nominal | range_only | 2.3 | 2.4 | 2.4 |
| nominal | fused | 3.5 | 3.8 | 3.8 |
| out_of_sequence | range_only | 0.0 | 0.0 | 0.0 |
| out_of_sequence | fused | 0.0 | 0.0 | 0.0 |
| range_dropout | range_only | 0.4 | 0.4 | 0.4 |
| range_dropout | fused | 1.6 | 2.0 | 2.0 |
| sensor_disagreement_large_bias | range_only | 2.3 | 2.4 | 2.4 |
| sensor_disagreement_large_bias | fused | 2.6 | 3.1 | 3.4 |
| sensor_disagreement_within_gate | range_only | 2.3 | 2.4 | 2.4 |
| sensor_disagreement_within_gate | fused | 4.2 | 4.6 | 4.6 |
| sensor_disagreement_within_gate_high | range_only | 2.3 | 2.4 | 2.4 |
| sensor_disagreement_within_gate_high | fused | 3.5 | 4.2 | 4.2 |
| sensor_disagreement_within_gate_low | range_only | 2.3 | 2.4 | 2.4 |
| sensor_disagreement_within_gate_low | fused | 3.9 | 4.4 | 4.4 |
| uncertainty_miscalibration | range_only | 1.7 | 1.6 | 1.6 |
| uncertainty_miscalibration | fused | 22.8 | 26.1 | 26.3 |
| vision_dropout | range_only | 2.3 | 2.4 | 2.4 |
| vision_dropout | fused | 3.8 | 4.2 | 4.2 |

## Vision observation acceptance (fused method)

Mean per seed. `Generated` = produced by vision sensors; `Delivered` = left the
pending queue (generated minus those still pending at the end); `Gate-rejected` =
at least one track was evaluated and none passed the chi-square gate;
`Lost competition` = passed the gate for some track but lost the one-to-one
assignment; `Other unassigned` = no evaluable candidate track; `Stale/invalid` =
rejected outside association; `Applied` = used in a track update.

| Scenario | Generated | Delivered | Gate-rejected | Lost competition | Other unassigned | Stale/invalid | Applied |
|---|---|---|---|---|---|---|---|
| crossing_targets | 275.2 | 275.2 | 9.0 | 0.2 | 0.0 | 0.0 | 266.0 |
| delivery_delay | 274.1 | 271.3 | 13.5 | 0.8 | 0.0 | 1.6 | 255.3 |
| dense_clutter | 1098.8 | 1098.8 | 532.6 | 19.3 | 0.0 | 0.0 | 547.0 |
| false_observations | 577.7 | 577.7 | 278.2 | 2.8 | 0.0 | 0.0 | 296.8 |
| measurement_bias | 275.2 | 275.2 | 13.8 | 0.0 | 0.0 | 0.0 | 261.4 |
| moving_observer | 275.2 | 275.2 | 14.8 | 0.1 | 0.0 | 0.0 | 260.3 |
| nominal | 275.2 | 275.2 | 14.6 | 0.2 | 0.0 | 0.0 | 260.4 |
| out_of_sequence | 274.1 | 266.2 | 0.0 | 0.0 | 0.3 | 265.8 | 0.0 |
| range_dropout | 275.2 | 275.2 | 19.3 | 0.2 | 0.2 | 0.0 | 255.5 |
| sensor_disagreement_large_bias | 275.2 | 275.2 | 264.7 | 0.3 | 0.0 | 0.0 | 10.2 |
| sensor_disagreement_within_gate | 275.2 | 275.2 | 30.8 | 0.2 | 0.0 | 0.0 | 244.2 |
| sensor_disagreement_within_gate_high | 275.2 | 275.2 | 52.8 | 0.2 | 0.0 | 0.0 | 222.2 |
| sensor_disagreement_within_gate_low | 275.2 | 275.2 | 20.8 | 0.0 | 0.0 | 0.0 | 254.4 |
| uncertainty_miscalibration | 275.2 | 275.2 | 38.3 | 0.1 | 0.0 | 0.0 | 236.8 |
| vision_dropout | 140.0 | 140.0 | 7.7 | 0.0 | 0.0 | 0.0 | 132.3 |

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
| crossing_targets | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| crossing_targets | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| delivery_delay | range_only | 285.0 | 1.4 | 1.4 | 2.8 | 0.099 | 283.6 |
| delivery_delay | fused | 556.3 | 3.0 | 3.0 | 5.6 | 0.099 | 553.3 |
| dense_clutter | range_only | 692.1 | 0.0 | 0.0 | 0.0 | 0.000 | 692.1 |
| dense_clutter | fused | 1790.9 | 0.0 | 0.0 | 0.0 | 0.000 | 1790.9 |
| false_observations | range_only | 388.9 | 0.0 | 0.0 | 0.0 | 0.000 | 388.9 |
| false_observations | fused | 966.6 | 0.0 | 0.0 | 0.0 | 0.000 | 966.6 |
| measurement_bias | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| measurement_bias | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| moving_observer | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| moving_observer | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| nominal | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| nominal | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| out_of_sequence | range_only | 279.0 | 278.4 | 278.4 | 8.8 | 0.100 | 0.6 |
| out_of_sequence | fused | 545.1 | 544.2 | 544.2 | 16.7 | 0.100 | 0.9 |
| range_dropout | range_only | 166.2 | 0.0 | 0.0 | 0.0 | 0.000 | 166.2 |
| range_dropout | fused | 441.4 | 0.0 | 0.0 | 0.0 | 0.000 | 441.4 |
| sensor_disagreement_large_bias | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_large_bias | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_within_gate | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate_high | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_within_gate_high | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate_low | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_within_gate_low | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| uncertainty_miscalibration | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| uncertainty_miscalibration | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| vision_dropout | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| vision_dropout | fused | 429.2 | 0.0 | 0.0 | 0.0 | 0.000 | 429.2 |

## Per-seed results

| Scenario | Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused − Range) |
|---|---|---|---|---|
| crossing_targets | 0 | 0.108 | 0.119 | +0.011 |
| crossing_targets | 1 | 0.121 | 0.090 | -0.032 |
| crossing_targets | 2 | 0.149 | 0.242 | +0.093 |
| crossing_targets | 3 | 0.145 | 0.191 | +0.046 |
| crossing_targets | 4 | 0.133 | 0.127 | -0.007 |
| crossing_targets | 5 | 0.201 | 0.211 | +0.009 |
| crossing_targets | 6 | 0.136 | 0.113 | -0.022 |
| crossing_targets | 7 | 0.211 | 0.232 | +0.021 |
| crossing_targets | 8 | 0.172 | 0.171 | -0.002 |
| crossing_targets | 9 | 0.231 | 0.185 | -0.047 |
| crossing_targets | 10 | 0.139 | 0.125 | -0.014 |
| crossing_targets | 11 | 0.123 | 0.147 | +0.024 |
| crossing_targets | 12 | 0.125 | 0.144 | +0.019 |
| crossing_targets | 13 | 0.141 | 0.107 | -0.033 |
| crossing_targets | 14 | 0.114 | 0.104 | -0.010 |
| crossing_targets | 15 | 0.175 | 0.157 | -0.018 |
| crossing_targets | 16 | 0.113 | 0.108 | -0.005 |
| crossing_targets | 17 | 0.197 | 0.201 | +0.004 |
| crossing_targets | 18 | 0.132 | 0.135 | +0.003 |
| crossing_targets | 19 | 0.130 | 0.160 | +0.030 |
| crossing_targets | 20 | 0.112 | 0.097 | -0.015 |
| crossing_targets | 21 | 0.160 | 0.135 | -0.025 |
| crossing_targets | 22 | 0.135 | 0.135 | -0.001 |
| crossing_targets | 23 | 0.145 | 0.107 | -0.038 |
| crossing_targets | 24 | 0.146 | 0.105 | -0.042 |
| delivery_delay | 0 | 0.286 | 0.237 | -0.049 |
| delivery_delay | 1 | 0.274 | 0.234 | -0.040 |
| delivery_delay | 2 | 0.264 | 0.226 | -0.038 |
| delivery_delay | 3 | 0.253 | 0.245 | -0.008 |
| delivery_delay | 4 | 0.240 | 0.216 | -0.024 |
| delivery_delay | 5 | 0.366 | 0.254 | -0.112 |
| delivery_delay | 6 | 0.227 | 0.268 | +0.041 |
| delivery_delay | 7 | 0.208 | 0.238 | +0.031 |
| delivery_delay | 8 | 0.320 | 0.278 | -0.042 |
| delivery_delay | 9 | 0.296 | 0.268 | -0.028 |
| delivery_delay | 10 | 0.305 | 0.332 | +0.027 |
| delivery_delay | 11 | 0.243 | 0.225 | -0.018 |
| delivery_delay | 12 | 0.256 | 0.215 | -0.041 |
| delivery_delay | 13 | 0.280 | 0.244 | -0.036 |
| delivery_delay | 14 | 0.276 | 0.268 | -0.009 |
| delivery_delay | 15 | 0.300 | 0.305 | +0.005 |
| delivery_delay | 16 | 0.289 | 0.292 | +0.003 |
| delivery_delay | 17 | 0.371 | 0.399 | +0.027 |
| delivery_delay | 18 | 0.276 | 0.296 | +0.020 |
| delivery_delay | 19 | 0.311 | 0.312 | +0.001 |
| delivery_delay | 20 | 0.267 | 0.263 | -0.004 |
| delivery_delay | 21 | 0.296 | 0.233 | -0.063 |
| delivery_delay | 22 | 0.338 | 0.335 | -0.003 |
| delivery_delay | 23 | 0.305 | 0.302 | -0.003 |
| delivery_delay | 24 | 0.287 | 0.216 | -0.071 |
| dense_clutter | 0 | 0.248 | 0.213 | -0.035 |
| dense_clutter | 1 | 0.187 | 0.219 | +0.031 |
| dense_clutter | 2 | 0.170 | 0.188 | +0.018 |
| dense_clutter | 3 | 0.234 | 0.190 | -0.044 |
| dense_clutter | 4 | 0.266 | 0.238 | -0.028 |
| dense_clutter | 5 | 0.248 | 0.208 | -0.040 |
| dense_clutter | 6 | 0.221 | 0.195 | -0.026 |
| dense_clutter | 7 | 0.185 | 0.137 | -0.048 |
| dense_clutter | 8 | 0.270 | 0.249 | -0.021 |
| dense_clutter | 9 | 0.272 | 0.225 | -0.047 |
| dense_clutter | 10 | 0.185 | 0.171 | -0.014 |
| dense_clutter | 11 | 0.260 | 0.230 | -0.029 |
| dense_clutter | 12 | 0.183 | 0.183 | -0.000 |
| dense_clutter | 13 | 0.225 | 0.197 | -0.028 |
| dense_clutter | 14 | 0.187 | 0.200 | +0.013 |
| dense_clutter | 15 | 0.221 | 0.201 | -0.020 |
| dense_clutter | 16 | 0.141 | 0.141 | +0.000 |
| dense_clutter | 17 | 0.297 | 0.276 | -0.021 |
| dense_clutter | 18 | 0.211 | 0.201 | -0.010 |
| dense_clutter | 19 | 0.257 | 0.306 | +0.049 |
| dense_clutter | 20 | 0.199 | 0.206 | +0.007 |
| dense_clutter | 21 | 0.175 | 0.171 | -0.004 |
| dense_clutter | 22 | 0.211 | 0.226 | +0.014 |
| dense_clutter | 23 | 0.153 | 0.159 | +0.006 |
| dense_clutter | 24 | 0.271 | 0.225 | -0.046 |
| false_observations | 0 | 0.220 | 0.202 | -0.018 |
| false_observations | 1 | 0.206 | 0.186 | -0.020 |
| false_observations | 2 | 0.187 | 0.171 | -0.016 |
| false_observations | 3 | 0.286 | 0.226 | -0.060 |
| false_observations | 4 | 0.168 | 0.150 | -0.018 |
| false_observations | 5 | 0.267 | 0.240 | -0.027 |
| false_observations | 6 | 0.174 | 0.220 | +0.046 |
| false_observations | 7 | 0.172 | 0.148 | -0.024 |
| false_observations | 8 | 0.190 | 0.203 | +0.013 |
| false_observations | 9 | 0.245 | 0.259 | +0.015 |
| false_observations | 10 | 0.197 | 0.240 | +0.043 |
| false_observations | 11 | 0.231 | 0.232 | +0.000 |
| false_observations | 12 | 0.221 | 0.197 | -0.024 |
| false_observations | 13 | 0.247 | 0.132 | -0.115 |
| false_observations | 14 | 0.153 | 0.143 | -0.009 |
| false_observations | 15 | 0.155 | 0.117 | -0.037 |
| false_observations | 16 | 0.176 | 0.142 | -0.035 |
| false_observations | 17 | 0.241 | 0.281 | +0.040 |
| false_observations | 18 | 0.179 | 0.165 | -0.015 |
| false_observations | 19 | 0.312 | 0.190 | -0.121 |
| false_observations | 20 | 0.162 | 0.129 | -0.032 |
| false_observations | 21 | 0.198 | 0.193 | -0.005 |
| false_observations | 22 | 0.239 | 0.199 | -0.039 |
| false_observations | 23 | 0.157 | 0.163 | +0.006 |
| false_observations | 24 | 0.208 | 0.207 | -0.001 |
| measurement_bias | 0 | 1.619 | 1.603 | -0.016 |
| measurement_bias | 1 | 1.601 | 1.556 | -0.045 |
| measurement_bias | 2 | 1.558 | 1.498 | -0.060 |
| measurement_bias | 3 | 1.602 | 1.567 | -0.035 |
| measurement_bias | 4 | 1.543 | 1.533 | -0.010 |
| measurement_bias | 5 | 1.589 | 1.542 | -0.048 |
| measurement_bias | 6 | 1.602 | 1.566 | -0.036 |
| measurement_bias | 7 | 1.565 | 1.588 | +0.022 |
| measurement_bias | 8 | 1.636 | 1.568 | -0.068 |
| measurement_bias | 9 | 1.555 | 1.536 | -0.018 |
| measurement_bias | 10 | 1.617 | 1.557 | -0.060 |
| measurement_bias | 11 | 1.660 | 1.591 | -0.069 |
| measurement_bias | 12 | 1.630 | 1.584 | -0.046 |
| measurement_bias | 13 | 1.609 | 1.536 | -0.072 |
| measurement_bias | 14 | 1.588 | 1.557 | -0.031 |
| measurement_bias | 15 | 1.607 | 1.527 | -0.080 |
| measurement_bias | 16 | 1.615 | 1.504 | -0.111 |
| measurement_bias | 17 | 1.537 | 1.484 | -0.054 |
| measurement_bias | 18 | 1.582 | 1.603 | +0.021 |
| measurement_bias | 19 | 1.582 | 1.582 | +0.000 |
| measurement_bias | 20 | 1.567 | 1.596 | +0.029 |
| measurement_bias | 21 | 1.569 | 1.507 | -0.063 |
| measurement_bias | 22 | 1.581 | 1.588 | +0.007 |
| measurement_bias | 23 | 1.601 | 1.544 | -0.057 |
| measurement_bias | 24 | 1.640 | 1.577 | -0.062 |
| moving_observer | 0 | 0.194 | 0.189 | -0.005 |
| moving_observer | 1 | 0.181 | 0.147 | -0.035 |
| moving_observer | 2 | 0.184 | 0.229 | +0.045 |
| moving_observer | 3 | 0.285 | 0.320 | +0.035 |
| moving_observer | 4 | 0.256 | 0.153 | -0.103 |
| moving_observer | 5 | 0.249 | 0.181 | -0.068 |
| moving_observer | 6 | 0.198 | 0.187 | -0.011 |
| moving_observer | 7 | 0.240 | 0.220 | -0.020 |
| moving_observer | 8 | 0.271 | 0.182 | -0.088 |
| moving_observer | 9 | 0.360 | 0.261 | -0.099 |
| moving_observer | 10 | 0.188 | 0.214 | +0.026 |
| moving_observer | 11 | 0.223 | 0.205 | -0.017 |
| moving_observer | 12 | 0.148 | 0.121 | -0.026 |
| moving_observer | 13 | 0.150 | 0.138 | -0.012 |
| moving_observer | 14 | 0.171 | 0.116 | -0.055 |
| moving_observer | 15 | 0.238 | 0.202 | -0.036 |
| moving_observer | 16 | 0.170 | 0.112 | -0.057 |
| moving_observer | 17 | 0.285 | 0.262 | -0.023 |
| moving_observer | 18 | 0.259 | 0.232 | -0.027 |
| moving_observer | 19 | 0.238 | 0.200 | -0.038 |
| moving_observer | 20 | 0.139 | 0.098 | -0.041 |
| moving_observer | 21 | 0.236 | 0.230 | -0.006 |
| moving_observer | 22 | 0.218 | 0.187 | -0.031 |
| moving_observer | 23 | 0.144 | 0.144 | +0.001 |
| moving_observer | 24 | 0.215 | 0.182 | -0.033 |
| nominal | 0 | 0.168 | 0.200 | +0.032 |
| nominal | 1 | 0.226 | 0.221 | -0.005 |
| nominal | 2 | 0.200 | 0.190 | -0.010 |
| nominal | 3 | 0.268 | 0.239 | -0.028 |
| nominal | 4 | 0.225 | 0.216 | -0.009 |
| nominal | 5 | 0.224 | 0.232 | +0.008 |
| nominal | 6 | 0.186 | 0.186 | +0.000 |
| nominal | 7 | 0.223 | 0.191 | -0.032 |
| nominal | 8 | 0.244 | 0.207 | -0.036 |
| nominal | 9 | 0.334 | 0.265 | -0.068 |
| nominal | 10 | 0.187 | 0.189 | +0.002 |
| nominal | 11 | 0.225 | 0.197 | -0.028 |
| nominal | 12 | 0.159 | 0.233 | +0.074 |
| nominal | 13 | 0.147 | 0.168 | +0.021 |
| nominal | 14 | 0.190 | 0.151 | -0.039 |
| nominal | 15 | 0.196 | 0.173 | -0.023 |
| nominal | 16 | 0.187 | 0.116 | -0.070 |
| nominal | 17 | 0.267 | 0.247 | -0.020 |
| nominal | 18 | 0.225 | 0.200 | -0.025 |
| nominal | 19 | 0.214 | 0.205 | -0.009 |
| nominal | 20 | 0.164 | 0.121 | -0.042 |
| nominal | 21 | 0.262 | 0.208 | -0.054 |
| nominal | 22 | 0.209 | 0.194 | -0.015 |
| nominal | 23 | 0.189 | 0.127 | -0.062 |
| nominal | 24 | 0.211 | 0.203 | -0.008 |
| out_of_sequence | 0 | N/A | N/A | N/A |
| out_of_sequence | 1 | N/A | N/A | N/A |
| out_of_sequence | 2 | N/A | N/A | N/A |
| out_of_sequence | 3 | N/A | N/A | N/A |
| out_of_sequence | 4 | N/A | N/A | N/A |
| out_of_sequence | 5 | N/A | N/A | N/A |
| out_of_sequence | 6 | N/A | N/A | N/A |
| out_of_sequence | 7 | N/A | N/A | N/A |
| out_of_sequence | 8 | N/A | N/A | N/A |
| out_of_sequence | 9 | N/A | N/A | N/A |
| out_of_sequence | 10 | N/A | N/A | N/A |
| out_of_sequence | 11 | N/A | N/A | N/A |
| out_of_sequence | 12 | N/A | N/A | N/A |
| out_of_sequence | 13 | N/A | N/A | N/A |
| out_of_sequence | 14 | N/A | N/A | N/A |
| out_of_sequence | 15 | N/A | N/A | N/A |
| out_of_sequence | 16 | N/A | N/A | N/A |
| out_of_sequence | 17 | N/A | N/A | N/A |
| out_of_sequence | 18 | N/A | N/A | N/A |
| out_of_sequence | 19 | N/A | N/A | N/A |
| out_of_sequence | 20 | N/A | N/A | N/A |
| out_of_sequence | 21 | N/A | N/A | N/A |
| out_of_sequence | 22 | N/A | N/A | N/A |
| out_of_sequence | 23 | N/A | N/A | N/A |
| out_of_sequence | 24 | N/A | N/A | N/A |
| range_dropout | 0 | 0.240 | 0.173 | -0.068 |
| range_dropout | 1 | 0.333 | 0.372 | +0.039 |
| range_dropout | 2 | 0.247 | 0.218 | -0.029 |
| range_dropout | 3 | 0.268 | 0.225 | -0.043 |
| range_dropout | 4 | 0.225 | 0.180 | -0.045 |
| range_dropout | 5 | 0.237 | 0.235 | -0.002 |
| range_dropout | 6 | 0.201 | 0.213 | +0.012 |
| range_dropout | 7 | 0.229 | 0.305 | +0.076 |
| range_dropout | 8 | 0.234 | 0.234 | +0.000 |
| range_dropout | 9 | 0.295 | 0.258 | -0.036 |
| range_dropout | 10 | 0.274 | 0.230 | -0.043 |
| range_dropout | 11 | 0.248 | 0.237 | -0.011 |
| range_dropout | 12 | 0.227 | 0.189 | -0.038 |
| range_dropout | 13 | 0.266 | 0.151 | -0.115 |
| range_dropout | 14 | 0.173 | 0.168 | -0.005 |
| range_dropout | 15 | 0.258 | 0.163 | -0.095 |
| range_dropout | 16 | 0.211 | 0.166 | -0.046 |
| range_dropout | 17 | 0.251 | 0.247 | -0.003 |
| range_dropout | 18 | 0.199 | 0.203 | +0.005 |
| range_dropout | 19 | 0.318 | 0.298 | -0.019 |
| range_dropout | 20 | 0.260 | 0.201 | -0.058 |
| range_dropout | 21 | 0.242 | 0.228 | -0.014 |
| range_dropout | 22 | 0.277 | 0.188 | -0.089 |
| range_dropout | 23 | 0.248 | 0.201 | -0.047 |
| range_dropout | 24 | 0.236 | 0.188 | -0.047 |
| sensor_disagreement_large_bias | 0 | 0.168 | 0.168 | +0.000 |
| sensor_disagreement_large_bias | 1 | 0.226 | 0.202 | -0.024 |
| sensor_disagreement_large_bias | 2 | 0.200 | 0.198 | -0.002 |
| sensor_disagreement_large_bias | 3 | 0.268 | 0.300 | +0.033 |
| sensor_disagreement_large_bias | 4 | 0.225 | 0.225 | +0.000 |
| sensor_disagreement_large_bias | 5 | 0.224 | 0.224 | +0.000 |
| sensor_disagreement_large_bias | 6 | 0.186 | 0.176 | -0.010 |
| sensor_disagreement_large_bias | 7 | 0.223 | 0.223 | +0.000 |
| sensor_disagreement_large_bias | 8 | 0.244 | 0.210 | -0.034 |
| sensor_disagreement_large_bias | 9 | 0.334 | 0.345 | +0.011 |
| sensor_disagreement_large_bias | 10 | 0.187 | 0.188 | +0.001 |
| sensor_disagreement_large_bias | 11 | 0.225 | 0.225 | +0.000 |
| sensor_disagreement_large_bias | 12 | 0.159 | 0.159 | +0.000 |
| sensor_disagreement_large_bias | 13 | 0.147 | 0.150 | +0.003 |
| sensor_disagreement_large_bias | 14 | 0.190 | 0.190 | +0.000 |
| sensor_disagreement_large_bias | 15 | 0.196 | 0.196 | -0.000 |
| sensor_disagreement_large_bias | 16 | 0.187 | 0.187 | +0.000 |
| sensor_disagreement_large_bias | 17 | 0.267 | 0.259 | -0.009 |
| sensor_disagreement_large_bias | 18 | 0.225 | 0.227 | +0.002 |
| sensor_disagreement_large_bias | 19 | 0.214 | 0.214 | +0.000 |
| sensor_disagreement_large_bias | 20 | 0.164 | 0.147 | -0.017 |
| sensor_disagreement_large_bias | 21 | 0.262 | 0.261 | -0.001 |
| sensor_disagreement_large_bias | 22 | 0.209 | 0.233 | +0.024 |
| sensor_disagreement_large_bias | 23 | 0.189 | 0.166 | -0.023 |
| sensor_disagreement_large_bias | 24 | 0.211 | 0.211 | -0.001 |
| sensor_disagreement_within_gate | 0 | 0.168 | 0.275 | +0.108 |
| sensor_disagreement_within_gate | 1 | 0.226 | 0.263 | +0.037 |
| sensor_disagreement_within_gate | 2 | 0.200 | 0.274 | +0.074 |
| sensor_disagreement_within_gate | 3 | 0.268 | 0.320 | +0.052 |
| sensor_disagreement_within_gate | 4 | 0.225 | 0.337 | +0.111 |
| sensor_disagreement_within_gate | 5 | 0.224 | 0.231 | +0.007 |
| sensor_disagreement_within_gate | 6 | 0.186 | 0.237 | +0.051 |
| sensor_disagreement_within_gate | 7 | 0.223 | 0.323 | +0.100 |
| sensor_disagreement_within_gate | 8 | 0.244 | 0.285 | +0.041 |
| sensor_disagreement_within_gate | 9 | 0.334 | 0.345 | +0.011 |
| sensor_disagreement_within_gate | 10 | 0.187 | 0.242 | +0.055 |
| sensor_disagreement_within_gate | 11 | 0.225 | 0.309 | +0.085 |
| sensor_disagreement_within_gate | 12 | 0.159 | 0.323 | +0.164 |
| sensor_disagreement_within_gate | 13 | 0.147 | 0.209 | +0.062 |
| sensor_disagreement_within_gate | 14 | 0.190 | 0.194 | +0.004 |
| sensor_disagreement_within_gate | 15 | 0.196 | 0.264 | +0.068 |
| sensor_disagreement_within_gate | 16 | 0.187 | 0.219 | +0.033 |
| sensor_disagreement_within_gate | 17 | 0.267 | 0.342 | +0.075 |
| sensor_disagreement_within_gate | 18 | 0.225 | 0.250 | +0.025 |
| sensor_disagreement_within_gate | 19 | 0.214 | 0.328 | +0.114 |
| sensor_disagreement_within_gate | 20 | 0.164 | 0.262 | +0.099 |
| sensor_disagreement_within_gate | 21 | 0.262 | 0.244 | -0.018 |
| sensor_disagreement_within_gate | 22 | 0.209 | 0.308 | +0.099 |
| sensor_disagreement_within_gate | 23 | 0.189 | 0.203 | +0.014 |
| sensor_disagreement_within_gate | 24 | 0.211 | 0.248 | +0.037 |
| sensor_disagreement_within_gate_high | 0 | 0.168 | 0.311 | +0.144 |
| sensor_disagreement_within_gate_high | 1 | 0.226 | 0.259 | +0.033 |
| sensor_disagreement_within_gate_high | 2 | 0.200 | 0.216 | +0.016 |
| sensor_disagreement_within_gate_high | 3 | 0.268 | 0.333 | +0.065 |
| sensor_disagreement_within_gate_high | 4 | 0.225 | 0.326 | +0.100 |
| sensor_disagreement_within_gate_high | 5 | 0.224 | 0.330 | +0.106 |
| sensor_disagreement_within_gate_high | 6 | 0.186 | 0.225 | +0.040 |
| sensor_disagreement_within_gate_high | 7 | 0.223 | 0.260 | +0.037 |
| sensor_disagreement_within_gate_high | 8 | 0.244 | 0.311 | +0.067 |
| sensor_disagreement_within_gate_high | 9 | 0.334 | 0.322 | -0.011 |
| sensor_disagreement_within_gate_high | 10 | 0.187 | 0.239 | +0.051 |
| sensor_disagreement_within_gate_high | 11 | 0.225 | 0.290 | +0.065 |
| sensor_disagreement_within_gate_high | 12 | 0.159 | 0.299 | +0.140 |
| sensor_disagreement_within_gate_high | 13 | 0.147 | 0.202 | +0.055 |
| sensor_disagreement_within_gate_high | 14 | 0.190 | 0.233 | +0.042 |
| sensor_disagreement_within_gate_high | 15 | 0.196 | 0.276 | +0.080 |
| sensor_disagreement_within_gate_high | 16 | 0.187 | 0.281 | +0.094 |
| sensor_disagreement_within_gate_high | 17 | 0.267 | 0.336 | +0.068 |
| sensor_disagreement_within_gate_high | 18 | 0.225 | 0.265 | +0.040 |
| sensor_disagreement_within_gate_high | 19 | 0.214 | 0.310 | +0.096 |
| sensor_disagreement_within_gate_high | 20 | 0.164 | 0.297 | +0.133 |
| sensor_disagreement_within_gate_high | 21 | 0.262 | 0.269 | +0.007 |
| sensor_disagreement_within_gate_high | 22 | 0.209 | 0.285 | +0.076 |
| sensor_disagreement_within_gate_high | 23 | 0.189 | 0.203 | +0.014 |
| sensor_disagreement_within_gate_high | 24 | 0.211 | 0.275 | +0.063 |
| sensor_disagreement_within_gate_low | 0 | 0.168 | 0.265 | +0.098 |
| sensor_disagreement_within_gate_low | 1 | 0.226 | 0.216 | -0.010 |
| sensor_disagreement_within_gate_low | 2 | 0.200 | 0.218 | +0.018 |
| sensor_disagreement_within_gate_low | 3 | 0.268 | 0.302 | +0.035 |
| sensor_disagreement_within_gate_low | 4 | 0.225 | 0.322 | +0.097 |
| sensor_disagreement_within_gate_low | 5 | 0.224 | 0.282 | +0.057 |
| sensor_disagreement_within_gate_low | 6 | 0.186 | 0.224 | +0.038 |
| sensor_disagreement_within_gate_low | 7 | 0.223 | 0.319 | +0.096 |
| sensor_disagreement_within_gate_low | 8 | 0.244 | 0.298 | +0.054 |
| sensor_disagreement_within_gate_low | 9 | 0.334 | 0.297 | -0.037 |
| sensor_disagreement_within_gate_low | 10 | 0.187 | 0.225 | +0.038 |
| sensor_disagreement_within_gate_low | 11 | 0.225 | 0.318 | +0.094 |
| sensor_disagreement_within_gate_low | 12 | 0.159 | 0.308 | +0.149 |
| sensor_disagreement_within_gate_low | 13 | 0.147 | 0.194 | +0.047 |
| sensor_disagreement_within_gate_low | 14 | 0.190 | 0.175 | -0.015 |
| sensor_disagreement_within_gate_low | 15 | 0.196 | 0.249 | +0.053 |
| sensor_disagreement_within_gate_low | 16 | 0.187 | 0.213 | +0.026 |
| sensor_disagreement_within_gate_low | 17 | 0.267 | 0.288 | +0.020 |
| sensor_disagreement_within_gate_low | 18 | 0.225 | 0.227 | +0.002 |
| sensor_disagreement_within_gate_low | 19 | 0.214 | 0.262 | +0.048 |
| sensor_disagreement_within_gate_low | 20 | 0.164 | 0.244 | +0.080 |
| sensor_disagreement_within_gate_low | 21 | 0.262 | 0.245 | -0.017 |
| sensor_disagreement_within_gate_low | 22 | 0.209 | 0.259 | +0.051 |
| sensor_disagreement_within_gate_low | 23 | 0.189 | 0.179 | -0.009 |
| sensor_disagreement_within_gate_low | 24 | 0.211 | 0.260 | +0.049 |
| uncertainty_miscalibration | 0 | 0.352 | 0.413 | +0.061 |
| uncertainty_miscalibration | 1 | 0.370 | 0.346 | -0.024 |
| uncertainty_miscalibration | 2 | 0.385 | 0.410 | +0.025 |
| uncertainty_miscalibration | 3 | 0.432 | 0.463 | +0.031 |
| uncertainty_miscalibration | 4 | 0.501 | 0.383 | -0.118 |
| uncertainty_miscalibration | 5 | 0.472 | 0.430 | -0.042 |
| uncertainty_miscalibration | 6 | 0.427 | 0.342 | -0.086 |
| uncertainty_miscalibration | 7 | 0.483 | 0.444 | -0.039 |
| uncertainty_miscalibration | 8 | 0.453 | 0.418 | -0.035 |
| uncertainty_miscalibration | 9 | 0.453 | 0.426 | -0.028 |
| uncertainty_miscalibration | 10 | 0.334 | 0.356 | +0.022 |
| uncertainty_miscalibration | 11 | 0.486 | 0.438 | -0.048 |
| uncertainty_miscalibration | 12 | 0.554 | 0.456 | -0.098 |
| uncertainty_miscalibration | 13 | 0.405 | 0.407 | +0.002 |
| uncertainty_miscalibration | 14 | 0.406 | 0.427 | +0.021 |
| uncertainty_miscalibration | 15 | 0.412 | 0.442 | +0.029 |
| uncertainty_miscalibration | 16 | 0.508 | 0.360 | -0.148 |
| uncertainty_miscalibration | 17 | 0.519 | 0.490 | -0.029 |
| uncertainty_miscalibration | 18 | 0.394 | 0.312 | -0.083 |
| uncertainty_miscalibration | 19 | 0.491 | 0.473 | -0.017 |
| uncertainty_miscalibration | 20 | 0.351 | 0.425 | +0.073 |
| uncertainty_miscalibration | 21 | 0.342 | 0.450 | +0.108 |
| uncertainty_miscalibration | 22 | 0.411 | 0.365 | -0.046 |
| uncertainty_miscalibration | 23 | 0.379 | 0.300 | -0.079 |
| uncertainty_miscalibration | 24 | 0.465 | 0.453 | -0.012 |
| vision_dropout | 0 | 0.168 | 0.172 | +0.005 |
| vision_dropout | 1 | 0.226 | 0.187 | -0.038 |
| vision_dropout | 2 | 0.200 | 0.195 | -0.005 |
| vision_dropout | 3 | 0.268 | 0.255 | -0.013 |
| vision_dropout | 4 | 0.225 | 0.253 | +0.027 |
| vision_dropout | 5 | 0.224 | 0.225 | +0.001 |
| vision_dropout | 6 | 0.186 | 0.156 | -0.030 |
| vision_dropout | 7 | 0.223 | 0.229 | +0.006 |
| vision_dropout | 8 | 0.244 | 0.277 | +0.034 |
| vision_dropout | 9 | 0.334 | 0.292 | -0.042 |
| vision_dropout | 10 | 0.187 | 0.137 | -0.051 |
| vision_dropout | 11 | 0.225 | 0.212 | -0.013 |
| vision_dropout | 12 | 0.159 | 0.213 | +0.055 |
| vision_dropout | 13 | 0.147 | 0.167 | +0.020 |
| vision_dropout | 14 | 0.190 | 0.168 | -0.022 |
| vision_dropout | 15 | 0.196 | 0.240 | +0.044 |
| vision_dropout | 16 | 0.187 | 0.196 | +0.009 |
| vision_dropout | 17 | 0.267 | 0.321 | +0.054 |
| vision_dropout | 18 | 0.225 | 0.231 | +0.007 |
| vision_dropout | 19 | 0.214 | 0.219 | +0.006 |
| vision_dropout | 20 | 0.164 | 0.133 | -0.030 |
| vision_dropout | 21 | 0.262 | 0.220 | -0.042 |
| vision_dropout | 22 | 0.209 | 0.165 | -0.044 |
| vision_dropout | 23 | 0.189 | 0.137 | -0.052 |
| vision_dropout | 24 | 0.211 | 0.199 | -0.012 |

## Findings

- On the aggregate position RMSE, fused was better in 8 scenario(s),
  worse in 3 scenario(s), and within 0.01 m in 3 scenario(s).
- Fused precision was higher in 0 scenario(s) and lower
  in 14. Fused 95% coverage was higher in 2
  scenario(s) and lower in 12. Accuracy alone does not
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
