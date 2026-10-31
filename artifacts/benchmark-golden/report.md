# Mosaic Benchmark Report

This report is generated from the code in this repository. It contains no
hand-edited numbers and no wall-clock timestamps, so repeated runs with the
same seeds and commit are byte-identical.

## Code and protocol

- Package version: `0.1.0`
- Git commit: `0262ffa8f31164b89297edd662a7a6130c8aa409`
- Seeds: 0, 1
- Seed group: development
- Duration: 2.0 s at dt=0.1 s
- Objects per world: 2
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
| nominal | range_only | 0.234 ± 0.162 | 0.196 | 0.337 | 0.869 | 0.905 | 0.921 | 36/42 | 0.0 | 0.0 | 1.5 | 1.5 | 0.0 | 0.738 | 0.669 | 0.757 |
| nominal | fused | 0.240 ± 0.168 | 0.186 | 0.202 | 0.905 | 0.698 | 0.763 | 38/42 | 1.0 | 1.0 | 1.0 | 1.5 | 0.0 | 0.488 | 0.714 | 1.276 |
| nominal | fused_bias_estimated | 0.267 ± 0.132 | 0.195 | 0.198 | 0.905 | 0.679 | 0.724 | 38/42 | 1.0 | 1.0 | 0.5 | 1.0 | 0.0 | 0.464 | 0.766 | 1.361 |
| sensor_disagreement_within_gate | range_only | 0.234 ± 0.162 | 0.196 | 0.337 | 0.869 | 0.905 | 0.921 | 36/42 | 0.0 | 0.0 | 1.5 | 1.5 | 0.0 | 0.738 | 0.669 | 0.757 |
| sensor_disagreement_within_gate | fused | 0.378 ± 0.046 | 0.315 | 0.441 | 0.905 | 0.640 | 0.118 | 38/42 | 2.5 | 2.5 | 1.0 | 4.5 | 0.0 | 0.369 | 0.670 | 1.716 |
| sensor_disagreement_within_gate | fused_bias_estimated | 0.347 ± 0.040 | 0.260 | 0.398 | 0.905 | 0.655 | 0.500 | 38/42 | 2.5 | 2.5 | 0.0 | 2.5 | 0.0 | 0.429 | 0.760 | 1.528 |

## Paired differences (fused minus range-only)

Mean per-seed difference with a two-sided 95% t interval over seeds. Seeds with
an undefined value on either side are dropped (`n` is the number kept). Lower is
better for the RMSE metrics and GOSPA, so a negative difference favours the
treatment; higher is better for recall, precision, coverage, MOTA and IDF1, so a
positive one does. The interval describes seed-to-seed variation in this synthetic
setup and is not a claim about other worlds.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| nominal | gospa_p1 | 2 | +0.519 | [+0.228, +0.811] |
| nominal | idf1 | 2 | +0.045 | [-1.295, +1.385] |
| nominal | mota | 2 | -0.250 | [-0.401, -0.099] |
| nominal | position_coverage_95 | 2 | -0.158 | [-2.164, +1.848] |
| nominal | position_rmse | 2 | +0.006 | [-0.043, +0.056] |
| nominal | position_rmse_distance_only | 2 | -0.010 | [-0.166, +0.146] |
| nominal | precision | 2 | -0.207 | [-0.486, +0.072] |
| nominal | recall | 2 | +0.036 | [-0.418, +0.490] |
| sensor_disagreement_within_gate | gospa_p1 | 2 | +0.959 | [-2.748, +4.667] |
| sensor_disagreement_within_gate | idf1 | 2 | +0.000 | [-0.782, +0.783] |
| sensor_disagreement_within_gate | mota | 2 | -0.369 | [-1.428, +0.690] |
| sensor_disagreement_within_gate | position_coverage_95 | 2 | -0.803 | [-0.970, -0.635] |
| sensor_disagreement_within_gate | position_rmse | 2 | +0.144 | [-0.900, +1.189] |
| sensor_disagreement_within_gate | position_rmse_distance_only | 2 | +0.119 | [-1.058, +1.296] |
| sensor_disagreement_within_gate | precision | 2 | -0.265 | [-1.129, +0.599] |
| sensor_disagreement_within_gate | recall | 2 | +0.036 | [-0.418, +0.490] |

## Paired differences (fused-bias-estimated minus fused)

Same conventions as the first comparison.

| Scenario | Metric | n | Mean diff | 95% interval |
|---|---|---|---|---|
| nominal | gospa_p1 | 2 | +0.085 | [-0.547, +0.717] |
| nominal | idf1 | 2 | +0.051 | [-0.794, +0.897] |
| nominal | mota | 2 | -0.024 | [-0.326, +0.279] |
| nominal | position_coverage_95 | 2 | -0.039 | [-0.541, +0.462] |
| nominal | position_rmse | 2 | +0.027 | [-0.293, +0.347] |
| nominal | position_rmse_distance_only | 2 | +0.009 | [-0.536, +0.554] |
| nominal | precision | 2 | -0.018 | [-0.083, +0.046] |
| nominal | recall | 2 | +0.000 | [+0.000, +0.000] |
| sensor_disagreement_within_gate | gospa_p1 | 2 | -0.188 | [-1.669, +1.294] |
| sensor_disagreement_within_gate | idf1 | 2 | +0.090 | [+0.034, +0.146] |
| sensor_disagreement_within_gate | mota | 2 | +0.060 | [-0.999, +1.118] |
| sensor_disagreement_within_gate | position_coverage_95 | 2 | +0.382 | [-0.454, +1.218] |
| sensor_disagreement_within_gate | position_rmse | 2 | -0.031 | [-0.089, +0.026] |
| sensor_disagreement_within_gate | position_rmse_distance_only | 2 | -0.055 | [-0.493, +0.383] |
| sensor_disagreement_within_gate | precision | 2 | +0.016 | [-0.470, +0.501] |
| sensor_disagreement_within_gate | recall | 2 | +0.000 | [+0.000, +0.000] |

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
| nominal | range_only | N/A | N/A | 0.000 | 0.0 |
| nominal | fused | 1.000 | 1.000 | 0.500 | 19.0 |
| nominal | fused_bias_estimated | 1.000 | 1.000 | 0.500 | 19.0 |
| sensor_disagreement_within_gate | range_only | N/A | N/A | 0.000 | 0.0 |
| sensor_disagreement_within_gate | fused | 1.000 | 1.000 | 0.500 | 19.0 |
| sensor_disagreement_within_gate | fused_bias_estimated | 1.000 | 1.000 | 0.500 | 19.0 |

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
| nominal | range_only | 1.139 [0.784, 1.242] within | 1.353 [0.784, 1.242] above | 0.679 [0.820, 1.197] below | 36 | 36.0 | 6 |
| nominal | fused | 2.121 [0.788, 1.237] above | 1.337 [0.788, 1.237] above | 0.661 [0.843, 1.170] below | 38 | 72.0 | 4 |
| nominal | fused_bias_estimated | 2.299 [0.788, 1.237] above | 1.228 [0.788, 1.237] within | 0.701 [0.844, 1.169] below | 38 | 72.5 | 4 |
| sensor_disagreement_within_gate | range_only | 1.139 [0.784, 1.242] within | 1.353 [0.784, 1.242] above | 0.679 [0.820, 1.197] below | 36 | 36.0 | 6 |
| sensor_disagreement_within_gate | fused | 10.714 [0.788, 1.237] above | 1.841 [0.788, 1.237] above | 0.846 [0.841, 1.173] within | 38 | 70.0 | 4 |
| sensor_disagreement_within_gate | fused_bias_estimated | 3.505 [0.788, 1.237] above | 1.481 [0.788, 1.237] above | 0.760 [0.842, 1.172] below | 38 | 70.0 | 4 |

## Duplicate-track sensitivity to the matching gate

Mean number of duplicate tracks per seed when the evaluation matching gate is
1.0, 2.0 or 3.0 m. The three gates were chosen before running (see the project issue
tracker). The 2.0 m column is the headline gate used everywhere else in this
report when it is the evaluator gate; the others show how much the
duplicate count depends on that choice, not which gate is correct.

| Scenario | Method | 1.0 m | 2.0 m | 3.0 m |
|---|---|---|---|---|
| nominal | range_only | 0.0 | 0.0 | 0.0 |
| nominal | fused | 0.5 | 1.0 | 1.0 |
| nominal | fused_bias_estimated | 1.0 | 1.0 | 1.0 |
| sensor_disagreement_within_gate | range_only | 0.0 | 0.0 | 0.0 |
| sensor_disagreement_within_gate | fused | 2.5 | 2.5 | 2.5 |
| sensor_disagreement_within_gate | fused_bias_estimated | 2.5 | 2.5 | 2.5 |

## Vision observation acceptance (fused method)

Mean per seed. `Generated` = produced by vision sensors; `Delivered` = left the
pending queue (generated minus those still pending at the end); `Gate-rejected` =
at least one track was evaluated and none passed the chi-square gate;
`Lost competition` = passed the gate for some track but lost the one-to-one
assignment; `Other unassigned` = no evaluable candidate track; `Stale/invalid` =
rejected outside association; `Applied` = used in a track update.

| Scenario | Generated | Delivered | Gate-rejected | Lost competition | Other unassigned | Stale/invalid | Applied |
|---|---|---|---|---|---|---|---|
| nominal | 39.0 | 39.0 | 3.0 | 0.0 | 0.0 | 0.0 | 36.0 |
| nominal | 39.0 | 39.0 | 3.0 | 0.0 | 0.0 | 0.0 | 36.0 |
| sensor_disagreement_within_gate | 39.0 | 39.0 | 3.5 | 0.0 | 0.0 | 0.0 | 35.5 |
| sensor_disagreement_within_gate | 39.0 | 39.0 | 4.5 | 0.0 | 0.0 | 0.0 | 34.5 |

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
| nominal | 0.0000 | -0.0001 | 18.5 |
| sensor_disagreement_within_gate | 0.0150 | 0.0150 | 18.5 |

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
| nominal | range_only | 41.5 | 0.0 | 0.0 | 0.0 | 0.000 | 41.5 |
| nominal | fused | 80.5 | 0.0 | 0.0 | 0.0 | 0.000 | 80.5 |
| nominal | fused_bias_estimated | 80.5 | 0.0 | 0.0 | 0.0 | 0.000 | 80.5 |
| sensor_disagreement_within_gate | range_only | 41.5 | 0.0 | 0.0 | 0.0 | 0.000 | 41.5 |
| sensor_disagreement_within_gate | fused | 80.5 | 0.0 | 0.0 | 0.0 | 0.000 | 80.5 |
| sensor_disagreement_within_gate | fused_bias_estimated | 80.5 | 0.0 | 0.0 | 0.0 | 0.000 | 80.5 |

## Per-seed results

| Scenario | Seed | Range RMSE (m) | Fused RMSE (m) | Δ (Fused − Range) | Bias-estimated RMSE (m) |
|---|---|---|---|---|---|
| nominal | 0 | 0.348 | 0.359 | +0.010 | 0.360 |
| nominal | 1 | 0.119 | 0.122 | +0.003 | 0.173 |
| sensor_disagreement_within_gate | 0 | 0.348 | 0.411 | +0.062 | 0.375 |
| sensor_disagreement_within_gate | 1 | 0.119 | 0.346 | +0.227 | 0.319 |

## Findings

- Position RMSE: the paired interval excludes zero in favour of fusion in 0 scenario(s) and against fusion in 0 scenario(s); it includes zero (or has fewer than two seeds) in 2 scenario(s).
- The RMSE tally depends on the matcher: with a distance-only matcher the interval excludes zero in favour of fusion in 0 scenario(s), against fusion in 0, and includes zero in 2.
- MOTA, IDF1 and GOSPA (interval excludes zero): fusion better in 0, 0 and 0 scenario(s) and worse in 1, 0 and 1, respectively.
- fused-bias-estimated against fused (interval excludes zero): position RMSE: better in 0, worse in 0, inconclusive in 2; precision: better in 0, worse in 0, inconclusive in 2; MOTA: better in 0, worse in 0, inconclusive in 2; GOSPA: better in 0, worse in 0, inconclusive in 2.
- Fused precision is lower (interval excludes zero) in 0 scenario(s) and higher in 0; fused 95% coverage is lower in 1 and higher in 0. Accuracy alone does not establish that fusion improved association or calibration.
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
- Scenarios with no matched samples (for example `stale_rejection`)
  report `N/A` accuracy because their observations are rejected as stale;
  that is an explicit non-result, not a zero-error result.
- This report uses 2 development seed(s). The reserved held-out range (25-49) is not included here and no held-out claim is made.

## Limitations

- Synthetic 2-D world; simplified sensor models, not hardware validation.
- Vision-only track initiation is not supported (bearing alone cannot
  determine range).
- Out-of-sequence observations older than one tracker epoch are explicitly
  rejected and counted, not silently dropped. Their accuracy impact is
  therefore not represented as a successful fusion result.
- Results on development seeds include choices made while building the workbench and are not confirmatory. A held-out evaluation exists only when the reserved seeds (25-49) appear in the `Seeds` line above.
