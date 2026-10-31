# Evaluation Metrics

All metrics are computed from **per-epoch track snapshots recorded during the
run**. The evaluator never uses final track states to reconstruct history.

## Matching

At each ground-truth timestamp:

- Candidate tracks are snapshots with status `CONFIRMED` or `COASTING`.
  `TENTATIVE` and `DELETED` snapshots are excluded.
- Candidate objects are all ground-truth objects at that timestamp.
- The headline matcher is continuity-first, as in TrackEval's CLEAR matching: a
  one-to-one Hungarian assignment that maximises `1000 * previous_pairing +
  similarity` over in-gate pairs only (similarity is `1 - distance/gate`, zero
  outside the gate), then keeps only in-gate matches. A pairing from the
  immediately preceding frame that is still inside the gate therefore wins even
  when keeping it costs another object its match; an object unmatched in the
  preceding frame has no preference. The distance-only matcher instead maximises
  the number of in-gate pairs first and total distance second. A distance-only
  matcher flips between nearby tracks, which inflates identity switches without
  changing which samples are matched; `identity_switches_distance_only` reports
  the count under distance-only matching (issue #17).
- A pair is admissible only if the distance is at most the matching gate
  (`2.0 m` by default). No object and no track can be matched more than once in
  a frame.
- Matching is independent at each timestamp; identity continuity is measured
  afterwards, not enforced by the matcher.

## Accuracy

| Metric | Definition | Denominator |
|---|---|---|
| `position_rmse` | `sqrt(mean(||p_est - p_true||^2))` over matched samples, metres | matched samples |
| `position_rmse_distance_only` | `position_rmse` recomputed under a distance-only matcher (each object paired with its nearest in-gate track). It differs from `position_rmse` because the continuity preference can keep a farther track; a gap between the two means the accuracy conclusion depends on the matcher | matched samples (distance-only pairing) |
| `velocity_rmse` | `sqrt(mean(||v_est - v_true||^2))` over matched samples, m/s | matched samples |

`None`/`N/A` means there were no matched samples. It is not reported as zero.

## Association and track quality

| Metric | Definition | Denominator |
|---|---|---|
| `recall` | matched samples / all ground-truth object samples | `ground_truth_samples` |
| `precision` | matched samples / all confirmed-or-coasting track samples | `confirmed_track_samples` |
| `identity_switches` | for each object, number of changes in matched track ID between consecutive matched frames, under the continuity-preferring matcher | none; `None` if nothing matched |
| `identity_switches_distance_only` | the same count under a distance-only matcher; the gap to `identity_switches` shows how much the continuity preference matters | none; `None` if nothing matched |
| `num_unmatched_confirmed_tracks` | confirmed/coasting track IDs that were never matched in any frame. Formerly `num_false_tracks`; renamed because many are duplicates, not spurious objects | count of track IDs |
| `num_duplicate_tracks` | unmatched confirmed track IDs that, in at least one frame, were unmatched while a ground-truth object lay within the matching gate | count of track IDs |
| `duplicate_track_samples` | evaluated track snapshots left unmatched in a frame while a ground-truth object lay within the matching gate (the object was claimed by another track) | count of track samples, a subset of `unmatched_track_samples` |
| `num_duplicate_tracks_gate_1m`, `_2m`, `_3m` | `num_duplicate_tracks` recomputed with a 1.0, 2.0 or 3.0 m matching gate (fixed in advance); the 2 m value equals the headline when the headline gate is 2.0 m | count of track IDs |
| `class_accuracy` | `class_correct_samples / class_classified_samples` | matched samples where the track's class estimate and the true class are both known (not `UNKNOWN`); `None` if there are none |
| `class_classified_samples`, `class_correct_samples` | numerator and denominator of `class_accuracy` | count of matched samples |
| `vision_bias_estimate`, `vision_bias_updates` | Final estimate (rad) of the vision bearing bias and the number of vision updates that fed it, for the bias-estimated fusion method only (`None` / 0 otherwise). A single global scalar Kalman filter on vision innovations of confirmed tracks, prior standard deviation 0.05 rad, random walk 1e-4 rad per epoch, fixed in advance; uncertain tracks are down-weighted by their larger innovation variance, and only gate-passing observations are applied, so a bias too large for the gate is never learned | applied vision updates |
| `vision_bias_configured` | The bearing bias injected by the scenario, recorded for comparison with the estimate. Evaluator-side metadata; never an estimator input | none |
| `nees_samples`, `nees_position_sum`, `nees_velocity_sum` | Matched samples with a valid covariance and the sums of their 2-DOF position and velocity normalised estimation error squared (NEES, `e' P^-1 e` with the position or velocity covariance block). Conditioned on the matching gate | matched samples |
| `anees_position`, `anees_velocity` | Mean NEES per matched sample (`sum / samples`); nominal value 2 for a consistent filter. `None` without samples | `nees_samples` |
| `nis_updates`, `nis_sum`, `nis_dof_sum` | Applied filter updates, the sum of their normalised innovation squared (`v' S^-1 v`, from the filter's own innovation and covariance) and the sum of their measurement dimensions. No ground truth. Only updates that passed the gate are applied, so NIS is truncated | applied updates |
| `anis` | `nis_sum / nis_dof_sum`, mean NIS per degree of freedom (nominal 1.0, slightly below under gating). `None` without updates | `nis_dof_sum` |
| `anees_position_per_dof_pooled`, `anees_velocity_per_dof_pooled`, `anis_pooled` | Pooled over all seeds of a scenario: total NEES (or NIS) divided by the total degrees of freedom (`2 x samples` for NEES, `nis_dof_sum` for NIS). Reported with a two-sided 95% interval from the chi-square quantiles at those degrees of freedom divided by them (`_low`, `_high`, `_dof` in the aggregate). Samples within a track are correlated, so the interval is optimistic | pooled degrees of freedom |
| `class_accuracy_pooled` | total `class_correct_samples` / total `class_classified_samples` over all seeds of a scenario (a pooled aggregate, not a per-run value) | matched samples with known estimate and truth, summed over seeds; `None` if none |
| `class_classified_fraction_pooled` | total `class_classified_samples` / total `matched_samples` over all seeds (a pooled aggregate) | matched samples, summed over seeds; `None` if none |
| `num_tracks` | unique track IDs that appear in any snapshot, including tentative/deleted | count of track IDs |
| `num_confirmed_tracks` | unique track IDs that were ever confirmed or coasting | count of track IDs |
| `track_fragmentation` | total interruptions, counted once per gap (however many frames long) in which a matched object goes unmatched and is matched again later, summed over objects; `None` if no object is ever matched | count of interruptions, over objects matched at least once |
| `mota` | CLEAR-MOT accuracy: `1 - (misses + false positives + identity switches) / ground-truth samples`. Misses are unmatched ground-truth samples, false positives are unmatched evaluated track samples (duplicates included), switches are `identity_switches`. Can be negative; `None` without ground truth. Follows Bernardin and Stiefelhagen's definition as implemented in TrackEval's CLEAR metrics | ground-truth samples |
| `idf1`, `idp`, `idr` | Trajectory-level identity scores (Ristani et al., 2016): the best global pairing of tracks to objects by co-occurrence within the matching gate gives `IDTP`; `IDP = IDTP/(IDTP+IDFP)`, `IDR = IDTP/(IDTP+IDFN)`, `IDF1 = 2*IDTP/(2*IDTP+IDFP+IDFN)`. A duplicate track adds identity false positives that per-frame matching forgives. IDF1 uses its own global pairing and is independent of the per-frame matcher (and its continuity preference) that `mota`, `identity_switches` and the RMSE metrics use. `None` when the denominator is zero | object and track detections (samples) |
| `gospa_p1`, `gospa_p2` | Mean per-frame GOSPA distance (Rahmathullah et al., 2017), alpha = 2, cut-off 2.0 m (fixed in advance, equal to the matching gate), `p` = 1 or 2. Per frame `(sum over optimally assigned pairs of min(d, c)^p + c^p/2 * (m + n - 2k))^(1/p)` with `k = min(m, n)`; each missed object or false track costs `c^p/2`. Frames without objects or tracks contribute 0; metres | frames |

The explicit count fields `matched_samples`, `ground_truth_samples`,
`confirmed_track_samples`, `unmatched_ground_truth_samples`,
`unmatched_track_samples` and `coverage_samples` are stored with every result so
denominators can be audited. `evaluated_frames` and `matching_gate_m` are also
recorded.

### Skipped samples and invalid input

Coverage and NEES use a covariance block only if it is finite, symmetric and
positive definite. A non-PSD (for example `diag(1, -1, 1, 1)`), singular or
non-finite block is skipped, not inverted. Each matched sample with a rejected
block is counted: `coverage_skipped_samples` for the position coverage block,
`nees_skipped_samples` for a sample missing a valid position or velocity block.
The position and velocity blocks are judged separately, so a singular velocity
block keeps the position sample: `nees_samples` counts valid position blocks,
`nees_velocity_samples` valid velocity blocks, and `anees_position` and
`anees_velocity` divide by their own counts.

The evaluator raises `ValueError` rather than skipping when a track snapshot time
matches no world-state time (within 1e-9 s), or when two snapshots share a
`(track_id, time)`.

## Cross-check against TrackEval

`mota`, `idf1`, `idp`, `idr`, the CLEAR counts (`matched_samples`,
`unmatched_ground_truth_samples` as misses, `unmatched_track_samples` as false
positives) and `identity_switches` are cross-checked against TrackEval's
reference CLEAR and ID metric implementations (Bernardin and Stiefelhagen's
CLEAR; Ristani et al.'s ID metrics) on five fixed hand-built sequences:

| Sequence | Corner case |
|---|---|
| `clean_two_objects` | perfect tracking; both sides must score a clean run |
| `duplicate_track` | one object shadowed by a second track in every frame (false positives) |
| `identity_switch` | a track changes which object it follows, then the first object is missed |
| `miss_and_spurious` | late misses plus a track that never matches anything |
| `continuity_over_cardinality` | keeping a still-valid previous pairing costs another object its match (#58); six-metre boxes make the IoU > 0.5 threshold equal our 2 m gate |

The sequences and the expected numbers live in `tests/crosscheck/`; the
expected numbers are generated by the pinned TrackEval version recorded in
`tests/crosscheck/trackeval_reference.json` (repository and commit included).
The unit test compares our pipeline against those numbers offline; when the
development dependency group is installed it also re-runs TrackEval live so a
stale fixture cannot pass. Regenerate the fixture with
`make trackeval-reference`.

**Differences found: none.** Both implementations agree exactly on all five
sequences (`clean_two_objects`, `duplicate_track`, `identity_switch`,
`miss_and_spurious`, `continuity_over_cardinality`): same MOTA, same counts, same identity scores.

**Known definitional differences that these sequences deliberately avoid:**

- *Association*. TrackEval's CLEAR associates per frame by IoU at a 0.5
  threshold with an identity-switch bonus (we feed TrackEval the per-frame
  boxes built from our snapshots; TrackEval performs the matching and counting
  itself); ours associates by Euclidean
  distance at a 2.0 m gate with a continuity-first score (see above). The sequences keep
  intended matches at offsets where both gates accept (<= 0.2 m, IoU >= 0.667)
  and distinct objects far apart where both reject, so the matchers cannot
  disagree about *which* pairs are made. In a dense scene where IoU and the
  2 m gate disagree about a pair, per-frame matches — and therefore MOTA —
  can differ between the implementations.
- *IDF1 pairing*. TrackEval pairs identities over pairs that clear the IoU
  threshold; ours pairs over co-occurrence within the 2.0 m matching gate.
  Same boundary: the fixed sequences sit inside both thresholds.
- *Denominator*. Both MOTA implementations divide by the total number of
  ground-truth detections in the evaluated frames; frames are identical
  inputs, so this agrees by construction.

**Not cross-checked against TrackEval** (hand-computed tests only):
`gospa_p1`, `gospa_p2`, `nees_*`, `anees_*`, `nis_*`/`anis`, coverage,
`track_fragmentation`, `class_accuracy`, the `_distance_only` variants,
duplicate-track sensitivity metrics, and all aggregates. TrackEval does not
implement them in the form used here.

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
