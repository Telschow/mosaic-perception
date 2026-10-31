# Mosaic Benchmark Report

This report is generated from the code in this repository. It contains no
hand-edited numbers and no wall-clock timestamps, so repeated runs with the
same seeds and commit are byte-identical.

## Code and protocol

- Package version: `0.1.0`
- Git commit: `8baa778e86826ddbdcb4b27ef07d7ca9b993e354`
- Seeds: 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49
- Seed group: custom_or_held_out
- Duration: 10.0 s at dt=0.1 s
- Objects per world: 3
- Methods: range-only (range-bearing sensor only), fused (range-bearing + vision bearing) and, where present, fused-bias-estimated (fused plus an estimate of the vision bearing bias, subtracted before gating and updating)
- Paired: same world states and the same sensor random streams per seed; the fused runs only add vision observations, and bias estimation changes only how they are used.
- Evaluation matching gate: 2.00 m, one-to-one Hungarian assignment per timestamp, preferring each object's previous track while it stays inside the gate.
- Accuracy denominators: matched sample pairs. Recall denominator: all ground-truth object samples. Precision denominator: all confirmed/coasting track samples.
- 95% position coverage threshold: chi-square(2, 0.95) = 5.991.

## Aggregate results

Values are mean ± sample standard deviation across seeds. `N/A` means the
metric was not defined for any seed (for example, no matched tracks); it is
never a fabricated zero.

| Scenario | Method | Pos RMSE (m) | Pos RMSE, distance-only matcher (m) | Vel RMSE (m/s) | Recall | Precision | Cov95 | Matched/GT (mean) | Unmatched confirmed tracks | Duplicate tracks | ID switches | ID switches (distance-only) | Fragmentation | MOTA | IDF1 | GOSPA (p=1, m) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crossing_targets | range_only | 0.180 ± 0.051 | 0.169 | 0.158 | 0.978 | 0.837 | 0.840 | 296/303 | 3.8 | 3.8 | 1.6 | 7.3 | 0.0 | 0.774 | 0.812 | 1.069 |
| crossing_targets | fused | 0.191 ± 0.060 | 0.177 | 0.112 | 0.979 | 0.700 | 0.750 | 297/303 | 5.1 | 5.0 | 0.6 | 8.0 | 0.0 | 0.535 | 0.790 | 1.815 |
| crossing_targets | fused_bias_estimated | 0.190 ± 0.062 | 0.174 | 0.125 | 0.979 | 0.690 | 0.745 | 297/303 | 5.0 | 4.9 | 1.1 | 8.4 | 0.0 | 0.514 | 0.775 | 1.865 |
| delivery_delay | range_only | 0.294 ± 0.065 | 0.271 | 0.334 | 0.968 | 0.808 | 0.546 | 293/303 | 3.2 | 3.2 | 6.5 | 9.5 | 0.0 | 0.712 | 0.612 | 1.494 |
| delivery_delay | fused | 0.305 ± 0.085 | 0.252 | 0.299 | 0.970 | 0.667 | 0.352 | 294/303 | 6.2 | 6.2 | 4.8 | 10.9 | 0.0 | 0.453 | 0.611 | 2.253 |
| delivery_delay | fused_bias_estimated | 0.319 ± 0.088 | 0.254 | 0.306 | 0.970 | 0.665 | 0.338 | 294/303 | 6.4 | 6.3 | 4.7 | 11.4 | 0.0 | 0.450 | 0.608 | 2.259 |
| delivery_delay_retrodiction | range_only | 0.281 ± 0.056 | 0.250 | 0.403 | 0.969 | 0.793 | 0.825 | 293/303 | 4.3 | 4.3 | 11.4 | 16.9 | 0.1 | 0.675 | 0.497 | 1.471 |
| delivery_delay_retrodiction | fused | 0.311 ± 0.080 | 0.236 | 0.392 | 0.969 | 0.636 | 0.723 | 294/303 | 10.4 | 10.4 | 11.0 | 19.7 | 0.1 | 0.369 | 0.482 | 2.360 |
| delivery_delay_retrodiction | fused_bias_estimated | 0.336 ± 0.083 | 0.251 | 0.432 | 0.969 | 0.648 | 0.720 | 294/303 | 10.4 | 10.3 | 13.0 | 22.6 | 0.1 | 0.389 | 0.454 | 2.306 |
| dense_clutter | range_only | 0.226 ± 0.047 | 0.201 | 0.323 | 0.977 | 0.829 | 0.854 | 296/303 | 3.4 | 3.4 | 5.7 | 9.5 | 0.1 | 0.751 | 0.660 | 1.179 |
| dense_clutter | fused | 0.276 ± 0.092 | 0.196 | 0.317 | 0.979 | 0.350 | 0.734 | 297/303 | 73.2 | 9.1 | 4.6 | 10.4 | 0.0 | -0.870 | 0.405 | 6.039 |
| dense_clutter | fused_bias_estimated | 0.280 ± 0.080 | 0.203 | 0.328 | 0.979 | 0.346 | 0.708 | 297/303 | 73.8 | 9.3 | 4.8 | 11.2 | 0.0 | -0.901 | 0.397 | 6.147 |
| false_observations | range_only | 0.237 ± 0.064 | 0.216 | 0.307 | 0.977 | 0.834 | 0.808 | 296/303 | 2.9 | 2.9 | 5.9 | 9.2 | 0.2 | 0.753 | 0.656 | 1.217 |
| false_observations | fused | 0.274 ± 0.109 | 0.189 | 0.303 | 0.978 | 0.617 | 0.749 | 296/303 | 13.6 | 7.2 | 4.2 | 8.8 | 0.0 | 0.338 | 0.604 | 2.398 |
| false_observations | fused_bias_estimated | 0.281 ± 0.098 | 0.199 | 0.312 | 0.978 | 0.603 | 0.678 | 296/303 | 13.8 | 7.4 | 5.0 | 10.4 | 0.0 | 0.297 | 0.574 | 2.547 |
| measurement_bias | range_only | 1.640 ± 0.034 | 1.602 | 0.514 | 0.862 | 0.722 | 0.001 | 261/303 | 1.8 | 1.3 | 11.0 | 13.4 | 5.4 | 0.490 | 0.308 | 5.499 |
| measurement_bias | fused | 1.622 ± 0.034 | 1.550 | 0.516 | 0.873 | 0.572 | 0.012 | 265/303 | 3.6 | 2.6 | 10.8 | 15.2 | 4.7 | 0.177 | 0.289 | 6.334 |
| measurement_bias | fused_bias_estimated | 1.620 ± 0.043 | 1.543 | 0.500 | 0.879 | 0.569 | 0.012 | 266/303 | 3.6 | 2.7 | 10.9 | 15.0 | 4.6 | 0.170 | 0.294 | 6.357 |
| moving_observer | range_only | 0.238 ± 0.063 | 0.219 | 0.312 | 0.978 | 0.858 | 0.820 | 296/303 | 2.8 | 2.8 | 5.9 | 7.9 | 0.0 | 0.792 | 0.672 | 1.099 |
| moving_observer | fused | 0.260 ± 0.088 | 0.197 | 0.292 | 0.979 | 0.705 | 0.711 | 297/303 | 5.3 | 5.3 | 4.2 | 9.6 | 0.0 | 0.538 | 0.647 | 1.815 |
| moving_observer | fused_bias_estimated | 0.275 ± 0.088 | 0.211 | 0.295 | 0.979 | 0.698 | 0.670 | 297/303 | 5.4 | 5.4 | 4.7 | 10.7 | 0.0 | 0.522 | 0.639 | 1.904 |
| nominal | range_only | 0.242 ± 0.046 | 0.219 | 0.311 | 0.978 | 0.828 | 0.805 | 296/303 | 3.0 | 3.0 | 6.7 | 8.7 | 0.1 | 0.750 | 0.633 | 1.222 |
| nominal | fused | 0.257 ± 0.088 | 0.196 | 0.280 | 0.979 | 0.680 | 0.735 | 297/303 | 6.0 | 6.0 | 4.3 | 8.4 | 0.0 | 0.487 | 0.643 | 1.972 |
| nominal | fused_bias_estimated | 0.263 ± 0.079 | 0.205 | 0.284 | 0.979 | 0.681 | 0.672 | 297/303 | 5.5 | 5.5 | 4.8 | 9.4 | 0.0 | 0.487 | 0.639 | 1.999 |
| range_dropout | range_only | 0.261 ± 0.056 | 0.258 | 0.352 | 0.880 | 0.975 | 0.895 | 267/303 | 0.4 | 0.4 | 7.2 | 7.3 | 5.0 | 0.834 | 0.569 | 0.978 |
| range_dropout | fused | 0.284 ± 0.088 | 0.230 | 0.291 | 0.970 | 0.803 | 0.806 | 294/303 | 4.0 | 4.0 | 4.0 | 7.0 | 0.1 | 0.709 | 0.692 | 1.358 |
| range_dropout | fused_bias_estimated | 0.296 ± 0.083 | 0.240 | 0.305 | 0.970 | 0.795 | 0.747 | 294/303 | 3.6 | 3.6 | 4.3 | 7.2 | 0.1 | 0.695 | 0.680 | 1.428 |
| sensor_disagreement_large_bias | range_only | 0.242 ± 0.046 | 0.219 | 0.311 | 0.978 | 0.828 | 0.805 | 296/303 | 3.0 | 3.0 | 6.7 | 8.7 | 0.1 | 0.750 | 0.633 | 1.222 |
| sensor_disagreement_large_bias | fused | 0.254 ± 0.059 | 0.220 | 0.320 | 0.978 | 0.799 | 0.799 | 296/303 | 4.0 | 3.7 | 6.8 | 8.8 | 0.1 | 0.703 | 0.623 | 1.362 |
| sensor_disagreement_large_bias | fused_bias_estimated | 0.250 ± 0.052 | 0.220 | 0.324 | 0.978 | 0.800 | 0.801 | 296/303 | 4.2 | 3.8 | 6.7 | 8.8 | 0.1 | 0.705 | 0.627 | 1.356 |
| sensor_disagreement_within_gate | range_only | 0.242 ± 0.046 | 0.219 | 0.311 | 0.978 | 0.828 | 0.805 | 296/303 | 3.0 | 3.0 | 6.7 | 8.7 | 0.1 | 0.750 | 0.633 | 1.222 |
| sensor_disagreement_within_gate | fused | 0.410 ± 0.075 | 0.268 | 0.399 | 0.978 | 0.558 | 0.227 | 296/303 | 9.6 | 9.4 | 7.4 | 20.1 | 0.0 | 0.167 | 0.497 | 3.118 |
| sensor_disagreement_within_gate | fused_bias_estimated | 0.270 ± 0.072 | 0.199 | 0.328 | 0.978 | 0.672 | 0.665 | 296/303 | 5.9 | 5.9 | 5.2 | 10.7 | 0.0 | 0.463 | 0.629 | 2.047 |
| sensor_disagreement_within_gate_high | range_only | 0.242 ± 0.046 | 0.219 | 0.311 | 0.978 | 0.828 | 0.805 | 296/303 | 3.0 | 3.0 | 6.7 | 8.7 | 0.1 | 0.750 | 0.633 | 1.222 |
| sensor_disagreement_within_gate_high | fused | 0.451 ± 0.091 | 0.272 | 0.436 | 0.978 | 0.509 | 0.311 | 296/303 | 10.2 | 10.1 | 7.4 | 20.7 | 0.0 | 0.006 | 0.488 | 3.598 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 0.273 ± 0.077 | 0.197 | 0.345 | 0.978 | 0.673 | 0.694 | 296/303 | 6.0 | 6.0 | 5.4 | 10.5 | 0.0 | 0.471 | 0.627 | 2.010 |
| sensor_disagreement_within_gate_low | range_only | 0.242 ± 0.046 | 0.219 | 0.311 | 0.978 | 0.828 | 0.805 | 296/303 | 3.0 | 3.0 | 6.7 | 8.7 | 0.1 | 0.750 | 0.633 | 1.222 |
| sensor_disagreement_within_gate_low | fused | 0.334 ± 0.070 | 0.242 | 0.322 | 0.979 | 0.612 | 0.344 | 297/303 | 8.3 | 8.3 | 5.6 | 15.2 | 0.0 | 0.325 | 0.559 | 2.598 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 0.264 ± 0.074 | 0.201 | 0.307 | 0.979 | 0.672 | 0.689 | 297/303 | 5.9 | 5.9 | 4.9 | 10.9 | 0.0 | 0.467 | 0.635 | 2.043 |
| stale_rejection | range_only | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| stale_rejection | fused | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| stale_rejection | fused_bias_estimated | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| uncertainty_miscalibration | range_only | 0.451 ± 0.055 | 0.424 | 0.604 | 0.513 | 0.837 | 0.101 | 155/303 | 2.3 | 2.3 | 24.9 | 27.1 | 15.6 | 0.329 | 0.140 | 2.324 |
| uncertainty_miscalibration | fused | 0.515 ± 0.059 | 0.387 | 0.622 | 0.937 | 0.436 | 0.119 | 284/303 | 37.5 | 37.1 | 35.2 | 55.9 | 2.8 | -0.403 | 0.177 | 4.746 |
| uncertainty_miscalibration | fused_bias_estimated | 0.520 ± 0.058 | 0.391 | 0.627 | 0.931 | 0.434 | 0.114 | 282/303 | 37.6 | 37.2 | 34.8 | 55.4 | 3.1 | -0.410 | 0.172 | 4.771 |
| vision_dropout | range_only | 0.242 ± 0.046 | 0.219 | 0.311 | 0.978 | 0.828 | 0.805 | 296/303 | 3.0 | 3.0 | 6.7 | 8.7 | 0.1 | 0.750 | 0.633 | 1.222 |
| vision_dropout | fused | 0.236 ± 0.071 | 0.199 | 0.281 | 0.979 | 0.748 | 0.785 | 297/303 | 4.8 | 4.7 | 5.6 | 9.4 | 0.0 | 0.617 | 0.642 | 1.575 |
| vision_dropout | fused_bias_estimated | 0.241 ± 0.081 | 0.201 | 0.288 | 0.979 | 0.736 | 0.760 | 297/303 | 5.1 | 5.1 | 5.9 | 10.5 | 0.0 | 0.597 | 0.641 | 1.645 |

## Paired differences (fused minus range-only)

Mean per-seed difference with a two-sided 95% t interval over seeds. Seeds with
an undefined value on either side are dropped (`n` is the number kept). Lower is
better for the RMSE metrics and GOSPA, so a negative difference favours the
treatment; higher is better for recall, precision, coverage, MOTA and IDF1, so a
positive one does. The interval describes seed-to-seed variation in this synthetic
setup and is not a claim about other worlds.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| crossing_targets | gospa_p1 | 25 | +0.746 | [+0.487, +1.006] |
| crossing_targets | idf1 | 25 | -0.022 | [-0.076, +0.032] |
| crossing_targets | mota | 25 | -0.238 | [-0.318, -0.158] |
| crossing_targets | position_coverage_95 | 25 | -0.090 | [-0.144, -0.036] |
| crossing_targets | position_rmse | 25 | +0.011 | [-0.007, +0.029] |
| crossing_targets | position_rmse_distance_only | 25 | +0.008 | [-0.008, +0.023] |
| crossing_targets | precision | 25 | -0.137 | [-0.182, -0.092] |
| crossing_targets | recall | 25 | +0.001 | [-0.000, +0.002] |
| delivery_delay | gospa_p1 | 25 | +0.759 | [+0.552, +0.966] |
| delivery_delay | idf1 | 25 | -0.001 | [-0.038, +0.037] |
| delivery_delay | mota | 25 | -0.260 | [-0.323, -0.196] |
| delivery_delay | position_coverage_95 | 25 | -0.194 | [-0.248, -0.140] |
| delivery_delay | position_rmse | 25 | +0.011 | [-0.017, +0.039] |
| delivery_delay | position_rmse_distance_only | 25 | -0.019 | [-0.033, -0.006] |
| delivery_delay | precision | 25 | -0.141 | [-0.171, -0.110] |
| delivery_delay | recall | 25 | +0.001 | [+0.000, +0.002] |
| delivery_delay_retrodiction | gospa_p1 | 25 | +0.889 | [+0.757, +1.021] |
| delivery_delay_retrodiction | idf1 | 25 | -0.015 | [-0.063, +0.032] |
| delivery_delay_retrodiction | mota | 25 | -0.306 | [-0.346, -0.267] |
| delivery_delay_retrodiction | position_coverage_95 | 25 | -0.102 | [-0.137, -0.066] |
| delivery_delay_retrodiction | position_rmse | 25 | +0.030 | [+0.003, +0.057] |
| delivery_delay_retrodiction | position_rmse_distance_only | 25 | -0.014 | [-0.028, -0.001] |
| delivery_delay_retrodiction | precision | 25 | -0.158 | [-0.175, -0.140] |
| delivery_delay_retrodiction | recall | 25 | +0.001 | [-0.000, +0.002] |
| dense_clutter | gospa_p1 | 25 | +4.861 | [+4.555, +5.167] |
| dense_clutter | idf1 | 25 | -0.255 | [-0.293, -0.218] |
| dense_clutter | mota | 25 | -1.621 | [-1.717, -1.525] |
| dense_clutter | position_coverage_95 | 25 | -0.120 | [-0.165, -0.076] |
| dense_clutter | position_rmse | 25 | +0.049 | [+0.016, +0.083] |
| dense_clutter | position_rmse_distance_only | 25 | -0.004 | [-0.015, +0.006] |
| dense_clutter | precision | 25 | -0.479 | [-0.505, -0.452] |
| dense_clutter | recall | 25 | +0.002 | [-0.000, +0.004] |
| false_observations | gospa_p1 | 25 | +1.181 | [+0.931, +1.430] |
| false_observations | idf1 | 25 | -0.053 | [-0.092, -0.013] |
| false_observations | mota | 25 | -0.416 | [-0.490, -0.341] |
| false_observations | position_coverage_95 | 25 | -0.058 | [-0.115, -0.001] |
| false_observations | position_rmse | 25 | +0.036 | [-0.003, +0.075] |
| false_observations | position_rmse_distance_only | 25 | -0.027 | [-0.045, -0.010] |
| false_observations | precision | 25 | -0.216 | [-0.249, -0.184] |
| false_observations | recall | 25 | +0.001 | [-0.000, +0.002] |
| measurement_bias | gospa_p1 | 25 | +0.835 | [+0.697, +0.974] |
| measurement_bias | idf1 | 25 | -0.019 | [-0.031, -0.006] |
| measurement_bias | mota | 25 | -0.313 | [-0.362, -0.264] |
| measurement_bias | position_coverage_95 | 25 | +0.011 | [+0.003, +0.019] |
| measurement_bias | position_rmse | 25 | -0.017 | [-0.029, -0.005] |
| measurement_bias | position_rmse_distance_only | 25 | -0.052 | [-0.068, -0.035] |
| measurement_bias | precision | 25 | -0.150 | [-0.171, -0.129] |
| measurement_bias | recall | 25 | +0.012 | [-0.009, +0.033] |
| moving_observer | gospa_p1 | 25 | +0.716 | [+0.460, +0.972] |
| moving_observer | idf1 | 25 | -0.025 | [-0.071, +0.021] |
| moving_observer | mota | 25 | -0.254 | [-0.328, -0.180] |
| moving_observer | position_coverage_95 | 25 | -0.109 | [-0.158, -0.060] |
| moving_observer | position_rmse | 25 | +0.022 | [-0.008, +0.052] |
| moving_observer | position_rmse_distance_only | 25 | -0.022 | [-0.041, -0.003] |
| moving_observer | precision | 25 | -0.153 | [-0.193, -0.114] |
| moving_observer | recall | 25 | +0.001 | [-0.000, +0.003] |
| nominal | gospa_p1 | 25 | +0.751 | [+0.526, +0.976] |
| nominal | idf1 | 25 | +0.009 | [-0.022, +0.040] |
| nominal | mota | 25 | -0.263 | [-0.329, -0.196] |
| nominal | position_coverage_95 | 25 | -0.070 | [-0.121, -0.018] |
| nominal | position_rmse | 25 | +0.015 | [-0.013, +0.044] |
| nominal | position_rmse_distance_only | 25 | -0.024 | [-0.038, -0.009] |
| nominal | precision | 25 | -0.148 | [-0.181, -0.116] |
| nominal | recall | 25 | +0.000 | [-0.000, +0.001] |
| range_dropout | gospa_p1 | 25 | +0.380 | [+0.236, +0.525] |
| range_dropout | idf1 | 25 | +0.124 | [+0.062, +0.185] |
| range_dropout | mota | 25 | -0.125 | [-0.171, -0.079] |
| range_dropout | position_coverage_95 | 25 | -0.089 | [-0.118, -0.060] |
| range_dropout | position_rmse | 25 | +0.022 | [-0.007, +0.051] |
| range_dropout | position_rmse_distance_only | 25 | -0.028 | [-0.046, -0.011] |
| range_dropout | precision | 25 | -0.172 | [-0.200, -0.145] |
| range_dropout | recall | 25 | +0.090 | [+0.073, +0.106] |
| sensor_disagreement_large_bias | gospa_p1 | 25 | +0.141 | [+0.065, +0.216] |
| sensor_disagreement_large_bias | idf1 | 25 | -0.010 | [-0.024, +0.003] |
| sensor_disagreement_large_bias | mota | 25 | -0.047 | [-0.072, -0.022] |
| sensor_disagreement_large_bias | position_coverage_95 | 25 | -0.006 | [-0.019, +0.006] |
| sensor_disagreement_large_bias | position_rmse | 25 | +0.012 | [-0.004, +0.028] |
| sensor_disagreement_large_bias | position_rmse_distance_only | 25 | +0.001 | [-0.003, +0.005] |
| sensor_disagreement_large_bias | precision | 25 | -0.029 | [-0.044, -0.014] |
| sensor_disagreement_large_bias | recall | 25 | +0.000 | [-0.000, +0.000] |
| sensor_disagreement_within_gate | gospa_p1 | 25 | +1.896 | [+1.700, +2.092] |
| sensor_disagreement_within_gate | idf1 | 25 | -0.137 | [-0.179, -0.094] |
| sensor_disagreement_within_gate | mota | 25 | -0.583 | [-0.644, -0.522] |
| sensor_disagreement_within_gate | position_coverage_95 | 25 | -0.579 | [-0.634, -0.523] |
| sensor_disagreement_within_gate | position_rmse | 25 | +0.168 | [+0.142, +0.195] |
| sensor_disagreement_within_gate | position_rmse_distance_only | 25 | +0.048 | [+0.029, +0.068] |
| sensor_disagreement_within_gate | precision | 25 | -0.270 | [-0.296, -0.245] |
| sensor_disagreement_within_gate | recall | 25 | -0.001 | [-0.003, +0.001] |
| sensor_disagreement_within_gate_high | gospa_p1 | 25 | +2.377 | [+2.267, +2.487] |
| sensor_disagreement_within_gate_high | idf1 | 25 | -0.146 | [-0.177, -0.115] |
| sensor_disagreement_within_gate_high | mota | 25 | -0.744 | [-0.778, -0.709] |
| sensor_disagreement_within_gate_high | position_coverage_95 | 25 | -0.495 | [-0.563, -0.426] |
| sensor_disagreement_within_gate_high | position_rmse | 25 | +0.209 | [+0.174, +0.244] |
| sensor_disagreement_within_gate_high | position_rmse_distance_only | 25 | +0.052 | [+0.034, +0.071] |
| sensor_disagreement_within_gate_high | precision | 25 | -0.319 | [-0.337, -0.302] |
| sensor_disagreement_within_gate_high | recall | 25 | -0.001 | [-0.003, +0.001] |
| sensor_disagreement_within_gate_low | gospa_p1 | 25 | +1.376 | [+1.171, +1.582] |
| sensor_disagreement_within_gate_low | idf1 | 25 | -0.075 | [-0.109, -0.041] |
| sensor_disagreement_within_gate_low | mota | 25 | -0.425 | [-0.488, -0.362] |
| sensor_disagreement_within_gate_low | position_coverage_95 | 25 | -0.461 | [-0.512, -0.410] |
| sensor_disagreement_within_gate_low | position_rmse | 25 | +0.092 | [+0.067, +0.117] |
| sensor_disagreement_within_gate_low | position_rmse_distance_only | 25 | +0.023 | [+0.005, +0.041] |
| sensor_disagreement_within_gate_low | precision | 25 | -0.216 | [-0.243, -0.189] |
| sensor_disagreement_within_gate_low | recall | 25 | +0.001 | [-0.000, +0.001] |
| stale_rejection | gospa_p1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | idf1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | mota | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | position_coverage_95 | 0 | N/A | N/A |
| stale_rejection | position_rmse | 0 | N/A | N/A |
| stale_rejection | position_rmse_distance_only | 0 | N/A | N/A |
| stale_rejection | precision | 0 | N/A | N/A |
| stale_rejection | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| uncertainty_miscalibration | gospa_p1 | 25 | +2.422 | [+2.237, +2.607] |
| uncertainty_miscalibration | idf1 | 25 | +0.037 | [+0.019, +0.054] |
| uncertainty_miscalibration | mota | 25 | -0.731 | [-0.795, -0.667] |
| uncertainty_miscalibration | position_coverage_95 | 25 | +0.018 | [-0.009, +0.044] |
| uncertainty_miscalibration | position_rmse | 25 | +0.064 | [+0.034, +0.095] |
| uncertainty_miscalibration | position_rmse_distance_only | 25 | -0.036 | [-0.060, -0.013] |
| uncertainty_miscalibration | precision | 25 | -0.401 | [-0.418, -0.383] |
| uncertainty_miscalibration | recall | 25 | +0.425 | [+0.397, +0.452] |
| vision_dropout | gospa_p1 | 25 | +0.354 | [+0.137, +0.571] |
| vision_dropout | idf1 | 25 | +0.008 | [-0.027, +0.043] |
| vision_dropout | mota | 25 | -0.133 | [-0.196, -0.070] |
| vision_dropout | position_coverage_95 | 25 | -0.020 | [-0.068, +0.027] |
| vision_dropout | position_rmse | 25 | -0.006 | [-0.028, +0.017] |
| vision_dropout | position_rmse_distance_only | 25 | -0.021 | [-0.034, -0.008] |
| vision_dropout | precision | 25 | -0.080 | [-0.117, -0.043] |
| vision_dropout | recall | 25 | +0.000 | [-0.001, +0.001] |

## Paired differences (fused-bias-estimated minus fused)

Same conventions as the first comparison.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| crossing_targets | gospa_p1 | 25 | +0.049 | [-0.159, +0.257] |
| crossing_targets | idf1 | 25 | -0.015 | [-0.040, +0.009] |
| crossing_targets | mota | 25 | -0.021 | [-0.078, +0.036] |
| crossing_targets | position_coverage_95 | 25 | -0.005 | [-0.060, +0.051] |
| crossing_targets | position_rmse | 25 | -0.001 | [-0.021, +0.019] |
| crossing_targets | position_rmse_distance_only | 25 | -0.003 | [-0.020, +0.014] |
| crossing_targets | precision | 25 | -0.010 | [-0.036, +0.016] |
| crossing_targets | recall | 25 | +0.000 | [-0.000, +0.001] |
| delivery_delay | gospa_p1 | 25 | +0.006 | [-0.158, +0.170] |
| delivery_delay | idf1 | 25 | -0.002 | [-0.029, +0.025] |
| delivery_delay | mota | 25 | -0.003 | [-0.054, +0.049] |
| delivery_delay | position_coverage_95 | 25 | -0.014 | [-0.050, +0.023] |
| delivery_delay | position_rmse | 25 | +0.014 | [+0.002, +0.026] |
| delivery_delay | position_rmse_distance_only | 25 | +0.002 | [-0.007, +0.011] |
| delivery_delay | precision | 25 | -0.002 | [-0.024, +0.020] |
| delivery_delay | recall | 25 | -0.000 | [-0.000, +0.000] |
| delivery_delay_retrodiction | gospa_p1 | 25 | -0.054 | [-0.228, +0.120] |
| delivery_delay_retrodiction | idf1 | 25 | -0.028 | [-0.067, +0.011] |
| delivery_delay_retrodiction | mota | 25 | +0.020 | [-0.031, +0.071] |
| delivery_delay_retrodiction | position_coverage_95 | 25 | -0.003 | [-0.044, +0.039] |
| delivery_delay_retrodiction | position_rmse | 25 | +0.025 | [+0.003, +0.046] |
| delivery_delay_retrodiction | position_rmse_distance_only | 25 | +0.015 | [-0.001, +0.031] |
| delivery_delay_retrodiction | precision | 25 | +0.012 | [-0.010, +0.035] |
| delivery_delay_retrodiction | recall | 25 | -0.000 | [-0.002, +0.001] |
| dense_clutter | gospa_p1 | 25 | +0.107 | [-0.060, +0.275] |
| dense_clutter | idf1 | 25 | -0.008 | [-0.023, +0.008] |
| dense_clutter | mota | 25 | -0.031 | [-0.082, +0.020] |
| dense_clutter | position_coverage_95 | 25 | -0.026 | [-0.062, +0.010] |
| dense_clutter | position_rmse | 25 | +0.005 | [-0.016, +0.026] |
| dense_clutter | position_rmse_distance_only | 25 | +0.007 | [-0.003, +0.017] |
| dense_clutter | precision | 25 | -0.004 | [-0.010, +0.002] |
| dense_clutter | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| false_observations | gospa_p1 | 25 | +0.149 | [-0.025, +0.324] |
| false_observations | idf1 | 25 | -0.030 | [-0.055, -0.005] |
| false_observations | mota | 25 | -0.040 | [-0.090, +0.009] |
| false_observations | position_coverage_95 | 25 | -0.072 | [-0.125, -0.018] |
| false_observations | position_rmse | 25 | +0.008 | [-0.014, +0.029] |
| false_observations | position_rmse_distance_only | 25 | +0.010 | [-0.008, +0.027] |
| false_observations | precision | 25 | -0.014 | [-0.033, +0.004] |
| false_observations | recall | 25 | -0.001 | [-0.002, +0.001] |
| measurement_bias | gospa_p1 | 25 | +0.023 | [-0.097, +0.144] |
| measurement_bias | idf1 | 25 | +0.004 | [-0.002, +0.011] |
| measurement_bias | mota | 25 | -0.007 | [-0.046, +0.032] |
| measurement_bias | position_coverage_95 | 25 | +0.000 | [-0.004, +0.004] |
| measurement_bias | position_rmse | 25 | -0.002 | [-0.009, +0.005] |
| measurement_bias | position_rmse_distance_only | 25 | -0.007 | [-0.015, +0.000] |
| measurement_bias | precision | 25 | -0.003 | [-0.017, +0.011] |
| measurement_bias | recall | 25 | +0.005 | [-0.008, +0.019] |
| moving_observer | gospa_p1 | 25 | +0.089 | [-0.122, +0.300] |
| moving_observer | idf1 | 25 | -0.008 | [-0.029, +0.013] |
| moving_observer | mota | 25 | -0.016 | [-0.075, +0.043] |
| moving_observer | position_coverage_95 | 25 | -0.042 | [-0.099, +0.016] |
| moving_observer | position_rmse | 25 | +0.015 | [-0.009, +0.039] |
| moving_observer | position_rmse_distance_only | 25 | +0.015 | [+0.000, +0.029] |
| moving_observer | precision | 25 | -0.007 | [-0.035, +0.020] |
| moving_observer | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| nominal | gospa_p1 | 25 | +0.026 | [-0.163, +0.216] |
| nominal | idf1 | 25 | -0.004 | [-0.020, +0.012] |
| nominal | mota | 25 | -0.000 | [-0.056, +0.055] |
| nominal | position_coverage_95 | 25 | -0.064 | [-0.108, -0.020] |
| nominal | position_rmse | 25 | +0.005 | [-0.020, +0.030] |
| nominal | position_rmse_distance_only | 25 | +0.009 | [-0.000, +0.019] |
| nominal | precision | 25 | +0.001 | [-0.024, +0.026] |
| nominal | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| range_dropout | gospa_p1 | 25 | +0.069 | [-0.055, +0.193] |
| range_dropout | idf1 | 25 | -0.012 | [-0.031, +0.007] |
| range_dropout | mota | 25 | -0.014 | [-0.050, +0.023] |
| range_dropout | position_coverage_95 | 25 | -0.059 | [-0.092, -0.027] |
| range_dropout | position_rmse | 25 | +0.012 | [-0.001, +0.024] |
| range_dropout | position_rmse_distance_only | 25 | +0.010 | [-0.002, +0.022] |
| range_dropout | precision | 25 | -0.007 | [-0.030, +0.015] |
| range_dropout | recall | 25 | -0.000 | [-0.002, +0.001] |
| sensor_disagreement_large_bias | gospa_p1 | 25 | -0.007 | [-0.031, +0.017] |
| sensor_disagreement_large_bias | idf1 | 25 | +0.004 | [-0.001, +0.009] |
| sensor_disagreement_large_bias | mota | 25 | +0.002 | [-0.007, +0.010] |
| sensor_disagreement_large_bias | position_coverage_95 | 25 | +0.002 | [-0.005, +0.009] |
| sensor_disagreement_large_bias | position_rmse | 25 | -0.004 | [-0.013, +0.006] |
| sensor_disagreement_large_bias | position_rmse_distance_only | 25 | -0.000 | [-0.003, +0.003] |
| sensor_disagreement_large_bias | precision | 25 | +0.001 | [-0.005, +0.006] |
| sensor_disagreement_large_bias | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| sensor_disagreement_within_gate | gospa_p1 | 25 | -1.071 | [-1.320, -0.822] |
| sensor_disagreement_within_gate | idf1 | 25 | +0.132 | [+0.092, +0.172] |
| sensor_disagreement_within_gate | mota | 25 | +0.296 | [+0.221, +0.371] |
| sensor_disagreement_within_gate | position_coverage_95 | 25 | +0.438 | [+0.374, +0.502] |
| sensor_disagreement_within_gate | position_rmse | 25 | -0.140 | [-0.172, -0.109] |
| sensor_disagreement_within_gate | position_rmse_distance_only | 25 | -0.068 | [-0.090, -0.047] |
| sensor_disagreement_within_gate | precision | 25 | +0.114 | [+0.084, +0.145] |
| sensor_disagreement_within_gate | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| sensor_disagreement_within_gate_high | gospa_p1 | 25 | -1.588 | [-1.753, -1.423] |
| sensor_disagreement_within_gate_high | idf1 | 25 | +0.139 | [+0.106, +0.172] |
| sensor_disagreement_within_gate_high | mota | 25 | +0.465 | [+0.416, +0.513] |
| sensor_disagreement_within_gate_high | position_coverage_95 | 25 | +0.383 | [+0.302, +0.465] |
| sensor_disagreement_within_gate_high | position_rmse | 25 | -0.177 | [-0.221, -0.134] |
| sensor_disagreement_within_gate_high | position_rmse_distance_only | 25 | -0.075 | [-0.094, -0.057] |
| sensor_disagreement_within_gate_high | precision | 25 | +0.164 | [+0.140, +0.189] |
| sensor_disagreement_within_gate_high | recall | 25 | +0.000 | [-0.000, +0.000] |
| sensor_disagreement_within_gate_low | gospa_p1 | 25 | -0.555 | [-0.748, -0.363] |
| sensor_disagreement_within_gate_low | idf1 | 25 | +0.076 | [+0.046, +0.106] |
| sensor_disagreement_within_gate_low | mota | 25 | +0.143 | [+0.083, +0.202] |
| sensor_disagreement_within_gate_low | position_coverage_95 | 25 | +0.345 | [+0.287, +0.404] |
| sensor_disagreement_within_gate_low | position_rmse | 25 | -0.070 | [-0.103, -0.038] |
| sensor_disagreement_within_gate_low | position_rmse_distance_only | 25 | -0.041 | [-0.058, -0.024] |
| sensor_disagreement_within_gate_low | precision | 25 | +0.060 | [+0.034, +0.086] |
| sensor_disagreement_within_gate_low | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | gospa_p1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | idf1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | mota | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | position_coverage_95 | 0 | N/A | N/A |
| stale_rejection | position_rmse | 0 | N/A | N/A |
| stale_rejection | position_rmse_distance_only | 0 | N/A | N/A |
| stale_rejection | precision | 0 | N/A | N/A |
| stale_rejection | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| uncertainty_miscalibration | gospa_p1 | 25 | +0.026 | [-0.136, +0.188] |
| uncertainty_miscalibration | idf1 | 25 | -0.005 | [-0.021, +0.012] |
| uncertainty_miscalibration | mota | 25 | -0.007 | [-0.062, +0.048] |
| uncertainty_miscalibration | position_coverage_95 | 25 | -0.004 | [-0.025, +0.016] |
| uncertainty_miscalibration | position_rmse | 25 | +0.005 | [-0.030, +0.040] |
| uncertainty_miscalibration | position_rmse_distance_only | 25 | +0.004 | [-0.018, +0.026] |
| uncertainty_miscalibration | precision | 25 | -0.002 | [-0.013, +0.009] |
| uncertainty_miscalibration | recall | 25 | -0.006 | [-0.012, +0.000] |
| vision_dropout | gospa_p1 | 25 | +0.070 | [-0.078, +0.217] |
| vision_dropout | idf1 | 25 | -0.001 | [-0.024, +0.023] |
| vision_dropout | mota | 25 | -0.020 | [-0.064, +0.023] |
| vision_dropout | position_coverage_95 | 25 | -0.025 | [-0.060, +0.010] |
| vision_dropout | position_rmse | 25 | +0.004 | [-0.005, +0.014] |
| vision_dropout | position_rmse_distance_only | 25 | +0.002 | [-0.006, +0.010] |
| vision_dropout | precision | 25 | -0.013 | [-0.036, +0.011] |
| vision_dropout | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |

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
| crossing_targets | fused | 0.992 | 0.992 | 0.660 | 195.6 |
| crossing_targets | fused_bias_estimated | 0.990 | 0.990 | 0.658 | 195.0 |
| delivery_delay | range_only | N/A | N/A | 0.000 | 0.0 |
| delivery_delay | fused | 0.996 | 0.995 | 0.653 | 191.8 |
| delivery_delay | fused_bias_estimated | 0.997 | 0.996 | 0.653 | 191.7 |
| delivery_delay_retrodiction | range_only | N/A | N/A | 0.000 | 0.0 |
| delivery_delay_retrodiction | fused | 0.997 | 0.996 | 0.651 | 191.1 |
| delivery_delay_retrodiction | fused_bias_estimated | 0.997 | 0.996 | 0.650 | 190.7 |
| dense_clutter | range_only | N/A | N/A | 0.000 | 0.0 |
| dense_clutter | fused | 0.998 | 0.998 | 0.620 | 184.0 |
| dense_clutter | fused_bias_estimated | 1.000 | 0.999 | 0.618 | 183.2 |
| false_observations | range_only | N/A | N/A | 0.000 | 0.0 |
| false_observations | fused | 1.000 | 0.999 | 0.638 | 189.1 |
| false_observations | fused_bias_estimated | 1.000 | 1.000 | 0.639 | 189.4 |
| measurement_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| measurement_bias | fused | 0.997 | 0.996 | 0.648 | 171.4 |
| measurement_bias | fused_bias_estimated | 0.998 | 0.997 | 0.654 | 174.1 |
| moving_observer | range_only | N/A | N/A | 0.000 | 0.0 |
| moving_observer | fused | 1.000 | 1.000 | 0.652 | 193.6 |
| moving_observer | fused_bias_estimated | 0.999 | 0.999 | 0.652 | 193.5 |
| nominal | range_only | N/A | N/A | 0.000 | 0.0 |
| nominal | fused | 0.999 | 0.998 | 0.653 | 193.7 |
| nominal | fused_bias_estimated | 0.999 | 0.999 | 0.653 | 193.8 |
| range_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| range_dropout | fused | 0.998 | 0.997 | 0.653 | 191.8 |
| range_dropout | fused_bias_estimated | 0.999 | 0.999 | 0.652 | 191.6 |
| sensor_disagreement_large_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_large_bias | fused | 0.417 | 0.323 | 0.029 | 8.7 |
| sensor_disagreement_large_bias | fused_bias_estimated | 0.427 | 0.276 | 0.020 | 5.8 |
| sensor_disagreement_within_gate | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate | fused | 0.994 | 0.992 | 0.637 | 188.7 |
| sensor_disagreement_within_gate | fused_bias_estimated | 0.998 | 0.997 | 0.653 | 193.4 |
| sensor_disagreement_within_gate_high | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_high | fused | 0.971 | 0.960 | 0.607 | 179.8 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 0.997 | 0.996 | 0.646 | 191.3 |
| sensor_disagreement_within_gate_low | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_low | fused | 0.999 | 0.998 | 0.649 | 192.4 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 0.999 | 0.999 | 0.653 | 193.7 |
| stale_rejection | range_only | N/A | N/A | N/A | 0.0 |
| stale_rejection | fused | N/A | N/A | N/A | 0.0 |
| stale_rejection | fused_bias_estimated | N/A | N/A | N/A | 0.0 |
| uncertainty_miscalibration | range_only | N/A | N/A | 0.000 | 0.0 |
| uncertainty_miscalibration | fused | 0.997 | 0.996 | 0.631 | 179.2 |
| uncertainty_miscalibration | fused_bias_estimated | 0.998 | 0.997 | 0.638 | 180.1 |
| vision_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| vision_dropout | fused | 0.999 | 0.999 | 0.648 | 192.2 |
| vision_dropout | fused_bias_estimated | 0.999 | 0.999 | 0.646 | 191.6 |

## Estimator consistency (NEES and NIS)

Statistics per degree of freedom, pooled over seeds; the nominal value for a
consistent filter is 1.0 and the bracket is the two-sided 95% chi-square interval
for the pooled degrees of freedom. `within`, `above` or `below` says where the value
falls: above means overconfident, below means underconfident.

- NEES (position and velocity, 2 DOF each) uses only samples matched to a ground-truth
  object inside the 2 m matching gate, so it is conditioned on that gate;
  `Unmatched GT samples` is the mean number of ground-truth samples with no matched
  track (no track inside the gate, or its tracks matched other objects), which are
  therefore absent from NEES.
- NIS uses the filter's own innovations for every applied update, with no ground
  truth. Updates exist only after gating, so NIS is truncated and sits slightly
  below 1.0 even for a correct filter.
- Samples within one track are correlated and seeds share the scenario, so the
  intervals assume more independence than there is and are optimistic.

| Scenario | Method | Position NEES per DOF | Velocity NEES per DOF | NIS per DOF | NEES samples (mean) | NIS updates (mean) | Unmatched GT samples |
|---|---|---|---|---|---|---|---|
| crossing_targets | range_only | 1.616 [0.977, 1.023] above | 0.555 [0.977, 1.023] below | 0.755 [0.981, 1.019] below | 296 | 276.6 | 7 |
| crossing_targets | fused | 2.181 [0.977, 1.023] above | 0.578 [0.977, 1.023] below | 0.695 [0.983, 1.017] below | 297 | 545.1 | 6 |
| crossing_targets | fused_bias_estimated | 3.178 [0.977, 1.023] above | 0.785 [0.977, 1.023] below | 0.694 [0.983, 1.017] below | 297 | 543.3 | 6 |
| delivery_delay | range_only | 10.990 [0.977, 1.023] above | 2.084 [0.977, 1.023] above | 0.811 [0.981, 1.020] below | 293 | 268.0 | 10 |
| delivery_delay | fused | 35.853 [0.977, 1.023] above | 2.616 [0.977, 1.023] above | 0.758 [0.983, 1.017] below | 294 | 526.4 | 9 |
| delivery_delay | fused_bias_estimated | 29.829 [0.977, 1.023] above | 2.632 [0.977, 1.023] above | 0.764 [0.983, 1.017] below | 294 | 524.8 | 9 |
| delivery_delay_retrodiction | range_only | 1.886 [0.977, 1.023] above | 1.830 [0.977, 1.023] above | 0.975 [0.980, 1.020] below | 293 | 262.3 | 10 |
| delivery_delay_retrodiction | fused | 5.155 [0.977, 1.023] above | 2.254 [0.977, 1.023] above | 2.215 [0.983, 1.018] above | 294 | 483.9 | 9 |
| delivery_delay_retrodiction | fused_bias_estimated | 6.353 [0.977, 1.023] above | 2.480 [0.977, 1.023] above | 1.881 [0.982, 1.018] above | 294 | 481.0 | 9 |
| dense_clutter | range_only | 1.666 [0.977, 1.023] above | 1.633 [0.977, 1.023] above | 0.829 [0.981, 1.019] below | 296 | 282.9 | 7 |
| dense_clutter | fused | 34.319 [0.977, 1.023] above | 2.214 [0.977, 1.023] above | 0.840 [0.985, 1.015] below | 297 | 821.3 | 6 |
| dense_clutter | fused_bias_estimated | 34.382 [0.977, 1.023] above | 2.378 [0.977, 1.023] above | 0.844 [0.985, 1.015] below | 297 | 817.2 | 6 |
| false_observations | range_only | 1.863 [0.977, 1.023] above | 1.583 [0.977, 1.023] above | 0.801 [0.981, 1.019] below | 296 | 274.2 | 7 |
| false_observations | fused | 3.607 [0.977, 1.023] above | 2.173 [0.977, 1.023] above | 0.775 [0.983, 1.017] below | 296 | 571.7 | 7 |
| false_observations | fused_bias_estimated | 4.964 [0.977, 1.023] above | 2.267 [0.977, 1.023] above | 0.775 [0.983, 1.017] below | 296 | 570.2 | 7 |
| measurement_bias | range_only | 76.615 [0.976, 1.024] above | 12.130 [0.976, 1.024] above | 0.852 [0.981, 1.020] below | 261 | 268.8 | 42 |
| measurement_bias | fused | 74.655 [0.976, 1.024] above | 12.912 [0.976, 1.024] above | 0.791 [0.983, 1.017] below | 265 | 532.0 | 38 |
| measurement_bias | fused_bias_estimated | 74.455 [0.976, 1.024] above | 12.318 [0.976, 1.024] above | 0.790 [0.983, 1.017] below | 266 | 530.7 | 37 |
| moving_observer | range_only | 1.896 [0.977, 1.023] above | 1.609 [0.977, 1.023] above | 0.833 [0.981, 1.019] below | 296 | 273.2 | 7 |
| moving_observer | fused | 2.464 [0.977, 1.023] above | 2.103 [0.977, 1.023] above | 0.774 [0.983, 1.017] below | 297 | 536.1 | 6 |
| moving_observer | fused_bias_estimated | 2.842 [0.977, 1.023] above | 2.189 [0.977, 1.023] above | 0.768 [0.983, 1.017] below | 297 | 533.6 | 6 |
| nominal | range_only | 1.852 [0.977, 1.023] above | 1.607 [0.977, 1.023] above | 0.815 [0.981, 1.019] below | 296 | 272.7 | 7 |
| nominal | fused | 2.453 [0.977, 1.023] above | 2.037 [0.977, 1.023] above | 0.757 [0.983, 1.017] below | 297 | 537.2 | 6 |
| nominal | fused_bias_estimated | 2.798 [0.977, 1.023] above | 2.069 [0.977, 1.023] above | 0.760 [0.983, 1.017] below | 297 | 535.9 | 6 |
| range_dropout | range_only | 1.332 [0.976, 1.024] above | 1.408 [0.976, 1.024] above | 0.824 [0.974, 1.026] below | 267 | 149.9 | 36 |
| range_dropout | fused | 1.941 [0.977, 1.023] above | 2.018 [0.977, 1.023] above | 0.768 [0.979, 1.021] below | 294 | 410.2 | 9 |
| range_dropout | fused_bias_estimated | 3.856 [0.977, 1.023] above | 2.118 [0.977, 1.023] above | 0.778 [0.979, 1.021] below | 294 | 409.1 | 9 |
| sensor_disagreement_large_bias | range_only | 1.852 [0.977, 1.023] above | 1.607 [0.977, 1.023] above | 0.815 [0.981, 1.019] below | 296 | 272.7 | 7 |
| sensor_disagreement_large_bias | fused | 7.521 [0.977, 1.023] above | 1.902 [0.977, 1.023] above | 0.821 [0.981, 1.019] below | 296 | 284.2 | 7 |
| sensor_disagreement_large_bias | fused_bias_estimated | 6.513 [0.977, 1.023] above | 1.820 [0.977, 1.023] above | 0.818 [0.981, 1.019] below | 296 | 284.0 | 7 |
| sensor_disagreement_within_gate | range_only | 1.852 [0.977, 1.023] above | 1.607 [0.977, 1.023] above | 0.815 [0.981, 1.019] below | 296 | 272.7 | 7 |
| sensor_disagreement_within_gate | fused | 12.465 [0.977, 1.023] above | 2.822 [0.977, 1.023] above | 0.828 [0.983, 1.017] below | 296 | 516.8 | 7 |
| sensor_disagreement_within_gate | fused_bias_estimated | 3.216 [0.977, 1.023] above | 2.289 [0.977, 1.023] above | 0.774 [0.983, 1.017] below | 296 | 532.0 | 7 |
| sensor_disagreement_within_gate_high | range_only | 1.852 [0.977, 1.023] above | 1.607 [0.977, 1.023] above | 0.815 [0.981, 1.019] below | 296 | 272.7 | 7 |
| sensor_disagreement_within_gate_high | fused | 21.229 [0.977, 1.023] above | 2.985 [0.977, 1.023] above | 0.825 [0.983, 1.017] below | 296 | 507.7 | 7 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 2.918 [0.977, 1.023] above | 2.262 [0.977, 1.023] above | 0.778 [0.983, 1.017] below | 296 | 527.5 | 7 |
| sensor_disagreement_within_gate_low | range_only | 1.852 [0.977, 1.023] above | 1.607 [0.977, 1.023] above | 0.815 [0.981, 1.019] below | 296 | 272.7 | 7 |
| sensor_disagreement_within_gate_low | fused | 32.004 [0.977, 1.023] above | 2.328 [0.977, 1.023] above | 0.809 [0.983, 1.017] below | 297 | 525.8 | 6 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 2.757 [0.977, 1.023] above | 2.174 [0.977, 1.023] above | 0.763 [0.983, 1.017] below | 297 | 533.8 | 6 |
| stale_rejection | range_only | N/A | N/A | N/A | 0 | 0.0 | 303 |
| stale_rejection | fused | N/A | N/A | N/A | 0 | 0.0 | 303 |
| stale_rejection | fused_bias_estimated | N/A | N/A | N/A | 0 | 0.0 | 303 |
| uncertainty_miscalibration | range_only | 27.465 [0.969, 1.032] above | 8.316 [0.969, 1.032] above | 1.052 [0.974, 1.026] above | 155 | 152.3 | 148 |
| uncertainty_miscalibration | fused | 24.750 [0.977, 1.023] above | 8.397 [0.977, 1.023] above | 0.983 [0.979, 1.022] within | 284 | 383.5 | 19 |
| uncertainty_miscalibration | fused_bias_estimated | 3250.580 [0.977, 1.023] above | 8.597 [0.977, 1.023] above | 0.993 [0.979, 1.021] within | 282 | 384.2 | 21 |
| vision_dropout | range_only | 1.852 [0.977, 1.023] above | 1.607 [0.977, 1.023] above | 0.815 [0.981, 1.019] below | 296 | 272.7 | 7 |
| vision_dropout | fused | 3.294 [0.977, 1.023] above | 1.857 [0.977, 1.023] above | 0.791 [0.982, 1.018] below | 297 | 402.5 | 6 |
| vision_dropout | fused_bias_estimated | 3.438 [0.977, 1.023] above | 1.902 [0.977, 1.023] above | 0.788 [0.982, 1.018] below | 297 | 399.5 | 6 |

## Duplicate-track sensitivity to the matching gate

Mean number of duplicate tracks per seed when the evaluation matching gate is
1.0, 2.0 or 3.0 m. The three gates were chosen before running (see the project issue
tracker). The 2.0 m column is the headline gate used everywhere else in this
report when it is the evaluator gate; the others show how much the
duplicate count depends on that choice, not which gate is correct.

| Scenario | Method | 1.0 m | 2.0 m | 3.0 m |
|---|---|---|---|---|
| crossing_targets | range_only | 3.7 | 3.8 | 3.8 |
| crossing_targets | fused | 4.6 | 5.0 | 5.1 |
| crossing_targets | fused_bias_estimated | 4.6 | 4.9 | 5.0 |
| delivery_delay | range_only | 3.1 | 3.2 | 3.2 |
| delivery_delay | fused | 5.5 | 6.2 | 6.2 |
| delivery_delay | fused_bias_estimated | 5.4 | 6.3 | 6.4 |
| delivery_delay_retrodiction | range_only | 4.2 | 4.3 | 4.3 |
| delivery_delay_retrodiction | fused | 9.2 | 10.4 | 10.5 |
| delivery_delay_retrodiction | fused_bias_estimated | 9.3 | 10.3 | 10.4 |
| dense_clutter | range_only | 3.4 | 3.4 | 3.4 |
| dense_clutter | fused | 6.8 | 9.1 | 11.0 |
| dense_clutter | fused_bias_estimated | 7.2 | 9.3 | 11.4 |
| false_observations | range_only | 2.8 | 2.9 | 2.9 |
| false_observations | fused | 5.9 | 7.2 | 7.4 |
| false_observations | fused_bias_estimated | 6.0 | 7.4 | 7.6 |
| measurement_bias | range_only | 0.0 | 1.3 | 2.6 |
| measurement_bias | fused | 0.0 | 2.6 | 6.3 |
| measurement_bias | fused_bias_estimated | 0.1 | 2.7 | 6.4 |
| moving_observer | range_only | 2.6 | 2.8 | 2.8 |
| moving_observer | fused | 4.6 | 5.3 | 5.3 |
| moving_observer | fused_bias_estimated | 4.8 | 5.4 | 5.4 |
| nominal | range_only | 2.9 | 3.0 | 3.0 |
| nominal | fused | 5.3 | 6.0 | 6.0 |
| nominal | fused_bias_estimated | 5.1 | 5.5 | 5.5 |
| range_dropout | range_only | 0.3 | 0.4 | 0.4 |
| range_dropout | fused | 3.3 | 4.0 | 4.1 |
| range_dropout | fused_bias_estimated | 3.0 | 3.6 | 3.7 |
| sensor_disagreement_large_bias | range_only | 2.9 | 3.0 | 3.0 |
| sensor_disagreement_large_bias | fused | 3.2 | 3.7 | 3.9 |
| sensor_disagreement_large_bias | fused_bias_estimated | 3.2 | 3.8 | 4.0 |
| sensor_disagreement_within_gate | range_only | 2.9 | 3.0 | 3.0 |
| sensor_disagreement_within_gate | fused | 8.0 | 9.4 | 9.8 |
| sensor_disagreement_within_gate | fused_bias_estimated | 5.4 | 5.9 | 6.0 |
| sensor_disagreement_within_gate_high | range_only | 2.9 | 3.0 | 3.0 |
| sensor_disagreement_within_gate_high | fused | 8.8 | 10.1 | 10.3 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 5.7 | 6.0 | 6.1 |
| sensor_disagreement_within_gate_low | range_only | 2.9 | 3.0 | 3.0 |
| sensor_disagreement_within_gate_low | fused | 7.6 | 8.3 | 8.4 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 5.5 | 5.9 | 5.9 |
| stale_rejection | range_only | 0.0 | 0.0 | 0.0 |
| stale_rejection | fused | 0.0 | 0.0 | 0.0 |
| stale_rejection | fused_bias_estimated | 0.0 | 0.0 | 0.0 |
| uncertainty_miscalibration | range_only | 2.4 | 2.3 | 2.3 |
| uncertainty_miscalibration | fused | 33.0 | 37.1 | 37.8 |
| uncertainty_miscalibration | fused_bias_estimated | 34.3 | 37.2 | 38.1 |
| vision_dropout | range_only | 2.9 | 3.0 | 3.0 |
| vision_dropout | fused | 4.4 | 4.7 | 4.8 |
| vision_dropout | fused_bias_estimated | 4.7 | 5.1 | 5.1 |

## Vision observation acceptance (fused method)

Mean per seed. `Generated` = produced by vision sensors; `Delivered` = left the
pending queue (generated minus those still pending at the end); `Gate-rejected` =
at least one track was evaluated and none passed the chi-square gate;
`Lost competition` = passed the gate for some track but lost the one-to-one
assignment; `Other unassigned` = no evaluable candidate track; `Stale/invalid` =
rejected outside association; `Applied` = used in a track update.

| Scenario | Generated | Delivered | Gate-rejected | Lost competition | Other unassigned | Stale/invalid | Applied |
|---|---|---|---|---|---|---|---|
| crossing_targets | 275.8 | 275.8 | 8.8 | 0.1 | 0.0 | 0.0 | 267.0 |
| crossing_targets | 275.8 | 275.8 | 9.9 | 0.1 | 0.0 | 0.0 | 265.9 |
| delivery_delay | 274.8 | 271.9 | 11.2 | 0.9 | 0.0 | 1.7 | 258.2 |
| delivery_delay | 274.8 | 271.9 | 12.8 | 0.6 | 0.0 | 1.7 | 256.9 |
| delivery_delay_retrodiction | 274.8 | 271.9 | 43.3 | 1.0 | 0.0 | 1.7 | 226.0 |
| delivery_delay_retrodiction | 274.8 | 271.9 | 44.2 | 0.9 | 0.0 | 1.7 | 225.1 |
| dense_clutter | 1071.9 | 1071.9 | 512.5 | 20.6 | 0.0 | 0.0 | 538.8 |
| dense_clutter | 1071.9 | 1071.9 | 516.0 | 20.8 | 0.0 | 0.0 | 535.0 |
| false_observations | 571.9 | 571.9 | 271.1 | 2.9 | 0.0 | 0.0 | 297.9 |
| false_observations | 571.9 | 571.9 | 271.9 | 3.0 | 0.0 | 0.0 | 296.9 |
| measurement_bias | 275.8 | 275.8 | 12.6 | 0.0 | 0.0 | 0.0 | 263.2 |
| measurement_bias | 275.8 | 275.8 | 13.9 | 0.0 | 0.0 | 0.0 | 261.9 |
| moving_observer | 275.8 | 275.8 | 13.2 | 0.1 | 0.0 | 0.0 | 262.5 |
| moving_observer | 275.8 | 275.8 | 14.6 | 0.0 | 0.0 | 0.0 | 261.2 |
| nominal | 275.8 | 275.8 | 12.0 | 0.0 | 0.0 | 0.0 | 263.8 |
| nominal | 275.8 | 275.8 | 13.1 | 0.0 | 0.0 | 0.0 | 262.7 |
| range_dropout | 275.8 | 275.8 | 17.0 | 0.0 | 0.2 | 0.0 | 258.6 |
| range_dropout | 275.8 | 275.8 | 18.2 | 0.1 | 0.2 | 0.0 | 257.3 |
| sensor_disagreement_large_bias | 275.8 | 275.8 | 263.7 | 0.3 | 0.0 | 0.0 | 11.8 |
| sensor_disagreement_large_bias | 275.8 | 275.8 | 263.7 | 0.4 | 0.0 | 0.0 | 11.8 |
| sensor_disagreement_within_gate | 275.8 | 275.8 | 25.3 | 0.1 | 0.0 | 0.0 | 250.5 |
| sensor_disagreement_within_gate | 275.8 | 275.8 | 16.3 | 0.0 | 0.0 | 0.0 | 259.5 |
| sensor_disagreement_within_gate_high | 275.8 | 275.8 | 34.2 | 0.0 | 0.0 | 0.0 | 241.7 |
| sensor_disagreement_within_gate_high | 275.8 | 275.8 | 20.4 | 0.0 | 0.0 | 0.0 | 255.5 |
| sensor_disagreement_within_gate_low | 275.8 | 275.8 | 19.4 | 0.0 | 0.0 | 0.0 | 256.4 |
| sensor_disagreement_within_gate_low | 275.8 | 275.8 | 14.8 | 0.0 | 0.0 | 0.0 | 261.0 |
| stale_rejection | 274.8 | 266.3 | 0.0 | 0.0 | 0.4 | 265.9 | 0.0 |
| stale_rejection | 274.8 | 266.3 | 0.0 | 0.0 | 0.4 | 265.9 | 0.0 |
| uncertainty_miscalibration | 275.8 | 275.8 | 36.0 | 0.0 | 0.0 | 0.0 | 239.8 |
| uncertainty_miscalibration | 275.8 | 275.8 | 36.1 | 0.0 | 0.0 | 0.0 | 239.7 |
| vision_dropout | 136.6 | 136.6 | 7.2 | 0.0 | 0.0 | 0.0 | 129.4 |
| vision_dropout | 136.6 | 136.6 | 9.4 | 0.0 | 0.0 | 0.0 | 127.2 |

## Vision bias estimation (bias-estimated fusion)

A single global bearing bias per vision sensor, estimated by a scalar Kalman filter
from vision innovations on confirmed tracks (prior standard deviation 0.05 rad, random
walk 1e-4 rad per epoch; fixed in advance) and subtracted before gating and updating.
`Configured bias` is the bias injected by the scenario (never given to the estimator);
`Mean estimate` is the final estimate averaged over seeds. Only observations that pass the
gate are applied, so a bias too large for the gate is never learned, and vision updates
also pull the track toward the biased bearing, which slows learning.

| Scenario | Configured bias (rad) | Mean estimate (rad) | Estimator updates (mean) |
|---|---|---|---|
| crossing_targets | 0.0000 | 0.0002 | 173.8 |
| delivery_delay | 0.0000 | 0.0000 | 154.0 |
| delivery_delay_retrodiction | 0.0000 | -0.0002 | 113.8 |
| dense_clutter | 0.0000 | 0.0005 | 143.6 |
| false_observations | 0.0000 | -0.0002 | 156.3 |
| measurement_bias | 0.0000 | 0.0000 | 149.3 |
| moving_observer | 0.0000 | 0.0002 | 167.8 |
| nominal | 0.0000 | 0.0002 | 166.3 |
| range_dropout | 0.0000 | -0.0003 | 101.8 |
| sensor_disagreement_large_bias | 0.1200 | 0.0004 | 1.1 |
| sensor_disagreement_within_gate | 0.0150 | 0.0152 | 162.2 |
| sensor_disagreement_within_gate_high | 0.0200 | 0.0197 | 160.9 |
| sensor_disagreement_within_gate_low | 0.0100 | 0.0102 | 163.0 |
| stale_rejection | 0.0000 | 0.0000 | 0.0 |
| uncertainty_miscalibration | 0.0000 | 0.0005 | 4.3 |
| vision_dropout | 0.0000 | 0.0000 | 80.8 |

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
| crossing_targets | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| crossing_targets | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| crossing_targets | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| delivery_delay | range_only | 286.2 | 1.8 | 1.8 | 3.0 | 0.100 | 284.5 |
| delivery_delay | fused | 558.2 | 3.4 | 3.4 | 5.8 | 0.099 | 554.7 |
| delivery_delay | fused_bias_estimated | 558.2 | 3.4 | 3.4 | 5.8 | 0.099 | 554.7 |
| delivery_delay_retrodiction | range_only | 286.2 | 1.8 | 1.8 | 3.0 | 0.100 | 284.5 |
| delivery_delay_retrodiction | fused | 558.2 | 3.4 | 3.4 | 5.8 | 0.099 | 554.7 |
| delivery_delay_retrodiction | fused_bias_estimated | 558.2 | 3.4 | 3.4 | 5.8 | 0.099 | 554.7 |
| dense_clutter | range_only | 693.3 | 0.0 | 0.0 | 0.0 | 0.000 | 693.3 |
| dense_clutter | fused | 1765.2 | 0.0 | 0.0 | 0.0 | 0.000 | 1765.2 |
| dense_clutter | fused_bias_estimated | 1765.2 | 0.0 | 0.0 | 0.0 | 0.000 | 1765.2 |
| false_observations | range_only | 390.6 | 0.0 | 0.0 | 0.0 | 0.000 | 390.6 |
| false_observations | fused | 962.5 | 0.0 | 0.0 | 0.0 | 0.000 | 962.5 |
| false_observations | fused_bias_estimated | 962.5 | 0.0 | 0.0 | 0.0 | 0.000 | 962.5 |
| measurement_bias | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| measurement_bias | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| measurement_bias | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| moving_observer | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| moving_observer | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| moving_observer | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| nominal | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| nominal | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| nominal | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| range_dropout | range_only | 164.8 | 0.0 | 0.0 | 0.0 | 0.000 | 164.8 |
| range_dropout | fused | 440.6 | 0.0 | 0.0 | 0.0 | 0.000 | 440.6 |
| range_dropout | fused_bias_estimated | 440.6 | 0.0 | 0.0 | 0.0 | 0.000 | 440.6 |
| sensor_disagreement_large_bias | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| sensor_disagreement_large_bias | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| sensor_disagreement_large_bias | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| sensor_disagreement_within_gate | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| sensor_disagreement_within_gate | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| sensor_disagreement_within_gate | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| sensor_disagreement_within_gate_high | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| sensor_disagreement_within_gate_high | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| sensor_disagreement_within_gate_low | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| sensor_disagreement_within_gate_low | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| stale_rejection | range_only | 280.5 | 280.2 | 280.2 | 8.8 | 0.100 | 0.2 |
| stale_rejection | fused | 546.8 | 546.1 | 546.1 | 17.2 | 0.100 | 0.7 |
| stale_rejection | fused_bias_estimated | 546.8 | 546.1 | 546.1 | 17.2 | 0.100 | 0.7 |
| uncertainty_miscalibration | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| uncertainty_miscalibration | fused | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| uncertainty_miscalibration | fused_bias_estimated | 564.9 | 0.0 | 0.0 | 0.0 | 0.000 | 564.9 |
| vision_dropout | range_only | 289.1 | 0.0 | 0.0 | 0.0 | 0.000 | 289.1 |
| vision_dropout | fused | 425.7 | 0.0 | 0.0 | 0.0 | 0.000 | 425.7 |
| vision_dropout | fused_bias_estimated | 425.7 | 0.0 | 0.0 | 0.0 | 0.000 | 425.7 |

## Per-seed results

| Scenario | Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused − Range) | Bias-estimated RMSE (m) |
|---|---|---|---|---|---|
| crossing_targets | 25 | 0.153 | 0.154 | +0.001 | 0.153 |
| crossing_targets | 26 | 0.259 | 0.260 | +0.001 | 0.241 |
| crossing_targets | 27 | 0.144 | 0.135 | -0.009 | 0.125 |
| crossing_targets | 28 | 0.169 | 0.183 | +0.014 | 0.169 |
| crossing_targets | 29 | 0.178 | 0.127 | -0.051 | 0.262 |
| crossing_targets | 30 | 0.126 | 0.085 | -0.040 | 0.085 |
| crossing_targets | 31 | 0.154 | 0.173 | +0.019 | 0.169 |
| crossing_targets | 32 | 0.200 | 0.223 | +0.023 | 0.228 |
| crossing_targets | 33 | 0.161 | 0.147 | -0.014 | 0.147 |
| crossing_targets | 34 | 0.140 | 0.229 | +0.089 | 0.157 |
| crossing_targets | 35 | 0.238 | 0.333 | +0.096 | 0.394 |
| crossing_targets | 36 | 0.255 | 0.286 | +0.031 | 0.212 |
| crossing_targets | 37 | 0.126 | 0.155 | +0.028 | 0.157 |
| crossing_targets | 38 | 0.282 | 0.308 | +0.026 | 0.223 |
| crossing_targets | 39 | 0.209 | 0.177 | -0.032 | 0.210 |
| crossing_targets | 40 | 0.145 | 0.132 | -0.013 | 0.167 |
| crossing_targets | 41 | 0.162 | 0.184 | +0.022 | 0.259 |
| crossing_targets | 42 | 0.156 | 0.204 | +0.048 | 0.188 |
| crossing_targets | 43 | 0.150 | 0.166 | +0.015 | 0.167 |
| crossing_targets | 44 | 0.227 | 0.162 | -0.065 | 0.196 |
| crossing_targets | 45 | 0.111 | 0.200 | +0.089 | 0.207 |
| crossing_targets | 46 | 0.285 | 0.246 | -0.039 | 0.235 |
| crossing_targets | 47 | 0.198 | 0.193 | -0.004 | 0.130 |
| crossing_targets | 48 | 0.147 | 0.123 | -0.024 | 0.125 |
| crossing_targets | 49 | 0.123 | 0.194 | +0.071 | 0.140 |
| delivery_delay | 25 | 0.186 | 0.218 | +0.033 | 0.224 |
| delivery_delay | 26 | 0.243 | 0.240 | -0.004 | 0.242 |
| delivery_delay | 27 | 0.303 | 0.483 | +0.180 | 0.501 |
| delivery_delay | 28 | 0.329 | 0.274 | -0.055 | 0.275 |
| delivery_delay | 29 | 0.307 | 0.395 | +0.088 | 0.329 |
| delivery_delay | 30 | 0.281 | 0.296 | +0.015 | 0.299 |
| delivery_delay | 31 | 0.284 | 0.300 | +0.017 | 0.367 |
| delivery_delay | 32 | 0.264 | 0.213 | -0.052 | 0.233 |
| delivery_delay | 33 | 0.248 | 0.276 | +0.027 | 0.239 |
| delivery_delay | 34 | 0.340 | 0.297 | -0.043 | 0.301 |
| delivery_delay | 35 | 0.320 | 0.281 | -0.039 | 0.303 |
| delivery_delay | 36 | 0.496 | 0.503 | +0.007 | 0.489 |
| delivery_delay | 37 | 0.238 | 0.235 | -0.003 | 0.296 |
| delivery_delay | 38 | 0.259 | 0.468 | +0.209 | 0.521 |
| delivery_delay | 39 | 0.380 | 0.392 | +0.013 | 0.401 |
| delivery_delay | 40 | 0.347 | 0.316 | -0.032 | 0.362 |
| delivery_delay | 41 | 0.342 | 0.264 | -0.078 | 0.280 |
| delivery_delay | 42 | 0.302 | 0.283 | -0.019 | 0.290 |
| delivery_delay | 43 | 0.328 | 0.356 | +0.029 | 0.410 |
| delivery_delay | 44 | 0.247 | 0.277 | +0.030 | 0.307 |
| delivery_delay | 45 | 0.267 | 0.316 | +0.049 | 0.334 |
| delivery_delay | 46 | 0.219 | 0.239 | +0.020 | 0.260 |
| delivery_delay | 47 | 0.285 | 0.227 | -0.058 | 0.250 |
| delivery_delay | 48 | 0.197 | 0.173 | -0.024 | 0.178 |
| delivery_delay | 49 | 0.339 | 0.309 | -0.029 | 0.297 |
| delivery_delay_retrodiction | 25 | 0.233 | 0.263 | +0.030 | 0.322 |
| delivery_delay_retrodiction | 26 | 0.240 | 0.310 | +0.070 | 0.286 |
| delivery_delay_retrodiction | 27 | 0.284 | 0.379 | +0.095 | 0.376 |
| delivery_delay_retrodiction | 28 | 0.217 | 0.355 | +0.138 | 0.340 |
| delivery_delay_retrodiction | 29 | 0.294 | 0.251 | -0.043 | 0.342 |
| delivery_delay_retrodiction | 30 | 0.312 | 0.254 | -0.058 | 0.247 |
| delivery_delay_retrodiction | 31 | 0.228 | 0.346 | +0.118 | 0.318 |
| delivery_delay_retrodiction | 32 | 0.296 | 0.306 | +0.011 | 0.407 |
| delivery_delay_retrodiction | 33 | 0.237 | 0.211 | -0.026 | 0.208 |
| delivery_delay_retrodiction | 34 | 0.332 | 0.351 | +0.019 | 0.449 |
| delivery_delay_retrodiction | 35 | 0.328 | 0.314 | -0.014 | 0.355 |
| delivery_delay_retrodiction | 36 | 0.346 | 0.523 | +0.176 | 0.463 |
| delivery_delay_retrodiction | 37 | 0.195 | 0.220 | +0.025 | 0.258 |
| delivery_delay_retrodiction | 38 | 0.264 | 0.237 | -0.027 | 0.258 |
| delivery_delay_retrodiction | 39 | 0.363 | 0.499 | +0.136 | 0.463 |
| delivery_delay_retrodiction | 40 | 0.272 | 0.265 | -0.006 | 0.262 |
| delivery_delay_retrodiction | 41 | 0.327 | 0.380 | +0.053 | 0.455 |
| delivery_delay_retrodiction | 42 | 0.350 | 0.336 | -0.015 | 0.474 |
| delivery_delay_retrodiction | 43 | 0.324 | 0.329 | +0.005 | 0.346 |
| delivery_delay_retrodiction | 44 | 0.244 | 0.339 | +0.096 | 0.364 |
| delivery_delay_retrodiction | 45 | 0.237 | 0.242 | +0.005 | 0.333 |
| delivery_delay_retrodiction | 46 | 0.286 | 0.293 | +0.007 | 0.317 |
| delivery_delay_retrodiction | 47 | 0.238 | 0.208 | -0.030 | 0.230 |
| delivery_delay_retrodiction | 48 | 0.188 | 0.230 | +0.041 | 0.180 |
| delivery_delay_retrodiction | 49 | 0.399 | 0.344 | -0.055 | 0.344 |
| dense_clutter | 25 | 0.221 | 0.195 | -0.026 | 0.193 |
| dense_clutter | 26 | 0.178 | 0.266 | +0.088 | 0.230 |
| dense_clutter | 27 | 0.231 | 0.451 | +0.220 | 0.453 |
| dense_clutter | 28 | 0.162 | 0.176 | +0.014 | 0.178 |
| dense_clutter | 29 | 0.169 | 0.176 | +0.008 | 0.165 |
| dense_clutter | 30 | 0.244 | 0.232 | -0.012 | 0.236 |
| dense_clutter | 31 | 0.197 | 0.227 | +0.030 | 0.382 |
| dense_clutter | 32 | 0.246 | 0.245 | -0.001 | 0.249 |
| dense_clutter | 33 | 0.186 | 0.206 | +0.020 | 0.194 |
| dense_clutter | 34 | 0.298 | 0.295 | -0.003 | 0.293 |
| dense_clutter | 35 | 0.278 | 0.362 | +0.084 | 0.339 |
| dense_clutter | 36 | 0.264 | 0.410 | +0.146 | 0.376 |
| dense_clutter | 37 | 0.253 | 0.206 | -0.048 | 0.212 |
| dense_clutter | 38 | 0.175 | 0.297 | +0.122 | 0.303 |
| dense_clutter | 39 | 0.259 | 0.426 | +0.168 | 0.368 |
| dense_clutter | 40 | 0.210 | 0.205 | -0.005 | 0.245 |
| dense_clutter | 41 | 0.273 | 0.426 | +0.152 | 0.421 |
| dense_clutter | 42 | 0.273 | 0.218 | -0.055 | 0.246 |
| dense_clutter | 43 | 0.305 | 0.340 | +0.035 | 0.353 |
| dense_clutter | 44 | 0.184 | 0.387 | +0.203 | 0.252 |
| dense_clutter | 45 | 0.190 | 0.318 | +0.128 | 0.339 |
| dense_clutter | 46 | 0.164 | 0.207 | +0.043 | 0.291 |
| dense_clutter | 47 | 0.167 | 0.119 | -0.048 | 0.179 |
| dense_clutter | 48 | 0.234 | 0.217 | -0.016 | 0.228 |
| dense_clutter | 49 | 0.295 | 0.282 | -0.013 | 0.282 |
| false_observations | 25 | 0.223 | 0.195 | -0.028 | 0.239 |
| false_observations | 26 | 0.234 | 0.204 | -0.030 | 0.259 |
| false_observations | 27 | 0.227 | 0.546 | +0.319 | 0.508 |
| false_observations | 28 | 0.143 | 0.208 | +0.065 | 0.223 |
| false_observations | 29 | 0.201 | 0.188 | -0.013 | 0.203 |
| false_observations | 30 | 0.204 | 0.176 | -0.028 | 0.177 |
| false_observations | 31 | 0.244 | 0.323 | +0.079 | 0.346 |
| false_observations | 32 | 0.102 | 0.171 | +0.068 | 0.133 |
| false_observations | 33 | 0.328 | 0.139 | -0.189 | 0.276 |
| false_observations | 34 | 0.209 | 0.234 | +0.025 | 0.197 |
| false_observations | 35 | 0.365 | 0.335 | -0.029 | 0.334 |
| false_observations | 36 | 0.345 | 0.435 | +0.090 | 0.382 |
| false_observations | 37 | 0.188 | 0.205 | +0.017 | 0.182 |
| false_observations | 38 | 0.261 | 0.423 | +0.162 | 0.427 |
| false_observations | 39 | 0.309 | 0.401 | +0.091 | 0.323 |
| false_observations | 40 | 0.181 | 0.191 | +0.010 | 0.145 |
| false_observations | 41 | 0.292 | 0.255 | -0.037 | 0.315 |
| false_observations | 42 | 0.302 | 0.377 | +0.076 | 0.360 |
| false_observations | 43 | 0.296 | 0.415 | +0.118 | 0.393 |
| false_observations | 44 | 0.222 | 0.371 | +0.149 | 0.395 |
| false_observations | 45 | 0.247 | 0.189 | -0.059 | 0.336 |
| false_observations | 46 | 0.165 | 0.159 | -0.006 | 0.165 |
| false_observations | 47 | 0.241 | 0.237 | -0.004 | 0.238 |
| false_observations | 48 | 0.185 | 0.219 | +0.035 | 0.213 |
| false_observations | 49 | 0.214 | 0.241 | +0.026 | 0.259 |
| measurement_bias | 25 | 1.683 | 1.669 | -0.015 | 1.671 |
| measurement_bias | 26 | 1.605 | 1.563 | -0.042 | 1.562 |
| measurement_bias | 27 | 1.674 | 1.677 | +0.003 | 1.667 |
| measurement_bias | 28 | 1.644 | 1.629 | -0.014 | 1.631 |
| measurement_bias | 29 | 1.639 | 1.623 | -0.016 | 1.651 |
| measurement_bias | 30 | 1.673 | 1.669 | -0.004 | 1.669 |
| measurement_bias | 31 | 1.646 | 1.652 | +0.006 | 1.650 |
| measurement_bias | 32 | 1.649 | 1.625 | -0.023 | 1.621 |
| measurement_bias | 33 | 1.590 | 1.628 | +0.038 | 1.635 |
| measurement_bias | 34 | 1.675 | 1.659 | -0.016 | 1.643 |
| measurement_bias | 35 | 1.632 | 1.611 | -0.020 | 1.601 |
| measurement_bias | 36 | 1.591 | 1.592 | +0.000 | 1.561 |
| measurement_bias | 37 | 1.631 | 1.641 | +0.010 | 1.680 |
| measurement_bias | 38 | 1.647 | 1.626 | -0.021 | 1.632 |
| measurement_bias | 39 | 1.645 | 1.570 | -0.075 | 1.553 |
| measurement_bias | 40 | 1.692 | 1.624 | -0.068 | 1.607 |
| measurement_bias | 41 | 1.552 | 1.558 | +0.005 | 1.539 |
| measurement_bias | 42 | 1.679 | 1.651 | -0.028 | 1.665 |
| measurement_bias | 43 | 1.623 | 1.642 | +0.019 | 1.658 |
| measurement_bias | 44 | 1.630 | 1.634 | +0.004 | 1.625 |
| measurement_bias | 45 | 1.641 | 1.610 | -0.031 | 1.567 |
| measurement_bias | 46 | 1.627 | 1.601 | -0.026 | 1.591 |
| measurement_bias | 47 | 1.608 | 1.557 | -0.051 | 1.556 |
| measurement_bias | 48 | 1.690 | 1.617 | -0.073 | 1.641 |
| measurement_bias | 49 | 1.623 | 1.631 | +0.009 | 1.636 |
| moving_observer | 25 | 0.217 | 0.331 | +0.114 | 0.292 |
| moving_observer | 26 | 0.232 | 0.268 | +0.035 | 0.285 |
| moving_observer | 27 | 0.228 | 0.221 | -0.007 | 0.435 |
| moving_observer | 28 | 0.170 | 0.247 | +0.077 | 0.203 |
| moving_observer | 29 | 0.161 | 0.256 | +0.095 | 0.266 |
| moving_observer | 30 | 0.286 | 0.251 | -0.035 | 0.257 |
| moving_observer | 31 | 0.200 | 0.322 | +0.122 | 0.357 |
| moving_observer | 32 | 0.179 | 0.211 | +0.031 | 0.213 |
| moving_observer | 33 | 0.191 | 0.155 | -0.036 | 0.232 |
| moving_observer | 34 | 0.301 | 0.205 | -0.096 | 0.236 |
| moving_observer | 35 | 0.336 | 0.471 | +0.135 | 0.430 |
| moving_observer | 36 | 0.320 | 0.474 | +0.154 | 0.452 |
| moving_observer | 37 | 0.152 | 0.167 | +0.015 | 0.136 |
| moving_observer | 38 | 0.218 | 0.242 | +0.024 | 0.293 |
| moving_observer | 39 | 0.217 | 0.167 | -0.050 | 0.238 |
| moving_observer | 40 | 0.272 | 0.212 | -0.060 | 0.231 |
| moving_observer | 41 | 0.367 | 0.284 | -0.082 | 0.374 |
| moving_observer | 42 | 0.303 | 0.300 | -0.003 | 0.284 |
| moving_observer | 43 | 0.324 | 0.372 | +0.048 | 0.390 |
| moving_observer | 44 | 0.251 | 0.201 | -0.050 | 0.234 |
| moving_observer | 45 | 0.176 | 0.183 | +0.007 | 0.187 |
| moving_observer | 46 | 0.273 | 0.268 | -0.005 | 0.255 |
| moving_observer | 47 | 0.157 | 0.290 | +0.133 | 0.208 |
| moving_observer | 48 | 0.164 | 0.117 | -0.047 | 0.118 |
| moving_observer | 49 | 0.268 | 0.291 | +0.023 | 0.281 |
| nominal | 25 | 0.230 | 0.282 | +0.051 | 0.275 |
| nominal | 26 | 0.244 | 0.223 | -0.021 | 0.239 |
| nominal | 27 | 0.289 | 0.362 | +0.073 | 0.398 |
| nominal | 28 | 0.166 | 0.130 | -0.036 | 0.149 |
| nominal | 29 | 0.298 | 0.200 | -0.097 | 0.212 |
| nominal | 30 | 0.222 | 0.186 | -0.036 | 0.201 |
| nominal | 31 | 0.195 | 0.197 | +0.002 | 0.217 |
| nominal | 32 | 0.219 | 0.204 | -0.015 | 0.256 |
| nominal | 33 | 0.264 | 0.127 | -0.137 | 0.159 |
| nominal | 34 | 0.252 | 0.210 | -0.042 | 0.242 |
| nominal | 35 | 0.301 | 0.353 | +0.052 | 0.483 |
| nominal | 36 | 0.314 | 0.459 | +0.144 | 0.325 |
| nominal | 37 | 0.191 | 0.208 | +0.017 | 0.222 |
| nominal | 38 | 0.251 | 0.320 | +0.069 | 0.213 |
| nominal | 39 | 0.290 | 0.357 | +0.067 | 0.415 |
| nominal | 40 | 0.232 | 0.200 | -0.032 | 0.264 |
| nominal | 41 | 0.323 | 0.438 | +0.116 | 0.284 |
| nominal | 42 | 0.277 | 0.203 | -0.074 | 0.244 |
| nominal | 43 | 0.251 | 0.291 | +0.040 | 0.265 |
| nominal | 44 | 0.228 | 0.316 | +0.088 | 0.306 |
| nominal | 45 | 0.210 | 0.235 | +0.025 | 0.231 |
| nominal | 46 | 0.229 | 0.251 | +0.022 | 0.274 |
| nominal | 47 | 0.171 | 0.294 | +0.123 | 0.302 |
| nominal | 48 | 0.158 | 0.143 | -0.014 | 0.154 |
| nominal | 49 | 0.244 | 0.243 | -0.000 | 0.235 |
| range_dropout | 25 | 0.223 | 0.220 | -0.003 | 0.229 |
| range_dropout | 26 | 0.209 | 0.174 | -0.035 | 0.202 |
| range_dropout | 27 | 0.276 | 0.478 | +0.201 | 0.453 |
| range_dropout | 28 | 0.182 | 0.142 | -0.040 | 0.144 |
| range_dropout | 29 | 0.193 | 0.236 | +0.043 | 0.260 |
| range_dropout | 30 | 0.295 | 0.231 | -0.064 | 0.239 |
| range_dropout | 31 | 0.270 | 0.359 | +0.089 | 0.359 |
| range_dropout | 32 | 0.295 | 0.207 | -0.088 | 0.254 |
| range_dropout | 33 | 0.201 | 0.227 | +0.026 | 0.220 |
| range_dropout | 34 | 0.234 | 0.188 | -0.046 | 0.194 |
| range_dropout | 35 | 0.292 | 0.237 | -0.054 | 0.233 |
| range_dropout | 36 | 0.344 | 0.423 | +0.079 | 0.438 |
| range_dropout | 37 | 0.163 | 0.195 | +0.032 | 0.249 |
| range_dropout | 38 | 0.248 | 0.417 | +0.170 | 0.362 |
| range_dropout | 39 | 0.349 | 0.366 | +0.017 | 0.348 |
| range_dropout | 40 | 0.245 | 0.214 | -0.032 | 0.249 |
| range_dropout | 41 | 0.341 | 0.346 | +0.005 | 0.401 |
| range_dropout | 42 | 0.260 | 0.264 | +0.004 | 0.288 |
| range_dropout | 43 | 0.365 | 0.381 | +0.017 | 0.376 |
| range_dropout | 44 | 0.178 | 0.294 | +0.116 | 0.309 |
| range_dropout | 45 | 0.245 | 0.308 | +0.063 | 0.288 |
| range_dropout | 46 | 0.260 | 0.293 | +0.034 | 0.349 |
| range_dropout | 47 | 0.276 | 0.252 | -0.025 | 0.213 |
| range_dropout | 48 | 0.318 | 0.370 | +0.052 | 0.410 |
| range_dropout | 49 | 0.275 | 0.271 | -0.004 | 0.325 |
| sensor_disagreement_large_bias | 25 | 0.230 | 0.231 | +0.000 | 0.231 |
| sensor_disagreement_large_bias | 26 | 0.244 | 0.241 | -0.003 | 0.241 |
| sensor_disagreement_large_bias | 27 | 0.289 | 0.246 | -0.043 | 0.289 |
| sensor_disagreement_large_bias | 28 | 0.166 | 0.167 | +0.001 | 0.167 |
| sensor_disagreement_large_bias | 29 | 0.298 | 0.304 | +0.006 | 0.304 |
| sensor_disagreement_large_bias | 30 | 0.222 | 0.366 | +0.144 | 0.371 |
| sensor_disagreement_large_bias | 31 | 0.195 | 0.195 | +0.000 | 0.195 |
| sensor_disagreement_large_bias | 32 | 0.219 | 0.215 | -0.004 | 0.215 |
| sensor_disagreement_large_bias | 33 | 0.264 | 0.264 | +0.000 | 0.264 |
| sensor_disagreement_large_bias | 34 | 0.252 | 0.255 | +0.003 | 0.255 |
| sensor_disagreement_large_bias | 35 | 0.301 | 0.301 | +0.000 | 0.301 |
| sensor_disagreement_large_bias | 36 | 0.314 | 0.363 | +0.049 | 0.315 |
| sensor_disagreement_large_bias | 37 | 0.191 | 0.191 | +0.000 | 0.191 |
| sensor_disagreement_large_bias | 38 | 0.251 | 0.256 | +0.005 | 0.258 |
| sensor_disagreement_large_bias | 39 | 0.290 | 0.290 | -0.000 | 0.290 |
| sensor_disagreement_large_bias | 40 | 0.232 | 0.233 | +0.000 | 0.233 |
| sensor_disagreement_large_bias | 41 | 0.323 | 0.323 | +0.000 | 0.323 |
| sensor_disagreement_large_bias | 42 | 0.277 | 0.277 | +0.000 | 0.277 |
| sensor_disagreement_large_bias | 43 | 0.251 | 0.251 | +0.000 | 0.251 |
| sensor_disagreement_large_bias | 44 | 0.228 | 0.229 | +0.000 | 0.229 |
| sensor_disagreement_large_bias | 45 | 0.210 | 0.225 | +0.015 | 0.225 |
| sensor_disagreement_large_bias | 46 | 0.229 | 0.227 | -0.002 | 0.224 |
| sensor_disagreement_large_bias | 47 | 0.171 | 0.171 | +0.000 | 0.171 |
| sensor_disagreement_large_bias | 48 | 0.158 | 0.158 | +0.000 | 0.158 |
| sensor_disagreement_large_bias | 49 | 0.244 | 0.362 | +0.119 | 0.270 |
| sensor_disagreement_within_gate | 25 | 0.230 | 0.336 | +0.106 | 0.302 |
| sensor_disagreement_within_gate | 26 | 0.244 | 0.442 | +0.198 | 0.257 |
| sensor_disagreement_within_gate | 27 | 0.289 | 0.463 | +0.175 | 0.383 |
| sensor_disagreement_within_gate | 28 | 0.166 | 0.293 | +0.127 | 0.162 |
| sensor_disagreement_within_gate | 29 | 0.298 | 0.325 | +0.027 | 0.307 |
| sensor_disagreement_within_gate | 30 | 0.222 | 0.463 | +0.241 | 0.194 |
| sensor_disagreement_within_gate | 31 | 0.195 | 0.473 | +0.278 | 0.230 |
| sensor_disagreement_within_gate | 32 | 0.219 | 0.253 | +0.034 | 0.174 |
| sensor_disagreement_within_gate | 33 | 0.264 | 0.400 | +0.136 | 0.153 |
| sensor_disagreement_within_gate | 34 | 0.252 | 0.445 | +0.193 | 0.227 |
| sensor_disagreement_within_gate | 35 | 0.301 | 0.478 | +0.177 | 0.342 |
| sensor_disagreement_within_gate | 36 | 0.314 | 0.514 | +0.199 | 0.328 |
| sensor_disagreement_within_gate | 37 | 0.191 | 0.330 | +0.138 | 0.263 |
| sensor_disagreement_within_gate | 38 | 0.251 | 0.433 | +0.182 | 0.294 |
| sensor_disagreement_within_gate | 39 | 0.290 | 0.550 | +0.260 | 0.424 |
| sensor_disagreement_within_gate | 40 | 0.232 | 0.399 | +0.167 | 0.210 |
| sensor_disagreement_within_gate | 41 | 0.323 | 0.486 | +0.163 | 0.301 |
| sensor_disagreement_within_gate | 42 | 0.277 | 0.419 | +0.142 | 0.282 |
| sensor_disagreement_within_gate | 43 | 0.251 | 0.528 | +0.277 | 0.301 |
| sensor_disagreement_within_gate | 44 | 0.228 | 0.372 | +0.144 | 0.341 |
| sensor_disagreement_within_gate | 45 | 0.210 | 0.378 | +0.168 | 0.240 |
| sensor_disagreement_within_gate | 46 | 0.229 | 0.388 | +0.159 | 0.270 |
| sensor_disagreement_within_gate | 47 | 0.171 | 0.378 | +0.207 | 0.347 |
| sensor_disagreement_within_gate | 48 | 0.158 | 0.381 | +0.223 | 0.150 |
| sensor_disagreement_within_gate | 49 | 0.244 | 0.332 | +0.088 | 0.266 |
| sensor_disagreement_within_gate_high | 25 | 0.230 | 0.413 | +0.183 | 0.307 |
| sensor_disagreement_within_gate_high | 26 | 0.244 | 0.390 | +0.146 | 0.262 |
| sensor_disagreement_within_gate_high | 27 | 0.289 | 0.556 | +0.267 | 0.386 |
| sensor_disagreement_within_gate_high | 28 | 0.166 | 0.418 | +0.252 | 0.211 |
| sensor_disagreement_within_gate_high | 29 | 0.298 | 0.353 | +0.055 | 0.225 |
| sensor_disagreement_within_gate_high | 30 | 0.222 | 0.611 | +0.390 | 0.231 |
| sensor_disagreement_within_gate_high | 31 | 0.195 | 0.527 | +0.332 | 0.183 |
| sensor_disagreement_within_gate_high | 32 | 0.219 | 0.306 | +0.087 | 0.135 |
| sensor_disagreement_within_gate_high | 33 | 0.264 | 0.576 | +0.312 | 0.162 |
| sensor_disagreement_within_gate_high | 34 | 0.252 | 0.367 | +0.115 | 0.253 |
| sensor_disagreement_within_gate_high | 35 | 0.301 | 0.504 | +0.204 | 0.273 |
| sensor_disagreement_within_gate_high | 36 | 0.314 | 0.527 | +0.213 | 0.330 |
| sensor_disagreement_within_gate_high | 37 | 0.191 | 0.360 | +0.169 | 0.277 |
| sensor_disagreement_within_gate_high | 38 | 0.251 | 0.427 | +0.176 | 0.272 |
| sensor_disagreement_within_gate_high | 39 | 0.290 | 0.541 | +0.251 | 0.383 |
| sensor_disagreement_within_gate_high | 40 | 0.232 | 0.564 | +0.332 | 0.209 |
| sensor_disagreement_within_gate_high | 41 | 0.323 | 0.592 | +0.270 | 0.443 |
| sensor_disagreement_within_gate_high | 42 | 0.277 | 0.471 | +0.194 | 0.384 |
| sensor_disagreement_within_gate_high | 43 | 0.251 | 0.440 | +0.189 | 0.309 |
| sensor_disagreement_within_gate_high | 44 | 0.228 | 0.317 | +0.089 | 0.321 |
| sensor_disagreement_within_gate_high | 45 | 0.210 | 0.332 | +0.123 | 0.294 |
| sensor_disagreement_within_gate_high | 46 | 0.229 | 0.420 | +0.191 | 0.312 |
| sensor_disagreement_within_gate_high | 47 | 0.171 | 0.445 | +0.274 | 0.226 |
| sensor_disagreement_within_gate_high | 48 | 0.158 | 0.424 | +0.266 | 0.159 |
| sensor_disagreement_within_gate_high | 49 | 0.244 | 0.385 | +0.142 | 0.290 |
| sensor_disagreement_within_gate_low | 25 | 0.230 | 0.306 | +0.075 | 0.289 |
| sensor_disagreement_within_gate_low | 26 | 0.244 | 0.277 | +0.033 | 0.257 |
| sensor_disagreement_within_gate_low | 27 | 0.289 | 0.418 | +0.129 | 0.383 |
| sensor_disagreement_within_gate_low | 28 | 0.166 | 0.298 | +0.132 | 0.152 |
| sensor_disagreement_within_gate_low | 29 | 0.298 | 0.297 | -0.000 | 0.217 |
| sensor_disagreement_within_gate_low | 30 | 0.222 | 0.313 | +0.091 | 0.208 |
| sensor_disagreement_within_gate_low | 31 | 0.195 | 0.355 | +0.160 | 0.217 |
| sensor_disagreement_within_gate_low | 32 | 0.219 | 0.228 | +0.009 | 0.173 |
| sensor_disagreement_within_gate_low | 33 | 0.264 | 0.421 | +0.157 | 0.141 |
| sensor_disagreement_within_gate_low | 34 | 0.252 | 0.301 | +0.049 | 0.243 |
| sensor_disagreement_within_gate_low | 35 | 0.301 | 0.445 | +0.145 | 0.428 |
| sensor_disagreement_within_gate_low | 36 | 0.314 | 0.430 | +0.115 | 0.320 |
| sensor_disagreement_within_gate_low | 37 | 0.191 | 0.344 | +0.152 | 0.200 |
| sensor_disagreement_within_gate_low | 38 | 0.251 | 0.399 | +0.148 | 0.301 |
| sensor_disagreement_within_gate_low | 39 | 0.290 | 0.458 | +0.168 | 0.356 |
| sensor_disagreement_within_gate_low | 40 | 0.232 | 0.371 | +0.139 | 0.243 |
| sensor_disagreement_within_gate_low | 41 | 0.323 | 0.306 | -0.017 | 0.285 |
| sensor_disagreement_within_gate_low | 42 | 0.277 | 0.326 | +0.049 | 0.242 |
| sensor_disagreement_within_gate_low | 43 | 0.251 | 0.418 | +0.167 | 0.291 |
| sensor_disagreement_within_gate_low | 44 | 0.228 | 0.345 | +0.116 | 0.304 |
| sensor_disagreement_within_gate_low | 45 | 0.210 | 0.213 | +0.004 | 0.233 |
| sensor_disagreement_within_gate_low | 46 | 0.229 | 0.296 | +0.067 | 0.309 |
| sensor_disagreement_within_gate_low | 47 | 0.171 | 0.241 | +0.070 | 0.374 |
| sensor_disagreement_within_gate_low | 48 | 0.158 | 0.287 | +0.130 | 0.174 |
| sensor_disagreement_within_gate_low | 49 | 0.244 | 0.261 | +0.018 | 0.255 |
| stale_rejection | 25 | N/A | N/A | N/A | N/A |
| stale_rejection | 26 | N/A | N/A | N/A | N/A |
| stale_rejection | 27 | N/A | N/A | N/A | N/A |
| stale_rejection | 28 | N/A | N/A | N/A | N/A |
| stale_rejection | 29 | N/A | N/A | N/A | N/A |
| stale_rejection | 30 | N/A | N/A | N/A | N/A |
| stale_rejection | 31 | N/A | N/A | N/A | N/A |
| stale_rejection | 32 | N/A | N/A | N/A | N/A |
| stale_rejection | 33 | N/A | N/A | N/A | N/A |
| stale_rejection | 34 | N/A | N/A | N/A | N/A |
| stale_rejection | 35 | N/A | N/A | N/A | N/A |
| stale_rejection | 36 | N/A | N/A | N/A | N/A |
| stale_rejection | 37 | N/A | N/A | N/A | N/A |
| stale_rejection | 38 | N/A | N/A | N/A | N/A |
| stale_rejection | 39 | N/A | N/A | N/A | N/A |
| stale_rejection | 40 | N/A | N/A | N/A | N/A |
| stale_rejection | 41 | N/A | N/A | N/A | N/A |
| stale_rejection | 42 | N/A | N/A | N/A | N/A |
| stale_rejection | 43 | N/A | N/A | N/A | N/A |
| stale_rejection | 44 | N/A | N/A | N/A | N/A |
| stale_rejection | 45 | N/A | N/A | N/A | N/A |
| stale_rejection | 46 | N/A | N/A | N/A | N/A |
| stale_rejection | 47 | N/A | N/A | N/A | N/A |
| stale_rejection | 48 | N/A | N/A | N/A | N/A |
| stale_rejection | 49 | N/A | N/A | N/A | N/A |
| uncertainty_miscalibration | 25 | 0.465 | 0.435 | -0.031 | 0.472 |
| uncertainty_miscalibration | 26 | 0.452 | 0.473 | +0.022 | 0.507 |
| uncertainty_miscalibration | 27 | 0.513 | 0.533 | +0.020 | 0.544 |
| uncertainty_miscalibration | 28 | 0.436 | 0.624 | +0.188 | 0.429 |
| uncertainty_miscalibration | 29 | 0.354 | 0.599 | +0.246 | 0.437 |
| uncertainty_miscalibration | 30 | 0.513 | 0.491 | -0.022 | 0.572 |
| uncertainty_miscalibration | 31 | 0.483 | 0.425 | -0.058 | 0.595 |
| uncertainty_miscalibration | 32 | 0.412 | 0.518 | +0.106 | 0.450 |
| uncertainty_miscalibration | 33 | 0.426 | 0.514 | +0.089 | 0.429 |
| uncertainty_miscalibration | 34 | 0.394 | 0.441 | +0.047 | 0.540 |
| uncertainty_miscalibration | 35 | 0.477 | 0.515 | +0.038 | 0.538 |
| uncertainty_miscalibration | 36 | 0.484 | 0.584 | +0.100 | 0.614 |
| uncertainty_miscalibration | 37 | 0.413 | 0.441 | +0.028 | 0.444 |
| uncertainty_miscalibration | 38 | 0.358 | 0.450 | +0.092 | 0.490 |
| uncertainty_miscalibration | 39 | 0.420 | 0.590 | +0.170 | 0.618 |
| uncertainty_miscalibration | 40 | 0.474 | 0.512 | +0.038 | 0.499 |
| uncertainty_miscalibration | 41 | 0.390 | 0.496 | +0.106 | 0.542 |
| uncertainty_miscalibration | 42 | 0.504 | 0.558 | +0.054 | 0.536 |
| uncertainty_miscalibration | 43 | 0.589 | 0.595 | +0.006 | 0.560 |
| uncertainty_miscalibration | 44 | 0.485 | 0.464 | -0.021 | 0.547 |
| uncertainty_miscalibration | 45 | 0.470 | 0.473 | +0.003 | 0.510 |
| uncertainty_miscalibration | 46 | 0.371 | 0.533 | +0.162 | 0.523 |
| uncertainty_miscalibration | 47 | 0.474 | 0.564 | +0.091 | 0.571 |
| uncertainty_miscalibration | 48 | 0.492 | 0.583 | +0.091 | 0.447 |
| uncertainty_miscalibration | 49 | 0.434 | 0.470 | +0.036 | 0.586 |
| vision_dropout | 25 | 0.230 | 0.210 | -0.021 | 0.193 |
| vision_dropout | 26 | 0.244 | 0.250 | +0.005 | 0.246 |
| vision_dropout | 27 | 0.289 | 0.237 | -0.052 | 0.238 |
| vision_dropout | 28 | 0.166 | 0.161 | -0.005 | 0.141 |
| vision_dropout | 29 | 0.298 | 0.165 | -0.132 | 0.168 |
| vision_dropout | 30 | 0.222 | 0.183 | -0.039 | 0.188 |
| vision_dropout | 31 | 0.195 | 0.222 | +0.027 | 0.202 |
| vision_dropout | 32 | 0.219 | 0.269 | +0.050 | 0.221 |
| vision_dropout | 33 | 0.264 | 0.161 | -0.103 | 0.165 |
| vision_dropout | 34 | 0.252 | 0.249 | -0.003 | 0.267 |
| vision_dropout | 35 | 0.301 | 0.300 | -0.001 | 0.374 |
| vision_dropout | 36 | 0.314 | 0.457 | +0.142 | 0.488 |
| vision_dropout | 37 | 0.191 | 0.173 | -0.018 | 0.211 |
| vision_dropout | 38 | 0.251 | 0.216 | -0.035 | 0.234 |
| vision_dropout | 39 | 0.290 | 0.279 | -0.011 | 0.290 |
| vision_dropout | 40 | 0.232 | 0.205 | -0.027 | 0.240 |
| vision_dropout | 41 | 0.323 | 0.324 | +0.001 | 0.319 |
| vision_dropout | 42 | 0.277 | 0.271 | -0.006 | 0.281 |
| vision_dropout | 43 | 0.251 | 0.369 | +0.118 | 0.370 |
| vision_dropout | 44 | 0.228 | 0.225 | -0.004 | 0.238 |
| vision_dropout | 45 | 0.210 | 0.170 | -0.039 | 0.171 |
| vision_dropout | 46 | 0.229 | 0.221 | -0.007 | 0.218 |
| vision_dropout | 47 | 0.171 | 0.182 | +0.011 | 0.153 |
| vision_dropout | 48 | 0.158 | 0.156 | -0.002 | 0.152 |
| vision_dropout | 49 | 0.244 | 0.256 | +0.012 | 0.255 |

## Findings

- Position RMSE: the paired interval excludes zero in favour of fusion in 1 scenario(s) and against fusion in 6 scenario(s); it includes zero (or has fewer than two seeds) in 8 scenario(s).
- The RMSE tally depends on the matcher: with a distance-only matcher the interval excludes zero in favour of fusion in 9 scenario(s), against fusion in 3, and includes zero in 3.
- MOTA, IDF1 and GOSPA (interval excludes zero): fusion better in 0, 2 and 0 scenario(s) and worse in 15, 6 and 15, respectively.
- fused-bias-estimated against fused (interval excludes zero): position RMSE: better in 3, worse in 2, inconclusive in 10; precision: better in 3, worse in 0, inconclusive in 12; MOTA: better in 3, worse in 0, inconclusive in 13; GOSPA: better in 3, worse in 0, inconclusive in 13.
- Fused precision is lower (interval excludes zero) in 15 scenario(s) and higher in 0; fused 95% coverage is lower in 11 and higher in 1. Accuracy alone does not establish that fusion improved association or calibration.
- Fusion is not guaranteed to improve accuracy. Systematic sensor bias,
  miscalibrated uncertainty, missed detections, false observations and
  association errors can all reverse the comparison.
- Precision is sample-based: matched samples over all confirmed/coasting
  track samples. `Unmatched confirmed tracks` are confirmed track IDs never
  matched to a ground-truth object. `Duplicate tracks` is the subset that, in
  at least one frame, was left unmatched while a ground-truth object lay
  within the matching gate (the object had been claimed by another track).
  The rest were never near an unclaimed object under that gate.
- Fixed text (not derived from the numbers) in the next two bullets:
- `sensor_disagreement_large_bias` (0.12 rad) is a gate-rejection
  experiment: see the vision acceptance table for how many biased
  observations the gate rejected versus applied. It does not measure the
  cost of fusing biased data.
- `sensor_disagreement_within_gate` (0.015 rad) applies a bias small
  enough to pass the gate often, so it measures what happens when biased
  vision data is actually fused. Neither scenario establishes real-world
  sensor-fusion performance; both are descriptive synthetic results;
  intervals reflect seed-to-seed variation only.
- `track_fragmentation` counts interruptions in an object's matched frames, summed
  over objects; it is independent of identity switches.
- `identity_switches` counts changes of matched track ID for the same
  ground-truth object across consecutive matched frames.
- Coverage is empirical and only defined over matched samples; its
  denominator is reported in `per_seed.csv` and `benchmark.json`.
- Scenarios with no matched samples (for example `stale_rejection`)
  report `N/A` accuracy because their observations are rejected as stale;
  that is an explicit non-result, not a zero-error result.
- This run includes seeds outside the development range (custom_or_held_out); do not read it as the development benchmark. A held-out evaluation requires a single run on frozen code, reported separately.

## Counting rules

- Fixed text: tallies count scenarios, not independent trials. A scenario with
  `n == 0` for a metric is skipped in that metric's tally, so better, worse and
  inconclusive counts can sum to fewer than the number of scenarios. Scored in 15 of 16 scenario(s) for position RMSE.
- No multiplicity correction is applied across scenarios, metrics or comparisons;
  with this many 95% intervals some will exclude zero by chance.
- 4 zero-width interval(s) are not counted as findings: identical paired differences give no spread estimate, so they are tallied as inconclusive and marked `(degenerate)` in the paired table.

## Limitations

- Synthetic 2-D world; simplified sensor models, not hardware validation.
- Vision-only track initiation is not supported (bearing alone cannot
  determine range).
- Out-of-sequence observations older than one tracker epoch are explicitly
  rejected and counted, not silently dropped. Their accuracy impact is
  therefore not represented as a successful fusion result.
- This run uses seeds outside the development range; whether it is a held-out evaluation depends on how the code was frozen before it.
