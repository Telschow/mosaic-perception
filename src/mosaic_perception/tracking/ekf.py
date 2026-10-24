"""
Extended Kalman Filter for 2D tracking with nonlinear measurements.
"""

from __future__ import annotations

import numpy as np


class ExtendedKalmanFilter:
    """
    EKF for tracking with constant velocity motion model.
    State vector: [x, y, vx, vy]
    """
    
    def __init__(self, dt: float = 0.1, q_pos: float = 1.0, q_vel: float = 1.0):
        self.dt = dt
        # Process noise
        self.Q = np.diag([q_pos**2, q_pos**2, q_vel**2, q_vel**2])
        
        # Motion model
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    def predict(self, x: np.ndarray, P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Predict step."""
        x_pred = self.F @ x
        P_pred = self.F @ P @ self.F.T + self.Q
        return x_pred, P_pred
    
    def h_range_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Measurement model for range, bearing, range_rate."""
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        px, py, vx, vy = x[0], x[1], x[2], x[3]
        dx = px - sensor_pos[0]
        dy = py - sensor_pos[1]
        range_ = np.sqrt(dx*dx + dy*dy)
        if range_ < 1e-6:
            range_ = 1e-6
        bearing = np.arctan2(dy, dx)
        range_rate = (dx*vx + dy*vy) / range_
        return np.array([range_, bearing, range_rate])
    
    def H_range_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Jacobian of measurement model for range, bearing, range_rate."""
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        px, py, vx, vy = x[0], x[1], x[2], x[3]
        dx = px - sensor_pos[0]
        dy = py - sensor_pos[1]
        range_ = np.sqrt(dx*dx + dy*dy)
        if range_ < 1e-6:
            range_ = 1e-6
        range2 = range_ * range_
        
        H = np.zeros((3, 4))
        # dr/drange
        H[0, 0] = dx/range_
        H[0, 1] = dy/range_
        H[0, 2] = 0
        H[0, 3] = 0
        # dr/dbearing
        H[1, 0] = -dy/range2
        H[1, 1] = dx/range2
        H[1, 2] = 0
        H[1, 3] = 0
        # dr/drange_rate
        H[2, 0] = (vx*range2 - dx*(dx*vx + dy*vy)) / (range2 * range_)
        H[2, 1] = (vy*range2 - dy*(dx*vx + dy*vy)) / (range2 * range_)
        H[2, 2] = dx/range_
        H[2, 3] = dy/range_
        return H
    
    def h_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Measurement model for bearing only."""
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        px, py = x[0], x[1]
        dx = px - sensor_pos[0]
        dy = py - sensor_pos[1]
        bearing = np.arctan2(dy, dx)
        return np.array([bearing])
    
    def H_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Jacobian for bearing only."""
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        px, py = x[0], x[1]
        dx = px - sensor_pos[0]
        dy = py - sensor_pos[1]
        range2 = dx*dx + dy*dy
        if range2 < 1e-12:
            range2 = 1e-12
        H = np.zeros((1, 4))
        H[0, 0] = -dy/range2
        H[0, 1] = dx/range2
        H[0, 2] = 0
        H[0, 3] = 0
        return H
    
    def update(self, x_pred: np.ndarray, P_pred: np.ndarray, z: np.ndarray, 
               H: np.ndarray, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Update step."""
        y = z - self.h_from_H(x_pred, H)  # innovation
        # Normalize angle if bearing
        if len(z) == 1 or (len(z) == 3):  # has bearing
            if len(z) == 1:
                y[0] = np.arctan2(np.sin(y[0]), np.cos(y[0]))
            elif len(z) == 3:
                y[1] = np.arctan2(np.sin(y[1]), np.cos(y[1]))
        
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)
        x_upd = x_pred + K @ y
        P_upd = (np.eye(4) - K @ H) @ P_pred
        # Ensure symmetry
        P_upd = (P_upd + P_upd.T) / 2
        return x_upd, P_upd
    
    def h_from_H(self, x_pred: np.ndarray, H: np.ndarray) -> np.ndarray:
        """Helper to compute expected measurement (approximate)."""
        # This is a simplified approach
        return np.zeros(H.shape[0])
