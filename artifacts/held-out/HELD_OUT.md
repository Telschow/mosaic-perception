# Held-out evaluation (issue #7)

This directory is the single held-out run of the reserved seeds 25-49.

- Code: commit `8baa778e86826ddbdcb4b27ef07d7ca9b993e354`, tagged `held-out-freeze`.
  The code was merged and frozen before the run; no code or scenario change followed it.
- Command: `mosaic benchmark --scenario all --seeds 25-49 --duration 10.0 --output artifacts/held-out`
- Seeds: 25-49 (25 seeds). The development benchmark in `artifacts/benchmark/` uses seeds 0-24.
- The run was not repeated after the results were seen.
- `report.md` marks its seed group `custom_or_held_out` because the generator does not
  distinguish the two; this note is the label that it is the held-out run.
- Claims are limited to the synthetic world, scenarios and sensor models in this repository.
  Nothing here says anything about real sensors or real scenes.
