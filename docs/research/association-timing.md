# Association, timing and track lifecycle: source-level verification (issue #39)

Branch `research/association-timing`, based on `main` at d3e88d9. No source changes.
Line numbers refer to that commit.

## Method and environment

Read `tracking/association.py`, `tracking/tracker.py`, `domain/models.py`, the four named
test files and the three named docs. Ran repro scripts against the tracker. The script was
kept outside the repo (`/tmp/repro/r.py`) and run with
`PYTHONPATH=.:src python r.py` in a scratch venv (numpy, scipy, pydantic, pytest).
The four test files pass (60 passed). The full suite was not run.

## Verified as documented

| Check | Evidence |
|---|---|
| Per-group gates by measurement dimension, no dimension-less fallback | `association.py:51-71`, `:170-173`; test `test_gate_lookup_has_no_dimensionless_fallback` |
| Hungarian one-to-one inside a group, `1e12` filler maximises finite pairs first | `association.py:223-232` |
| Range first, then vision, vision gated against the post-range posterior | `tracker.py:34`, `:205-231` (tracks are mutated in place before the vision `associate()` call) |
| No cross-group competition | groups associated in separate `associate()` calls (`tracker.py:211`) |
| Range-only ignores vision entirely | `tracker.py:423-428` drops it before queueing. Repro G: no counters move (see F6) |
| Vision cannot initiate | initiation only in `group == "range_bearing"` (`tracker.py:243-248`), and `_initiate_track` re-checks `range` (`:599`). Repro I: 0 tracks, `vision_unassigned_other == 1` |
| Pending queue ordering | `_take_due` sorts `(delivery, capture, id)` (`tracker.py:445-451`); `associate` re-sorts identically (`association.py:135-138`) |
| One-epoch staleness | `age > dt + 1e-6 + 1e-9` rejected, counted, logged (`tracker.py:183-193`) |
| Retrodiction opt-in | default `"delivery_time"` (`tracker.py:81`); replay only if `retrodiction` and the observation is delayed and a stored posterior exists (`:548`) |
| Retrodiction gates against delivery-time state | `associate()` reads `track.state_array()` after prediction (`association.py:178`) |
| Lifecycle thresholds | Repro F: confirmed at 3 hits, coasting at 2 misses, deleted at 5 misses |
| Identity isolation | `rg "true_"` over `src/mosaic_perception/tracking/` finds only comments. `_true_object_id` is written in `sensors/range_bearing.py:150` and `vision_bearing.py:136` and cleared in `experiment.py:159`. Nothing in `tracking/` reads it |

## Findings

### F1. Retrodiction loses earlier updates when a second call uses the same `current_time` (P2, confirmed defect)

- `tracker.py:161` resets `_epoch_applied` at every call. `:396` returns early from `_advance_time` for a repeated time, so `_prev_posterior` still holds the posterior from before the first call at that time.
- `_replay_epoch` (`:581-595`) restarts from that stored posterior and replays only the current call's observations. The updates applied in the earlier same-time call are discarded.
- Repro A2: confirmed track, `r0` at t=0, `r1` on time at t=0.1, then a second call at t=0.1 delivering a delayed vision observation captured at t=0.
  - `delivery_time` mode: trace(P) 0.7906 to 0.6634 (a measurement update reduces it).
  - `retrodiction` mode: trace(P) 0.7906 to 1.227 (it grows, because `r1` has been dropped).
  - `track.associated_observations` still lists `r1`, so the bookkeeping disagrees with the state.
- Expected: the replay includes every observation applied this epoch, or a repeated time is rejected or merged.
- Confidence: high on the mechanism and the repro. Not verified: whether the experiment runner ever calls twice at one time (`tracker.py:155` documents "non-decreasing"); I did not read the runner.

### F2. A repeated `current_time` runs a full extra epoch (P3, confirmed)

- `:250-252` run `_finish_epoch`, `epoch += 1` and snapshot emission even when no time elapsed.
- Repro A: a track updated at t=0 then called again at t=0 with no observations goes from `misses 0, age 1, epoch 1` to `misses 1, age 2, epoch 2`, with a duplicate snapshot.
- Expected: one miss per elapsed epoch, or an error for a repeated time.
- This is the same root cause as F1.

### F3. Staleness and age of information are measured at tick processing time, not at delivery time (P3, confirmed; docs mismatch)

- `:183` uses `age = now - capture_time` and `:202` stores it in `_delivered_ages`. `docs/measurement-models.md:121` says the reported age is "the time between capture and delivery".
- Repro: capture 0.0, delivery 0.01, processed at 0.1 gives `mean_age_of_information == 0.1`, not 0.01.
- Repro B: capture 0.99, delivery 1.01 (latency 0.02), processed at 1.1, so age 0.11, which is rejected as stale.
- Consequence: the one-epoch rule is a function of tick phase, so a low-latency observation can be rejected. The docs do say "delivery epoch", but the age statistic is mislabelled relative to `SensorObservation.age_of_information()`.
- Expected: document it, or compute the statistic from `delivery_time`.

### F4. An unknown class name in `class_probs` raises out of `process_observations` (P2, confirmed)

- `ObjectClass(best_class)` at `tracker.py:656` and `:692` is not guarded. In `process_observations` the vision path calls it at `:230`, after the state update has been applied.
- Repro C: `class_probs={"bogus": 1.0}` raises `ValueError: 'bogus' is not a valid ObjectClass`. The batch is aborted, and `_finish_epoch` is skipped.
- On the vision path the track is left updated, with hit and miss accounting not run, and `_last_time` not advanced.
- Expected: reject the observation as invalid, as other malformed input is (`_reject_invalid`).
- Not verified: whether the shipped sensors can emit non-enum names. I did not check, so this is a robustness issue, not a known production failure.

### F5. A duplicate observation id mid-batch leaves the tracker half-advanced (P3, confirmed)

- `_advance_time` (`:162`) runs before `_enqueue` (`:163`). `_enqueue` raises on a duplicate id (`:429-430`) after earlier items in the batch were already queued.
- Repro H: tracks are predicted to t=0.1, `h1` stays pending, and `epoch` is unchanged. A retry with the same batch then fails on `h1`.
- Expected: validate the whole batch first, or document the failure as fatal.

### F6. Vision dropped in range-only mode is invisible in statistics (P3, confirmed, design choice)

- `:426-428` `continue` before any counter. Repro G: after a vision observation in range-only mode, `vision_delivered`, `rejected_observations` and `pending_observations` are all 0.
- This is intended isolation, but `vision_generated` (set by the runner) will exceed the sum of the delivered buckets with no bucket accounting for the difference. `vision_invalid_or_stale` is only computed from delivered counts. Not verified against the runner's reporting code.

### F7. Confirmation counts total hits, not consecutive or windowed hits (P3, design note)

- `:718`: `hits >= min_hits_confirm`. `misses` resets on a hit but `hits` never decays.
- Repro E: pattern hit, miss, hit, miss, hit confirms the track at epoch 5. A tentative track is deleted only after 5 consecutive misses.
- `TrackEstimate` documents `hits` as "epochs with at least one accepted measurement", so this matches the stated semantics. It is not an M-of-N rule, and `docs/architecture.md:65-67` does not say which one is used. Unimplemented feature, not a defect.

### F8. Duplicate tracks and false alarms follow from the documented same-group policy (P3, expected behaviour)

- Every unmatched range-bearing observation initiates a track (`:244-248`), including those that lost the one-to-one competition and gate-rejected ones. Repro D: two range observations of one target at one epoch create two tracks. The policy is stated in `association.py:12-16` and tested (`test_same_group_policy_assigns_one_observation_and_initiates_from_the_other`).
- A false alarm therefore creates a tentative track, deleted after 5 misses unless it collects 3 hits. There is no initiation gate, no minimum separation from existing tracks, and no track merging. `docs/limitations.md:33` and `:132-151` describe the duplicate-track consequence.

### F9. Tracks initiated from a delayed observation (P3, hypothesis)

- `_initiate_track` (`:597-677`) builds the state from the observation's capture-time geometry but stamps `time=now` and applies no prediction over the age. Repro J: a track initiated at t=0.1 from a t=0.0 observation reports `time=0.1` and the capture-time position.
- No stored posterior exists for it, so a delayed observation that follows silently takes the delivery-time path even in `retrodiction` mode. The age is bounded by one epoch, so the size is small, but it is undocumented. Magnitude in a real scenario not measured.

## Not verified

- Whether the sensors or the runner can trigger F1, F2 and F4. I did not read the runner or sensor code beyond the `_true_object_id` greps.
- That `class_probs` produced by the vision sensor do not derive from `true_class` in a way that leaks into track class. The tracker only reads `class_probs`; how the sensor makes them was outside scope.
- Behaviour with more than one skipped epoch under retrodiction (only the last prediction step is stored, `:407-413`). Reasoned from code, not run.
- No benchmark output, golden checks or the full test suite were run.

## Suggested follow-ups (not done, source is out of scope)

- Add regression tests for F1 and F4 once a decision is made.
- Decide whether a repeated time should raise, merge, or be a no-op (F1, F2).
- Change F3 either in the docs or in the statistic.
