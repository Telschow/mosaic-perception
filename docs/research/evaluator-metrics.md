# Evaluator, metrics and statistics: source-level verification (issue #40)

Source commit examined: `d3e88d9` (main). No source code was modified. Every
reproduction below was run in this checkout; probe scripts were throwaway and are
described inline rather than committed. TrackEval was the pinned commit
`12c8791b303e0a0b50f753af204249e622d0281a`, which equals `master` HEAD on the
upstream remote (checked with `git ls-remote`), and was importable here, so the
live cross-check test ran (5 passed, none skipped).

Severity: P0 wrong headline number, P1 likely wrong conclusion, P2 claim/behaviour
mismatch that can change a number, P3 robustness or wording. Status: CONFIRMED
defect, HYPOTHESIS, or UNIMPLEMENTED.

## Summary

The evaluator computes what `docs/metrics.md` says for every metric checked. The
denominators match the docs, undefined values are `None`, and no metric or
evaluator path reads a ground-truth-only field into the estimator. The material
finding is F1: the continuity matcher is documented as TrackEval's CLEAR matching
but ranks differently when a previous pairing conflicts with match count. The
rest are robustness gaps and wording issues.

## Verified as correct

| Check | How | Result |
|---|---|---|
| GOSPA (alpha=2, c=2.0, p=1,2) | Brute-force over all partial assignments (only pairs with d<c assignable), 200 random frames with 0-4 objects and tracks, compared with `metrics.py:241` | max abs difference 4.4e-16 |
| Paired 95% t interval | 25 random pairs vs `scipy.stats.ttest_1samp(...).confidence_interval(0.95)` against `statistics.py:24` | identical to 1e-15 |
| Report tallies | Recomputed from `artifacts/benchmark/per_seed.csv` with `paired_difference` (range_only vs fused, 16 scenarios, 1200 rows) | position_rmse 1 better/6 worse/8 incl; distance-only 7/3/5; MOTA 0/14; IDF1 2/5; GOSPA 0/14; precision 0/14; coverage 1/12. All equal the `## Findings` lines in `report.md` |
| MOTA/IDF1/IDP/IDR/CLEAR counts/IDSW vs TrackEval | `pytest tests/unit/test_trackeval_crosscheck.py` live | agree on the four fixed sequences |
| TrackEval pin validity | `pyproject.toml:69`, `uv.lock:1925`, `git ls-remote` | commit is upstream master HEAD |
| chi-square thresholds | `scipy.stats.chi2.ppf` | 5.9915 and 2.2789; docs `metrics.md:135` correct |
| Ground-truth isolation | `grep _true_object_id src`; `experiment.py:157-160` | set in `range_bearing.py:150`, `vision_bearing.py:136`, cleared at `experiment.py:159` before `tracker.process_observations`. `tracker.py` never reads `_true_object_id`, `true_class` or `WorldState`; it receives only observations and `world_state.time`. NIS (`metrics.py:526`) comes from tracker statistics, not ground truth. `vision_bias_configured` is set after evaluation (`experiment.py:176`), not fed back |
| Snapshot-based evaluation, 2.0 m gate, one-to-one, EVALUATED_STATUSES | `frames.py:19,52-140` | as documented. Cardinality is protected by the 1e9 out-of-gate sentinel |
| Denominators | `metrics.py:390-393` and `mota` | recall = matched/GT samples, precision = matched/evaluated-track samples, MOTA over GT samples, ANEES over `nees_samples`, class accuracy over known-both samples |
| Undefined handling | `metrics.py` | `None` for RMSE without matches, class accuracy without classified samples, switches/fragmentation without matches. `stale_rejection` MOTA/IDF1 = 0.000 and GOSPA 3.000 are genuine values (303 misses, 0 tracks, 3 objects * c/2), not fabricated zeros |

## Findings

### F1. Continuity matcher prioritises match count over continuity, unlike the TrackEval behaviour it cites. P2, CONFIRMED, high confidence

- Where: `frames.py:47-49` (comment: a still-valid previous pairing "always beats a closer alternative (as in TrackEval's CLEAR)"), `frames.py:60`, `metrics.py:338`, `docs/metrics.md:14-16`.
- Mechanism: `frames.py:114` replaces out-of-gate cells with 1e9 *after* the 1000 bonus, so the Hungarian solve maximises the number of in-gate pairs first and continuity second. TrackEval's CLEAR does the reverse: `1000 * prev_match + similarity`, zeroed below threshold, so it keeps a valid previous pairing even if that costs another object's match.
- Reproduction: two frames; frame 0: A-T1 at 0 m, B-T2 at 10 m. Frame 1: A at 0, B at 1.5, T1 at 0.5 (inside the gate of both), T2 at -1.8 (inside A's gate only). Built with the `tests/crosscheck` helpers and `BOX_SIZE=6` so the IoU 0.5 threshold coincides with 2.0 m on a line. Ours: `matched=4, fn=0, fp=0, idsw=2` (A and B both swap tracks). TrackEval (`run_trackeval`): `clr_tp=3, clr_fn=1, clr_fp=1, idsw=0`. MOTA happens to be 0.5 in both, but the counts and switches differ.
- Observed vs expected: docs and comments say "as TrackEval"; behaviour agrees only when no previous pairing conflicts with cardinality. The four fixed cross-check sequences never create such a frame, so the "Differences found: none" statement (`metrics.md:95`) holds only for those inputs.
- Impact: the headline `identity_switches` and `position_rmse` depend on this tie-break. How often it occurs in the benchmark was not measured (a hypothesis, not a finding). The report already shows the headline RMSE tally is matcher-dependent (1 better/6 worse vs 7/3 distance-only).
- Not covered by tests: `test_frame_metrics.py:300-330` has no case where continuity conflicts with cardinality.

### F2. `metrics.md` contradicts itself on matcher independence. P3, CONFIRMED, high

`docs/metrics.md:23-24` says matching is independent at each timestamp and continuity is not enforced by the matcher; `docs/metrics.md:14-19` and `frames.py:66,85` say the previous frame's pairing is an input to the next. The latter is the real behaviour.

### F3. Report prose has a garbled sentence. P3, CONFIRMED, high

`reporting/markdown.py:241-243` produces "both are descriptive synthetic results on / results; intervals reflect..." (`report.md` Findings, the `sensor_disagreement_within_gate` bullet). A word is missing after "on". Those two bullets are also static text, not derived from the numbers, so they would stay in the report even if the scenarios changed.

### F4. Findings tallies treat non-independent scenarios as independent and are uncorrected. P3, CONFIRMED (the facts), wording judgement

- `range_only` rows are bit-identical in six scenarios (`nominal`, `sensor_disagreement_large_bias`, `_within_gate`, `_within_gate_high`, `_within_gate_low`, `vision_dropout`; checked on `position_rmse` across all 25 seeds). A tally such as "worse in 14 scenario(s)" therefore counts the same baseline repeatedly, and no multiplicity correction is applied across 16 scenarios x 7 metrics of 95% intervals.
- `markdown._tally` (`markdown.py:21-41`) skips scenarios with `n == 0` (`stale_rejection`) in every count, so "8 scenario(s)" inconclusive sums with the others to 15 of 16 without saying so.
- The wording is hedged ("interval excludes zero", "seed-to-seed variation"), so none of the report's claims is false; they are descriptive counts.

### F5. Silent handling of mismatched snapshot times and duplicate IDs. P3, CONFIRMED, high; not triggered by the benchmark

- `frames.py:38-44,69-71`: snapshots are keyed by `round(time, 9)`; a snapshot whose time differs from every world-state time by more than 1e-9 is dropped without warning. Reproduction: one object, one track with `time=1e-6`: `recall=0.0, precision=None, confirmed_track_samples=0` but `num_confirmed_tracks=1`.
- `frames.py:43`: two snapshots with the same `(track_id, time)` overwrite each other. Reproduction: a track at (0,0) then another with the same ID at (50,0): `confirmed_track_samples=1, recall=0.0`.
- `experiment.py` always uses the world-state time, so the benchmark does not hit either path. A user-supplied snapshot list could.

### F6. Coverage/NEES sample selection. P3, CONFIRMED behaviour, HYPOTHESIS on relevance

- `metrics.py:96-102,292-303`: singular or non-finite covariances are skipped without a count of skips; `coverage_samples` and `nees_samples` are reported, so the shortfall against `matched_samples` is visible but not labelled.
- An indefinite (non-PSD) but invertible covariance is accepted: `diag(1,-1,1,1)` with error (1, 0.5) gives `coverage_samples=1, position_coverage_95=1.0, anees_position=0.75`. Whether the tracker can emit such matrices was not verified, so this is a hypothesis.
- `nees_sums` skips a sample if either the position or the velocity block is singular, so a valid position sample is lost when only velocity is degenerate (probe: velocity block zero gives `coverage_samples=1, nees_samples=0`). `coverage_samples` and `nees_samples` therefore need not match. `metrics.md` says "valid covariance" without this coupling.

### F7. Paired-difference interval with zero variance. P3, CONFIRMED behaviour, HYPOTHESIS on relevance

`statistics.py:48`: identical non-zero differences give a zero-width interval (`[1.0, 1.0]` in a probe), which `_tally` reads as "excludes zero". Exact constant differences are unlikely with real seeds; the benchmark's constant case (`stale_rejection`, all-zero differences) yields `[0, 0]`, which is classed as inconclusive. `test_identical_differences_give_a_degenerate_interval` pins the behaviour, so this is intentional but unflagged in the report.

### F8. The estimator receives the exact observer pose. P3, CONFIRMED, by design

`range_bearing.py:144-148` and `vision_bearing.py:129,163` copy `world_state.observer_pose` into each observation, noise-free. `docs/measurement-models.md:13-14` calls this platform metadata rather than object ground truth, and it is not object ground truth, but it is the simulator's true state, and `WorldState`'s docstring (`models.py:98`) says the world state "must never leak into estimator inputs". Perfect ego-pose knowledge is a modelling assumption that I could not find stated in `docs/limitations.md`. This is relevant to what the results can transfer to, not a bug in the evaluator.

## TrackEval cross-check: what is and is not compared

Compared (fixed sequences, `tests/crosscheck/sequences.py`, 6 frames, static objects, unit boxes): `mota`, `clr_tp/fn/fp`, `idsw`, `idf1`, `idp`, `idr`. Fixture `trackeval_reference.json` records repository, commit and version, and the live test re-runs TrackEval when it is importable.

Limits:
- The four sequences are clean (offsets <= 0.2 m, objects >= 10 m apart), so the matchers cannot disagree. They do not exercise contested frames, continuity versus cardinality (F1), crossing or moving objects, gaps within an object's trajectory, ties, or a gate/IoU disagreement. The docs say the last of these is deliberately avoided (`metrics.md:97-107`).
- The boxes are synthetic: TrackEval is fed 1 m boxes built from our points, so it cross-checks formulas on identical associations, not the 2.0 m gate.
- The fixture was regenerated on a 1.0.dev1 install; only the commit is pinned, not the numpy shim, which `trackeval_harness.py:30-45` patches at run time.
- Not cross-checked (as `metrics.md:109-113` already says): GOSPA, NEES/ANEES, NIS/ANIS, coverage, fragmentation, class accuracy, the distance-only variants, duplicate-track metrics, pooled aggregates. GOSPA was verified here against brute force (above). The others are verified only by hand-computed unit tests and by my reading of the source.
- UNIMPLEMENTED: HOTA, MT/ML/PT, OSPA(T) and any held-out-seed results; none are claimed.

## What I could not verify

- How often the F1 conflict occurs in the benchmark: this would need instrumenting `match_frame` or re-running the benchmark with a TrackEval-style matcher, which is source modification or a larger experiment than this ticket.
- Whether the tracker can emit non-PSD covariances (F6).
- Whether the `artifacts/benchmark/` numbers reproduce from the code; the full benchmark and `make provenance-check` were not run (out of scope and slow). I only re-derived the paired statistics and tallies from the committed `per_seed.csv`.
- NIS and ANIS correctness: they come from `tracking/tracker.py` filter internals, which belong to the tracker tickets.
