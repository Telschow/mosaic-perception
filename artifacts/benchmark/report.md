# Mosaic Benchmark Report

This report is generated from the code in this repository. It contains no
hand-edited numbers and no wall-clock timestamps, so repeated runs with the
same seeds and commit are byte-identical.

## Code and protocol

- Package version: `0.1.0`
- Git commit: `f31b8b89fd2c5096ed7c34e65b527ba34821d569`
- Seeds: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24
- Seed group: development
- Duration: 10.0 s at dt=0.1 s
- Objects per world: 3
- Methods: range-only (range-bearing sensor only) and fused (range-bearing + vision bearing)
- Paired: same world states and the same range-sensor random stream per seed; the fused run only adds vision observations.
- Evaluation matching gate: 2.00 m, one-to-one Hungarian assignment per timestamp, preferring each object's previous track while it stays inside the gate.
- Accuracy denominators: matched sample pairs. Recall denominator: all ground-truth object samples. Precision denominator: all confirmed/coasting track samples.
- 95% position coverage threshold: chi-square(2, 0.95) = 5.991.

## Aggregate results

Values are mean ± sample standard deviation across seeds. `N/A` means the
metric was not defined for any seed (for example, no matched tracks); it is
never a fabricated zero.

| Scenario | Method | Pos RMSE (m) | Pos RMSE, distance-only matcher (m) | Vel RMSE (m/s) | Recall | Precision | Cov95 | Matched/GT (mean) | Unmatched confirmed tracks | Duplicate tracks | ID switches | ID switches (distance-only) | Fragmentation | MOTA | IDF1 | GOSPA (p=1, m) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crossing_targets | range_only | 0.151 ± 0.035 | 0.148 | 0.148 | 0.977 | 0.856 | 0.920 | 296/303 | 3.8 | 3.8 | 1.2 | 4.4 | 0.0 | 0.804 | 0.852 | 0.924 |
| crossing_targets | fused | 0.160 ± 0.058 | 0.146 | 0.116 | 0.979 | 0.718 | 0.859 | 297/303 | 5.6 | 5.6 | 0.8 | 6.8 | 0.0 | 0.573 | 0.790 | 1.614 |
| delivery_delay | range_only | 0.308 ± 0.046 | 0.285 | 0.327 | 0.968 | 0.807 | 0.512 | 293/303 | 3.8 | 3.8 | 6.9 | 10.6 | 0.1 | 0.708 | 0.592 | 1.542 |
| delivery_delay | fused | 0.329 ± 0.062 | 0.268 | 0.311 | 0.970 | 0.660 | 0.338 | 294/303 | 6.8 | 6.8 | 5.1 | 11.2 | 0.0 | 0.437 | 0.591 | 2.330 |
| dense_clutter | range_only | 0.242 ± 0.051 | 0.219 | 0.317 | 0.979 | 0.816 | 0.805 | 297/303 | 3.6 | 3.6 | 6.7 | 10.0 | 0.0 | 0.732 | 0.621 | 1.281 |
| dense_clutter | fused | 0.285 ± 0.091 | 0.206 | 0.307 | 0.979 | 0.338 | 0.662 | 297/303 | 73.4 | 8.6 | 5.0 | 10.9 | 0.0 | -0.977 | 0.376 | 6.397 |
| false_observations | range_only | 0.230 ± 0.051 | 0.208 | 0.306 | 0.977 | 0.840 | 0.833 | 296/303 | 3.0 | 3.0 | 6.6 | 10.0 | 0.0 | 0.765 | 0.611 | 1.145 |
| false_observations | fused | 0.247 ± 0.064 | 0.189 | 0.309 | 0.979 | 0.639 | 0.743 | 297/303 | 12.5 | 6.0 | 5.2 | 10.3 | 0.0 | 0.399 | 0.577 | 2.212 |
| measurement_bias | range_only | 1.641 ± 0.032 | 1.594 | 0.521 | 0.889 | 0.715 | 0.001 | 269/303 | 1.7 | 1.1 | 11.4 | 13.7 | 5.3 | 0.495 | 0.299 | 5.590 |
| measurement_bias | fused | 1.620 ± 0.029 | 1.556 | 0.498 | 0.909 | 0.599 | 0.006 | 275/303 | 3.0 | 1.8 | 11.0 | 14.1 | 4.1 | 0.255 | 0.291 | 6.283 |
| moving_observer | range_only | 0.241 ± 0.077 | 0.218 | 0.345 | 0.975 | 0.833 | 0.832 | 296/303 | 3.6 | 3.6 | 5.8 | 8.4 | 0.1 | 0.754 | 0.665 | 1.219 |
| moving_observer | fused | 0.260 ± 0.096 | 0.188 | 0.312 | 0.978 | 0.714 | 0.751 | 296/303 | 6.3 | 6.2 | 4.4 | 8.2 | 0.0 | 0.557 | 0.640 | 1.749 |
| nominal | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| nominal | fused | 0.253 ± 0.083 | 0.195 | 0.301 | 0.980 | 0.696 | 0.749 | 297/303 | 6.0 | 5.9 | 4.7 | 10.6 | 0.0 | 0.520 | 0.612 | 1.865 |
| out_of_sequence | range_only | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| out_of_sequence | fused | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| range_dropout | range_only | 0.253 ± 0.040 | 0.248 | 0.349 | 0.881 | 0.972 | 0.890 | 267/303 | 0.5 | 0.5 | 7.8 | 8.2 | 5.0 | 0.828 | 0.541 | 0.982 |
| range_dropout | fused | 0.268 ± 0.083 | 0.219 | 0.296 | 0.970 | 0.816 | 0.808 | 294/303 | 3.2 | 3.2 | 4.4 | 7.2 | 0.3 | 0.729 | 0.680 | 1.275 |
| sensor_disagreement_large_bias | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_large_bias | fused | 0.239 ± 0.077 | 0.211 | 0.318 | 0.977 | 0.807 | 0.806 | 296/303 | 4.3 | 3.9 | 5.9 | 8.6 | 0.0 | 0.715 | 0.635 | 1.321 |
| sensor_disagreement_within_gate | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_within_gate | fused | 0.381 ± 0.097 | 0.273 | 0.395 | 0.979 | 0.560 | 0.284 | 297/303 | 9.6 | 9.6 | 8.0 | 19.1 | 0.0 | 0.169 | 0.490 | 3.124 |
| sensor_disagreement_within_gate_high | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_within_gate_high | fused | 0.467 ± 0.096 | 0.278 | 0.465 | 0.978 | 0.535 | 0.317 | 296/303 | 9.4 | 9.4 | 8.6 | 17.6 | 0.0 | 0.092 | 0.476 | 3.339 |
| sensor_disagreement_within_gate_low | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_within_gate_low | fused | 0.335 ± 0.067 | 0.256 | 0.350 | 0.979 | 0.617 | 0.332 | 297/303 | 7.9 | 7.8 | 6.1 | 14.7 | 0.0 | 0.332 | 0.546 | 2.612 |
| uncertainty_miscalibration | range_only | 0.461 ± 0.066 | 0.431 | 0.627 | 0.521 | 0.832 | 0.089 | 158/303 | 2.8 | 2.8 | 25.6 | 28.2 | 15.6 | 0.330 | 0.136 | 2.339 |
| uncertainty_miscalibration | fused | 0.525 ± 0.068 | 0.409 | 0.656 | 0.932 | 0.445 | 0.106 | 282/303 | 39.3 | 38.9 | 34.8 | 56.6 | 3.6 | -0.353 | 0.174 | 4.636 |
| vision_dropout | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| vision_dropout | fused | 0.241 ± 0.071 | 0.208 | 0.296 | 0.978 | 0.726 | 0.750 | 296/303 | 5.6 | 5.6 | 5.0 | 8.6 | 0.0 | 0.582 | 0.633 | 1.713 |

## Paired differences (fused minus range-only)

Mean per-seed difference with a two-sided 95% t interval over seeds. Seeds with
an undefined value on either side are dropped (`n` is the number kept). A
negative RMSE difference favours fusion; for recall, precision and coverage a
positive one does. The interval describes seed-to-seed variation in this
synthetic setup and is not a claim about other worlds.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| crossing_targets | position_rmse | 25 | +0.009 | [-0.008, +0.026] |
| crossing_targets | position_rmse_distance_only | 25 | -0.002 | [-0.015, +0.011] |
| crossing_targets | recall | 25 | +0.002 | [+0.000, +0.003] |
| crossing_targets | precision | 25 | -0.138 | [-0.171, -0.106] |
| crossing_targets | position_coverage_95 | 25 | -0.061 | [-0.097, -0.025] |
| crossing_targets | mota | 25 | -0.230 | [-0.289, -0.172] |
| crossing_targets | idf1 | 25 | -0.062 | [-0.100, -0.025] |
| crossing_targets | gospa_p1 | 25 | +0.690 | [+0.505, +0.874] |
| delivery_delay | position_rmse | 25 | +0.020 | [-0.005, +0.046] |
| delivery_delay | position_rmse_distance_only | 25 | -0.017 | [-0.032, -0.003] |
| delivery_delay | recall | 25 | +0.001 | [+0.000, +0.002] |
| delivery_delay | precision | 25 | -0.147 | [-0.174, -0.120] |
| delivery_delay | position_coverage_95 | 25 | -0.173 | [-0.238, -0.109] |
| delivery_delay | mota | 25 | -0.270 | [-0.331, -0.210] |
| delivery_delay | idf1 | 25 | -0.001 | [-0.037, +0.035] |
| delivery_delay | gospa_p1 | 25 | +0.788 | [+0.586, +0.991] |
| dense_clutter | position_rmse | 25 | +0.043 | [+0.013, +0.073] |
| dense_clutter | position_rmse_distance_only | 25 | -0.013 | [-0.024, -0.002] |
| dense_clutter | recall | 25 | +0.001 | [-0.000, +0.001] |
| dense_clutter | precision | 25 | -0.478 | [-0.499, -0.457] |
| dense_clutter | position_coverage_95 | 25 | -0.143 | [-0.183, -0.103] |
| dense_clutter | mota | 25 | -1.709 | [-1.817, -1.602] |
| dense_clutter | idf1 | 25 | -0.246 | [-0.277, -0.214] |
| dense_clutter | gospa_p1 | 25 | +5.115 | [+4.779, +5.452] |
| false_observations | position_rmse | 25 | +0.017 | [-0.008, +0.042] |
| false_observations | position_rmse_distance_only | 25 | -0.018 | [-0.035, -0.002] |
| false_observations | recall | 25 | +0.002 | [+0.001, +0.004] |
| false_observations | precision | 25 | -0.202 | [-0.238, -0.165] |
| false_observations | position_coverage_95 | 25 | -0.090 | [-0.140, -0.040] |
| false_observations | mota | 25 | -0.366 | [-0.435, -0.297] |
| false_observations | idf1 | 25 | -0.034 | [-0.075, +0.007] |
| false_observations | gospa_p1 | 25 | +1.068 | [+0.841, +1.294] |
| measurement_bias | position_rmse | 25 | -0.021 | [-0.034, -0.008] |
| measurement_bias | position_rmse_distance_only | 25 | -0.038 | [-0.053, -0.024] |
| measurement_bias | recall | 25 | +0.020 | [+0.007, +0.033] |
| measurement_bias | precision | 25 | -0.117 | [-0.137, -0.096] |
| measurement_bias | position_coverage_95 | 25 | +0.005 | [+0.002, +0.008] |
| measurement_bias | mota | 25 | -0.239 | [-0.289, -0.190] |
| measurement_bias | idf1 | 25 | -0.008 | [-0.021, +0.005] |
| measurement_bias | gospa_p1 | 25 | +0.693 | [+0.573, +0.814] |
| moving_observer | position_rmse | 25 | +0.019 | [-0.015, +0.052] |
| moving_observer | position_rmse_distance_only | 25 | -0.029 | [-0.044, -0.014] |
| moving_observer | recall | 25 | +0.002 | [+0.000, +0.004] |
| moving_observer | precision | 25 | -0.119 | [-0.150, -0.089] |
| moving_observer | position_coverage_95 | 25 | -0.080 | [-0.129, -0.031] |
| moving_observer | mota | 25 | -0.197 | [-0.249, -0.144] |
| moving_observer | idf1 | 25 | -0.024 | [-0.057, +0.009] |
| moving_observer | gospa_p1 | 25 | +0.530 | [+0.356, +0.704] |
| nominal | position_rmse | 25 | +0.020 | [-0.004, +0.044] |
| nominal | position_rmse_distance_only | 25 | -0.018 | [-0.031, -0.005] |
| nominal | recall | 25 | +0.003 | [+0.001, +0.004] |
| nominal | precision | 25 | -0.130 | [-0.162, -0.099] |
| nominal | position_coverage_95 | 25 | -0.064 | [-0.109, -0.018] |
| nominal | mota | 25 | -0.226 | [-0.286, -0.167] |
| nominal | idf1 | 25 | -0.027 | [-0.064, +0.010] |
| nominal | gospa_p1 | 25 | +0.635 | [+0.447, +0.822] |
| out_of_sequence | position_rmse | 0 | N/A | N/A |
| out_of_sequence | position_rmse_distance_only | 0 | N/A | N/A |
| out_of_sequence | recall | 25 | +0.000 | [+0.000, +0.000] |
| out_of_sequence | precision | 0 | N/A | N/A |
| out_of_sequence | position_coverage_95 | 0 | N/A | N/A |
| out_of_sequence | mota | 25 | +0.000 | [+0.000, +0.000] |
| out_of_sequence | idf1 | 25 | +0.000 | [+0.000, +0.000] |
| out_of_sequence | gospa_p1 | 25 | +0.000 | [+0.000, +0.000] |
| range_dropout | position_rmse | 25 | +0.015 | [-0.016, +0.046] |
| range_dropout | position_rmse_distance_only | 25 | -0.029 | [-0.046, -0.012] |
| range_dropout | recall | 25 | +0.090 | [+0.074, +0.105] |
| range_dropout | precision | 25 | -0.156 | [-0.182, -0.129] |
| range_dropout | position_coverage_95 | 25 | -0.082 | [-0.117, -0.047] |
| range_dropout | mota | 25 | -0.100 | [-0.139, -0.061] |
| range_dropout | idf1 | 25 | +0.139 | [+0.087, +0.191] |
| range_dropout | gospa_p1 | 25 | +0.292 | [+0.171, +0.413] |
| sensor_disagreement_large_bias | position_rmse | 25 | +0.006 | [-0.004, +0.016] |
| sensor_disagreement_large_bias | position_rmse_distance_only | 25 | -0.002 | [-0.007, +0.004] |
| sensor_disagreement_large_bias | recall | 25 | +0.000 | [-0.000, +0.000] |
| sensor_disagreement_large_bias | precision | 25 | -0.018 | [-0.038, +0.001] |
| sensor_disagreement_large_bias | position_coverage_95 | 25 | -0.007 | [-0.022, +0.009] |
| sensor_disagreement_large_bias | mota | 25 | -0.030 | [-0.064, +0.004] |
| sensor_disagreement_large_bias | idf1 | 25 | -0.004 | [-0.015, +0.007] |
| sensor_disagreement_large_bias | gospa_p1 | 25 | +0.090 | [-0.013, +0.194] |
| sensor_disagreement_within_gate | position_rmse | 25 | +0.148 | [+0.117, +0.178] |
| sensor_disagreement_within_gate | position_rmse_distance_only | 25 | +0.060 | [+0.043, +0.078] |
| sensor_disagreement_within_gate | recall | 25 | +0.002 | [+0.001, +0.003] |
| sensor_disagreement_within_gate | precision | 25 | -0.265 | [-0.292, -0.239] |
| sensor_disagreement_within_gate | position_coverage_95 | 25 | -0.529 | [-0.599, -0.458] |
| sensor_disagreement_within_gate | mota | 25 | -0.577 | [-0.641, -0.512] |
| sensor_disagreement_within_gate | idf1 | 25 | -0.149 | [-0.191, -0.108] |
| sensor_disagreement_within_gate | gospa_p1 | 25 | +1.894 | [+1.681, +2.106] |
| sensor_disagreement_within_gate_high | position_rmse | 25 | +0.233 | [+0.187, +0.280] |
| sensor_disagreement_within_gate_high | position_rmse_distance_only | 25 | +0.065 | [+0.048, +0.082] |
| sensor_disagreement_within_gate_high | recall | 25 | +0.001 | [-0.000, +0.002] |
| sensor_disagreement_within_gate_high | precision | 25 | -0.291 | [-0.314, -0.267] |
| sensor_disagreement_within_gate_high | position_coverage_95 | 25 | -0.496 | [-0.582, -0.409] |
| sensor_disagreement_within_gate_high | mota | 25 | -0.654 | [-0.709, -0.599] |
| sensor_disagreement_within_gate_high | idf1 | 25 | -0.163 | [-0.197, -0.128] |
| sensor_disagreement_within_gate_high | gospa_p1 | 25 | +2.108 | [+1.926, +2.290] |
| sensor_disagreement_within_gate_low | position_rmse | 25 | +0.101 | [+0.070, +0.133] |
| sensor_disagreement_within_gate_low | position_rmse_distance_only | 25 | +0.042 | [+0.024, +0.061] |
| sensor_disagreement_within_gate_low | recall | 25 | +0.002 | [+0.001, +0.003] |
| sensor_disagreement_within_gate_low | precision | 25 | -0.209 | [-0.241, -0.177] |
| sensor_disagreement_within_gate_low | position_coverage_95 | 25 | -0.481 | [-0.538, -0.424] |
| sensor_disagreement_within_gate_low | mota | 25 | -0.414 | [-0.487, -0.340] |
| sensor_disagreement_within_gate_low | idf1 | 25 | -0.093 | [-0.127, -0.060] |
| sensor_disagreement_within_gate_low | gospa_p1 | 25 | +1.381 | [+1.131, +1.631] |
| uncertainty_miscalibration | position_rmse | 25 | +0.064 | [+0.031, +0.097] |
| uncertainty_miscalibration | position_rmse_distance_only | 25 | -0.022 | [-0.048, +0.003] |
| uncertainty_miscalibration | recall | 25 | +0.411 | [+0.387, +0.435] |
| uncertainty_miscalibration | precision | 25 | -0.386 | [-0.405, -0.367] |
| uncertainty_miscalibration | position_coverage_95 | 25 | +0.017 | [-0.011, +0.045] |
| uncertainty_miscalibration | mota | 25 | -0.682 | [-0.738, -0.627] |
| uncertainty_miscalibration | idf1 | 25 | +0.037 | [+0.017, +0.058] |
| uncertainty_miscalibration | gospa_p1 | 25 | +2.297 | [+2.133, +2.461] |
| vision_dropout | position_rmse | 25 | +0.008 | [-0.008, +0.024] |
| vision_dropout | position_rmse_distance_only | 25 | -0.005 | [-0.018, +0.008] |
| vision_dropout | recall | 25 | +0.001 | [+0.000, +0.002] |
| vision_dropout | precision | 25 | -0.100 | [-0.124, -0.075] |
| vision_dropout | position_coverage_95 | 25 | -0.063 | [-0.105, -0.021] |
| vision_dropout | mota | 25 | -0.163 | [-0.208, -0.119] |
| vision_dropout | idf1 | 25 | -0.006 | [-0.036, +0.025] |
| vision_dropout | gospa_p1 | 25 | +0.482 | [+0.324, +0.641] |

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
| crossing_targets | fused | 0.990 | 0.990 | 0.657 | 194.9 |
| delivery_delay | range_only | N/A | N/A | 0.000 | 0.0 |
| delivery_delay | fused | 0.998 | 0.999 | 0.665 | 195.5 |
| dense_clutter | range_only | N/A | N/A | 0.000 | 0.0 |
| dense_clutter | fused | 0.998 | 0.998 | 0.632 | 187.7 |
| false_observations | range_only | N/A | N/A | 0.000 | 0.0 |
| false_observations | fused | 0.998 | 0.998 | 0.654 | 194.2 |
| measurement_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| measurement_bias | fused | 0.997 | 0.996 | 0.661 | 181.9 |
| moving_observer | range_only | N/A | N/A | 0.000 | 0.0 |
| moving_observer | fused | 0.999 | 0.999 | 0.665 | 197.1 |
| nominal | range_only | N/A | N/A | 0.000 | 0.0 |
| nominal | fused | 0.999 | 0.998 | 0.662 | 196.6 |
| out_of_sequence | range_only | N/A | N/A | N/A | 0.0 |
| out_of_sequence | fused | N/A | N/A | N/A | 0.0 |
| range_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| range_dropout | fused | 0.999 | 0.999 | 0.665 | 195.6 |
| sensor_disagreement_large_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_large_bias | fused | 0.429 | 0.320 | 0.043 | 12.8 |
| sensor_disagreement_within_gate | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate | fused | 0.995 | 0.994 | 0.651 | 193.3 |
| sensor_disagreement_within_gate_high | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_high | fused | 0.986 | 0.983 | 0.635 | 188.4 |
| sensor_disagreement_within_gate_low | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_low | fused | 0.994 | 0.991 | 0.661 | 196.0 |
| uncertainty_miscalibration | range_only | N/A | N/A | 0.000 | 0.0 |
| uncertainty_miscalibration | fused | 0.998 | 0.997 | 0.637 | 179.8 |
| vision_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| vision_dropout | fused | 0.999 | 0.999 | 0.658 | 195.0 |

## Estimator consistency (NEES and NIS)

Statistics per degree of freedom, pooled over seeds; the nominal value for a
consistent filter is 1.0 and the bracket is the two-sided 95% chi-square interval
for the pooled degrees of freedom. `within`, `above` or `below` says where the value
falls: above means overconfident, below means underconfident.

- NEES (position and velocity, 2 DOF each) uses only samples matched to a ground-truth
  object inside the 2 m matching gate, so it is conditioned on that gate;
  `GT samples outside gate` is the mean number of ground-truth samples excluded.
- NIS uses the filter's own innovations for every applied update, with no ground
  truth. Updates exist only after gating, so NIS is truncated and sits slightly
  below 1.0 even for a correct filter.
- Samples within one track are correlated and seeds share the scenario, so the
  intervals assume more independence than there is and are optimistic.

| Scenario | Method | Position NEES per DOF | Velocity NEES per DOF | NIS per DOF | NEES samples (mean) | NIS updates (mean) | GT samples outside gate |
|---|---|---|---|---|---|---|---|
| crossing_targets | range_only | 1.350 [0.977, 1.023] above | 0.556 [0.977, 1.023] below | 0.759 [0.981, 1.019] below | 296 | 276.6 | 7 |
| crossing_targets | fused | 2.557 [0.977, 1.023] above | 0.558 [0.977, 1.023] below | 0.708 [0.983, 1.017] below | 297 | 542.7 | 6 |
| delivery_delay | range_only | 4.936 [0.977, 1.023] above | 2.219 [0.977, 1.023] above | 0.800 [0.980, 1.020] below | 293 | 265.9 | 10 |
| delivery_delay | fused | 11.338 [0.977, 1.023] above | 2.732 [0.977, 1.023] above | 0.745 [0.983, 1.017] below | 294 | 521.6 | 9 |
| dense_clutter | range_only | 1.872 [0.977, 1.023] above | 1.834 [0.977, 1.023] above | 0.830 [0.981, 1.019] below | 297 | 282.0 | 6 |
| dense_clutter | fused | 3.020 [0.977, 1.023] above | 2.326 [0.977, 1.023] above | 0.835 [0.985, 1.015] below | 297 | 829.0 | 6 |
| false_observations | range_only | 1.709 [0.977, 1.023] above | 1.784 [0.977, 1.023] above | 0.829 [0.981, 1.019] below | 296 | 273.9 | 7 |
| false_observations | fused | 2.429 [0.977, 1.023] above | 2.203 [0.977, 1.023] above | 0.780 [0.983, 1.017] below | 297 | 570.3 | 6 |
| measurement_bias | range_only | 75.000 [0.976, 1.024] above | 12.601 [0.976, 1.024] above | 0.839 [0.981, 1.020] below | 269 | 269.0 | 34 |
| measurement_bias | fused | 72.993 [0.977, 1.024] above | 12.577 [0.977, 1.024] above | 0.788 [0.983, 1.017] below | 275 | 530.3 | 28 |
| moving_observer | range_only | 1.814 [0.977, 1.023] above | 1.813 [0.977, 1.023] above | 0.818 [0.981, 1.020] below | 296 | 271.1 | 7 |
| moving_observer | fused | 2.553 [0.977, 1.023] above | 2.264 [0.977, 1.023] above | 0.781 [0.983, 1.017] below | 296 | 532.1 | 7 |
| nominal | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| nominal | fused | 2.479 [0.977, 1.023] above | 2.193 [0.977, 1.023] above | 0.769 [0.983, 1.017] below | 297 | 532.9 | 6 |
| out_of_sequence | range_only | N/A | N/A | N/A | 0 | 0.0 | 303 |
| out_of_sequence | fused | N/A | N/A | 2.053 [0.001, 5.024] within | 0 | 0.0 | 303 |
| range_dropout | range_only | 1.499 [0.976, 1.024] above | 1.635 [0.976, 1.024] above | 0.832 [0.974, 1.026] below | 267 | 150.3 | 36 |
| range_dropout | fused | 2.127 [0.977, 1.023] above | 2.153 [0.977, 1.023] above | 0.793 [0.979, 1.021] below | 294 | 408.6 | 9 |
| sensor_disagreement_large_bias | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_large_bias | fused | 2.885 [0.977, 1.023] above | 2.031 [0.977, 1.023] above | 0.825 [0.981, 1.019] below | 296 | 282.0 | 7 |
| sensor_disagreement_within_gate | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_within_gate | fused | 10.255 [0.977, 1.023] above | 2.849 [0.977, 1.023] above | 0.827 [0.983, 1.017] below | 297 | 509.9 | 6 |
| sensor_disagreement_within_gate_high | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_within_gate_high | fused | 15.394 [0.977, 1.023] above | 3.436 [0.977, 1.023] above | 0.842 [0.983, 1.017] below | 296 | 487.4 | 7 |
| sensor_disagreement_within_gate_low | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_within_gate_low | fused | 6.390 [0.977, 1.023] above | 2.504 [0.977, 1.023] above | 0.810 [0.983, 1.017] below | 297 | 523.8 | 6 |
| uncertainty_miscalibration | range_only | 26.776 [0.969, 1.031] above | 9.143 [0.969, 1.031] above | 1.051 [0.974, 1.026] above | 158 | 152.7 | 145 |
| uncertainty_miscalibration | fused | 31.724 [0.977, 1.023] above | 9.849 [0.977, 1.023] above | 1.006 [0.979, 1.022] within | 282 | 379.5 | 21 |
| vision_dropout | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| vision_dropout | fused | 2.253 [0.977, 1.023] above | 1.989 [0.977, 1.023] above | 0.789 [0.982, 1.018] below | 296 | 404.9 | 7 |

## Duplicate-track sensitivity to the matching gate

Mean number of duplicate tracks per seed when the evaluation matching gate is
1.0, 2.0 or 3.0 m. The three gates were chosen before running (see the project issue
tracker). The 2.0 m column is the headline gate used everywhere else in this
report when it is the evaluator gate; the others show how much the
duplicate count depends on that choice, not which gate is correct.

| Scenario | Method | 1.0 m | 2.0 m | 3.0 m |
|---|---|---|---|---|
| crossing_targets | range_only | 3.7 | 3.8 | 3.8 |
| crossing_targets | fused | 5.2 | 5.6 | 5.6 |
| delivery_delay | range_only | 3.6 | 3.8 | 3.8 |
| delivery_delay | fused | 5.9 | 6.8 | 6.8 |
| dense_clutter | range_only | 3.6 | 3.6 | 3.6 |
| dense_clutter | fused | 6.8 | 8.6 | 10.2 |
| false_observations | range_only | 2.9 | 3.0 | 3.0 |
| false_observations | fused | 5.2 | 6.0 | 6.2 |
| measurement_bias | range_only | 0.0 | 1.1 | 2.5 |
| measurement_bias | fused | 0.0 | 1.8 | 5.7 |
| moving_observer | range_only | 3.6 | 3.6 | 3.6 |
| moving_observer | fused | 5.6 | 6.2 | 6.3 |
| nominal | range_only | 3.0 | 3.1 | 3.1 |
| nominal | fused | 5.4 | 5.9 | 6.0 |
| out_of_sequence | range_only | 0.0 | 0.0 | 0.0 |
| out_of_sequence | fused | 0.0 | 0.0 | 0.0 |
| range_dropout | range_only | 0.4 | 0.5 | 0.5 |
| range_dropout | fused | 2.6 | 3.2 | 3.2 |
| sensor_disagreement_large_bias | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_large_bias | fused | 3.4 | 3.9 | 4.2 |
| sensor_disagreement_within_gate | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_within_gate | fused | 8.8 | 9.6 | 9.6 |
| sensor_disagreement_within_gate_high | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_within_gate_high | fused | 7.9 | 9.4 | 9.4 |
| sensor_disagreement_within_gate_low | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_within_gate_low | fused | 7.0 | 7.8 | 7.9 |
| uncertainty_miscalibration | range_only | 2.8 | 2.8 | 2.7 |
| uncertainty_miscalibration | fused | 34.2 | 38.9 | 39.3 |
| vision_dropout | range_only | 3.0 | 3.1 | 3.1 |
| vision_dropout | fused | 5.2 | 5.6 | 5.6 |

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
| crossing_targets | 0 | 0.112 | 0.119 | +0.006 |
| crossing_targets | 1 | 0.121 | 0.090 | -0.032 |
| crossing_targets | 2 | 0.150 | 0.253 | +0.104 |
| crossing_targets | 3 | 0.145 | 0.191 | +0.046 |
| crossing_targets | 4 | 0.134 | 0.132 | -0.002 |
| crossing_targets | 5 | 0.209 | 0.291 | +0.082 |
| crossing_targets | 6 | 0.136 | 0.127 | -0.009 |
| crossing_targets | 7 | 0.211 | 0.306 | +0.094 |
| crossing_targets | 8 | 0.174 | 0.188 | +0.015 |
| crossing_targets | 9 | 0.240 | 0.200 | -0.040 |
| crossing_targets | 10 | 0.139 | 0.143 | +0.004 |
| crossing_targets | 11 | 0.127 | 0.166 | +0.039 |
| crossing_targets | 12 | 0.126 | 0.163 | +0.036 |
| crossing_targets | 13 | 0.141 | 0.107 | -0.034 |
| crossing_targets | 14 | 0.114 | 0.120 | +0.006 |
| crossing_targets | 15 | 0.179 | 0.160 | -0.018 |
| crossing_targets | 16 | 0.113 | 0.108 | -0.005 |
| crossing_targets | 17 | 0.213 | 0.219 | +0.006 |
| crossing_targets | 18 | 0.132 | 0.135 | +0.004 |
| crossing_targets | 19 | 0.141 | 0.174 | +0.033 |
| crossing_targets | 20 | 0.112 | 0.097 | -0.015 |
| crossing_targets | 21 | 0.160 | 0.157 | -0.004 |
| crossing_targets | 22 | 0.135 | 0.135 | -0.001 |
| crossing_targets | 23 | 0.145 | 0.107 | -0.038 |
| crossing_targets | 24 | 0.156 | 0.105 | -0.051 |
| delivery_delay | 0 | 0.318 | 0.344 | +0.026 |
| delivery_delay | 1 | 0.285 | 0.352 | +0.067 |
| delivery_delay | 2 | 0.290 | 0.243 | -0.047 |
| delivery_delay | 3 | 0.272 | 0.321 | +0.049 |
| delivery_delay | 4 | 0.263 | 0.289 | +0.026 |
| delivery_delay | 5 | 0.392 | 0.280 | -0.112 |
| delivery_delay | 6 | 0.256 | 0.375 | +0.119 |
| delivery_delay | 7 | 0.218 | 0.326 | +0.108 |
| delivery_delay | 8 | 0.328 | 0.338 | +0.010 |
| delivery_delay | 9 | 0.343 | 0.337 | -0.006 |
| delivery_delay | 10 | 0.325 | 0.454 | +0.129 |
| delivery_delay | 11 | 0.261 | 0.272 | +0.011 |
| delivery_delay | 12 | 0.286 | 0.237 | -0.049 |
| delivery_delay | 13 | 0.291 | 0.264 | -0.026 |
| delivery_delay | 14 | 0.286 | 0.304 | +0.018 |
| delivery_delay | 15 | 0.305 | 0.401 | +0.095 |
| delivery_delay | 16 | 0.294 | 0.295 | +0.001 |
| delivery_delay | 17 | 0.428 | 0.441 | +0.013 |
| delivery_delay | 18 | 0.314 | 0.422 | +0.108 |
| delivery_delay | 19 | 0.338 | 0.356 | +0.017 |
| delivery_delay | 20 | 0.272 | 0.304 | +0.032 |
| delivery_delay | 21 | 0.323 | 0.305 | -0.018 |
| delivery_delay | 22 | 0.379 | 0.412 | +0.033 |
| delivery_delay | 23 | 0.311 | 0.309 | -0.003 |
| delivery_delay | 24 | 0.329 | 0.235 | -0.093 |
| dense_clutter | 0 | 0.286 | 0.477 | +0.191 |
| dense_clutter | 1 | 0.199 | 0.375 | +0.176 |
| dense_clutter | 2 | 0.192 | 0.196 | +0.004 |
| dense_clutter | 3 | 0.246 | 0.309 | +0.064 |
| dense_clutter | 4 | 0.290 | 0.284 | -0.007 |
| dense_clutter | 5 | 0.259 | 0.366 | +0.107 |
| dense_clutter | 6 | 0.236 | 0.222 | -0.014 |
| dense_clutter | 7 | 0.192 | 0.213 | +0.021 |
| dense_clutter | 8 | 0.304 | 0.273 | -0.031 |
| dense_clutter | 9 | 0.314 | 0.366 | +0.051 |
| dense_clutter | 10 | 0.208 | 0.194 | -0.014 |
| dense_clutter | 11 | 0.298 | 0.271 | -0.027 |
| dense_clutter | 12 | 0.210 | 0.191 | -0.019 |
| dense_clutter | 13 | 0.248 | 0.318 | +0.070 |
| dense_clutter | 14 | 0.196 | 0.253 | +0.056 |
| dense_clutter | 15 | 0.234 | 0.411 | +0.176 |
| dense_clutter | 16 | 0.153 | 0.150 | -0.003 |
| dense_clutter | 17 | 0.322 | 0.309 | -0.013 |
| dense_clutter | 18 | 0.249 | 0.329 | +0.080 |
| dense_clutter | 19 | 0.317 | 0.501 | +0.184 |
| dense_clutter | 20 | 0.207 | 0.223 | +0.016 |
| dense_clutter | 21 | 0.182 | 0.175 | -0.008 |
| dense_clutter | 22 | 0.241 | 0.253 | +0.012 |
| dense_clutter | 23 | 0.162 | 0.218 | +0.056 |
| dense_clutter | 24 | 0.302 | 0.255 | -0.048 |
| false_observations | 0 | 0.250 | 0.254 | +0.004 |
| false_observations | 1 | 0.218 | 0.236 | +0.018 |
| false_observations | 2 | 0.195 | 0.178 | -0.017 |
| false_observations | 3 | 0.313 | 0.295 | -0.018 |
| false_observations | 4 | 0.194 | 0.175 | -0.018 |
| false_observations | 5 | 0.292 | 0.259 | -0.033 |
| false_observations | 6 | 0.193 | 0.262 | +0.070 |
| false_observations | 7 | 0.189 | 0.155 | -0.034 |
| false_observations | 8 | 0.209 | 0.247 | +0.038 |
| false_observations | 9 | 0.281 | 0.299 | +0.018 |
| false_observations | 10 | 0.202 | 0.332 | +0.130 |
| false_observations | 11 | 0.247 | 0.369 | +0.122 |
| false_observations | 12 | 0.245 | 0.212 | -0.032 |
| false_observations | 13 | 0.290 | 0.320 | +0.030 |
| false_observations | 14 | 0.182 | 0.172 | -0.009 |
| false_observations | 15 | 0.164 | 0.226 | +0.062 |
| false_observations | 16 | 0.179 | 0.166 | -0.013 |
| false_observations | 17 | 0.289 | 0.330 | +0.041 |
| false_observations | 18 | 0.214 | 0.330 | +0.116 |
| false_observations | 19 | 0.354 | 0.209 | -0.145 |
| false_observations | 20 | 0.173 | 0.149 | -0.024 |
| false_observations | 21 | 0.211 | 0.315 | +0.104 |
| false_observations | 22 | 0.277 | 0.262 | -0.015 |
| false_observations | 23 | 0.164 | 0.185 | +0.021 |
| false_observations | 24 | 0.215 | 0.224 | +0.009 |
| measurement_bias | 0 | 1.686 | 1.688 | +0.002 |
| measurement_bias | 1 | 1.656 | 1.614 | -0.043 |
| measurement_bias | 2 | 1.613 | 1.632 | +0.019 |
| measurement_bias | 3 | 1.611 | 1.592 | -0.019 |
| measurement_bias | 4 | 1.593 | 1.590 | -0.003 |
| measurement_bias | 5 | 1.607 | 1.623 | +0.016 |
| measurement_bias | 6 | 1.641 | 1.598 | -0.042 |
| measurement_bias | 7 | 1.589 | 1.588 | -0.002 |
| measurement_bias | 8 | 1.647 | 1.610 | -0.036 |
| measurement_bias | 9 | 1.593 | 1.598 | +0.005 |
| measurement_bias | 10 | 1.646 | 1.601 | -0.045 |
| measurement_bias | 11 | 1.705 | 1.657 | -0.048 |
| measurement_bias | 12 | 1.667 | 1.612 | -0.056 |
| measurement_bias | 13 | 1.641 | 1.605 | -0.036 |
| measurement_bias | 14 | 1.655 | 1.611 | -0.044 |
| measurement_bias | 15 | 1.679 | 1.617 | -0.062 |
| measurement_bias | 16 | 1.668 | 1.603 | -0.065 |
| measurement_bias | 17 | 1.602 | 1.592 | -0.010 |
| measurement_bias | 18 | 1.626 | 1.669 | +0.043 |
| measurement_bias | 19 | 1.664 | 1.628 | -0.035 |
| measurement_bias | 20 | 1.621 | 1.627 | +0.006 |
| measurement_bias | 21 | 1.642 | 1.616 | -0.027 |
| measurement_bias | 22 | 1.642 | 1.690 | +0.048 |
| measurement_bias | 23 | 1.654 | 1.597 | -0.057 |
| measurement_bias | 24 | 1.682 | 1.642 | -0.039 |
| moving_observer | 0 | 0.226 | 0.250 | +0.024 |
| moving_observer | 1 | 0.198 | 0.320 | +0.122 |
| moving_observer | 2 | 0.195 | 0.247 | +0.051 |
| moving_observer | 3 | 0.310 | 0.343 | +0.033 |
| moving_observer | 4 | 0.280 | 0.171 | -0.110 |
| moving_observer | 5 | 0.255 | 0.417 | +0.163 |
| moving_observer | 6 | 0.205 | 0.205 | +0.000 |
| moving_observer | 7 | 0.240 | 0.232 | -0.008 |
| moving_observer | 8 | 0.284 | 0.208 | -0.075 |
| moving_observer | 9 | 0.471 | 0.477 | +0.006 |
| moving_observer | 10 | 0.200 | 0.242 | +0.043 |
| moving_observer | 11 | 0.260 | 0.243 | -0.017 |
| moving_observer | 12 | 0.150 | 0.121 | -0.029 |
| moving_observer | 13 | 0.153 | 0.369 | +0.216 |
| moving_observer | 14 | 0.171 | 0.116 | -0.056 |
| moving_observer | 15 | 0.253 | 0.316 | +0.063 |
| moving_observer | 16 | 0.173 | 0.112 | -0.061 |
| moving_observer | 17 | 0.409 | 0.416 | +0.007 |
| moving_observer | 18 | 0.284 | 0.261 | -0.022 |
| moving_observer | 19 | 0.261 | 0.249 | -0.012 |
| moving_observer | 20 | 0.152 | 0.345 | +0.193 |
| moving_observer | 21 | 0.262 | 0.255 | -0.007 |
| moving_observer | 22 | 0.242 | 0.196 | -0.046 |
| moving_observer | 23 | 0.151 | 0.183 | +0.032 |
| moving_observer | 24 | 0.245 | 0.206 | -0.040 |
| nominal | 0 | 0.183 | 0.256 | +0.073 |
| nominal | 1 | 0.253 | 0.346 | +0.094 |
| nominal | 2 | 0.208 | 0.225 | +0.017 |
| nominal | 3 | 0.302 | 0.390 | +0.088 |
| nominal | 4 | 0.275 | 0.235 | -0.040 |
| nominal | 5 | 0.231 | 0.296 | +0.065 |
| nominal | 6 | 0.189 | 0.306 | +0.116 |
| nominal | 7 | 0.223 | 0.203 | -0.020 |
| nominal | 8 | 0.279 | 0.237 | -0.042 |
| nominal | 9 | 0.444 | 0.485 | +0.041 |
| nominal | 10 | 0.216 | 0.212 | -0.004 |
| nominal | 11 | 0.240 | 0.235 | -0.006 |
| nominal | 12 | 0.164 | 0.236 | +0.072 |
| nominal | 13 | 0.153 | 0.279 | +0.127 |
| nominal | 14 | 0.191 | 0.152 | -0.039 |
| nominal | 15 | 0.201 | 0.258 | +0.057 |
| nominal | 16 | 0.191 | 0.117 | -0.074 |
| nominal | 17 | 0.317 | 0.345 | +0.029 |
| nominal | 18 | 0.240 | 0.336 | +0.096 |
| nominal | 19 | 0.241 | 0.224 | -0.017 |
| nominal | 20 | 0.171 | 0.128 | -0.043 |
| nominal | 21 | 0.284 | 0.244 | -0.040 |
| nominal | 22 | 0.212 | 0.214 | +0.002 |
| nominal | 23 | 0.198 | 0.150 | -0.048 |
| nominal | 24 | 0.231 | 0.229 | -0.002 |
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
| range_dropout | 0 | 0.240 | 0.228 | -0.012 |
| range_dropout | 1 | 0.350 | 0.493 | +0.143 |
| range_dropout | 2 | 0.253 | 0.232 | -0.022 |
| range_dropout | 3 | 0.287 | 0.447 | +0.160 |
| range_dropout | 4 | 0.225 | 0.182 | -0.044 |
| range_dropout | 5 | 0.240 | 0.409 | +0.169 |
| range_dropout | 6 | 0.201 | 0.314 | +0.114 |
| range_dropout | 7 | 0.229 | 0.306 | +0.077 |
| range_dropout | 8 | 0.234 | 0.239 | +0.005 |
| range_dropout | 9 | 0.297 | 0.266 | -0.031 |
| range_dropout | 10 | 0.274 | 0.299 | +0.025 |
| range_dropout | 11 | 0.256 | 0.266 | +0.010 |
| range_dropout | 12 | 0.227 | 0.189 | -0.038 |
| range_dropout | 13 | 0.269 | 0.181 | -0.088 |
| range_dropout | 14 | 0.173 | 0.185 | +0.012 |
| range_dropout | 15 | 0.265 | 0.231 | -0.034 |
| range_dropout | 16 | 0.216 | 0.195 | -0.022 |
| range_dropout | 17 | 0.254 | 0.310 | +0.056 |
| range_dropout | 18 | 0.204 | 0.327 | +0.123 |
| range_dropout | 19 | 0.334 | 0.305 | -0.030 |
| range_dropout | 20 | 0.260 | 0.211 | -0.049 |
| range_dropout | 21 | 0.242 | 0.233 | -0.010 |
| range_dropout | 22 | 0.294 | 0.206 | -0.088 |
| range_dropout | 23 | 0.250 | 0.244 | -0.006 |
| range_dropout | 24 | 0.243 | 0.197 | -0.047 |
| sensor_disagreement_large_bias | 0 | 0.183 | 0.184 | +0.000 |
| sensor_disagreement_large_bias | 1 | 0.253 | 0.240 | -0.012 |
| sensor_disagreement_large_bias | 2 | 0.208 | 0.216 | +0.008 |
| sensor_disagreement_large_bias | 3 | 0.302 | 0.330 | +0.029 |
| sensor_disagreement_large_bias | 4 | 0.275 | 0.275 | +0.000 |
| sensor_disagreement_large_bias | 5 | 0.231 | 0.231 | +0.000 |
| sensor_disagreement_large_bias | 6 | 0.189 | 0.178 | -0.011 |
| sensor_disagreement_large_bias | 7 | 0.223 | 0.223 | +0.000 |
| sensor_disagreement_large_bias | 8 | 0.279 | 0.249 | -0.030 |
| sensor_disagreement_large_bias | 9 | 0.444 | 0.496 | +0.053 |
| sensor_disagreement_large_bias | 10 | 0.216 | 0.217 | +0.001 |
| sensor_disagreement_large_bias | 11 | 0.240 | 0.240 | +0.000 |
| sensor_disagreement_large_bias | 12 | 0.164 | 0.164 | +0.000 |
| sensor_disagreement_large_bias | 13 | 0.153 | 0.155 | +0.003 |
| sensor_disagreement_large_bias | 14 | 0.191 | 0.191 | +0.000 |
| sensor_disagreement_large_bias | 15 | 0.201 | 0.200 | -0.000 |
| sensor_disagreement_large_bias | 16 | 0.191 | 0.191 | +0.000 |
| sensor_disagreement_large_bias | 17 | 0.317 | 0.393 | +0.076 |
| sensor_disagreement_large_bias | 18 | 0.240 | 0.247 | +0.007 |
| sensor_disagreement_large_bias | 19 | 0.241 | 0.275 | +0.034 |
| sensor_disagreement_large_bias | 20 | 0.171 | 0.152 | -0.019 |
| sensor_disagreement_large_bias | 21 | 0.284 | 0.281 | -0.003 |
| sensor_disagreement_large_bias | 22 | 0.212 | 0.252 | +0.040 |
| sensor_disagreement_large_bias | 23 | 0.198 | 0.172 | -0.026 |
| sensor_disagreement_large_bias | 24 | 0.231 | 0.230 | -0.001 |
| sensor_disagreement_within_gate | 0 | 0.183 | 0.354 | +0.171 |
| sensor_disagreement_within_gate | 1 | 0.253 | 0.348 | +0.096 |
| sensor_disagreement_within_gate | 2 | 0.208 | 0.377 | +0.169 |
| sensor_disagreement_within_gate | 3 | 0.302 | 0.471 | +0.169 |
| sensor_disagreement_within_gate | 4 | 0.275 | 0.542 | +0.267 |
| sensor_disagreement_within_gate | 5 | 0.231 | 0.271 | +0.040 |
| sensor_disagreement_within_gate | 6 | 0.189 | 0.374 | +0.185 |
| sensor_disagreement_within_gate | 7 | 0.223 | 0.371 | +0.148 |
| sensor_disagreement_within_gate | 8 | 0.279 | 0.356 | +0.077 |
| sensor_disagreement_within_gate | 9 | 0.444 | 0.614 | +0.171 |
| sensor_disagreement_within_gate | 10 | 0.216 | 0.327 | +0.111 |
| sensor_disagreement_within_gate | 11 | 0.240 | 0.486 | +0.246 |
| sensor_disagreement_within_gate | 12 | 0.164 | 0.466 | +0.301 |
| sensor_disagreement_within_gate | 13 | 0.153 | 0.245 | +0.092 |
| sensor_disagreement_within_gate | 14 | 0.191 | 0.218 | +0.028 |
| sensor_disagreement_within_gate | 15 | 0.201 | 0.436 | +0.236 |
| sensor_disagreement_within_gate | 16 | 0.191 | 0.288 | +0.097 |
| sensor_disagreement_within_gate | 17 | 0.317 | 0.466 | +0.149 |
| sensor_disagreement_within_gate | 18 | 0.240 | 0.301 | +0.060 |
| sensor_disagreement_within_gate | 19 | 0.241 | 0.501 | +0.260 |
| sensor_disagreement_within_gate | 20 | 0.171 | 0.319 | +0.148 |
| sensor_disagreement_within_gate | 21 | 0.284 | 0.344 | +0.060 |
| sensor_disagreement_within_gate | 22 | 0.212 | 0.402 | +0.191 |
| sensor_disagreement_within_gate | 23 | 0.198 | 0.280 | +0.082 |
| sensor_disagreement_within_gate | 24 | 0.231 | 0.367 | +0.136 |
| sensor_disagreement_within_gate_high | 0 | 0.183 | 0.509 | +0.326 |
| sensor_disagreement_within_gate_high | 1 | 0.253 | 0.420 | +0.167 |
| sensor_disagreement_within_gate_high | 2 | 0.208 | 0.370 | +0.161 |
| sensor_disagreement_within_gate_high | 3 | 0.302 | 0.522 | +0.220 |
| sensor_disagreement_within_gate_high | 4 | 0.275 | 0.592 | +0.316 |
| sensor_disagreement_within_gate_high | 5 | 0.231 | 0.480 | +0.249 |
| sensor_disagreement_within_gate_high | 6 | 0.189 | 0.299 | +0.110 |
| sensor_disagreement_within_gate_high | 7 | 0.223 | 0.427 | +0.204 |
| sensor_disagreement_within_gate_high | 8 | 0.279 | 0.416 | +0.137 |
| sensor_disagreement_within_gate_high | 9 | 0.444 | 0.520 | +0.077 |
| sensor_disagreement_within_gate_high | 10 | 0.216 | 0.375 | +0.158 |
| sensor_disagreement_within_gate_high | 11 | 0.240 | 0.420 | +0.180 |
| sensor_disagreement_within_gate_high | 12 | 0.164 | 0.560 | +0.396 |
| sensor_disagreement_within_gate_high | 13 | 0.153 | 0.653 | +0.501 |
| sensor_disagreement_within_gate_high | 14 | 0.191 | 0.399 | +0.209 |
| sensor_disagreement_within_gate_high | 15 | 0.201 | 0.535 | +0.334 |
| sensor_disagreement_within_gate_high | 16 | 0.191 | 0.427 | +0.236 |
| sensor_disagreement_within_gate_high | 17 | 0.317 | 0.506 | +0.189 |
| sensor_disagreement_within_gate_high | 18 | 0.240 | 0.370 | +0.129 |
| sensor_disagreement_within_gate_high | 19 | 0.241 | 0.692 | +0.451 |
| sensor_disagreement_within_gate_high | 20 | 0.171 | 0.557 | +0.387 |
| sensor_disagreement_within_gate_high | 21 | 0.284 | 0.355 | +0.071 |
| sensor_disagreement_within_gate_high | 22 | 0.212 | 0.428 | +0.217 |
| sensor_disagreement_within_gate_high | 23 | 0.198 | 0.397 | +0.199 |
| sensor_disagreement_within_gate_high | 24 | 0.231 | 0.444 | +0.214 |
| sensor_disagreement_within_gate_low | 0 | 0.183 | 0.340 | +0.157 |
| sensor_disagreement_within_gate_low | 1 | 0.253 | 0.298 | +0.046 |
| sensor_disagreement_within_gate_low | 2 | 0.208 | 0.245 | +0.036 |
| sensor_disagreement_within_gate_low | 3 | 0.302 | 0.431 | +0.129 |
| sensor_disagreement_within_gate_low | 4 | 0.275 | 0.364 | +0.089 |
| sensor_disagreement_within_gate_low | 5 | 0.231 | 0.478 | +0.247 |
| sensor_disagreement_within_gate_low | 6 | 0.189 | 0.377 | +0.187 |
| sensor_disagreement_within_gate_low | 7 | 0.223 | 0.364 | +0.141 |
| sensor_disagreement_within_gate_low | 8 | 0.279 | 0.359 | +0.080 |
| sensor_disagreement_within_gate_low | 9 | 0.444 | 0.370 | -0.074 |
| sensor_disagreement_within_gate_low | 10 | 0.216 | 0.280 | +0.064 |
| sensor_disagreement_within_gate_low | 11 | 0.240 | 0.386 | +0.146 |
| sensor_disagreement_within_gate_low | 12 | 0.164 | 0.381 | +0.217 |
| sensor_disagreement_within_gate_low | 13 | 0.153 | 0.333 | +0.180 |
| sensor_disagreement_within_gate_low | 14 | 0.191 | 0.219 | +0.029 |
| sensor_disagreement_within_gate_low | 15 | 0.201 | 0.381 | +0.180 |
| sensor_disagreement_within_gate_low | 16 | 0.191 | 0.218 | +0.027 |
| sensor_disagreement_within_gate_low | 17 | 0.317 | 0.401 | +0.084 |
| sensor_disagreement_within_gate_low | 18 | 0.240 | 0.373 | +0.132 |
| sensor_disagreement_within_gate_low | 19 | 0.241 | 0.346 | +0.105 |
| sensor_disagreement_within_gate_low | 20 | 0.171 | 0.294 | +0.123 |
| sensor_disagreement_within_gate_low | 21 | 0.284 | 0.277 | -0.007 |
| sensor_disagreement_within_gate_low | 22 | 0.212 | 0.353 | +0.142 |
| sensor_disagreement_within_gate_low | 23 | 0.198 | 0.213 | +0.015 |
| sensor_disagreement_within_gate_low | 24 | 0.231 | 0.291 | +0.060 |
| uncertainty_miscalibration | 0 | 0.365 | 0.558 | +0.193 |
| uncertainty_miscalibration | 1 | 0.380 | 0.498 | +0.118 |
| uncertainty_miscalibration | 2 | 0.475 | 0.541 | +0.066 |
| uncertainty_miscalibration | 3 | 0.472 | 0.627 | +0.155 |
| uncertainty_miscalibration | 4 | 0.534 | 0.509 | -0.025 |
| uncertainty_miscalibration | 5 | 0.477 | 0.548 | +0.071 |
| uncertainty_miscalibration | 6 | 0.481 | 0.482 | +0.001 |
| uncertainty_miscalibration | 7 | 0.522 | 0.617 | +0.095 |
| uncertainty_miscalibration | 8 | 0.482 | 0.605 | +0.124 |
| uncertainty_miscalibration | 9 | 0.515 | 0.556 | +0.041 |
| uncertainty_miscalibration | 10 | 0.350 | 0.437 | +0.087 |
| uncertainty_miscalibration | 11 | 0.510 | 0.515 | +0.005 |
| uncertainty_miscalibration | 12 | 0.591 | 0.531 | -0.060 |
| uncertainty_miscalibration | 13 | 0.427 | 0.483 | +0.056 |
| uncertainty_miscalibration | 14 | 0.432 | 0.567 | +0.135 |
| uncertainty_miscalibration | 15 | 0.448 | 0.527 | +0.080 |
| uncertainty_miscalibration | 16 | 0.545 | 0.438 | -0.107 |
| uncertainty_miscalibration | 17 | 0.539 | 0.672 | +0.133 |
| uncertainty_miscalibration | 18 | 0.407 | 0.385 | -0.023 |
| uncertainty_miscalibration | 19 | 0.501 | 0.549 | +0.048 |
| uncertainty_miscalibration | 20 | 0.374 | 0.502 | +0.129 |
| uncertainty_miscalibration | 21 | 0.364 | 0.594 | +0.230 |
| uncertainty_miscalibration | 22 | 0.422 | 0.423 | +0.001 |
| uncertainty_miscalibration | 23 | 0.417 | 0.457 | +0.040 |
| uncertainty_miscalibration | 24 | 0.502 | 0.504 | +0.002 |
| vision_dropout | 0 | 0.183 | 0.241 | +0.058 |
| vision_dropout | 1 | 0.253 | 0.218 | -0.034 |
| vision_dropout | 2 | 0.208 | 0.206 | -0.002 |
| vision_dropout | 3 | 0.302 | 0.293 | -0.009 |
| vision_dropout | 4 | 0.275 | 0.297 | +0.022 |
| vision_dropout | 5 | 0.231 | 0.237 | +0.006 |
| vision_dropout | 6 | 0.189 | 0.193 | +0.004 |
| vision_dropout | 7 | 0.223 | 0.230 | +0.007 |
| vision_dropout | 8 | 0.279 | 0.295 | +0.016 |
| vision_dropout | 9 | 0.444 | 0.462 | +0.019 |
| vision_dropout | 10 | 0.216 | 0.164 | -0.052 |
| vision_dropout | 11 | 0.240 | 0.234 | -0.006 |
| vision_dropout | 12 | 0.164 | 0.214 | +0.050 |
| vision_dropout | 13 | 0.153 | 0.212 | +0.060 |
| vision_dropout | 14 | 0.191 | 0.184 | -0.007 |
| vision_dropout | 15 | 0.201 | 0.307 | +0.107 |
| vision_dropout | 16 | 0.191 | 0.196 | +0.005 |
| vision_dropout | 17 | 0.317 | 0.384 | +0.067 |
| vision_dropout | 18 | 0.240 | 0.257 | +0.017 |
| vision_dropout | 19 | 0.241 | 0.248 | +0.007 |
| vision_dropout | 20 | 0.171 | 0.140 | -0.031 |
| vision_dropout | 21 | 0.284 | 0.231 | -0.054 |
| vision_dropout | 22 | 0.212 | 0.200 | -0.012 |
| vision_dropout | 23 | 0.198 | 0.139 | -0.058 |
| vision_dropout | 24 | 0.231 | 0.250 | +0.019 |

## Findings

- Position RMSE: the paired interval excludes zero in favour of fusion in 1 scenario(s) and against fusion in 5 scenario(s); it includes zero (or has fewer than two seeds) in 8 scenario(s).
- Fused precision is lower (interval excludes zero) in 13 scenario(s) and higher in 0; fused 95% coverage is lower in 11 and higher in 1. Accuracy alone does not establish that fusion improved association or calibration.
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
  results; intervals reflect seed-to-seed variation only.
- `track_fragmentation` counts interruptions in an object's matched frames, summed
  over objects; it is independent of identity switches.
- `identity_switches` counts changes of matched track ID for the same
  ground-truth object across consecutive matched frames.
- Coverage is empirical and only defined over matched samples; its
  denominator is reported in `per_seed.csv` and `benchmark.json`.
- Scenarios with no matched samples (for example `out_of_sequence`)
  report `N/A` accuracy because their observations are rejected as stale;
  that is an explicit non-result, not a zero-error result.
- This report uses 25 development seed(s). The reserved held-out range (25-49) is not included here and no held-out claim is made.

## Limitations

- Synthetic 2-D world; simplified sensor models, not hardware validation.
- Vision-only track initiation is not supported (bearing alone cannot
  determine range).
- Out-of-sequence observations older than one tracker epoch are explicitly
  rejected and counted, not silently dropped. Their accuracy impact is
  therefore not represented as a successful fusion result.
- Results on development seeds include choices made while building the workbench and are not confirmatory. A held-out evaluation exists only when the reserved seeds (25-49) appear in the `Seeds` line above.
