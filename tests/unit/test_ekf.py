"""Measurement-model, Jacobian and covariance tests for the EKF."""

from __future__ import annotations

import numpy as np
import pytest

from mosaic_perception.domain.models import Pose2D, Vector2, wrap_angle
from mosaic_perception.tracking.ekf import ExtendedKalmanFilter


def pose(x: float, y: float, heading: float = 0.0, vx: float = 0.0, vy: float = 0.0) -> Pose2D:
    return Pose2D(
        position=Vector2(x=x, y=y),
        heading=heading,
        velocity=Vector2(x=vx, y=vy),
    )


def test_range_bearing_stationary_zero_heading():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([10.0, 0.0, 1.0, 0.0])
    measurement = ekf.measurement_range_bearing(state, pose(0.0, 0.0, 0.0))
    assert np.allclose(measurement, [10.0, 0.0, 1.0])


def test_bearing_is_sensor_relative_with_nonzero_heading():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([10.0, 0.0, 0.0, 0.0])
    measurement = ekf.measurement_range_bearing(state, pose(0.0, 0.0, np.pi / 2.0))
    assert np.isclose(measurement[0], 10.0)
    assert np.isclose(wrap_angle(float(measurement[1])), -np.pi / 2.0)
    vision = ekf.measurement_bearing(state, pose(0.0, 0.0, np.pi / 2.0))
    assert np.isclose(wrap_angle(float(vision[0])), -np.pi / 2.0)


def test_range_rate_is_relative_to_observer_velocity():
    ekf = ExtendedKalmanFilter(dt=0.1)
    # Observer moves north at 1 m/s; object moves east at 2 m/s from (10, 0).
    # Relative velocity is (2, -1), so radial rate is +2 m/s.
    state = np.array([10.0, 0.0, 2.0, 0.0])
    measurement = ekf.measurement_range_bearing(state, pose(0.0, 0.0, np.pi / 2.0, vx=0.0, vy=1.0))
    assert np.isclose(measurement[0], 10.0)
    assert np.isclose(wrap_angle(float(measurement[1])), -np.pi / 2.0)
    assert np.isclose(measurement[2], 2.0)


def test_range_rate_stationary_object_with_moving_observer():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([0.0, 10.0, 0.0, 0.0])
    measurement = ekf.measurement_range_bearing(state, pose(0.0, 0.0, np.pi / 2.0, vx=1.0, vy=0.0))
    assert np.isclose(measurement[0], 10.0)
    assert np.isclose(measurement[2], 0.0)


def test_range_bearing_jacobian_matches_finite_differences():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([12.3, -4.5, 1.2, 0.8])
    observer = pose(2.0, -1.0, 0.7, vx=0.3, vy=-0.4)
    analytic = ekf.jacobian_range_bearing(state, observer)
    numerical = np.zeros((3, 4))
    epsilon = 1e-6
    for index in range(4):
        plus = state.copy()
        minus = state.copy()
        plus[index] += epsilon
        minus[index] -= epsilon
        plus_measurement = ekf.measurement_range_bearing(plus, observer)
        minus_measurement = ekf.measurement_range_bearing(minus, observer)
        plus_measurement[1] = float(measurement_unwrap(plus_measurement[1], minus_measurement[1]))
        numerical[:, index] = (plus_measurement - minus_measurement) / (2.0 * epsilon)
    assert np.allclose(analytic, numerical, atol=1e-5)


def test_bearing_jacobian_matches_finite_differences():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([-8.0, 6.0, 0.5, -0.2])
    observer = pose(1.0, 2.0, -0.4, vx=0.2, vy=0.1)
    analytic = ekf.jacobian_bearing(state, observer)
    numerical = np.zeros((1, 4))
    epsilon = 1e-6
    for index in range(4):
        plus = state.copy()
        minus = state.copy()
        plus[index] += epsilon
        minus[index] -= epsilon
        plus_measurement = ekf.measurement_bearing(plus, observer)
        minus_measurement = ekf.measurement_bearing(minus, observer)
        plus_measurement[0] = float(measurement_unwrap(plus_measurement[0], minus_measurement[0]))
        numerical[:, index] = (plus_measurement - minus_measurement) / (2.0 * epsilon)
    assert np.allclose(analytic, numerical, atol=1e-5)


def measurement_unwrap(value: float, reference: float) -> float:
    """Unwrap ``value`` to the copy nearest ``reference`` for finite differences."""
    while value - reference > np.pi:
        value -= 2.0 * np.pi
    while value - reference < -np.pi:
        value += 2.0 * np.pi
    return value


def test_innovation_wraps_bearing_across_pi():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([-10.0, 0.001, 0.0, 0.0])
    observer = pose(0.0, 0.0, 0.0)
    covariance = np.eye(4)
    predicted = ekf.measurement_range_bearing(state, observer)
    measurement = predicted.copy()
    measurement[1] = wrap_angle(float(predicted[1]) + 0.05)
    residual, _innovation_covariance = ekf.innovation(
        state,
        covariance,
        measurement,
        predicted,
        ekf.jacobian_range_bearing(state, observer),
        np.diag([0.25, 1e-4, 0.01]),
        angle_indices=(1,),
    )
    assert abs(float(residual[1])) < 0.06


def test_update_symmetry_and_positive_semidefinite_covariance():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([10.0, 1.0, 1.0, -0.5])
    covariance = np.diag([2.0, 1.0, 4.0, 3.0])
    observer = pose(0.0, 0.0, 0.3)

    range_measurement = ekf.measurement_range_bearing(state, observer)
    state, covariance = ekf.update(
        state,
        covariance,
        range_measurement,
        ekf.jacobian_range_bearing(state, observer),
        np.diag([0.25, 1e-4, 0.01]),
        range_measurement,
        angle_indices=(1,),
    )
    vision_measurement = ekf.measurement_bearing(state, observer)
    state, covariance = ekf.update(
        state,
        covariance,
        vision_measurement,
        ekf.jacobian_bearing(state, observer),
        np.array([[2.5e-5]]),
        vision_measurement,
        angle_indices=(0,),
    )

    assert np.allclose(covariance, covariance.T)
    eigenvalues = np.linalg.eigvalsh(covariance)
    assert np.all(eigenvalues >= -1e-10)
    assert np.all(np.isfinite(state))


def test_update_rejects_indefinite_measurement_covariance():
    ekf = ExtendedKalmanFilter(dt=0.1)
    state = np.array([10.0, 0.0, 0.0, 0.0])
    covariance = np.eye(4)
    observer = pose(0.0, 0.0, 0.0)
    predicted = ekf.measurement_bearing(state, observer)
    with pytest.raises(ValueError):
        ekf.update(
            state,
            covariance,
            predicted,
            ekf.jacobian_bearing(state, observer),
            np.array([[-1.0]]),
            predicted,
            angle_indices=(0,),
        )


def test_wrap_angle_boundaries():
    assert abs(wrap_angle(np.pi + 0.1) - (-np.pi + 0.1)) < 1e-12
    assert abs(wrap_angle(-np.pi - 0.1) - (np.pi - 0.1)) < 1e-12
    assert abs(abs(wrap_angle(3.0 * np.pi)) - np.pi) < 1e-12
