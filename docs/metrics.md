# Evaluation Metrics

All metrics are computed from **per-epoch track snapshots recorded during the
run**. The evaluator never uses final track states to reconstruct history.

## Matching

At each ground-truth timestamp:

- Candidate tracks are snapshots with status `CONFIRMED` or `COASTING`.
  `TENTATIVE` and `DELETED` snapshots are excluded.
- Candidate objects are all ground-truth objects at that timestamp.
- Matching is a one-to-one Hungarian assignment on Euclidean position distance.
- A pair is admissible only if the distance is at most the matching gate
  (`2.0 m` by default). No object and no track can be matched more than once in
  a frame.
- Matching is independent at each timestamp; identity continuity is measured
  afterwards, not enforced by the matcher.

## Accuracy

| Metric | Definition | Denominator |
|---|---|---|
| `position_rmse` | `sqrt(mean(||p_est - p_true||^2))` over matched samples, metres | matched samples |
| `velocity_rmse` | `sqrt(mean(||v_est - v_true||^2))` over matched samples, m/s | matched samples |

`None`/`N/A` means there were no matched samples. It is not reported as zero.

## Association and track quality

| Metric | Definition | Denominator |
|---|---|---|
| `recall` | matched samples / all ground-truth object samples | `ground_truth_samples` |
| `precision` | matched samples / all confirmed-or-coasting track samples | `confirmed_track_samples` |
| `identity_switches` | for each object, number of changes in matched track ID between consecutive matched frames | none; `None` if nothing matched |
| `num_unmatched_confirmed_tracks` | confirmed/coasting track IDs that were never matched in any frame. Formerly `num_false_tracks`; renamed because many are duplicates, not spurious objects | count of track IDs |
| `num_duplicate_tracks` | unmatched confirmed track IDs that, in at least one frame, were unmatched while a ground-truth object lay within the matching gate | count of track IDs |
| `duplicate_track_samples` | evaluated track snapshots left unmatched in a frame while a ground-truth object lay within the matching gate (the object was claimed by another track) | count of track samples, a subset of `unmatched_track_samples` |
| `num_duplicate_tracks_gate_1m`, `_2m`, `_3m` | `num_duplicate_tracks` recomputed with a 1.0, 2.0 or 3.0 m matching gate (fixed in advance); the 2 m value equals the headline when the headline gate is 2.0 m | count of track IDs |
| `class_accuracy` | `class_correct_samples / class_classified_samples` | matched samples where the track's class estimate and the true class are both known (not `UNKNOWN`); `None` if there are none |
| `class_classified_samples`, `class_correct_samples` | numerator and denominator of `class_accuracy` | count of matched samples |
| `class_accuracy_pooled` | total `class_correct_samples` / total `class_classified_samples` over all seeds of a scenario (a pooled aggregate, not a per-run value) | matched samples with known estimate and truth, summed over seeds; `None` if none |
| `class_classified_fraction_pooled` | total `class_classified_samples` / total `matched_samples` over all seeds (a pooled aggregate) | matched samples, summed over seeds; `None` if none |
| `num_tracks` | unique track IDs that appear in any snapshot, including tentative/deleted | count of track IDs |
| `num_confirmed_tracks` | unique track IDs that were ever confirmed or coasting | count of track IDs |
| `track_fragmentation` | total interruptions: frames where a matched object goes unmatched and is matched again later, summed over objects; `None` if no object is ever matched | count of interruptions, over objects matched at least once |
| `mota` | CLEAR-MOT accuracy: `1 - (misses + false positives + identity switches) / ground-truth samples`. Misses are unmatched ground-truth samples, false positives are unmatched evaluated track samples (duplicates included), switches are `identity_switches`. Can be negative; `None` without ground truth. Follows Bernardin and Stiefelhagen's definition as implemented in TrackEval's CLEAR metrics | ground-truth samples |
| `idf1`, `idp`, `idr` | Trajectory-level identity scores (Ristani et al., 2016): the best global pairing of tracks to objects by co-occurrence within the matching gate gives `IDTP`; `IDP = IDTP/(IDTP+IDFP)`, `IDR = IDTP/(IDTP+IDFN)`, `IDF1 = 2*IDTP/(2*IDTP+IDFP+IDFN)`. A duplicate track adds identity false positives that per-frame matching forgives. `None` when the denominator is zero | object and track detections (samples) |
| `gospa_p1`, `gospa_p2` | Mean per-frame GOSPA distance (Rahmathullah et al., 2017), alpha = 2, cut-off 2.0 m (fixed in advance, equal to the matching gate), `p` = 1 or 2. Per frame `(sum over optimally assigned pairs of min(d, c)^p + c^p/2 * (m + n - 2k))^(1/p)` with `k = min(m, n)`; each missed object or false track costs `c^p/2`. Frames without objects or tracks contribute 0; metres | frames |

The explicit count fields `matched_samples`, `ground_truth_samples`,
`confirmed_track_samples`, `unmatched_ground_truth_samples`,
`unmatched_track_samples` and `coverage_samples` are stored with every result so
denominators can be audited. `evaluated_frames` and `matching_gate_m` are also
recorded.

## Uncertainty calibration

For each matched sample with a solvable reported 2×2 position covariance:

```
d² = (p_est - p_true)^T P_position^-1 (p_est - p_true)
```

A sample is covered at the nominal level if `d²` is at most the chi-square
threshold for two dimensions:

- 95%: χ²(2, 0.95) = **5.991**
- 68%: χ²(2, 0.68) ≈ **2.279**

`position_coverage_95` and `position_coverage_68` divide covered samples by
`coverage_samples`. A fixed 0.85 threshold is not used. Coverage is only defined
over matched samples; it is not a detection metric.

Coverage can be low while RMSE is small, or vice versa. In particular, the
`uncertainty_miscalibration` scenario deliberately reports covariances 20× too
small and produces coverage far below 0.95.

## Timing and delivery

| Metric | Definition |
|---|---|
| `delivered_observations` | observations removed from the pending queue and processed |
| `rejected_observations` | delivered observations rejected as stale or invalid |
| `rejected_out_of_sequence` | observations older than the one-epoch staleness bound |
| `rejected_invalid` | observations with invalid metadata, covariance, frame, or a failed update |
| `pending_observations` | observations still queued at the end of the run |
| `age_samples` | number of observations whose processing age contributed to mean AoI |
| `mean_age_of_information` | mean of `processing_time - capture_time` for observations admitted by the staleness and group checks, seconds |
| `vision_generated` | vision observations produced by vision sensors (fused method only) |
| `vision_delivered` | vision observations removed from the pending queue (generated minus those still pending) |
| `vision_gate_rejected` | delivered vision observations for which at least one track was evaluated and none passed the chi-square gate |
| `vision_lost_competition` | passed the gate for some track but lost the one-to-one assignment |
| `vision_unassigned_other` | unassigned with no evaluable candidate (e.g. no tracks existed) |
| `vision_invalid_or_stale` | delivered but rejected outside association (stale, invalid, failed update) |
| `vision_applied` | used in a track update |

Identity: `vision_delivered = gate_rejected + lost_competition + unassigned_other + invalid_or_stale + applied`.

An observation older than `dt + 1e-6` seconds at processing time is counted as
rejected, not replayed or silently dropped. Because processing happens on the
tracker's discrete epoch grid, AoI is quantised by `dt`; it is not a sub-epoch
latency measurement. `mean_age_of_information` is `None`/`N/A` if no observation
was admitted.

There is no separate "measurement-to-output latency" metric. Wall-clock
execution time is deliberately not stored in benchmark artifacts.

## Reporting rules

- Every metric has a defined denominator and a sample count, or is explicitly
  unsupported.
- A metric that cannot be computed (for example RMSE with no matches) is `None`
  and renders as `N/A`, never as a fabricated zero.
- Results are reported across multiple seeds; a single seed is not treated as
  evidence.
- The benchmark uses development seeds only unless the artifact explicitly
  lists held-out seeds.
