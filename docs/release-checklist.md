# Release Checklist (v0.1.0)

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
