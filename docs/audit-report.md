# Mosaic Audit Report

**Date:** 2026-10-24  
**Auditor:** AI Assistant  
**Repository:** /Users/daniel/Development/mosaic-perception  
**Commit:** 6782de4 (Initial implementation)  
**Branch:** main  

## Summary

This audit reviewed the Mosaic perception workbench implementation for mathematical correctness, experimental validity, reproducibility, and code quality. The project has a solid foundation with a working vertical slice, but there are several areas that need attention.

## Baseline Check Results

### Tests
```bash
PYTHONPATH=src python3 -m pytest -v
```
**Result:** 7 passed, 5 warnings in 0.71s  
All tests pass.

### Linting (ruff)
```bash
PYTHONPATH=src ruff check src tests
```
**Result:** 261 errors found (198 fixable)  
Mostly style issues (unused imports, formatting, missing strict in zip, etc.) - not critical bugs.

### CLI Smoke Test
```bash
PYTHONPATH=src python3 -c "from mosaic_perception.cli.main import app; app(['run', '--scenario', 'nominal', '--seed', '42', '--duration', '5.0'])"
```
**Result:** Works correctly, produces reasonable output  
Range-only RMSE: ~0.705m, Fused RMSE: ~0.849m (varies by run)

### Multi-seed Comparison
```bash
PYTHONPATH=src python3 -c "from mosaic_perception.cli.main import app; app(['compare', '--scenario', 'nominal', '--seeds', '1,2,3', '--duration', '5.0'])"
```
**Result:** Works, shows fusion can help or hurt depending on scenario/seed

## Findings

### P0 - Critical
None identified. No ground-truth leakage found in normal estimator paths. Comparisons appear fair.

### P1 - High
1. **Observer position not passed to tracker** (tracker.py, cli/main.py) - Tracker defaults to sensor at origin [0,0], but sensors compute observations using observer position from world. With moving observer this would be wrong. Currently observer is static in tests.
2. **EKF.update() method is broken** - Uses `h_from_H()` which returns zeros. Not used by tracker (tracker does manual updates), but it's dead/broken code.
3. **Miss counting logic is convoluted** - Increments misses for all tracks every frame then resets on update. Works but confusing and error-prone.
4. **Vision-only track initiation disabled** - Correctly noted in comments (can't determine range from bearing alone), but this is a significant limitation.

### P2 - Medium
1. **Pydantic v2 deprecation warnings** - Using old-style `class Config:` instead of `ConfigDict`
2. **No angle wrapping in some places** - Bearing differences need careful wrapping; mostly handled but could be improved
3. **Covariance not forced symmetric in all paths** - Tracker does it, but better to be consistent
4. **Process noise is diagonal and simple** - May not be optimal but reasonable for v0.1
5. **No numerical stability checks** (matrix inversion failures caught but not logged)

### P3 - Low
1. Many linting/style issues
2. Some unused imports
3. Documentation could be more detailed
4. No integration tests for full pipeline
5. Streamlit app has some issues with state management

## Recommendations

### Immediate Fixes
1. Pass observer position from world to tracker
2. Clean up or fix EKF.update() method
3. Fix the README to not claim "evaluation report" command exists if not implemented
4. Add better error handling and logging
5. Improve test coverage for edge cases

### Future Improvements
1. Implement proper out-of-sequence handling or document limitation clearly
2. Add oracle association diagnostic for debugging
3. Improve uncertainty calibration metrics
4. Add more scenarios (all 8 mentioned in brief)
5. Better visualization of uncertainty ellipses

## Conclusion

The implementation is **technically promising but needs further hardening** before public presentation. The core functionality works and demonstrates the key concept well. The main issues are around observer position handling and some code quality issues. With targeted fixes, this could become a solid v0.1.


## Follow-up Hardening Report (2026-10-25)

### Fixed
- **Observer pose contract**: Tracker now accepts observer/sensor pose via `sensor_pos` or `observation.observer_pose` (propagated from sensors). Sensors attach observer pose context. Moving-observer scenarios tested.
- **Canonical EKF update**: `ExtendedKalmanFilter.update()` implemented with `h_pred` required, uses Joseph-form covariance update and linear solve where possible. Angular residuals wrapped. Tracker uses canonical path.
- **Track miss counting**: Misses incremented once per epoch for tracks not updated (after prediction/association/updates). Multiple updates in same epoch reset misses once.
- **Vision-only initiation**: Explicitly disabled; documented. Vision can update existing tracks in fused mode.
- **Pydantic v2**: Migrated to `ConfigDict` (warnings reduced/eliminated for these models).
- **Integration/regression tests**: Added EKF tests, observer-pose tests, full-pipeline integration tests (nominal deterministic, repeatability). Total tests: 14 passing.

### Verified
- Tests: 14 passed
- CLI nominal and compare work
- Reproducibility verified on same seed
- Moving observer path exercised

### Remaining
- Ruff has remaining style issues (51 errors) - many are in tests/legacy style; core logic is cleaned. Further cleanup possible but not blocking correctness.
- Streamlit state management could be hardened further.
- Some scenarios from brief not fully implemented.
