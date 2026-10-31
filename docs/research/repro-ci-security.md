# Verification: reproducibility, artifacts, CI and security (issue #41)


Source-level verification at `d3e88d9` (main). No source or workflow was modified.
Environment: Linux aarch64, Python 3.12.13, numpy 2.5.4 (scipy-openblas), uv.
Severity P0 (worst) – P3. Type: **D** confirmed defect, **H** hypothesis, **U** unimplemented feature.

## Check results (actually executed)

| Check | Command | Result |
|---|---|---|
| Locked install | `uv sync --locked --all-extras`; `uv lock --check` | OK (77 resolved, lock current) |
| Lint | `ruff check src tests` (+ `scripts`) | pass |
| Format | `ruff format --check .` | pass (138 files) |
| mypy | `mypy src` | pass (21 files) |
| Full suite | `uv run pytest -q` | **222 passed**, 82 s |
| Provenance | `scripts/check_artifact_provenance.py` | **pass** ("artifact from e433b8411bf2, source unchanged") |
| Golden | `scripts/check_benchmark_golden.py` | **FAIL, exit 1** — `per_seed.csv differs from golden copy` (see F1) |
| Full benchmark regen | `mosaic benchmark --scenario all --seeds 0-24 --duration 10.0` | 13 m 22 s, rc 0; compared in F1/F2 |
| GitHub CI | `gh run list` | last 6 runs on main/PR all success (x86 runners) |

## Findings

### F1 — Golden check is byte-exact on floats and fails on aarch64 (D, P2, confidence high)
- `scripts/check_benchmark_golden.py:68` compares bytes after normalising only 40-hex hashes (`:46`, `:48-50`).
  `docs/evaluation-protocol.md:93-100` claims "byte for byte"; `docs/limitations.md:179-181` says
  results are *not* guaranteed byte-identical across platforms.
- Reproduction: `uv run python scripts/check_benchmark_golden.py` → `FAIL per_seed.csv`, rc 1.
  Two local runs are byte-identical to each other (deterministic on one machine). `benchmark.json` and
  `report.md` pass (rounded values); `per_seed.csv` differs in 117 cells in the golden, all in
  last 1–3 digits (e.g. `position_rmse` 0.34844266454764317 vs golden 0.34844266454764494).
- Observed: gate is platform-fragile (CI x86 passes; arm64/other BLAS fails). Expected: tolerance-based
  numeric comparison, or a documented single supported platform. The tool correctly detects
  nondeterminism *within* a platform; it does not distinguish "bug" from "different libm/BLAS".
- Same effect on the full artifact: regenerated `per_seed.csv` differs from committed in 11 811 cells,
  max relative difference 2.8e-12; no discrete metric (counts, switches) differs. So the numbers are
  scientifically reproduced, not byte-reproduced, across platforms.

### F2 — Committed `report.md` is stale relative to `benchmark.json`/`per_seed.csv` (D, P1, confidence high)
- `artifacts/benchmark/report.md` records commit `9bdeccdd…`; `benchmark.json` records `e433b841…`
  (`grep -o '[0-9a-f]\{40\}' artifacts/benchmark/*`). The three outputs of one run must share a commit.
  `e433b84` ("group-frozen bias correction…") changed `fused_bias_estimated` after `9bdeccd`.
- Reproduction: `crossing_targets / fused_bias_estimated` position RMSE. Committed `per_seed.csv`
  mean 0.1636 ± 0.0539 (my recomputation) = regenerated report (0.164 ± 0.054), but committed
  `report.md` says 0.166 ± 0.060 (also IDF1 0.792 vs 0.801, GOSPA 1.570 vs 1.576). Regenerated report
  differs from committed in 481 lines, rows of all three methods incl. `fused_bias_estimated`
  across scenarios.
- Impact: any number quoted from `report.md` or docs derived from it may not match the data.
  "Artifact claims match the generated report" is **not** true for the committed report.
- Why CI misses it: provenance reads only `benchmark.json` (`check_artifact_provenance.py:30,43`);
  golden check covers the small config, not `artifacts/benchmark/`.

### F3 — Provenance check validates one file only; cross-file consistency unchecked (D, P2, high)
- `check_artifact_provenance.py:30-43` never opens `report.md` or `per_seed.csv`. A check that all
  recorded hashes agree (and ideally regenerate-and-compare in a scheduled job) would have caught F2.
- Positive: recorded commit `e433b84` exists, is an ancestor of HEAD, `git diff e433b84 HEAD -- src`
  is empty, version `0.1.0` matches `pyproject.toml`. (`9bdeccd` also an ancestor, but `src/` differs
  from HEAD in 5 files — consistent with F2.)
- Note: `SOURCE_PATHS = ("src/",)` (`:28`) excludes `uv.lock`/`pyproject.toml`; dependency drift is only
  caught by the golden check, which is itself fragile (F1). Doc states this deliberately.

### F4 — Seeds and held-out separation (OK, with one caveat; confidence high)
- Artifact `protocol.seeds` = 0–24, `seed_group` = development, 16 scenarios × 3 methods,
  1200 data rows + header (1201 lines), 10 s, 3 objects — matches `docs/evaluation-protocol.md:23-26`
  and the Makefile `benchmark` target (`Makefile:34`). Reserved seeds 25–49 are not run.
- Caveat (U, P3): separation is by convention only; nothing in code/CI rejects a run over 25–49, or
  records that the held-out range has been consumed. Docs say so (`evaluation-protocol.md:27-35`).

### F5 — Determinism (OK, confidence high)
- `tests/integration/test_pipeline.py:88-113` runs `evaluate` twice and asserts byte-equality of all
  three outputs (short config, in-process). I reproduced same-platform identity for the golden config
  (two runs `cmp`-identical). No wall-clock fields in artifacts. Limitation: no test of cross-process
  or cross-platform determinism (see F1).

### F6 — Dependency pinning (mostly OK; P3)
- `uv.lock` is current and used with `--locked` in CI and `make install`; lock has 1 398 sha256 hashes.
  TrackEval is pinned by git rev (`pyproject.toml:69`).
- `pyproject.toml:22-31` use only `>=` lower bounds, so `pip install` consumers are unpinned; only
  `uv` users get reproducibility. `requires-python = ">=3.12"` but CI tests only 3.12.
  The artifact records package version and commit but not dependency versions (numpy/scipy), which F1
  shows can matter at the 1e-12 level (D, P3).

### F7 — CI enforcement vs status document (mostly OK)
- Verified in `.github/workflows/ci.yml`: lint/format/mypy/pytest/smoke tests (`test` job),
  `secret-scan`, `artifact-checks` run on push and PR to main; recent runs green.
- Gaps (D, P3): CI lints `src tests` but not `scripts/` (`ci.yml:30`, `Makefile:11`; `ruff format --check .`
  does cover it; I ran `ruff check scripts`: passes). mypy covers `src` only (documented in limitations).
  `docs/implementation-status.md:150-155` "Implemented" is accurate for what runs, but the
  golden/provenance bullets overstate (F1–F3).

### F8 — Workflow permissions and action pinning (OK, confidence high)
- Top-level `permissions: contents: read` (`ci.yml:9-10`); jobs do not widen. No `pull_request_target`,
  no secrets referenced, no write tokens.
- Both actions pinned to SHAs; I verified via `gh api` that `11d5960a…` = `actions/checkout` v4.4.0
  and `d4b2f3b6…` = `astral-sh/setup-uv` v5.4.2, matching the comments. Gitleaks pinned by version
  with SHA-256 checked against the release checksums file — but the checksums file comes from the same
  release URL, so it protects against corruption, not a compromised release (H, P3).
- `uv python install` and `uv` itself (setup-uv installs latest uv unless `version:` is set) are not
  pinned (H, P3).

### F9 — Secret scan gating (partially unverifiable)
- Scan scope is right: `fetch-depth: 0` + `gitleaks git .` (`ci.yml:80-92`), exits non-zero on findings.
  Recorded result on issue #29: 46 commits, no leaks.
- Independent check I ran: `git log --all -G'<AKIA|ghp_|sk-|BEGIN PRIVATE KEY|xox[bp]->'` over history
  (excluding lock files): 0 matches; no tracked `.env/.pem/.key`. gitleaks itself is not installed here and
  I did not run it (no network install attempted).
- Gating: the job fails the workflow run, but nothing makes it *required*: `gh api …/branches/main/protection`
  returned 403 (token lacks admin), so **whether branch protection requires `secret-scan`,
  `artifact-checks` and `test` could not be verified** (H, P2). No `.gitleaks.toml`/allowlist exists, so
  there is no suppression risk. Scan is not run on a schedule, so a newly added rule/secret type is only
  caught on the next push.

### F10 — Dependency-vulnerability monitoring (U, P2)
- Today: none. `.github/` contains only `workflows/ci.yml`; no Dependabot/Renovate config, no `pip-audit`,
  no `uv audit`/OSV step, no scheduled workflow. The lockfile pins ~76 packages (incl. streamlit,
  pandas, plotly), so patches only arrive manually.
- Recommendation (not implemented): (1) Dependabot `uv` ecosystem (or Renovate, which handles the
  git-rev TrackEval pin better) plus `github-actions` ecosystem to bump SHA pins — weekly, grouped;
  (2) a scheduled + PR `pip-audit` (or `osv-scanner`) job against the exported lock
  (`uv export --locked | pip-audit -r /dev/stdin`), read-only permissions, advisory on schedule and
  failing on PR for high severity; (3) enable GitHub secret scanning/push protection and Dependabot
  alerts in repo settings. Because bumps change floats at the ULP level, pair Dependabot with the
  tolerant golden check (F1) or each bump will fail CI spuriously on some platforms.

## Could not verify
- Branch-protection / required status checks (403 on API).
- gitleaks run locally (not installed; relied on issue #29 record + my regex sweep).
- CI behaviour on x86 beyond the run history (no local x86 machine); F1 attribution to BLAS/libm is a hypothesis consistent with 1e-12 relative drift, not proven.
- Whether the committed artifact was ever byte-reproducible on its generating platform.

## Suggested follow-ups
1. Regenerate `artifacts/benchmark/*` in one run (fixes F2) and re-run provenance.
2. Extend provenance to require all three files record the same commit.
3. Make the golden comparison tolerance-based for floats (or document x86-only), keep exact for counts.
4. Add Dependabot + pip-audit (F10); confirm required status checks in repo settings.
