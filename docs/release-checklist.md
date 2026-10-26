# Release Checklist (v0.1.0, historical)

> **Status: historical and superseded.**
>
> For current state see [implementation-status.md](implementation-status.md).
>
> This checklist describes the published v0.1.0 release at `ae518f7`. It is
> retained for context only and is **not** a current release checklist. The
> v0.1.0 implementation contained the core defects documented in
> [core-validity-audit.md](core-validity-audit.md); its benchmark numbers are
> invalid and have been replaced. The current branch has not been released and
> must not be pushed or tagged as part of the repair review.
>
> For current verification, see the commands recorded in
> [core-validity-audit.md](core-validity-audit.md) and run the CI workflow
> locally (`uv sync --locked --all-extras`, `uv run ruff check src tests`,
> `uv run ruff format --check src tests`, `uv run pytest`).

## Verified locally
- [x] Tests pass (14/14)
- [x] CLI smoke test (run, compare)
- [x] Benchmark command generates artifacts (JSON/CSV/Markdown)
- [x] Benchmark outputs are consistent and reproducible (same seed)
- [x] Documentation added (walkthrough, FAQ, design decisions, demo script)
- [x] README updated with benchmark instructions
- [x] LICENSE present (MIT)

## Verified by inspection
- [x] Core functionality implemented as documented
- [x] Limitations clearly stated (synthetic only, vision-only initiation restricted, timing limitations)
- [x] No secrets in tracked files
- [x] Dependencies declared in pyproject.toml

## Not verified
- [ ] Clean install in isolated environment (network-dependent)
- [ ] Streamlit full UI test in browser
- [ ] CI pipeline execution
- [ ] Multi-OS testing

## Known limitations (for v0.1)
- Synthetic 2D environment only
- Simplified sensor models (no raw images/waveforms)
- Vision-only track initiation not implemented
- Limited out-of-sequence timing support
- Gated nearest-neighbor association only
- No hardware/field validation

## Publication steps (manual)
1. Review final diff
2. Create commit with appropriate message
3. Push to GitHub (Telschow/mosaic-perception)
4. Create release tag v0.1.0
5. Verify repository is public
