# Mosaic Benchmark Report

This report is generated from the code in this repository. It contains no
hand-edited numbers and no wall-clock timestamps, so repeated runs with the
same seeds and commit are byte-identical.

## Code and protocol

- Package version: `0.1.0`
- Git commit: `b286320c73991dbd997f1bce696b2f4795af2c82`
- Seeds: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24
- Seed group: development
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
| crossing_targets | range_only | 0.151 ± 0.035 | 0.148 | 0.148 | 0.977 | 0.856 | 0.920 | 296/303 | 3.8 | 3.8 | 1.2 | 4.4 | 0.0 | 0.804 | 0.852 | 0.924 |
| crossing_targets | fused | 0.160 ± 0.058 | 0.146 | 0.116 | 0.979 | 0.718 | 0.859 | 297/303 | 5.6 | 5.6 | 0.8 | 6.8 | 0.0 | 0.573 | 0.790 | 1.614 |
| crossing_targets | fused_bias_estimated | 0.164 ± 0.054 | 0.152 | 0.119 | 0.979 | 0.727 | 0.835 | 297/303 | 5.5 | 5.5 | 1.0 | 6.7 | 0.0 | 0.590 | 0.801 | 1.576 |
| delivery_delay | range_only | 0.308 ± 0.046 | 0.285 | 0.327 | 0.968 | 0.807 | 0.512 | 293/303 | 3.8 | 3.8 | 6.9 | 10.6 | 0.1 | 0.708 | 0.592 | 1.542 |
| delivery_delay | fused | 0.329 ± 0.062 | 0.268 | 0.311 | 0.970 | 0.660 | 0.338 | 294/303 | 6.8 | 6.8 | 5.1 | 11.2 | 0.0 | 0.437 | 0.591 | 2.330 |
| delivery_delay | fused_bias_estimated | 0.330 ± 0.063 | 0.277 | 0.302 | 0.970 | 0.660 | 0.311 | 294/303 | 7.0 | 7.0 | 5.2 | 12.0 | 0.0 | 0.442 | 0.593 | 2.341 |
| delivery_delay_retrodiction | range_only | 0.283 ± 0.054 | 0.252 | 0.385 | 0.968 | 0.771 | 0.810 | 293/303 | 4.8 | 4.8 | 11.1 | 15.1 | 0.2 | 0.636 | 0.491 | 1.609 |
| delivery_delay_retrodiction | fused | 0.335 ± 0.076 | 0.251 | 0.455 | 0.970 | 0.632 | 0.694 | 294/303 | 10.0 | 9.8 | 13.0 | 21.8 | 0.0 | 0.349 | 0.461 | 2.444 |
| delivery_delay_retrodiction | fused_bias_estimated | 0.346 ± 0.091 | 0.258 | 0.457 | 0.970 | 0.637 | 0.666 | 294/303 | 10.4 | 10.2 | 12.9 | 21.8 | 0.0 | 0.359 | 0.480 | 2.432 |
| dense_clutter | range_only | 0.242 ± 0.051 | 0.219 | 0.317 | 0.979 | 0.816 | 0.805 | 297/303 | 3.6 | 3.6 | 6.7 | 10.0 | 0.0 | 0.732 | 0.621 | 1.281 |
| dense_clutter | fused | 0.285 ± 0.091 | 0.206 | 0.307 | 0.979 | 0.338 | 0.662 | 297/303 | 73.4 | 8.6 | 5.0 | 10.9 | 0.0 | -0.977 | 0.376 | 6.397 |
| dense_clutter | fused_bias_estimated | 0.271 ± 0.083 | 0.204 | 0.307 | 0.980 | 0.341 | 0.680 | 297/303 | 73.9 | 9.1 | 5.0 | 12.0 | 0.0 | -0.956 | 0.382 | 6.324 |
| false_observations | range_only | 0.230 ± 0.051 | 0.208 | 0.306 | 0.977 | 0.840 | 0.833 | 296/303 | 3.0 | 3.0 | 6.6 | 10.0 | 0.0 | 0.765 | 0.611 | 1.145 |
| false_observations | fused | 0.247 ± 0.064 | 0.189 | 0.309 | 0.979 | 0.639 | 0.743 | 297/303 | 12.5 | 6.0 | 5.2 | 10.3 | 0.0 | 0.399 | 0.577 | 2.212 |
| false_observations | fused_bias_estimated | 0.260 ± 0.070 | 0.194 | 0.315 | 0.979 | 0.619 | 0.715 | 297/303 | 12.8 | 6.4 | 5.4 | 11.2 | 0.0 | 0.345 | 0.575 | 2.385 |
| measurement_bias | range_only | 1.641 ± 0.032 | 1.594 | 0.523 | 0.888 | 0.715 | 0.001 | 269/303 | 1.7 | 1.1 | 11.4 | 13.7 | 5.3 | 0.494 | 0.299 | 5.590 |
| measurement_bias | fused | 1.620 ± 0.029 | 1.556 | 0.501 | 0.909 | 0.599 | 0.006 | 275/303 | 3.0 | 1.8 | 10.9 | 14.1 | 4.2 | 0.255 | 0.291 | 6.283 |
| measurement_bias | fused_bias_estimated | 1.622 ± 0.027 | 1.556 | 0.495 | 0.915 | 0.598 | 0.006 | 277/303 | 2.8 | 1.6 | 11.0 | 14.0 | 3.8 | 0.255 | 0.290 | 6.313 |
| moving_observer | range_only | 0.242 ± 0.079 | 0.218 | 0.345 | 0.975 | 0.833 | 0.832 | 295/303 | 3.6 | 3.6 | 5.8 | 8.4 | 0.1 | 0.754 | 0.665 | 1.219 |
| moving_observer | fused | 0.262 ± 0.098 | 0.188 | 0.312 | 0.978 | 0.714 | 0.751 | 296/303 | 6.3 | 6.2 | 4.4 | 8.2 | 0.0 | 0.557 | 0.640 | 1.749 |
| moving_observer | fused_bias_estimated | 0.257 ± 0.078 | 0.203 | 0.309 | 0.978 | 0.698 | 0.711 | 296/303 | 6.0 | 5.9 | 4.6 | 9.8 | 0.0 | 0.521 | 0.626 | 1.892 |
| nominal | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| nominal | fused | 0.253 ± 0.083 | 0.195 | 0.301 | 0.980 | 0.696 | 0.749 | 297/303 | 6.0 | 5.9 | 4.7 | 10.6 | 0.0 | 0.520 | 0.612 | 1.865 |
| nominal | fused_bias_estimated | 0.249 ± 0.066 | 0.199 | 0.293 | 0.980 | 0.675 | 0.726 | 297/303 | 6.5 | 6.5 | 4.4 | 10.5 | 0.0 | 0.482 | 0.617 | 2.000 |
| range_dropout | range_only | 0.253 ± 0.040 | 0.248 | 0.349 | 0.881 | 0.972 | 0.890 | 267/303 | 0.5 | 0.5 | 7.8 | 8.2 | 5.0 | 0.828 | 0.541 | 0.982 |
| range_dropout | fused | 0.268 ± 0.083 | 0.219 | 0.296 | 0.970 | 0.816 | 0.808 | 294/303 | 3.2 | 3.2 | 4.4 | 7.2 | 0.3 | 0.729 | 0.680 | 1.275 |
| range_dropout | fused_bias_estimated | 0.277 ± 0.074 | 0.230 | 0.296 | 0.970 | 0.809 | 0.760 | 294/303 | 3.5 | 3.5 | 4.7 | 8.0 | 0.3 | 0.718 | 0.662 | 1.344 |
| sensor_disagreement_large_bias | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_large_bias | fused | 0.239 ± 0.077 | 0.211 | 0.318 | 0.977 | 0.807 | 0.806 | 296/303 | 4.3 | 3.9 | 5.9 | 8.6 | 0.0 | 0.715 | 0.635 | 1.321 |
| sensor_disagreement_large_bias | fused_bias_estimated | 0.244 ± 0.085 | 0.212 | 0.326 | 0.977 | 0.810 | 0.801 | 296/303 | 4.2 | 3.8 | 6.1 | 8.6 | 0.0 | 0.719 | 0.635 | 1.312 |
| sensor_disagreement_within_gate | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_within_gate | fused | 0.381 ± 0.097 | 0.273 | 0.395 | 0.979 | 0.560 | 0.284 | 297/303 | 9.6 | 9.6 | 8.0 | 19.1 | 0.0 | 0.169 | 0.490 | 3.124 |
| sensor_disagreement_within_gate | fused_bias_estimated | 0.268 ± 0.065 | 0.206 | 0.343 | 0.979 | 0.671 | 0.673 | 297/303 | 6.6 | 6.5 | 5.5 | 11.5 | 0.0 | 0.466 | 0.598 | 2.052 |
| sensor_disagreement_within_gate_high | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_within_gate_high | fused | 0.467 ± 0.096 | 0.278 | 0.465 | 0.978 | 0.535 | 0.317 | 296/303 | 9.4 | 9.4 | 8.6 | 17.6 | 0.0 | 0.092 | 0.476 | 3.339 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 0.275 ± 0.069 | 0.215 | 0.361 | 0.978 | 0.666 | 0.665 | 296/303 | 5.9 | 5.9 | 5.9 | 12.4 | 0.0 | 0.450 | 0.593 | 2.111 |
| sensor_disagreement_within_gate_low | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| sensor_disagreement_within_gate_low | fused | 0.335 ± 0.067 | 0.256 | 0.350 | 0.979 | 0.617 | 0.332 | 297/303 | 7.9 | 7.8 | 6.1 | 14.7 | 0.0 | 0.332 | 0.546 | 2.612 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 0.262 ± 0.072 | 0.202 | 0.328 | 0.980 | 0.681 | 0.687 | 297/303 | 6.0 | 5.9 | 5.1 | 11.4 | 0.0 | 0.487 | 0.618 | 1.987 |
| stale_rejection | range_only | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| stale_rejection | fused | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| stale_rejection | fused_bias_estimated | N/A | N/A | N/A | 0.000 | N/A | N/A | 0/303 | 0.0 | 0.0 | N/A | N/A | N/A | 0.000 | 0.000 | 3.000 |
| uncertainty_miscalibration | range_only | 0.460 ± 0.064 | 0.431 | 0.626 | 0.521 | 0.831 | 0.089 | 158/303 | 2.8 | 2.8 | 25.6 | 28.2 | 15.6 | 0.330 | 0.136 | 2.339 |
| uncertainty_miscalibration | fused | 0.525 ± 0.068 | 0.409 | 0.654 | 0.932 | 0.445 | 0.106 | 282/303 | 39.3 | 38.9 | 34.7 | 56.6 | 3.6 | -0.353 | 0.174 | 4.636 |
| uncertainty_miscalibration | fused_bias_estimated | 0.541 ± 0.056 | 0.419 | 0.703 | 0.924 | 0.448 | 0.091 | 280/303 | 37.6 | 37.3 | 37.2 | 59.0 | 3.9 | -0.347 | 0.163 | 4.613 |
| vision_dropout | range_only | 0.233 ± 0.061 | 0.213 | 0.309 | 0.977 | 0.826 | 0.813 | 296/303 | 3.1 | 3.1 | 6.1 | 8.9 | 0.0 | 0.746 | 0.639 | 1.231 |
| vision_dropout | fused | 0.241 ± 0.071 | 0.208 | 0.296 | 0.978 | 0.726 | 0.750 | 296/303 | 5.6 | 5.6 | 5.0 | 8.6 | 0.0 | 0.582 | 0.633 | 1.713 |
| vision_dropout | fused_bias_estimated | 0.256 ± 0.076 | 0.210 | 0.309 | 0.978 | 0.716 | 0.711 | 296/303 | 5.5 | 5.4 | 5.6 | 9.8 | 0.0 | 0.562 | 0.616 | 1.781 |

## Paired differences (fused minus range-only)

Mean per-seed difference with a two-sided 95% t interval over seeds. Seeds with
an undefined value on either side are dropped (`n` is the number kept). Lower is
better for the RMSE metrics and GOSPA, so a negative difference favours the
treatment; higher is better for recall, precision, coverage, MOTA and IDF1, so a
positive one does. The interval describes seed-to-seed variation in this synthetic
setup and is not a claim about other worlds.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| crossing_targets | gospa_p1 | 25 | +0.690 | [+0.505, +0.874] |
| crossing_targets | idf1 | 25 | -0.062 | [-0.100, -0.025] |
| crossing_targets | mota | 25 | -0.230 | [-0.289, -0.172] |
| crossing_targets | position_coverage_95 | 25 | -0.061 | [-0.097, -0.025] |
| crossing_targets | position_rmse | 25 | +0.009 | [-0.008, +0.026] |
| crossing_targets | position_rmse_distance_only | 25 | -0.002 | [-0.015, +0.011] |
| crossing_targets | precision | 25 | -0.138 | [-0.171, -0.106] |
| crossing_targets | recall | 25 | +0.002 | [+0.000, +0.003] |
| delivery_delay | gospa_p1 | 25 | +0.788 | [+0.586, +0.991] |
| delivery_delay | idf1 | 25 | -0.001 | [-0.037, +0.035] |
| delivery_delay | mota | 25 | -0.270 | [-0.331, -0.210] |
| delivery_delay | position_coverage_95 | 25 | -0.173 | [-0.238, -0.109] |
| delivery_delay | position_rmse | 25 | +0.020 | [-0.005, +0.046] |
| delivery_delay | position_rmse_distance_only | 25 | -0.017 | [-0.032, -0.003] |
| delivery_delay | precision | 25 | -0.147 | [-0.174, -0.120] |
| delivery_delay | recall | 25 | +0.001 | [+0.000, +0.002] |
| delivery_delay_retrodiction | gospa_p1 | 25 | +0.834 | [+0.660, +1.008] |
| delivery_delay_retrodiction | idf1 | 25 | -0.031 | [-0.065, +0.004] |
| delivery_delay_retrodiction | mota | 25 | -0.288 | [-0.341, -0.234] |
| delivery_delay_retrodiction | position_coverage_95 | 25 | -0.116 | [-0.143, -0.089] |
| delivery_delay_retrodiction | position_rmse | 25 | +0.053 | [+0.031, +0.074] |
| delivery_delay_retrodiction | position_rmse_distance_only | 25 | -0.001 | [-0.012, +0.010] |
| delivery_delay_retrodiction | precision | 25 | -0.138 | [-0.163, -0.114] |
| delivery_delay_retrodiction | recall | 25 | +0.002 | [+0.001, +0.003] |
| dense_clutter | gospa_p1 | 25 | +5.115 | [+4.779, +5.452] |
| dense_clutter | idf1 | 25 | -0.246 | [-0.277, -0.214] |
| dense_clutter | mota | 25 | -1.709 | [-1.817, -1.602] |
| dense_clutter | position_coverage_95 | 25 | -0.143 | [-0.183, -0.103] |
| dense_clutter | position_rmse | 25 | +0.043 | [+0.013, +0.073] |
| dense_clutter | position_rmse_distance_only | 25 | -0.013 | [-0.024, -0.002] |
| dense_clutter | precision | 25 | -0.478 | [-0.499, -0.457] |
| dense_clutter | recall | 25 | +0.001 | [-0.000, +0.001] |
| false_observations | gospa_p1 | 25 | +1.068 | [+0.841, +1.294] |
| false_observations | idf1 | 25 | -0.034 | [-0.075, +0.007] |
| false_observations | mota | 25 | -0.366 | [-0.435, -0.297] |
| false_observations | position_coverage_95 | 25 | -0.090 | [-0.140, -0.040] |
| false_observations | position_rmse | 25 | +0.017 | [-0.008, +0.042] |
| false_observations | position_rmse_distance_only | 25 | -0.018 | [-0.035, -0.002] |
| false_observations | precision | 25 | -0.202 | [-0.238, -0.165] |
| false_observations | recall | 25 | +0.002 | [+0.001, +0.004] |
| measurement_bias | gospa_p1 | 25 | +0.693 | [+0.573, +0.814] |
| measurement_bias | idf1 | 25 | -0.008 | [-0.021, +0.005] |
| measurement_bias | mota | 25 | -0.239 | [-0.289, -0.189] |
| measurement_bias | position_coverage_95 | 25 | +0.005 | [+0.002, +0.008] |
| measurement_bias | position_rmse | 25 | -0.021 | [-0.034, -0.008] |
| measurement_bias | position_rmse_distance_only | 25 | -0.038 | [-0.053, -0.024] |
| measurement_bias | precision | 25 | -0.116 | [-0.137, -0.096] |
| measurement_bias | recall | 25 | +0.020 | [+0.007, +0.033] |
| moving_observer | gospa_p1 | 25 | +0.530 | [+0.356, +0.704] |
| moving_observer | idf1 | 25 | -0.024 | [-0.057, +0.009] |
| moving_observer | mota | 25 | -0.196 | [-0.249, -0.144] |
| moving_observer | position_coverage_95 | 25 | -0.080 | [-0.129, -0.031] |
| moving_observer | position_rmse | 25 | +0.019 | [-0.014, +0.053] |
| moving_observer | position_rmse_distance_only | 25 | -0.029 | [-0.044, -0.014] |
| moving_observer | precision | 25 | -0.119 | [-0.149, -0.089] |
| moving_observer | recall | 25 | +0.002 | [+0.000, +0.004] |
| nominal | gospa_p1 | 25 | +0.635 | [+0.447, +0.822] |
| nominal | idf1 | 25 | -0.027 | [-0.064, +0.010] |
| nominal | mota | 25 | -0.226 | [-0.286, -0.167] |
| nominal | position_coverage_95 | 25 | -0.064 | [-0.109, -0.018] |
| nominal | position_rmse | 25 | +0.020 | [-0.004, +0.044] |
| nominal | position_rmse_distance_only | 25 | -0.018 | [-0.031, -0.005] |
| nominal | precision | 25 | -0.130 | [-0.162, -0.099] |
| nominal | recall | 25 | +0.003 | [+0.001, +0.004] |
| range_dropout | gospa_p1 | 25 | +0.292 | [+0.171, +0.413] |
| range_dropout | idf1 | 25 | +0.139 | [+0.087, +0.191] |
| range_dropout | mota | 25 | -0.100 | [-0.139, -0.061] |
| range_dropout | position_coverage_95 | 25 | -0.082 | [-0.117, -0.047] |
| range_dropout | position_rmse | 25 | +0.015 | [-0.016, +0.046] |
| range_dropout | position_rmse_distance_only | 25 | -0.029 | [-0.046, -0.012] |
| range_dropout | precision | 25 | -0.156 | [-0.182, -0.129] |
| range_dropout | recall | 25 | +0.090 | [+0.074, +0.105] |
| sensor_disagreement_large_bias | gospa_p1 | 25 | +0.090 | [-0.013, +0.194] |
| sensor_disagreement_large_bias | idf1 | 25 | -0.004 | [-0.015, +0.007] |
| sensor_disagreement_large_bias | mota | 25 | -0.030 | [-0.064, +0.004] |
| sensor_disagreement_large_bias | position_coverage_95 | 25 | -0.007 | [-0.022, +0.009] |
| sensor_disagreement_large_bias | position_rmse | 25 | +0.006 | [-0.004, +0.016] |
| sensor_disagreement_large_bias | position_rmse_distance_only | 25 | -0.002 | [-0.007, +0.004] |
| sensor_disagreement_large_bias | precision | 25 | -0.018 | [-0.038, +0.001] |
| sensor_disagreement_large_bias | recall | 25 | +0.000 | [-0.000, +0.000] |
| sensor_disagreement_within_gate | gospa_p1 | 25 | +1.894 | [+1.681, +2.106] |
| sensor_disagreement_within_gate | idf1 | 25 | -0.149 | [-0.191, -0.108] |
| sensor_disagreement_within_gate | mota | 25 | -0.577 | [-0.641, -0.512] |
| sensor_disagreement_within_gate | position_coverage_95 | 25 | -0.529 | [-0.599, -0.458] |
| sensor_disagreement_within_gate | position_rmse | 25 | +0.148 | [+0.117, +0.178] |
| sensor_disagreement_within_gate | position_rmse_distance_only | 25 | +0.060 | [+0.043, +0.078] |
| sensor_disagreement_within_gate | precision | 25 | -0.265 | [-0.292, -0.239] |
| sensor_disagreement_within_gate | recall | 25 | +0.002 | [+0.001, +0.003] |
| sensor_disagreement_within_gate_high | gospa_p1 | 25 | +2.108 | [+1.926, +2.290] |
| sensor_disagreement_within_gate_high | idf1 | 25 | -0.163 | [-0.197, -0.128] |
| sensor_disagreement_within_gate_high | mota | 25 | -0.654 | [-0.709, -0.599] |
| sensor_disagreement_within_gate_high | position_coverage_95 | 25 | -0.496 | [-0.582, -0.409] |
| sensor_disagreement_within_gate_high | position_rmse | 25 | +0.233 | [+0.187, +0.280] |
| sensor_disagreement_within_gate_high | position_rmse_distance_only | 25 | +0.065 | [+0.048, +0.082] |
| sensor_disagreement_within_gate_high | precision | 25 | -0.291 | [-0.314, -0.267] |
| sensor_disagreement_within_gate_high | recall | 25 | +0.001 | [-0.000, +0.002] |
| sensor_disagreement_within_gate_low | gospa_p1 | 25 | +1.381 | [+1.131, +1.631] |
| sensor_disagreement_within_gate_low | idf1 | 25 | -0.093 | [-0.127, -0.060] |
| sensor_disagreement_within_gate_low | mota | 25 | -0.414 | [-0.487, -0.340] |
| sensor_disagreement_within_gate_low | position_coverage_95 | 25 | -0.481 | [-0.538, -0.424] |
| sensor_disagreement_within_gate_low | position_rmse | 25 | +0.101 | [+0.070, +0.133] |
| sensor_disagreement_within_gate_low | position_rmse_distance_only | 25 | +0.042 | [+0.024, +0.061] |
| sensor_disagreement_within_gate_low | precision | 25 | -0.209 | [-0.241, -0.177] |
| sensor_disagreement_within_gate_low | recall | 25 | +0.002 | [+0.001, +0.003] |
| stale_rejection | gospa_p1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | idf1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | mota | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | position_coverage_95 | 0 | N/A | N/A |
| stale_rejection | position_rmse | 0 | N/A | N/A |
| stale_rejection | position_rmse_distance_only | 0 | N/A | N/A |
| stale_rejection | precision | 0 | N/A | N/A |
| stale_rejection | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| uncertainty_miscalibration | gospa_p1 | 25 | +2.297 | [+2.133, +2.461] |
| uncertainty_miscalibration | idf1 | 25 | +0.037 | [+0.017, +0.058] |
| uncertainty_miscalibration | mota | 25 | -0.683 | [-0.738, -0.627] |
| uncertainty_miscalibration | position_coverage_95 | 25 | +0.017 | [-0.011, +0.045] |
| uncertainty_miscalibration | position_rmse | 25 | +0.065 | [+0.032, +0.098] |
| uncertainty_miscalibration | position_rmse_distance_only | 25 | -0.022 | [-0.048, +0.003] |
| uncertainty_miscalibration | precision | 25 | -0.386 | [-0.405, -0.367] |
| uncertainty_miscalibration | recall | 25 | +0.411 | [+0.386, +0.435] |
| vision_dropout | gospa_p1 | 25 | +0.482 | [+0.324, +0.641] |
| vision_dropout | idf1 | 25 | -0.006 | [-0.036, +0.025] |
| vision_dropout | mota | 25 | -0.163 | [-0.208, -0.119] |
| vision_dropout | position_coverage_95 | 25 | -0.063 | [-0.105, -0.021] |
| vision_dropout | position_rmse | 25 | +0.008 | [-0.008, +0.024] |
| vision_dropout | position_rmse_distance_only | 25 | -0.005 | [-0.018, +0.008] |
| vision_dropout | precision | 25 | -0.100 | [-0.124, -0.075] |
| vision_dropout | recall | 25 | +0.001 | [+0.000, +0.002] |

## Paired differences (fused-bias-estimated minus fused)

Same conventions as the first comparison.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| crossing_targets | gospa_p1 | 25 | -0.038 | [-0.195, +0.120] |
| crossing_targets | idf1 | 25 | +0.012 | [-0.014, +0.038] |
| crossing_targets | mota | 25 | +0.016 | [-0.033, +0.066] |
| crossing_targets | position_coverage_95 | 25 | -0.023 | [-0.062, +0.015] |
| crossing_targets | position_rmse | 25 | +0.004 | [-0.007, +0.015] |
| crossing_targets | position_rmse_distance_only | 25 | +0.006 | [-0.003, +0.015] |
| crossing_targets | precision | 25 | +0.009 | [-0.017, +0.036] |
| crossing_targets | recall | 25 | +0.000 | [-0.000, +0.000] |
| delivery_delay | gospa_p1 | 25 | +0.010 | [-0.150, +0.171] |
| delivery_delay | idf1 | 25 | +0.002 | [-0.022, +0.026] |
| delivery_delay | mota | 25 | +0.005 | [-0.044, +0.053] |
| delivery_delay | position_coverage_95 | 25 | -0.027 | [-0.068, +0.014] |
| delivery_delay | position_rmse | 25 | +0.002 | [-0.017, +0.020] |
| delivery_delay | position_rmse_distance_only | 25 | +0.008 | [-0.003, +0.020] |
| delivery_delay | precision | 25 | +0.000 | [-0.021, +0.022] |
| delivery_delay | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| delivery_delay_retrodiction | gospa_p1 | 25 | -0.011 | [-0.128, +0.106] |
| delivery_delay_retrodiction | idf1 | 25 | +0.019 | [-0.005, +0.043] |
| delivery_delay_retrodiction | mota | 25 | +0.010 | [-0.028, +0.048] |
| delivery_delay_retrodiction | position_coverage_95 | 25 | -0.028 | [-0.063, +0.007] |
| delivery_delay_retrodiction | position_rmse | 25 | +0.010 | [-0.012, +0.033] |
| delivery_delay_retrodiction | position_rmse_distance_only | 25 | +0.007 | [-0.000, +0.014] |
| delivery_delay_retrodiction | precision | 25 | +0.005 | [-0.010, +0.019] |
| delivery_delay_retrodiction | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| dense_clutter | gospa_p1 | 25 | -0.073 | [-0.243, +0.098] |
| dense_clutter | idf1 | 25 | +0.006 | [-0.007, +0.019] |
| dense_clutter | mota | 25 | +0.021 | [-0.032, +0.073] |
| dense_clutter | position_coverage_95 | 25 | +0.018 | [-0.018, +0.054] |
| dense_clutter | position_rmse | 25 | -0.014 | [-0.037, +0.008] |
| dense_clutter | position_rmse_distance_only | 25 | -0.002 | [-0.014, +0.010] |
| dense_clutter | precision | 25 | +0.003 | [-0.003, +0.009] |
| dense_clutter | recall | 25 | +0.000 | [-0.000, +0.000] |
| false_observations | gospa_p1 | 25 | +0.172 | [+0.027, +0.317] |
| false_observations | idf1 | 25 | -0.003 | [-0.023, +0.018] |
| false_observations | mota | 25 | -0.054 | [-0.101, -0.007] |
| false_observations | position_coverage_95 | 25 | -0.028 | [-0.055, -0.001] |
| false_observations | position_rmse | 25 | +0.014 | [-0.003, +0.031] |
| false_observations | position_rmse_distance_only | 25 | +0.005 | [-0.002, +0.012] |
| false_observations | precision | 25 | -0.020 | [-0.039, -0.002] |
| false_observations | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| measurement_bias | gospa_p1 | 25 | +0.030 | [-0.062, +0.122] |
| measurement_bias | idf1 | 25 | -0.001 | [-0.010, +0.008] |
| measurement_bias | mota | 25 | -0.000 | [-0.035, +0.034] |
| measurement_bias | position_coverage_95 | 25 | -0.000 | [-0.002, +0.001] |
| measurement_bias | position_rmse | 25 | +0.002 | [-0.005, +0.009] |
| measurement_bias | position_rmse_distance_only | 25 | +0.000 | [-0.008, +0.009] |
| measurement_bias | precision | 25 | -0.000 | [-0.013, +0.012] |
| measurement_bias | recall | 25 | +0.006 | [-0.003, +0.016] |
| moving_observer | gospa_p1 | 25 | +0.143 | [-0.031, +0.317] |
| moving_observer | idf1 | 25 | -0.014 | [-0.037, +0.009] |
| moving_observer | mota | 25 | -0.036 | [-0.086, +0.014] |
| moving_observer | position_coverage_95 | 25 | -0.040 | [-0.085, +0.004] |
| moving_observer | position_rmse | 25 | -0.004 | [-0.033, +0.025] |
| moving_observer | position_rmse_distance_only | 25 | +0.014 | [-0.000, +0.029] |
| moving_observer | precision | 25 | -0.015 | [-0.041, +0.010] |
| moving_observer | recall | 25 | +0.000 | [-0.000, +0.001] |
| nominal | gospa_p1 | 25 | +0.135 | [-0.010, +0.279] |
| nominal | idf1 | 25 | +0.005 | [-0.013, +0.023] |
| nominal | mota | 25 | -0.038 | [-0.081, +0.005] |
| nominal | position_coverage_95 | 25 | -0.023 | [-0.053, +0.007] |
| nominal | position_rmse | 25 | -0.004 | [-0.018, +0.010] |
| nominal | position_rmse_distance_only | 25 | +0.004 | [-0.004, +0.012] |
| nominal | precision | 25 | -0.021 | [-0.043, +0.001] |
| nominal | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| range_dropout | gospa_p1 | 25 | +0.069 | [-0.045, +0.184] |
| range_dropout | idf1 | 25 | -0.017 | [-0.040, +0.005] |
| range_dropout | mota | 25 | -0.011 | [-0.042, +0.020] |
| range_dropout | position_coverage_95 | 25 | -0.048 | [-0.083, -0.014] |
| range_dropout | position_rmse | 25 | +0.010 | [-0.006, +0.025] |
| range_dropout | position_rmse_distance_only | 25 | +0.011 | [-0.003, +0.024] |
| range_dropout | precision | 25 | -0.007 | [-0.026, +0.012] |
| range_dropout | recall | 25 | +0.000 | [-0.002, +0.002] |
| sensor_disagreement_large_bias | gospa_p1 | 25 | -0.009 | [-0.030, +0.012] |
| sensor_disagreement_large_bias | idf1 | 25 | -0.000 | [-0.005, +0.004] |
| sensor_disagreement_large_bias | mota | 25 | +0.003 | [-0.004, +0.010] |
| sensor_disagreement_large_bias | position_coverage_95 | 25 | -0.005 | [-0.014, +0.004] |
| sensor_disagreement_large_bias | position_rmse | 25 | +0.004 | [-0.003, +0.011] |
| sensor_disagreement_large_bias | position_rmse_distance_only | 25 | +0.001 | [-0.002, +0.004] |
| sensor_disagreement_large_bias | precision | 25 | +0.002 | [-0.002, +0.007] |
| sensor_disagreement_large_bias | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| sensor_disagreement_within_gate | gospa_p1 | 25 | -1.072 | [-1.340, -0.805] |
| sensor_disagreement_within_gate | idf1 | 25 | +0.108 | [+0.072, +0.144] |
| sensor_disagreement_within_gate | mota | 25 | +0.297 | [+0.215, +0.378] |
| sensor_disagreement_within_gate | position_coverage_95 | 25 | +0.389 | [+0.317, +0.460] |
| sensor_disagreement_within_gate | position_rmse | 25 | -0.113 | [-0.152, -0.074] |
| sensor_disagreement_within_gate | position_rmse_distance_only | 25 | -0.067 | [-0.082, -0.053] |
| sensor_disagreement_within_gate | precision | 25 | +0.110 | [+0.076, +0.145] |
| sensor_disagreement_within_gate | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| sensor_disagreement_within_gate_high | gospa_p1 | 25 | -1.228 | [-1.494, -0.962] |
| sensor_disagreement_within_gate_high | idf1 | 25 | +0.117 | [+0.077, +0.156] |
| sensor_disagreement_within_gate_high | mota | 25 | +0.359 | [+0.281, +0.436] |
| sensor_disagreement_within_gate_high | position_coverage_95 | 25 | +0.347 | [+0.267, +0.428] |
| sensor_disagreement_within_gate_high | position_rmse | 25 | -0.192 | [-0.241, -0.143] |
| sensor_disagreement_within_gate_high | position_rmse_distance_only | 25 | -0.063 | [-0.084, -0.043] |
| sensor_disagreement_within_gate_high | precision | 25 | +0.131 | [+0.100, +0.162] |
| sensor_disagreement_within_gate_high | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| sensor_disagreement_within_gate_low | gospa_p1 | 25 | -0.625 | [-0.875, -0.376] |
| sensor_disagreement_within_gate_low | idf1 | 25 | +0.072 | [+0.035, +0.110] |
| sensor_disagreement_within_gate_low | mota | 25 | +0.155 | [+0.079, +0.231] |
| sensor_disagreement_within_gate_low | position_coverage_95 | 25 | +0.355 | [+0.295, +0.415] |
| sensor_disagreement_within_gate_low | position_rmse | 25 | -0.073 | [-0.102, -0.045] |
| sensor_disagreement_within_gate_low | position_rmse_distance_only | 25 | -0.053 | [-0.067, -0.040] |
| sensor_disagreement_within_gate_low | precision | 25 | +0.064 | [+0.032, +0.096] |
| sensor_disagreement_within_gate_low | recall | 25 | +0.000 | [-0.000, +0.000] |
| stale_rejection | gospa_p1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | idf1 | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | mota | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| stale_rejection | position_coverage_95 | 0 | N/A | N/A |
| stale_rejection | position_rmse | 0 | N/A | N/A |
| stale_rejection | position_rmse_distance_only | 0 | N/A | N/A |
| stale_rejection | precision | 0 | N/A | N/A |
| stale_rejection | recall | 25 | +0.000 | [+0.000, +0.000] (degenerate) |
| uncertainty_miscalibration | gospa_p1 | 25 | -0.023 | [-0.134, +0.088] |
| uncertainty_miscalibration | idf1 | 25 | -0.011 | [-0.030, +0.008] |
| uncertainty_miscalibration | mota | 25 | +0.006 | [-0.029, +0.040] |
| uncertainty_miscalibration | position_coverage_95 | 25 | -0.015 | [-0.041, +0.011] |
| uncertainty_miscalibration | position_rmse | 25 | +0.016 | [-0.010, +0.042] |
| uncertainty_miscalibration | position_rmse_distance_only | 25 | +0.010 | [-0.005, +0.025] |
| uncertainty_miscalibration | precision | 25 | +0.002 | [-0.005, +0.010] |
| uncertainty_miscalibration | recall | 25 | -0.008 | [-0.015, -0.001] |
| vision_dropout | gospa_p1 | 25 | +0.068 | [-0.103, +0.238] |
| vision_dropout | idf1 | 25 | -0.017 | [-0.051, +0.017] |
| vision_dropout | mota | 25 | -0.020 | [-0.070, +0.029] |
| vision_dropout | position_coverage_95 | 25 | -0.039 | [-0.083, +0.006] |
| vision_dropout | position_rmse | 25 | +0.015 | [-0.008, +0.038] |
| vision_dropout | position_rmse_distance_only | 25 | +0.002 | [-0.009, +0.014] |
| vision_dropout | precision | 25 | -0.011 | [-0.036, +0.015] |
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
| crossing_targets | fused | 0.990 | 0.990 | 0.657 | 194.9 |
| crossing_targets | fused_bias_estimated | 0.989 | 0.989 | 0.660 | 195.8 |
| delivery_delay | range_only | N/A | N/A | 0.000 | 0.0 |
| delivery_delay | fused | 0.998 | 0.999 | 0.665 | 195.5 |
| delivery_delay | fused_bias_estimated | 0.997 | 0.997 | 0.666 | 195.6 |
| delivery_delay_retrodiction | range_only | N/A | N/A | 0.000 | 0.0 |
| delivery_delay_retrodiction | fused | 0.996 | 0.995 | 0.660 | 194.0 |
| delivery_delay_retrodiction | fused_bias_estimated | 0.997 | 0.997 | 0.664 | 195.0 |
| dense_clutter | range_only | N/A | N/A | 0.000 | 0.0 |
| dense_clutter | fused | 0.998 | 0.998 | 0.632 | 187.7 |
| dense_clutter | fused_bias_estimated | 0.998 | 0.998 | 0.621 | 184.3 |
| false_observations | range_only | N/A | N/A | 0.000 | 0.0 |
| false_observations | fused | 0.998 | 0.998 | 0.654 | 194.2 |
| false_observations | fused_bias_estimated | 0.997 | 0.996 | 0.652 | 193.6 |
| measurement_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| measurement_bias | fused | 0.997 | 0.996 | 0.661 | 181.9 |
| measurement_bias | fused_bias_estimated | 0.999 | 0.998 | 0.664 | 183.9 |
| moving_observer | range_only | N/A | N/A | 0.000 | 0.0 |
| moving_observer | fused | 0.999 | 0.999 | 0.665 | 197.1 |
| moving_observer | fused_bias_estimated | 0.999 | 0.999 | 0.665 | 197.1 |
| nominal | range_only | N/A | N/A | 0.000 | 0.0 |
| nominal | fused | 0.999 | 0.998 | 0.662 | 196.6 |
| nominal | fused_bias_estimated | 0.998 | 0.997 | 0.663 | 196.9 |
| range_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| range_dropout | fused | 0.999 | 0.999 | 0.665 | 195.6 |
| range_dropout | fused_bias_estimated | 0.999 | 0.999 | 0.665 | 195.3 |
| sensor_disagreement_large_bias | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_large_bias | fused | 0.429 | 0.320 | 0.043 | 12.8 |
| sensor_disagreement_large_bias | fused_bias_estimated | 0.429 | 0.321 | 0.043 | 12.7 |
| sensor_disagreement_within_gate | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate | fused | 0.995 | 0.994 | 0.651 | 193.3 |
| sensor_disagreement_within_gate | fused_bias_estimated | 0.994 | 0.993 | 0.661 | 196.2 |
| sensor_disagreement_within_gate_high | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_high | fused | 0.986 | 0.983 | 0.635 | 188.4 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 0.998 | 0.998 | 0.661 | 195.9 |
| sensor_disagreement_within_gate_low | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate_low | fused | 0.994 | 0.991 | 0.661 | 196.0 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 0.992 | 0.991 | 0.662 | 196.6 |
| stale_rejection | range_only | N/A | N/A | N/A | 0.0 |
| stale_rejection | fused | N/A | N/A | N/A | 0.0 |
| stale_rejection | fused_bias_estimated | N/A | N/A | N/A | 0.0 |
| uncertainty_miscalibration | range_only | N/A | N/A | 0.000 | 0.0 |
| uncertainty_miscalibration | fused | 0.997 | 0.997 | 0.637 | 179.8 |
| uncertainty_miscalibration | fused_bias_estimated | 0.997 | 0.997 | 0.638 | 178.5 |
| vision_dropout | range_only | N/A | N/A | 0.000 | 0.0 |
| vision_dropout | fused | 0.999 | 0.999 | 0.658 | 195.0 |
| vision_dropout | fused_bias_estimated | 0.996 | 0.996 | 0.655 | 194.2 |

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
| crossing_targets | range_only | 1.350 [0.977, 1.023] above | 0.556 [0.977, 1.023] below | 0.759 [0.981, 1.019] below | 296 | 276.6 | 7 |
| crossing_targets | fused | 2.557 [0.977, 1.023] above | 0.558 [0.977, 1.023] below | 0.708 [0.983, 1.017] below | 297 | 542.7 | 6 |
| crossing_targets | fused_bias_estimated | 1.811 [0.977, 1.023] above | 0.553 [0.977, 1.023] below | 0.717 [0.983, 1.017] below | 297 | 541.4 | 6 |
| delivery_delay | range_only | 4.936 [0.977, 1.023] above | 2.219 [0.977, 1.023] above | 0.800 [0.980, 1.020] below | 293 | 265.9 | 10 |
| delivery_delay | fused | 11.338 [0.977, 1.023] above | 2.732 [0.977, 1.023] above | 0.745 [0.983, 1.017] below | 294 | 521.6 | 9 |
| delivery_delay | fused_bias_estimated | 11.750 [0.977, 1.023] above | 2.717 [0.977, 1.023] above | 0.751 [0.983, 1.017] below | 294 | 520.3 | 9 |
| delivery_delay_retrodiction | range_only | 1.895 [0.977, 1.023] above | 1.975 [0.977, 1.023] above | 0.912 [0.980, 1.020] below | 293 | 260.8 | 10 |
| delivery_delay_retrodiction | fused | 3.311 [0.977, 1.023] above | 2.833 [0.977, 1.023] above | 1.032 [0.982, 1.018] above | 294 | 482.7 | 9 |
| delivery_delay_retrodiction | fused_bias_estimated | 3.393 [0.977, 1.023] above | 2.766 [0.977, 1.023] above | 1.070 [0.982, 1.018] above | 294 | 481.1 | 9 |
| dense_clutter | range_only | 1.872 [0.977, 1.023] above | 1.834 [0.977, 1.023] above | 0.830 [0.981, 1.019] below | 297 | 282.0 | 6 |
| dense_clutter | fused | 3.020 [0.977, 1.023] above | 2.326 [0.977, 1.023] above | 0.835 [0.985, 1.015] below | 297 | 829.0 | 6 |
| dense_clutter | fused_bias_estimated | 3.148 [0.977, 1.023] above | 2.384 [0.977, 1.023] above | 0.845 [0.985, 1.015] below | 297 | 828.0 | 6 |
| false_observations | range_only | 1.709 [0.977, 1.023] above | 1.784 [0.977, 1.023] above | 0.829 [0.981, 1.019] below | 296 | 273.9 | 7 |
| false_observations | fused | 2.429 [0.977, 1.023] above | 2.203 [0.977, 1.023] above | 0.780 [0.983, 1.017] below | 297 | 570.3 | 6 |
| false_observations | fused_bias_estimated | 2.662 [0.977, 1.023] above | 2.242 [0.977, 1.023] above | 0.770 [0.983, 1.017] below | 297 | 568.9 | 6 |
| measurement_bias | range_only | 74.984 [0.976, 1.024] above | 12.605 [0.976, 1.024] above | 0.839 [0.981, 1.020] below | 269 | 269.0 | 34 |
| measurement_bias | fused | 72.986 [0.977, 1.024] above | 12.604 [0.977, 1.024] above | 0.788 [0.983, 1.017] below | 275 | 530.3 | 28 |
| measurement_bias | fused_bias_estimated | 72.886 [0.977, 1.024] above | 12.501 [0.977, 1.024] above | 0.785 [0.983, 1.017] below | 277 | 529.2 | 26 |
| moving_observer | range_only | 1.838 [0.977, 1.023] above | 1.812 [0.977, 1.023] above | 0.818 [0.981, 1.020] below | 295 | 271.1 | 8 |
| moving_observer | fused | 2.620 [0.977, 1.023] above | 2.258 [0.977, 1.023] above | 0.781 [0.983, 1.017] below | 296 | 532.1 | 7 |
| moving_observer | fused_bias_estimated | 2.637 [0.977, 1.023] above | 2.193 [0.977, 1.023] above | 0.777 [0.983, 1.017] below | 296 | 530.8 | 7 |
| nominal | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| nominal | fused | 2.479 [0.977, 1.023] above | 2.193 [0.977, 1.023] above | 0.769 [0.983, 1.017] below | 297 | 532.9 | 6 |
| nominal | fused_bias_estimated | 2.571 [0.977, 1.023] above | 2.209 [0.977, 1.023] above | 0.765 [0.983, 1.017] below | 297 | 532.4 | 6 |
| range_dropout | range_only | 1.499 [0.976, 1.024] above | 1.635 [0.976, 1.024] above | 0.832 [0.974, 1.026] below | 267 | 150.3 | 36 |
| range_dropout | fused | 2.127 [0.977, 1.023] above | 2.153 [0.977, 1.023] above | 0.793 [0.979, 1.021] below | 294 | 408.6 | 9 |
| range_dropout | fused_bias_estimated | 2.508 [0.977, 1.023] above | 2.178 [0.977, 1.023] above | 0.799 [0.979, 1.021] below | 294 | 407.4 | 9 |
| sensor_disagreement_large_bias | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_large_bias | fused | 2.885 [0.977, 1.023] above | 2.031 [0.977, 1.023] above | 0.825 [0.981, 1.019] below | 296 | 282.0 | 7 |
| sensor_disagreement_large_bias | fused_bias_estimated | 3.121 [0.977, 1.023] above | 2.309 [0.977, 1.023] above | 0.826 [0.981, 1.019] below | 296 | 281.2 | 7 |
| sensor_disagreement_within_gate | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_within_gate | fused | 10.255 [0.977, 1.023] above | 2.849 [0.977, 1.023] above | 0.827 [0.983, 1.017] below | 297 | 509.9 | 6 |
| sensor_disagreement_within_gate | fused_bias_estimated | 2.887 [0.977, 1.023] above | 2.343 [0.977, 1.023] above | 0.772 [0.983, 1.017] below | 297 | 528.0 | 6 |
| sensor_disagreement_within_gate_high | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_within_gate_high | fused | 15.394 [0.977, 1.023] above | 3.436 [0.977, 1.023] above | 0.842 [0.983, 1.017] below | 296 | 487.4 | 7 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 2.966 [0.977, 1.023] above | 2.337 [0.977, 1.023] above | 0.772 [0.983, 1.017] below | 296 | 524.6 | 7 |
| sensor_disagreement_within_gate_low | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| sensor_disagreement_within_gate_low | fused | 6.390 [0.977, 1.023] above | 2.504 [0.977, 1.023] above | 0.810 [0.983, 1.017] below | 297 | 523.8 | 6 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 2.809 [0.977, 1.023] above | 2.282 [0.977, 1.023] above | 0.772 [0.983, 1.017] below | 297 | 529.8 | 6 |
| stale_rejection | range_only | N/A | N/A | N/A | 0 | 0.0 | 303 |
| stale_rejection | fused | N/A | N/A | 2.053 [0.001, 5.024] within | 0 | 0.0 | 303 |
| stale_rejection | fused_bias_estimated | N/A | N/A | 2.053 [0.001, 5.024] within | 0 | 0.0 | 303 |
| uncertainty_miscalibration | range_only | 26.716 [0.969, 1.031] above | 9.110 [0.969, 1.031] above | 1.051 [0.974, 1.026] above | 158 | 152.7 | 145 |
| uncertainty_miscalibration | fused | 31.646 [0.977, 1.023] above | 9.593 [0.977, 1.023] above | 1.006 [0.979, 1.022] within | 282 | 379.5 | 21 |
| uncertainty_miscalibration | fused_bias_estimated | 1274.590 [0.977, 1.024] above | 10.136 [0.977, 1.024] above | 1.006 [0.979, 1.022] within | 280 | 377.4 | 23 |
| vision_dropout | range_only | 1.854 [0.977, 1.023] above | 1.835 [0.977, 1.023] above | 0.814 [0.981, 1.019] below | 296 | 272.2 | 7 |
| vision_dropout | fused | 2.253 [0.977, 1.023] above | 1.989 [0.977, 1.023] above | 0.789 [0.982, 1.018] below | 296 | 404.9 | 7 |
| vision_dropout | fused_bias_estimated | 2.510 [0.977, 1.023] above | 2.093 [0.977, 1.023] above | 0.788 [0.982, 1.018] below | 296 | 402.1 | 7 |

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
| crossing_targets | fused_bias_estimated | 5.0 | 5.5 | 5.5 |
| delivery_delay | range_only | 3.6 | 3.8 | 3.8 |
| delivery_delay | fused | 5.9 | 6.8 | 6.8 |
| delivery_delay | fused_bias_estimated | 6.3 | 7.0 | 7.0 |
| delivery_delay_retrodiction | range_only | 4.8 | 4.8 | 4.8 |
| delivery_delay_retrodiction | fused | 8.5 | 9.8 | 10.0 |
| delivery_delay_retrodiction | fused_bias_estimated | 9.2 | 10.2 | 10.5 |
| dense_clutter | range_only | 3.6 | 3.6 | 3.6 |
| dense_clutter | fused | 6.8 | 8.6 | 10.2 |
| dense_clutter | fused_bias_estimated | 7.1 | 9.1 | 10.7 |
| false_observations | range_only | 2.9 | 3.0 | 3.0 |
| false_observations | fused | 5.2 | 6.0 | 6.2 |
| false_observations | fused_bias_estimated | 5.6 | 6.4 | 6.6 |
| measurement_bias | range_only | 0.0 | 1.1 | 2.5 |
| measurement_bias | fused | 0.0 | 1.8 | 5.7 |
| measurement_bias | fused_bias_estimated | 0.0 | 1.6 | 5.2 |
| moving_observer | range_only | 3.6 | 3.6 | 3.6 |
| moving_observer | fused | 5.6 | 6.2 | 6.3 |
| moving_observer | fused_bias_estimated | 5.6 | 5.9 | 6.0 |
| nominal | range_only | 3.0 | 3.1 | 3.1 |
| nominal | fused | 5.4 | 5.9 | 6.0 |
| nominal | fused_bias_estimated | 5.8 | 6.5 | 6.5 |
| range_dropout | range_only | 0.4 | 0.5 | 0.5 |
| range_dropout | fused | 2.6 | 3.2 | 3.2 |
| range_dropout | fused_bias_estimated | 2.8 | 3.5 | 3.4 |
| sensor_disagreement_large_bias | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_large_bias | fused | 3.4 | 3.9 | 4.2 |
| sensor_disagreement_large_bias | fused_bias_estimated | 3.3 | 3.8 | 4.0 |
| sensor_disagreement_within_gate | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_within_gate | fused | 8.8 | 9.6 | 9.6 |
| sensor_disagreement_within_gate | fused_bias_estimated | 5.8 | 6.5 | 6.5 |
| sensor_disagreement_within_gate_high | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_within_gate_high | fused | 7.9 | 9.4 | 9.4 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 5.4 | 5.9 | 5.9 |
| sensor_disagreement_within_gate_low | range_only | 3.0 | 3.1 | 3.1 |
| sensor_disagreement_within_gate_low | fused | 7.0 | 7.8 | 7.9 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 5.4 | 5.9 | 6.0 |
| stale_rejection | range_only | 0.0 | 0.0 | 0.0 |
| stale_rejection | fused | 0.0 | 0.0 | 0.0 |
| stale_rejection | fused_bias_estimated | 0.0 | 0.0 | 0.0 |
| uncertainty_miscalibration | range_only | 2.8 | 2.8 | 2.7 |
| uncertainty_miscalibration | fused | 34.2 | 38.9 | 39.3 |
| uncertainty_miscalibration | fused_bias_estimated | 33.1 | 37.3 | 37.6 |
| vision_dropout | range_only | 3.0 | 3.1 | 3.1 |
| vision_dropout | fused | 5.2 | 5.6 | 5.6 |
| vision_dropout | fused_bias_estimated | 5.2 | 5.4 | 5.4 |

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
| crossing_targets | 275.2 | 275.2 | 10.2 | 0.1 | 0.0 | 0.0 | 264.9 |
| delivery_delay | 274.1 | 271.3 | 13.5 | 0.8 | 0.0 | 1.6 | 255.3 |
| delivery_delay | 274.1 | 271.3 | 14.4 | 0.7 | 0.0 | 1.6 | 254.5 |
| delivery_delay_retrodiction | 274.1 | 271.3 | 41.4 | 0.9 | 0.0 | 1.6 | 227.4 |
| delivery_delay_retrodiction | 274.1 | 271.3 | 43.1 | 0.6 | 0.0 | 1.6 | 225.9 |
| dense_clutter | 1098.8 | 1098.8 | 532.6 | 19.3 | 0.0 | 0.0 | 547.0 |
| dense_clutter | 1098.8 | 1098.8 | 533.0 | 19.6 | 0.0 | 0.0 | 546.2 |
| false_observations | 577.7 | 577.7 | 278.2 | 2.8 | 0.0 | 0.0 | 296.8 |
| false_observations | 577.7 | 577.7 | 279.0 | 2.7 | 0.0 | 0.0 | 296.1 |
| measurement_bias | 275.2 | 275.2 | 13.8 | 0.0 | 0.0 | 0.0 | 261.4 |
| measurement_bias | 275.2 | 275.2 | 14.9 | 0.0 | 0.0 | 0.0 | 260.3 |
| moving_observer | 275.2 | 275.2 | 14.8 | 0.1 | 0.0 | 0.0 | 260.3 |
| moving_observer | 275.2 | 275.2 | 15.8 | 0.1 | 0.0 | 0.0 | 259.3 |
| nominal | 275.2 | 275.2 | 14.6 | 0.2 | 0.0 | 0.0 | 260.4 |
| nominal | 275.2 | 275.2 | 15.1 | 0.1 | 0.0 | 0.0 | 260.0 |
| range_dropout | 275.2 | 275.2 | 19.3 | 0.2 | 0.2 | 0.0 | 255.5 |
| range_dropout | 275.2 | 275.2 | 20.0 | 0.1 | 0.2 | 0.0 | 254.9 |
| sensor_disagreement_large_bias | 275.2 | 275.2 | 264.7 | 0.3 | 0.0 | 0.0 | 10.2 |
| sensor_disagreement_large_bias | 275.2 | 275.2 | 265.6 | 0.2 | 0.0 | 0.0 | 9.4 |
| sensor_disagreement_within_gate | 275.2 | 275.2 | 30.8 | 0.2 | 0.0 | 0.0 | 244.2 |
| sensor_disagreement_within_gate | 275.2 | 275.2 | 18.3 | 0.1 | 0.0 | 0.0 | 256.8 |
| sensor_disagreement_within_gate_high | 275.2 | 275.2 | 52.8 | 0.2 | 0.0 | 0.0 | 222.2 |
| sensor_disagreement_within_gate_high | 275.2 | 275.2 | 21.7 | 0.1 | 0.0 | 0.0 | 253.4 |
| sensor_disagreement_within_gate_low | 275.2 | 275.2 | 20.8 | 0.0 | 0.0 | 0.0 | 254.4 |
| sensor_disagreement_within_gate_low | 275.2 | 275.2 | 17.2 | 0.2 | 0.0 | 0.0 | 257.8 |
| stale_rejection | 274.1 | 266.2 | 0.0 | 0.0 | 0.3 | 265.8 | 0.0 |
| stale_rejection | 274.1 | 266.2 | 0.0 | 0.0 | 0.3 | 265.8 | 0.0 |
| uncertainty_miscalibration | 275.2 | 275.2 | 38.3 | 0.1 | 0.0 | 0.0 | 236.8 |
| uncertainty_miscalibration | 275.2 | 275.2 | 38.9 | 0.0 | 0.0 | 0.0 | 236.3 |
| vision_dropout | 140.0 | 140.0 | 7.7 | 0.0 | 0.0 | 0.0 | 132.3 |
| vision_dropout | 140.0 | 140.0 | 9.6 | 0.1 | 0.0 | 0.0 | 130.3 |

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
| crossing_targets | 0.0000 | -0.0002 | 183.2 |
| delivery_delay | 0.0000 | 0.0002 | 152.2 |
| delivery_delay_retrodiction | 0.0000 | 0.0001 | 109.9 |
| dense_clutter | 0.0000 | 0.0002 | 149.1 |
| false_observations | 0.0000 | 0.0003 | 156.9 |
| measurement_bias | 0.0000 | 0.0001 | 149.5 |
| moving_observer | 0.0000 | 0.0000 | 166.5 |
| nominal | 0.0000 | 0.0000 | 160.8 |
| range_dropout | 0.0000 | 0.0002 | 102.6 |
| sensor_disagreement_large_bias | 0.1200 | -0.0053 | 1.3 |
| sensor_disagreement_within_gate | 0.0150 | 0.0149 | 157.3 |
| sensor_disagreement_within_gate_high | 0.0200 | 0.0199 | 153.3 |
| sensor_disagreement_within_gate_low | 0.0100 | 0.0101 | 160.8 |
| stale_rejection | 0.0000 | 0.0000 | 0.0 |
| uncertainty_miscalibration | 0.0000 | -0.0006 | 4.4 |
| vision_dropout | 0.0000 | 0.0011 | 80.0 |

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
| crossing_targets | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| delivery_delay | range_only | 285.0 | 1.4 | 1.4 | 2.8 | 0.050 | 283.6 |
| delivery_delay | fused | 556.3 | 3.0 | 3.0 | 5.6 | 0.050 | 553.3 |
| delivery_delay | fused_bias_estimated | 556.3 | 3.0 | 3.0 | 5.6 | 0.050 | 553.3 |
| delivery_delay_retrodiction | range_only | 285.0 | 1.4 | 1.4 | 2.8 | 0.050 | 283.6 |
| delivery_delay_retrodiction | fused | 556.3 | 3.0 | 3.0 | 5.6 | 0.050 | 553.3 |
| delivery_delay_retrodiction | fused_bias_estimated | 556.3 | 3.0 | 3.0 | 5.6 | 0.050 | 553.3 |
| dense_clutter | range_only | 692.1 | 0.0 | 0.0 | 0.0 | 0.000 | 692.1 |
| dense_clutter | fused | 1790.9 | 0.0 | 0.0 | 0.0 | 0.000 | 1790.9 |
| dense_clutter | fused_bias_estimated | 1790.9 | 0.0 | 0.0 | 0.0 | 0.000 | 1790.9 |
| false_observations | range_only | 388.9 | 0.0 | 0.0 | 0.0 | 0.000 | 388.9 |
| false_observations | fused | 966.6 | 0.0 | 0.0 | 0.0 | 0.000 | 966.6 |
| false_observations | fused_bias_estimated | 966.6 | 0.0 | 0.0 | 0.0 | 0.000 | 966.6 |
| measurement_bias | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| measurement_bias | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| measurement_bias | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| moving_observer | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| moving_observer | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| moving_observer | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| nominal | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| nominal | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| nominal | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| range_dropout | range_only | 166.2 | 0.0 | 0.0 | 0.0 | 0.000 | 166.2 |
| range_dropout | fused | 441.4 | 0.0 | 0.0 | 0.0 | 0.000 | 441.4 |
| range_dropout | fused_bias_estimated | 441.4 | 0.0 | 0.0 | 0.0 | 0.000 | 441.4 |
| sensor_disagreement_large_bias | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_large_bias | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_large_bias | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_within_gate | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate_high | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_within_gate_high | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate_high | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate_low | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| sensor_disagreement_within_gate_low | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| sensor_disagreement_within_gate_low | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| stale_rejection | range_only | 279.0 | 278.4 | 278.4 | 8.8 | 0.079 | 0.6 |
| stale_rejection | fused | 545.1 | 544.2 | 544.2 | 16.7 | 0.083 | 0.9 |
| stale_rejection | fused_bias_estimated | 545.1 | 544.2 | 544.2 | 16.7 | 0.083 | 0.9 |
| uncertainty_miscalibration | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| uncertainty_miscalibration | fused | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| uncertainty_miscalibration | fused_bias_estimated | 564.4 | 0.0 | 0.0 | 0.0 | 0.000 | 564.4 |
| vision_dropout | range_only | 289.2 | 0.0 | 0.0 | 0.0 | 0.000 | 289.2 |
| vision_dropout | fused | 429.2 | 0.0 | 0.0 | 0.0 | 0.000 | 429.2 |
| vision_dropout | fused_bias_estimated | 429.2 | 0.0 | 0.0 | 0.0 | 0.000 | 429.2 |

## Per-seed results

| Scenario | Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused − Range) | Bias-estimated RMSE (m) |
|---|---|---|---|---|---|
| crossing_targets | 0 | 0.112 | 0.119 | +0.006 | 0.127 |
| crossing_targets | 1 | 0.121 | 0.090 | -0.032 | 0.092 |
| crossing_targets | 2 | 0.150 | 0.253 | +0.104 | 0.246 |
| crossing_targets | 3 | 0.145 | 0.191 | +0.046 | 0.189 |
| crossing_targets | 4 | 0.134 | 0.132 | -0.002 | 0.195 |
| crossing_targets | 5 | 0.209 | 0.291 | +0.082 | 0.273 |
| crossing_targets | 6 | 0.136 | 0.127 | -0.009 | 0.117 |
| crossing_targets | 7 | 0.211 | 0.306 | +0.094 | 0.275 |
| crossing_targets | 8 | 0.174 | 0.188 | +0.015 | 0.172 |
| crossing_targets | 9 | 0.240 | 0.200 | -0.040 | 0.255 |
| crossing_targets | 10 | 0.139 | 0.143 | +0.004 | 0.148 |
| crossing_targets | 11 | 0.127 | 0.166 | +0.039 | 0.123 |
| crossing_targets | 12 | 0.126 | 0.163 | +0.036 | 0.152 |
| crossing_targets | 13 | 0.141 | 0.107 | -0.034 | 0.110 |
| crossing_targets | 14 | 0.114 | 0.120 | +0.006 | 0.114 |
| crossing_targets | 15 | 0.179 | 0.160 | -0.018 | 0.151 |
| crossing_targets | 16 | 0.113 | 0.108 | -0.005 | 0.134 |
| crossing_targets | 17 | 0.213 | 0.219 | +0.006 | 0.223 |
| crossing_targets | 18 | 0.132 | 0.135 | +0.004 | 0.127 |
| crossing_targets | 19 | 0.141 | 0.174 | +0.033 | 0.176 |
| crossing_targets | 20 | 0.112 | 0.097 | -0.015 | 0.119 |
| crossing_targets | 21 | 0.160 | 0.157 | -0.004 | 0.141 |
| crossing_targets | 22 | 0.135 | 0.135 | -0.001 | 0.180 |
| crossing_targets | 23 | 0.145 | 0.107 | -0.038 | 0.105 |
| crossing_targets | 24 | 0.156 | 0.105 | -0.051 | 0.146 |
| delivery_delay | 0 | 0.318 | 0.344 | +0.026 | 0.379 |
| delivery_delay | 1 | 0.285 | 0.352 | +0.067 | 0.354 |
| delivery_delay | 2 | 0.290 | 0.243 | -0.047 | 0.227 |
| delivery_delay | 3 | 0.272 | 0.321 | +0.049 | 0.346 |
| delivery_delay | 4 | 0.263 | 0.289 | +0.026 | 0.240 |
| delivery_delay | 5 | 0.392 | 0.280 | -0.112 | 0.292 |
| delivery_delay | 6 | 0.256 | 0.375 | +0.119 | 0.248 |
| delivery_delay | 7 | 0.218 | 0.326 | +0.108 | 0.319 |
| delivery_delay | 8 | 0.328 | 0.338 | +0.010 | 0.331 |
| delivery_delay | 9 | 0.343 | 0.337 | -0.006 | 0.359 |
| delivery_delay | 10 | 0.325 | 0.454 | +0.129 | 0.432 |
| delivery_delay | 11 | 0.261 | 0.272 | +0.011 | 0.269 |
| delivery_delay | 12 | 0.286 | 0.237 | -0.049 | 0.243 |
| delivery_delay | 13 | 0.291 | 0.264 | -0.026 | 0.265 |
| delivery_delay | 14 | 0.286 | 0.304 | +0.018 | 0.350 |
| delivery_delay | 15 | 0.305 | 0.401 | +0.095 | 0.413 |
| delivery_delay | 16 | 0.294 | 0.295 | +0.001 | 0.295 |
| delivery_delay | 17 | 0.428 | 0.441 | +0.013 | 0.443 |
| delivery_delay | 18 | 0.314 | 0.422 | +0.108 | 0.429 |
| delivery_delay | 19 | 0.338 | 0.356 | +0.017 | 0.382 |
| delivery_delay | 20 | 0.272 | 0.304 | +0.032 | 0.318 |
| delivery_delay | 21 | 0.323 | 0.305 | -0.018 | 0.288 |
| delivery_delay | 22 | 0.379 | 0.412 | +0.033 | 0.344 |
| delivery_delay | 23 | 0.311 | 0.309 | -0.003 | 0.331 |
| delivery_delay | 24 | 0.329 | 0.235 | -0.093 | 0.361 |
| delivery_delay_retrodiction | 0 | 0.287 | 0.416 | +0.129 | 0.382 |
| delivery_delay_retrodiction | 1 | 0.318 | 0.489 | +0.171 | 0.493 |
| delivery_delay_retrodiction | 2 | 0.208 | 0.318 | +0.111 | 0.352 |
| delivery_delay_retrodiction | 3 | 0.284 | 0.386 | +0.102 | 0.478 |
| delivery_delay_retrodiction | 4 | 0.235 | 0.207 | -0.028 | 0.186 |
| delivery_delay_retrodiction | 5 | 0.249 | 0.311 | +0.062 | 0.520 |
| delivery_delay_retrodiction | 6 | 0.333 | 0.431 | +0.098 | 0.438 |
| delivery_delay_retrodiction | 7 | 0.199 | 0.195 | -0.005 | 0.199 |
| delivery_delay_retrodiction | 8 | 0.258 | 0.302 | +0.044 | 0.349 |
| delivery_delay_retrodiction | 9 | 0.340 | 0.350 | +0.010 | 0.293 |
| delivery_delay_retrodiction | 10 | 0.326 | 0.389 | +0.063 | 0.422 |
| delivery_delay_retrodiction | 11 | 0.305 | 0.348 | +0.043 | 0.342 |
| delivery_delay_retrodiction | 12 | 0.237 | 0.251 | +0.013 | 0.258 |
| delivery_delay_retrodiction | 13 | 0.222 | 0.246 | +0.024 | 0.268 |
| delivery_delay_retrodiction | 14 | 0.260 | 0.268 | +0.008 | 0.267 |
| delivery_delay_retrodiction | 15 | 0.260 | 0.364 | +0.104 | 0.400 |
| delivery_delay_retrodiction | 16 | 0.186 | 0.237 | +0.051 | 0.195 |
| delivery_delay_retrodiction | 17 | 0.356 | 0.442 | +0.086 | 0.434 |
| delivery_delay_retrodiction | 18 | 0.364 | 0.354 | -0.010 | 0.362 |
| delivery_delay_retrodiction | 19 | 0.395 | 0.363 | -0.033 | 0.357 |
| delivery_delay_retrodiction | 20 | 0.286 | 0.411 | +0.125 | 0.345 |
| delivery_delay_retrodiction | 21 | 0.292 | 0.297 | +0.005 | 0.290 |
| delivery_delay_retrodiction | 22 | 0.338 | 0.394 | +0.056 | 0.407 |
| delivery_delay_retrodiction | 23 | 0.249 | 0.301 | +0.052 | 0.327 |
| delivery_delay_retrodiction | 24 | 0.278 | 0.313 | +0.035 | 0.279 |
| dense_clutter | 0 | 0.286 | 0.477 | +0.191 | 0.468 |
| dense_clutter | 1 | 0.199 | 0.375 | +0.176 | 0.344 |
| dense_clutter | 2 | 0.192 | 0.196 | +0.004 | 0.301 |
| dense_clutter | 3 | 0.246 | 0.309 | +0.064 | 0.347 |
| dense_clutter | 4 | 0.290 | 0.284 | -0.007 | 0.288 |
| dense_clutter | 5 | 0.259 | 0.366 | +0.107 | 0.275 |
| dense_clutter | 6 | 0.236 | 0.222 | -0.014 | 0.274 |
| dense_clutter | 7 | 0.192 | 0.213 | +0.021 | 0.219 |
| dense_clutter | 8 | 0.304 | 0.273 | -0.031 | 0.311 |
| dense_clutter | 9 | 0.314 | 0.366 | +0.051 | 0.366 |
| dense_clutter | 10 | 0.208 | 0.194 | -0.014 | 0.243 |
| dense_clutter | 11 | 0.298 | 0.271 | -0.027 | 0.229 |
| dense_clutter | 12 | 0.210 | 0.191 | -0.019 | 0.167 |
| dense_clutter | 13 | 0.248 | 0.318 | +0.070 | 0.211 |
| dense_clutter | 14 | 0.196 | 0.253 | +0.056 | 0.173 |
| dense_clutter | 15 | 0.234 | 0.411 | +0.176 | 0.374 |
| dense_clutter | 16 | 0.153 | 0.150 | -0.003 | 0.155 |
| dense_clutter | 17 | 0.322 | 0.309 | -0.013 | 0.352 |
| dense_clutter | 18 | 0.249 | 0.329 | +0.080 | 0.200 |
| dense_clutter | 19 | 0.317 | 0.501 | +0.184 | 0.408 |
| dense_clutter | 20 | 0.207 | 0.223 | +0.016 | 0.232 |
| dense_clutter | 21 | 0.182 | 0.175 | -0.008 | 0.177 |
| dense_clutter | 22 | 0.241 | 0.253 | +0.012 | 0.218 |
| dense_clutter | 23 | 0.162 | 0.218 | +0.056 | 0.193 |
| dense_clutter | 24 | 0.302 | 0.255 | -0.048 | 0.249 |
| false_observations | 0 | 0.250 | 0.254 | +0.004 | 0.265 |
| false_observations | 1 | 0.218 | 0.236 | +0.018 | 0.335 |
| false_observations | 2 | 0.195 | 0.178 | -0.017 | 0.211 |
| false_observations | 3 | 0.313 | 0.295 | -0.018 | 0.399 |
| false_observations | 4 | 0.194 | 0.175 | -0.018 | 0.161 |
| false_observations | 5 | 0.292 | 0.259 | -0.033 | 0.263 |
| false_observations | 6 | 0.193 | 0.262 | +0.070 | 0.267 |
| false_observations | 7 | 0.189 | 0.155 | -0.034 | 0.197 |
| false_observations | 8 | 0.209 | 0.247 | +0.038 | 0.238 |
| false_observations | 9 | 0.281 | 0.299 | +0.018 | 0.283 |
| false_observations | 10 | 0.202 | 0.332 | +0.130 | 0.316 |
| false_observations | 11 | 0.247 | 0.369 | +0.122 | 0.286 |
| false_observations | 12 | 0.245 | 0.212 | -0.032 | 0.205 |
| false_observations | 13 | 0.290 | 0.320 | +0.030 | 0.327 |
| false_observations | 14 | 0.182 | 0.172 | -0.009 | 0.170 |
| false_observations | 15 | 0.164 | 0.226 | +0.062 | 0.231 |
| false_observations | 16 | 0.179 | 0.166 | -0.013 | 0.165 |
| false_observations | 17 | 0.289 | 0.330 | +0.041 | 0.355 |
| false_observations | 18 | 0.214 | 0.330 | +0.116 | 0.324 |
| false_observations | 19 | 0.354 | 0.209 | -0.145 | 0.300 |
| false_observations | 20 | 0.173 | 0.149 | -0.024 | 0.153 |
| false_observations | 21 | 0.211 | 0.315 | +0.104 | 0.375 |
| false_observations | 22 | 0.277 | 0.262 | -0.015 | 0.263 |
| false_observations | 23 | 0.164 | 0.185 | +0.021 | 0.178 |
| false_observations | 24 | 0.215 | 0.224 | +0.009 | 0.240 |
| measurement_bias | 0 | 1.686 | 1.688 | +0.002 | 1.671 |
| measurement_bias | 1 | 1.656 | 1.614 | -0.043 | 1.608 |
| measurement_bias | 2 | 1.613 | 1.632 | +0.019 | 1.623 |
| measurement_bias | 3 | 1.611 | 1.592 | -0.019 | 1.568 |
| measurement_bias | 4 | 1.593 | 1.590 | -0.003 | 1.608 |
| measurement_bias | 5 | 1.607 | 1.623 | +0.016 | 1.624 |
| measurement_bias | 6 | 1.641 | 1.598 | -0.042 | 1.595 |
| measurement_bias | 7 | 1.589 | 1.588 | -0.002 | 1.621 |
| measurement_bias | 8 | 1.647 | 1.610 | -0.036 | 1.622 |
| measurement_bias | 9 | 1.593 | 1.598 | +0.005 | 1.600 |
| measurement_bias | 10 | 1.646 | 1.601 | -0.045 | 1.619 |
| measurement_bias | 11 | 1.705 | 1.657 | -0.048 | 1.656 |
| measurement_bias | 12 | 1.667 | 1.612 | -0.056 | 1.621 |
| measurement_bias | 13 | 1.641 | 1.605 | -0.036 | 1.604 |
| measurement_bias | 14 | 1.655 | 1.611 | -0.044 | 1.634 |
| measurement_bias | 15 | 1.679 | 1.617 | -0.062 | 1.610 |
| measurement_bias | 16 | 1.668 | 1.603 | -0.065 | 1.641 |
| measurement_bias | 17 | 1.596 | 1.590 | -0.006 | 1.598 |
| measurement_bias | 18 | 1.626 | 1.669 | +0.043 | 1.643 |
| measurement_bias | 19 | 1.664 | 1.628 | -0.035 | 1.651 |
| measurement_bias | 20 | 1.621 | 1.627 | +0.006 | 1.632 |
| measurement_bias | 21 | 1.642 | 1.616 | -0.027 | 1.605 |
| measurement_bias | 22 | 1.642 | 1.690 | +0.048 | 1.690 |
| measurement_bias | 23 | 1.654 | 1.597 | -0.057 | 1.579 |
| measurement_bias | 24 | 1.682 | 1.642 | -0.039 | 1.630 |
| moving_observer | 0 | 0.226 | 0.250 | +0.024 | 0.275 |
| moving_observer | 1 | 0.198 | 0.320 | +0.122 | 0.207 |
| moving_observer | 2 | 0.195 | 0.247 | +0.051 | 0.313 |
| moving_observer | 3 | 0.310 | 0.343 | +0.033 | 0.344 |
| moving_observer | 4 | 0.280 | 0.171 | -0.110 | 0.273 |
| moving_observer | 5 | 0.255 | 0.417 | +0.163 | 0.338 |
| moving_observer | 6 | 0.205 | 0.205 | +0.000 | 0.175 |
| moving_observer | 7 | 0.240 | 0.232 | -0.008 | 0.231 |
| moving_observer | 8 | 0.284 | 0.208 | -0.075 | 0.213 |
| moving_observer | 9 | 0.471 | 0.477 | +0.006 | 0.492 |
| moving_observer | 10 | 0.200 | 0.242 | +0.043 | 0.244 |
| moving_observer | 11 | 0.260 | 0.243 | -0.017 | 0.257 |
| moving_observer | 12 | 0.150 | 0.121 | -0.029 | 0.241 |
| moving_observer | 13 | 0.153 | 0.369 | +0.216 | 0.260 |
| moving_observer | 14 | 0.171 | 0.116 | -0.056 | 0.156 |
| moving_observer | 15 | 0.253 | 0.316 | +0.063 | 0.394 |
| moving_observer | 16 | 0.173 | 0.112 | -0.061 | 0.155 |
| moving_observer | 17 | 0.436 | 0.453 | +0.017 | 0.304 |
| moving_observer | 18 | 0.284 | 0.261 | -0.022 | 0.258 |
| moving_observer | 19 | 0.261 | 0.249 | -0.012 | 0.231 |
| moving_observer | 20 | 0.152 | 0.345 | +0.193 | 0.196 |
| moving_observer | 21 | 0.262 | 0.255 | -0.007 | 0.290 |
| moving_observer | 22 | 0.242 | 0.196 | -0.046 | 0.197 |
| moving_observer | 23 | 0.151 | 0.183 | +0.032 | 0.175 |
| moving_observer | 24 | 0.245 | 0.206 | -0.040 | 0.210 |
| nominal | 0 | 0.183 | 0.256 | +0.073 | 0.289 |
| nominal | 1 | 0.253 | 0.346 | +0.094 | 0.317 |
| nominal | 2 | 0.208 | 0.225 | +0.017 | 0.201 |
| nominal | 3 | 0.302 | 0.390 | +0.088 | 0.372 |
| nominal | 4 | 0.275 | 0.235 | -0.040 | 0.202 |
| nominal | 5 | 0.231 | 0.296 | +0.065 | 0.288 |
| nominal | 6 | 0.189 | 0.306 | +0.116 | 0.339 |
| nominal | 7 | 0.223 | 0.203 | -0.020 | 0.202 |
| nominal | 8 | 0.279 | 0.237 | -0.042 | 0.233 |
| nominal | 9 | 0.444 | 0.485 | +0.041 | 0.383 |
| nominal | 10 | 0.216 | 0.212 | -0.004 | 0.215 |
| nominal | 11 | 0.240 | 0.235 | -0.006 | 0.239 |
| nominal | 12 | 0.164 | 0.236 | +0.072 | 0.237 |
| nominal | 13 | 0.153 | 0.279 | +0.127 | 0.273 |
| nominal | 14 | 0.191 | 0.152 | -0.039 | 0.155 |
| nominal | 15 | 0.201 | 0.258 | +0.057 | 0.279 |
| nominal | 16 | 0.191 | 0.117 | -0.074 | 0.180 |
| nominal | 17 | 0.317 | 0.345 | +0.029 | 0.355 |
| nominal | 18 | 0.240 | 0.336 | +0.096 | 0.245 |
| nominal | 19 | 0.241 | 0.224 | -0.017 | 0.228 |
| nominal | 20 | 0.171 | 0.128 | -0.043 | 0.135 |
| nominal | 21 | 0.284 | 0.244 | -0.040 | 0.249 |
| nominal | 22 | 0.212 | 0.214 | +0.002 | 0.215 |
| nominal | 23 | 0.198 | 0.150 | -0.048 | 0.167 |
| nominal | 24 | 0.231 | 0.229 | -0.002 | 0.231 |
| range_dropout | 0 | 0.240 | 0.228 | -0.012 | 0.252 |
| range_dropout | 1 | 0.350 | 0.493 | +0.143 | 0.516 |
| range_dropout | 2 | 0.253 | 0.232 | -0.022 | 0.228 |
| range_dropout | 3 | 0.287 | 0.447 | +0.160 | 0.357 |
| range_dropout | 4 | 0.225 | 0.182 | -0.044 | 0.273 |
| range_dropout | 5 | 0.240 | 0.409 | +0.169 | 0.398 |
| range_dropout | 6 | 0.201 | 0.314 | +0.114 | 0.308 |
| range_dropout | 7 | 0.229 | 0.306 | +0.077 | 0.297 |
| range_dropout | 8 | 0.234 | 0.239 | +0.005 | 0.251 |
| range_dropout | 9 | 0.297 | 0.266 | -0.031 | 0.266 |
| range_dropout | 10 | 0.274 | 0.299 | +0.025 | 0.361 |
| range_dropout | 11 | 0.256 | 0.266 | +0.010 | 0.249 |
| range_dropout | 12 | 0.227 | 0.189 | -0.038 | 0.229 |
| range_dropout | 13 | 0.269 | 0.181 | -0.088 | 0.181 |
| range_dropout | 14 | 0.173 | 0.185 | +0.012 | 0.201 |
| range_dropout | 15 | 0.265 | 0.231 | -0.034 | 0.196 |
| range_dropout | 16 | 0.216 | 0.195 | -0.022 | 0.205 |
| range_dropout | 17 | 0.254 | 0.310 | +0.056 | 0.312 |
| range_dropout | 18 | 0.204 | 0.327 | +0.123 | 0.311 |
| range_dropout | 19 | 0.334 | 0.305 | -0.030 | 0.288 |
| range_dropout | 20 | 0.260 | 0.211 | -0.049 | 0.278 |
| range_dropout | 21 | 0.242 | 0.233 | -0.010 | 0.244 |
| range_dropout | 22 | 0.294 | 0.206 | -0.088 | 0.278 |
| range_dropout | 23 | 0.250 | 0.244 | -0.006 | 0.248 |
| range_dropout | 24 | 0.243 | 0.197 | -0.047 | 0.206 |
| sensor_disagreement_large_bias | 0 | 0.183 | 0.184 | +0.000 | 0.184 |
| sensor_disagreement_large_bias | 1 | 0.253 | 0.240 | -0.012 | 0.240 |
| sensor_disagreement_large_bias | 2 | 0.208 | 0.216 | +0.008 | 0.216 |
| sensor_disagreement_large_bias | 3 | 0.302 | 0.330 | +0.029 | 0.330 |
| sensor_disagreement_large_bias | 4 | 0.275 | 0.275 | +0.000 | 0.275 |
| sensor_disagreement_large_bias | 5 | 0.231 | 0.231 | +0.000 | 0.231 |
| sensor_disagreement_large_bias | 6 | 0.189 | 0.178 | -0.011 | 0.178 |
| sensor_disagreement_large_bias | 7 | 0.223 | 0.223 | +0.000 | 0.223 |
| sensor_disagreement_large_bias | 8 | 0.279 | 0.249 | -0.030 | 0.247 |
| sensor_disagreement_large_bias | 9 | 0.444 | 0.496 | +0.053 | 0.495 |
| sensor_disagreement_large_bias | 10 | 0.216 | 0.217 | +0.001 | 0.216 |
| sensor_disagreement_large_bias | 11 | 0.240 | 0.240 | +0.000 | 0.240 |
| sensor_disagreement_large_bias | 12 | 0.164 | 0.164 | +0.000 | 0.164 |
| sensor_disagreement_large_bias | 13 | 0.153 | 0.155 | +0.003 | 0.155 |
| sensor_disagreement_large_bias | 14 | 0.191 | 0.191 | +0.000 | 0.191 |
| sensor_disagreement_large_bias | 15 | 0.201 | 0.200 | -0.000 | 0.200 |
| sensor_disagreement_large_bias | 16 | 0.191 | 0.191 | +0.000 | 0.191 |
| sensor_disagreement_large_bias | 17 | 0.317 | 0.393 | +0.076 | 0.477 |
| sensor_disagreement_large_bias | 18 | 0.240 | 0.247 | +0.007 | 0.247 |
| sensor_disagreement_large_bias | 19 | 0.241 | 0.275 | +0.034 | 0.275 |
| sensor_disagreement_large_bias | 20 | 0.171 | 0.152 | -0.019 | 0.152 |
| sensor_disagreement_large_bias | 21 | 0.284 | 0.281 | -0.003 | 0.282 |
| sensor_disagreement_large_bias | 22 | 0.212 | 0.252 | +0.040 | 0.275 |
| sensor_disagreement_large_bias | 23 | 0.198 | 0.172 | -0.026 | 0.171 |
| sensor_disagreement_large_bias | 24 | 0.231 | 0.230 | -0.001 | 0.230 |
| sensor_disagreement_within_gate | 0 | 0.183 | 0.354 | +0.171 | 0.205 |
| sensor_disagreement_within_gate | 1 | 0.253 | 0.348 | +0.096 | 0.330 |
| sensor_disagreement_within_gate | 2 | 0.208 | 0.377 | +0.169 | 0.227 |
| sensor_disagreement_within_gate | 3 | 0.302 | 0.471 | +0.169 | 0.276 |
| sensor_disagreement_within_gate | 4 | 0.275 | 0.542 | +0.267 | 0.247 |
| sensor_disagreement_within_gate | 5 | 0.231 | 0.271 | +0.040 | 0.291 |
| sensor_disagreement_within_gate | 6 | 0.189 | 0.374 | +0.185 | 0.288 |
| sensor_disagreement_within_gate | 7 | 0.223 | 0.371 | +0.148 | 0.276 |
| sensor_disagreement_within_gate | 8 | 0.279 | 0.356 | +0.077 | 0.232 |
| sensor_disagreement_within_gate | 9 | 0.444 | 0.614 | +0.171 | 0.381 |
| sensor_disagreement_within_gate | 10 | 0.216 | 0.327 | +0.111 | 0.280 |
| sensor_disagreement_within_gate | 11 | 0.240 | 0.486 | +0.246 | 0.268 |
| sensor_disagreement_within_gate | 12 | 0.164 | 0.466 | +0.301 | 0.276 |
| sensor_disagreement_within_gate | 13 | 0.153 | 0.245 | +0.092 | 0.389 |
| sensor_disagreement_within_gate | 14 | 0.191 | 0.218 | +0.028 | 0.140 |
| sensor_disagreement_within_gate | 15 | 0.201 | 0.436 | +0.236 | 0.324 |
| sensor_disagreement_within_gate | 16 | 0.191 | 0.288 | +0.097 | 0.117 |
| sensor_disagreement_within_gate | 17 | 0.317 | 0.466 | +0.149 | 0.306 |
| sensor_disagreement_within_gate | 18 | 0.240 | 0.301 | +0.060 | 0.286 |
| sensor_disagreement_within_gate | 19 | 0.241 | 0.501 | +0.260 | 0.321 |
| sensor_disagreement_within_gate | 20 | 0.171 | 0.319 | +0.148 | 0.171 |
| sensor_disagreement_within_gate | 21 | 0.284 | 0.344 | +0.060 | 0.279 |
| sensor_disagreement_within_gate | 22 | 0.212 | 0.402 | +0.191 | 0.285 |
| sensor_disagreement_within_gate | 23 | 0.198 | 0.280 | +0.082 | 0.296 |
| sensor_disagreement_within_gate | 24 | 0.231 | 0.367 | +0.136 | 0.214 |
| sensor_disagreement_within_gate_high | 0 | 0.183 | 0.509 | +0.326 | 0.232 |
| sensor_disagreement_within_gate_high | 1 | 0.253 | 0.420 | +0.167 | 0.334 |
| sensor_disagreement_within_gate_high | 2 | 0.208 | 0.370 | +0.161 | 0.277 |
| sensor_disagreement_within_gate_high | 3 | 0.302 | 0.522 | +0.220 | 0.398 |
| sensor_disagreement_within_gate_high | 4 | 0.275 | 0.592 | +0.316 | 0.238 |
| sensor_disagreement_within_gate_high | 5 | 0.231 | 0.480 | +0.249 | 0.296 |
| sensor_disagreement_within_gate_high | 6 | 0.189 | 0.299 | +0.110 | 0.334 |
| sensor_disagreement_within_gate_high | 7 | 0.223 | 0.427 | +0.204 | 0.289 |
| sensor_disagreement_within_gate_high | 8 | 0.279 | 0.416 | +0.137 | 0.223 |
| sensor_disagreement_within_gate_high | 9 | 0.444 | 0.520 | +0.077 | 0.500 |
| sensor_disagreement_within_gate_high | 10 | 0.216 | 0.375 | +0.158 | 0.255 |
| sensor_disagreement_within_gate_high | 11 | 0.240 | 0.420 | +0.180 | 0.255 |
| sensor_disagreement_within_gate_high | 12 | 0.164 | 0.560 | +0.396 | 0.269 |
| sensor_disagreement_within_gate_high | 13 | 0.153 | 0.653 | +0.501 | 0.207 |
| sensor_disagreement_within_gate_high | 14 | 0.191 | 0.399 | +0.209 | 0.203 |
| sensor_disagreement_within_gate_high | 15 | 0.201 | 0.535 | +0.334 | 0.262 |
| sensor_disagreement_within_gate_high | 16 | 0.191 | 0.427 | +0.236 | 0.181 |
| sensor_disagreement_within_gate_high | 17 | 0.317 | 0.506 | +0.189 | 0.298 |
| sensor_disagreement_within_gate_high | 18 | 0.240 | 0.370 | +0.129 | 0.261 |
| sensor_disagreement_within_gate_high | 19 | 0.241 | 0.692 | +0.451 | 0.312 |
| sensor_disagreement_within_gate_high | 20 | 0.171 | 0.557 | +0.387 | 0.167 |
| sensor_disagreement_within_gate_high | 21 | 0.284 | 0.355 | +0.071 | 0.271 |
| sensor_disagreement_within_gate_high | 22 | 0.212 | 0.428 | +0.217 | 0.257 |
| sensor_disagreement_within_gate_high | 23 | 0.198 | 0.397 | +0.199 | 0.306 |
| sensor_disagreement_within_gate_high | 24 | 0.231 | 0.444 | +0.214 | 0.246 |
| sensor_disagreement_within_gate_low | 0 | 0.183 | 0.340 | +0.157 | 0.291 |
| sensor_disagreement_within_gate_low | 1 | 0.253 | 0.298 | +0.046 | 0.333 |
| sensor_disagreement_within_gate_low | 2 | 0.208 | 0.245 | +0.036 | 0.199 |
| sensor_disagreement_within_gate_low | 3 | 0.302 | 0.431 | +0.129 | 0.276 |
| sensor_disagreement_within_gate_low | 4 | 0.275 | 0.364 | +0.089 | 0.292 |
| sensor_disagreement_within_gate_low | 5 | 0.231 | 0.478 | +0.247 | 0.289 |
| sensor_disagreement_within_gate_low | 6 | 0.189 | 0.377 | +0.187 | 0.341 |
| sensor_disagreement_within_gate_low | 7 | 0.223 | 0.364 | +0.141 | 0.329 |
| sensor_disagreement_within_gate_low | 8 | 0.279 | 0.359 | +0.080 | 0.232 |
| sensor_disagreement_within_gate_low | 9 | 0.444 | 0.370 | -0.074 | 0.443 |
| sensor_disagreement_within_gate_low | 10 | 0.216 | 0.280 | +0.064 | 0.235 |
| sensor_disagreement_within_gate_low | 11 | 0.240 | 0.386 | +0.146 | 0.251 |
| sensor_disagreement_within_gate_low | 12 | 0.164 | 0.381 | +0.217 | 0.176 |
| sensor_disagreement_within_gate_low | 13 | 0.153 | 0.333 | +0.180 | 0.369 |
| sensor_disagreement_within_gate_low | 14 | 0.191 | 0.219 | +0.029 | 0.135 |
| sensor_disagreement_within_gate_low | 15 | 0.201 | 0.381 | +0.180 | 0.260 |
| sensor_disagreement_within_gate_low | 16 | 0.191 | 0.218 | +0.027 | 0.135 |
| sensor_disagreement_within_gate_low | 17 | 0.317 | 0.401 | +0.084 | 0.322 |
| sensor_disagreement_within_gate_low | 18 | 0.240 | 0.373 | +0.132 | 0.252 |
| sensor_disagreement_within_gate_low | 19 | 0.241 | 0.346 | +0.105 | 0.266 |
| sensor_disagreement_within_gate_low | 20 | 0.171 | 0.294 | +0.123 | 0.157 |
| sensor_disagreement_within_gate_low | 21 | 0.284 | 0.277 | -0.007 | 0.262 |
| sensor_disagreement_within_gate_low | 22 | 0.212 | 0.353 | +0.142 | 0.237 |
| sensor_disagreement_within_gate_low | 23 | 0.198 | 0.213 | +0.015 | 0.233 |
| sensor_disagreement_within_gate_low | 24 | 0.231 | 0.291 | +0.060 | 0.223 |
| stale_rejection | 0 | N/A | N/A | N/A | N/A |
| stale_rejection | 1 | N/A | N/A | N/A | N/A |
| stale_rejection | 2 | N/A | N/A | N/A | N/A |
| stale_rejection | 3 | N/A | N/A | N/A | N/A |
| stale_rejection | 4 | N/A | N/A | N/A | N/A |
| stale_rejection | 5 | N/A | N/A | N/A | N/A |
| stale_rejection | 6 | N/A | N/A | N/A | N/A |
| stale_rejection | 7 | N/A | N/A | N/A | N/A |
| stale_rejection | 8 | N/A | N/A | N/A | N/A |
| stale_rejection | 9 | N/A | N/A | N/A | N/A |
| stale_rejection | 10 | N/A | N/A | N/A | N/A |
| stale_rejection | 11 | N/A | N/A | N/A | N/A |
| stale_rejection | 12 | N/A | N/A | N/A | N/A |
| stale_rejection | 13 | N/A | N/A | N/A | N/A |
| stale_rejection | 14 | N/A | N/A | N/A | N/A |
| stale_rejection | 15 | N/A | N/A | N/A | N/A |
| stale_rejection | 16 | N/A | N/A | N/A | N/A |
| stale_rejection | 17 | N/A | N/A | N/A | N/A |
| stale_rejection | 18 | N/A | N/A | N/A | N/A |
| stale_rejection | 19 | N/A | N/A | N/A | N/A |
| stale_rejection | 20 | N/A | N/A | N/A | N/A |
| stale_rejection | 21 | N/A | N/A | N/A | N/A |
| stale_rejection | 22 | N/A | N/A | N/A | N/A |
| stale_rejection | 23 | N/A | N/A | N/A | N/A |
| stale_rejection | 24 | N/A | N/A | N/A | N/A |
| uncertainty_miscalibration | 0 | 0.365 | 0.558 | +0.193 | 0.502 |
| uncertainty_miscalibration | 1 | 0.380 | 0.498 | +0.118 | 0.574 |
| uncertainty_miscalibration | 2 | 0.475 | 0.541 | +0.066 | 0.511 |
| uncertainty_miscalibration | 3 | 0.472 | 0.627 | +0.155 | 0.561 |
| uncertainty_miscalibration | 4 | 0.534 | 0.509 | -0.025 | 0.498 |
| uncertainty_miscalibration | 5 | 0.477 | 0.548 | +0.071 | 0.551 |
| uncertainty_miscalibration | 6 | 0.481 | 0.482 | +0.001 | 0.484 |
| uncertainty_miscalibration | 7 | 0.522 | 0.617 | +0.095 | 0.586 |
| uncertainty_miscalibration | 8 | 0.482 | 0.605 | +0.124 | 0.527 |
| uncertainty_miscalibration | 9 | 0.515 | 0.556 | +0.041 | 0.548 |
| uncertainty_miscalibration | 10 | 0.350 | 0.437 | +0.087 | 0.442 |
| uncertainty_miscalibration | 11 | 0.510 | 0.515 | +0.005 | 0.614 |
| uncertainty_miscalibration | 12 | 0.591 | 0.531 | -0.060 | 0.482 |
| uncertainty_miscalibration | 13 | 0.427 | 0.483 | +0.056 | 0.574 |
| uncertainty_miscalibration | 14 | 0.432 | 0.567 | +0.135 | 0.581 |
| uncertainty_miscalibration | 15 | 0.448 | 0.527 | +0.080 | 0.641 |
| uncertainty_miscalibration | 16 | 0.545 | 0.438 | -0.107 | 0.521 |
| uncertainty_miscalibration | 17 | 0.512 | 0.672 | +0.160 | 0.545 |
| uncertainty_miscalibration | 18 | 0.407 | 0.385 | -0.023 | 0.422 |
| uncertainty_miscalibration | 19 | 0.501 | 0.549 | +0.048 | 0.574 |
| uncertainty_miscalibration | 20 | 0.374 | 0.502 | +0.129 | 0.582 |
| uncertainty_miscalibration | 21 | 0.364 | 0.588 | +0.224 | 0.649 |
| uncertainty_miscalibration | 22 | 0.422 | 0.423 | +0.001 | 0.520 |
| uncertainty_miscalibration | 23 | 0.417 | 0.457 | +0.040 | 0.506 |
| uncertainty_miscalibration | 24 | 0.502 | 0.504 | +0.002 | 0.523 |
| vision_dropout | 0 | 0.183 | 0.241 | +0.058 | 0.338 |
| vision_dropout | 1 | 0.253 | 0.218 | -0.034 | 0.225 |
| vision_dropout | 2 | 0.208 | 0.206 | -0.002 | 0.231 |
| vision_dropout | 3 | 0.302 | 0.293 | -0.009 | 0.291 |
| vision_dropout | 4 | 0.275 | 0.297 | +0.022 | 0.254 |
| vision_dropout | 5 | 0.231 | 0.237 | +0.006 | 0.233 |
| vision_dropout | 6 | 0.189 | 0.193 | +0.004 | 0.219 |
| vision_dropout | 7 | 0.223 | 0.230 | +0.007 | 0.255 |
| vision_dropout | 8 | 0.279 | 0.295 | +0.016 | 0.313 |
| vision_dropout | 9 | 0.444 | 0.462 | +0.019 | 0.480 |
| vision_dropout | 10 | 0.216 | 0.164 | -0.052 | 0.173 |
| vision_dropout | 11 | 0.240 | 0.234 | -0.006 | 0.232 |
| vision_dropout | 12 | 0.164 | 0.214 | +0.050 | 0.227 |
| vision_dropout | 13 | 0.153 | 0.212 | +0.060 | 0.341 |
| vision_dropout | 14 | 0.191 | 0.184 | -0.007 | 0.150 |
| vision_dropout | 15 | 0.201 | 0.307 | +0.107 | 0.237 |
| vision_dropout | 16 | 0.191 | 0.196 | +0.005 | 0.169 |
| vision_dropout | 17 | 0.317 | 0.384 | +0.067 | 0.321 |
| vision_dropout | 18 | 0.240 | 0.257 | +0.017 | 0.252 |
| vision_dropout | 19 | 0.241 | 0.248 | +0.007 | 0.242 |
| vision_dropout | 20 | 0.171 | 0.140 | -0.031 | 0.150 |
| vision_dropout | 21 | 0.284 | 0.231 | -0.054 | 0.257 |
| vision_dropout | 22 | 0.212 | 0.200 | -0.012 | 0.390 |
| vision_dropout | 23 | 0.198 | 0.139 | -0.058 | 0.196 |
| vision_dropout | 24 | 0.231 | 0.250 | +0.019 | 0.233 |

## Findings

- Position RMSE: the paired interval excludes zero in favour of fusion in 1 scenario(s) and against fusion in 6 scenario(s); it includes zero (or has fewer than two seeds) in 8 scenario(s).
- The RMSE tally depends on the matcher: with a distance-only matcher the interval excludes zero in favour of fusion in 7 scenario(s), against fusion in 3, and includes zero in 5.
- MOTA, IDF1 and GOSPA (interval excludes zero): fusion better in 0, 2 and 0 scenario(s) and worse in 14, 5 and 14, respectively.
- fused-bias-estimated against fused (interval excludes zero): position RMSE: better in 3, worse in 0, inconclusive in 12; precision: better in 3, worse in 1, inconclusive in 11; MOTA: better in 3, worse in 1, inconclusive in 12; GOSPA: better in 3, worse in 1, inconclusive in 12.
- Fused precision is lower (interval excludes zero) in 14 scenario(s) and higher in 0; fused 95% coverage is lower in 12 and higher in 1. Accuracy alone does not establish that fusion improved association or calibration.
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
- This report uses 25 development seed(s). The reserved held-out range (25-49) is not included here and no held-out claim is made.

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
- Results on development seeds include choices made while building the workbench and are not confirmatory. A held-out evaluation exists only when the reserved seeds (25-49) appear in the `Seeds` line above.
