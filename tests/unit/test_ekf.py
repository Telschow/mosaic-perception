"""Tests for EKF."""

import numpy as np

from mosaic_perception.tracking.ekf import ExtendedKalmanFilter, wrap_angle


def test_wrap_angle():
    assert (
        abs(wrap_angle(np.pi + 0.1) - (-np.pi + 0.1)) < 1e-10
        or abs(wrap_angle(3.5) - wrap_angle(3.5 - 2 * np.pi)) < 1e-10
    )
    assert abs(wrap_angle(-np.pi - 0.1) - (np.pi - 0.1)) < 1e-10


def test_bearing_residual_wrap():
    ekf = ExtendedKalmanFilter(dt=0.1)
    x = np.array([1.0, 0.0, 0.0, 0.0])
    p = np.eye(4)
    h = ekf.h_bearing(x)
    H_mat = ekf.H_bearing(x)
    R_mat = np.array([[0.01]])
    z = np.array([wrap_angle(float(h[0]) + 0.05)])
    x_u, p_u = ekf.update(x, p, z, H_mat, R_mat, h_pred=h)
    assert np.all(np.isfinite(x_u))
    assert np.all(np.isfinite(p_u))
    assert np.allclose(p_u, p_u.T)


def test_range_bearing_update():
    ekf = ExtendedKalmanFilter(dt=0.1)
    x = np.array([5.0, 0.0, 0.0, 0.0])
    p = np.diag([1.0, 1.0, 1.0, 1.0])
    h = ekf.h_range_bearing(x)
    H_mat = ekf.H_range_bearing(x)
    R_mat = np.diag([0.25, 1e-4, 0.01])
    z = h + np.array([0.1, -0.001, 0.01])
    x_u, p_u = ekf.update(x, p, z, H_mat, R_mat, h_pred=h)
    assert np.all(np.isfinite(x_u))
    assert np.allclose(p_u, p_u.T)
