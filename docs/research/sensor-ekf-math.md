# Sensor models and EKF mathematics: source-level verification (issue #38)

Base: `d3e88d9`. No source was modified. All commands run from the repo root as
`PYTHONPATH=src python docs/research/sensor-ekf-math/<script>.py` (the package is not
installed in the agent venv; numpy, scipy, pydantic, pytest were installed there with uv).

## Verdict

The documented model (`docs/measurement-models.md`) matches the code. No P0-P2 defects
were found. Six low-severity items follow; none changes a documented claim except F6.

Existing tests: `pytest tests/unit/test_ekf.py test_sensors.py test_observer_pose.py`
-> 22 passed; `pytest tests/unit/test_fusion.py -k bias` -> 13 passed.

## Verified correct (evidence)

| Check | Result | How |
|---|---|---|
| Range / bearing / range-rate equations (`ekf.py:158-177`, `range_bearing.py:98-117`) | Match the doc formulas. Sensor and EKF agree to 1e-8 with noise off, moving observer, heading 2.9 rad | `probe_sensor_model.py` item 1 |
| Jacobians (`ekf.py:179-231`) | Max relative error vs central differences (h=1e-6) over 2000 random states, random heading in [-7,7], random observer velocity: 1.0e-8 (range-bearing), 9.8e-10 (bearing). That is finite-difference noise level | `probe_ekf_jacobian_wrap_psd.py` |
| Sensor/EKF noise consistency | Mean NIS over 4000 draws with a known state = 2.98 (expected 3) | `probe_sensor_model.py` item 2 |
| Wraparound | Predicted bearing flips between +pi and -pi at the cut (`[3.14159265]` vs `[-3.14159265]` for dy=±1e-9). `innovation` wraps the residual (`ekf.py:269-271`), so the discontinuity does not reach the update | `probe_ekf_jacobian_wrap_psd.py` |
| Joseph form, symmetry, PSD | 3000 predict+update cycles on a 3-D measurement with moving observer and heading 2.5: asymmetry 0.0, min eigenvalue 3.4e-3 (>0). Near-singular R (1e-12) and a 1e6-variance prior also stay PSD | same script; `probe_psd_edges.py` |
| Coincident geometry | `measurement_range_bearing` raises `ValueError` at distance < 1e-9 (`ekf.py:172`); not silently NaN | `probe_ekf_jacobian_wrap_psd.py` |
| Zero P with zero R | Rejected as "innovation covariance is not positive definite" (`ekf.py:274-277`) rather than producing NaN | `probe_psd_edges.py` |

## Findings

### F1. Range floor is applied before bias and truncates the noise (P3, confirmed)
`range_bearing.py:110-111`: `max(range_meas, 0.1) + bias`. For a target at 0.2 m, sigma 0.5,
bias 0.3, 5000 draws: mean range 0.651 vs 0.5 expected, 42% of samples sit exactly at
0.4 (floor + bias). The noise is no longer Gaussian, so the reported covariance is wrong
there. Only matters inside ~1 m of the observer. The floor is undocumented (see F6).
Fix: clamp after bias, or drop the sample; add a test that range is never below the floor
and document it. Run: `probe_sensor_model.py` item 3.

### F2. Frame rate is quantised to the sim tick (P3, confirmed; design limitation)
`range_bearing.py:40-47`, identical code at `vision_bearing.py:38-45`. `_due` resets
`_last_emit_time` to the current time instead of advancing by one period. A 30 Hz sensor on
a 100 Hz sim emits 75 frames in 3 s (effective 25 Hz); a 10 Hz sensor on 0.07 s ticks emits
50 in 7 s (expected 70). Harmless at the default 10 Hz sensor on 0.1 s epoch. Fix: advance by
the period, or document that `frame_rate` must divide the sim rate. Run: item 7.

### F3. Inconsistent coincidence thresholds (P3, confirmed; downstream handling not verified at runtime)
Sensors skip objects at range < 1e-6 (`range_bearing.py:99`, `vision_bearing.py:88`); the
EKF raises below 1e-9 (`ekf.py:172,188,216,226`). Between them the Jacobian is huge:
d(bearing)/dy = 1e6 at 1e-6 m. A target at 1e-5 m is emitted with range 0.1 (the F1
floor) and bearing 0. `association.py:161,217` catch `ValueError`, so the exception path
appears handled, but I read it rather than executing a tracker through a coincident
state. Fix: one shared minimum-range constant; regression test running the tracker with a
track passing through the observer position.

### F4. Bias estimator trusts reported covariance (P3, hypothesis)
`tracker.py:336` (the estimator lives in `tracker.py:299-340`, not in `ekf.py`; the issue
scope "where it belongs to the EKF module" therefore has nothing to cover in `ekf.py`).
The measurement noise is `R_vision + R_range` from the *reported* covariance, so
`reported_cov_scale < 1` (the miscalibration scenario) makes the scalar filter
overconfident. Scalar replica (`probe_bias_estimator_scalar.py`, 300 seeds, 3000 updates):
scale 1.0 -> RMS error 0.00072 vs reported sd 0.00106 (consistent); scale 0.1 -> RMS
0.00131 vs reported 0.00059 (2.2x overconfident). Also confirmed: a range-bearing bearing
bias leaks 1:1 into the vision bias estimate (-0.004997 for 0.005), which the docstring
states as an assumption. Not verified against the real tracker loop (replica only).
Proposed test: tracker with `reported_cov_scale=0.1` on vision, check
`vision_bias_estimate` error against `_bias_var`.

### F5. `wrap_angle` passes NaN and is closed at both ends (P3, confirmed; informational)
`models.py:32-34`. `wrap_angle(nan)` returns nan, `wrap_angle(3*pi)` returns
3.1415926535897927, `wrap_angle(+-pi)` keeps its sign. The EKF rejects non-finite
inputs before wrapping, so nothing reaches it today. Test: add NaN and 3*pi cases to
`test_wrap_angle_boundaries`.

### F6. Doc gaps (P3, confirmed)
`docs/measurement-models.md` does not mention the 0.1 m range floor (F1), that the
floor precedes bias, the 1e-6 skip (F3), or that frame rate is tick-quantised (F2).
Its claims about Jacobian checks, observer velocity, and bearing convention are accurate.

### Maintainability note (no defect)
`predict_over` (`ekf.py:93-112`) rebuilds F and Q that `__init__` also builds
(`ekf.py:58-77`); `test_predict_over_the_nominal_step_equals_predict` guards drift.
`_due`, `_new_id`, `_delivery_time` are duplicated between the two sensors.

## Not verified
- Linearisation error at close range or large P (only Jacobian correctness was checked).
- The real tracker's bias loop, retrodiction and association (read, not exercised; other tickets).
- Statistical consistency of the full filter over a scenario (NIS was checked for the sensor/EKF pair only).
- Full test suite (not run, per ticket instruction).
