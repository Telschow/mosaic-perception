# Demonstration experiences

Specification for the three demonstrations (issue #47). This file specifies them; it does not contain the media. Media is produced later from `artifacts/benchmark/` by the asset pipeline (#43) and linked from the documentation site (#34). The existing live walkthrough in [demo-script.md](demo-script.md) is the basis for the five-minute demo.

Prototype: `make assets` writes `docs-site/src/assets/generated/position_rmse_paired.svg` from `artifacts/benchmark/` (`scripts/make_assets.py`); it refuses a stale artifact and a test checks the figure against the artifact.

Beats 1 and 2 of demo 1: `make assets` also writes `docs-site/src/assets/generated/scenario_clip.gif` (nominal scenario, seed 1, one target; `scripts/make_clips.py`) with a manifest of the plotted data, `scenario_clip.json`, checked by `tests/unit/test_make_clips.py`.

Beats 3 and 4 of demo 1: `make assets` also writes `scoreboard.svg` (precision and MOTA paired tallies, counted by the report's own rule) and `bias_recovery.svg` (how much of fusion's loss `fused_bias_estimated` recovers, in the scenario `make_assets.py` picks by rule: the largest paired precision gain whose 95% interval excludes zero) to the same folder, checked by `tests/unit/test_make_assets.py` against the artifact and the report's Findings.

The finished clip: `make assets` also assembles `summary_clip.gif` (under 60 s, all five beats, GIF only because ffmpeg is not a documented dependency) from the pieces above with `scripts/make_summary_clip.py`, plus `summary_clip.json`, a manifest of the beat order, source files and timings, checked by `tests/unit/test_make_summary_clip.py`. Regenerate it with `make assets` (or `uv run python scripts/make_summary_clip.py` alone). It lives at [docs-site/src/assets/generated/summary_clip.gif](../docs-site/src/assets/generated/summary_clip.gif) and is embedded, with alt text for each beat, on the landing page of the documentation site.

Hook video (issue #118): `make video` renders a 43 s 4:5 cut (`scripts/make_video.py`, Manim run through `uv run --with manim`; macOS also needs `brew install cairo pango ffmpeg`). One idea for a non-expert: a plain question, then one real object followed by one sensor and then with a camera added (the lines are the tracker's real tracks from one development run; the extra lines are ghosts), then two 100-dot pictograms of the share of reported tracks that were the real object (the artifact's scenario means), then a one-sentence close. Captions are held long enough to read, no confidence intervals or statistics appear, and the framing is "in this simulation". `hook_video.json` records the plan; `make assets` rewrites it without Manim.

Feed and README formats (issue #98). `make assets` also writes `hero_recovers.png` and `hero_hurts.png` (`scripts/make_hero.py`): three panels of one drawn run on the first development seed, range-only, fused and bias-estimated, with ground truth dashed, a 95% position ring, the label "SYNTHETIC WORLD" and the source commit. Their scenarios come from a rule on `benchmark.json` (`hurts`: the largest paired precision loss of fused against range-only whose interval excludes zero; `recovers`: the scenario of beat 4), the printed numbers are the paired benchmark values (not read off the drawn run), and `hero.json` records both. `hero_recovers.png` is the README hero. `make assets` also writes `alt_text.json` (`scripts/make_alt_text.py`), one alt text per image built from the manifests; the README and the landing page embed it, and `tests/unit/test_alt_text.py` checks that.

`make mp4` renders `summary_clip_9x16.mp4` (1080x1920) and `summary_clip_16x9.mp4` (1920x1080), H.264, about 32 s, with burned-in captions of at least 48 px (readable at 360 px wide), `summary_clip.srt`, a poster frame and `summary_clip_mp4.json` (plan, cue timings, source commit). It needs `ffmpeg` on the PATH and says so, rendering nothing, when it is missing (`brew install ffmpeg`). ffmpeg stays optional: CI does not render video, and the tests check the plan and the ffmpeg command, not encoded bytes. The scoreboard and recovery beats print their figures at 48 px, computed from the artifact.

Maintainer settings (an agent cannot change these): repository description "Does adding a sensor help tracking? A synthetic-world benchmark where it often doesn't.", homepage `https://telschow.github.io/mosaic-perception/`, and a social preview image (Settings, General, Social preview; the poster frame or `hero_recovers.png` cropped to 1280x640 works).

## Headline

> **More sensors don't automatically mean better tracking.**
> *I added a camera to a tracker and, in a simulated world, it mostly got worse. Here is why, and when it helps.*

The headline claims only what [artifacts/benchmark/report.md](../artifacts/benchmark/report.md) shows, and only for the synthetic scenarios and settings tested. Do not put numbers in the headline; point to the report.

## Rules for every demo

- "Synthetic world" is on screen the whole time.
- Every figure shown is traceable to `artifacts/benchmark/report.md` or to a command printed on screen. No hand-copied numbers.
- Never claim real-world accuracy, that fusion is better or worse in general, or anything about the held-out run beyond "consistent with development, inconclusive" (see [../artifacts/held-out/HELD_OUT.md](../artifacts/held-out/HELD_OUT.md)).
- State the limits in [limitations.md](limitations.md) rather than hide them.

## 1. Sixty-second summary

| | |
|---|---|
| Audience | Non-experts: collaborators and a general technical audience |
| The one question | Does adding a second sensor make tracking better? |
| Medium | Recorded clip (GIF or short video), captions on screen, no voice needed |
| Limitation shown | The surprise: the fused tracker scores worse on most measures, and there is one scenario where it helps |

Beats:

1. A moving target seen by the range sensor alone, with its track.
2. A camera is added and the track looks better.
3. The scoreboard shows the fused version is worse on precision and MOTA.
4. Where it helps: `sensor_disagreement_within_gate_high`, a vision sensor with a 0.020 rad bearing bias small enough to pass the association gate. The bias-estimated method recovers part of the loss (precision +0.131, 95% interval [0.100, 0.162]; MOTA +0.359, [0.281, 0.436]). In `measurement_bias`, where the bias is on the range sensor, it recovers nothing.
5. End card: "Synthetic world. Full results and limits: link."

Commands and artifacts: `uv run mosaic compare --scenario nominal --seeds 1,2,3,4,5`; `artifacts/benchmark/report.md`.
Must not claim: that fusion is bad in general, or any real-world accuracy.
Acceptance: under 60 s; every on-screen number appears in the report; the synthetic label is visible in every frame; reproducible from the commands above.

## 2. Five-minute technical deep dive

| | |
|---|---|
| Audience | Engineers and technically literate reviewers |
| The one question | How do you evaluate a tracker honestly? |
| Medium | Live Streamlit session with a script, plus a recorded run-through |
| Limitation shown | Paired-interval tally across the scenarios; the matcher choice changes the identity-switch count |

Beats follow [demo-script.md](demo-script.md): one scenario, the multi-seed evidence, the paired 95% intervals, the continuity-first versus distance-only matcher, then the limitations.
Commands: `uv run mosaic run --scenario nominal --seed 1`; `uv run streamlit run app/streamlit_app.py`; `uv run mosaic benchmark --scenario all --seeds 0-24 --duration 10.0`.
Must not claim: significance beyond the stated intervals, or that the 25 development seeds are held-out.
Acceptance: runs from a clean checkout in five minutes; every command in the script exists and succeeds; the limitations screen is shown.

## 3. Expert review

| | |
|---|---|
| Audience | Researchers and reviewers who will try to break it |
| The one question | Can I trust these numbers and reproduce them? |
| Medium | Annotated written walkthrough (document or recorded screen capture with captions) |
| Limitation shown | The held-out discipline, provenance checks and the known limitations |

Contents:

- The metrics cross-checked against TrackEval (`tests/crosscheck/`, [metrics.md](metrics.md)) and which are not.
- Provenance and reproducibility: `make provenance-check`, `make benchmark-golden-check`, and how the golden check tolerates float drift.
- The held-out run: frozen code, tag `held-out-freeze`, seeds 25-49, run once, never rerun.
- The audit: [audits/mosaic-perception-comprehensive-audit.md](audits/mosaic-perception-comprehensive-audit.md) and what was fixed or left documented.
- [limitations.md](limitations.md), including the open sensor-model edge cases left documented on purpose.

Must not claim: that the held-out result confirms the method, or any result outside the synthetic world.
Acceptance: every claim links to a file, command or test; a reader can run the two checks above and get a pass.

## Media and deliverable locations

Media lives under `docs-site/` assets (path decided in #48/#43), is generated by the asset pipeline from `artifacts/benchmark/` and documented seeds, and is checked in CI for drift. Hand-edited numbers are not allowed in any asset. Regenerating on macOS rewrites image bytes that differ from the Linux versions CI compares, so commit asset changes only when a manifest (`*.json`) changes.
