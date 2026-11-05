# Held-out evaluation (issue #7)

This directory is the single held-out run of the reserved seeds 25-49.

> Frozen historical result at `8baa778`. It predates later tracker and metric changes (for example the age-of-information definition), so it is not a result for the current code, not directly comparable to the development benchmark, and not a generalization claim.

- Code: commit `8baa778e86826ddbdcb4b27ef07d7ca9b993e354`, tagged `held-out-freeze`.
  The code was merged and frozen before the run. No change was made in response to the results.
- Command: `mosaic benchmark --scenario all --seeds 25-49 --duration 10.0 --output artifacts/held-out`
- Seeds: 25-49 (25 seeds). The development benchmark in `artifacts/benchmark/` uses seeds 0-24.
- The run was not repeated after the results were seen.
- `report.md` marks its seed group `custom_or_held_out` because the generator does not
  distinguish the two; this note is the label that it is the held-out run.
- Claims are limited to the synthetic world, scenarios and sensor models in this repository.
  Nothing here says anything about real sensors or real scenes.
- `FROZEN` declares the commit above. `scripts/check_artifact_provenance.py` accepts a
  frozen directory, prints the `src/` delta since the commit instead of failing on it, and
  fails if `report.md` and `benchmark.json` disagree about the commit.
- `per_seed.csv` is not kept (it is git-ignored). Regenerating it would mean rerunning
  seeds 25-49, which is not done.

## Later `src/` changes

`src/` has changed since `8baa778` (`git log --oneline 8baa778..HEAD -- src`). The numbers
here are as run at `8baa778` and are not regenerated. Commits that change reported fields
or the artifact:

- `2dcf237` redefines age of information as delivery latency. `delivery_delay`
  `mean_age_of_information` for seed 25 is 0.0996 here and 0.0508 at HEAD; RMSE is identical.
- `f108893` changes tracker time handling (repeated call time, latency rule, delayed
  initiation; #95).
- `1bcde4b` rejects non-PSD covariance and makes evaluator skips visible.
- `b286320` repairs the Findings text and states the counting rules in the report.
- `e5100a7` records numpy and scipy versions in artifact metadata.
