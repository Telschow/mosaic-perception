# Review standards

Judgement calls only. Anything a tool can check lives in the tool: `make check` (format, lint, types, tests, provenance, golden benchmark) and `tests/unit/test_repo_guardrails.py`.

## Evidence

- Held-out seeds 25-49 are never run, read for tuning, or regenerated. `artifacts/held-out/` is frozen (see its `FROZEN` and `HELD_OUT.md`).
- A public number comes from a generated artifact, never typed by hand. A claim states what it rests on: this tracker, these scenarios, these seeds.
- Say what a result does not show. Overclaims (real-world accuracy, "fusion is worse in general") fail review.

## Public assets

- Every public image, clip or caption carries the synthetic-world label and the source commit.
- Commit regenerated assets only when a manifest changes (see `docs/demos.md`).

## Code

- Reuse the shared helpers (`scripts/_draw.py`, `scripts/make_assets.py`, `evaluation/statistics.py`). A second copy of a helper fails review.
- A behaviour change has a test at a public seam. The test does not recompute the expected value the way the code does.
- A change to `src/` that alters numbers regenerates the artifacts in the same PR.

## Writing

- Plain words, short sentences, no em dashes.
