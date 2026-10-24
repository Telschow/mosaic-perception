"""
Range-bearing sensor model.
"""

from __future__ import annotations

import numpy as np
import uuid

from ..domain.models import (
    SensorConfig, SensorObservation, WorldState, CoordinateFrame
)


class RangeBearingSensor:
    """
    Abstract range-bearing sensor producing noisy range, bearing, and radial velocity.
    """
    
    def __init__(self, config: SensorConfig, rng: np.random.RandomState | None = None):
        self.config = config
        self.rng = rng if rng is not None else np.random.RandomState(42)
        
        # Default noise levels
        self.range_noise_std = config.noise_std.get("range", 0.5)  # meters
        self.bearing_noise_std = config.noise_std.get("bearing", 0.01)  # radians
        self.range_rate_noise_std = config.noise_std.get("range_rate", 0.1)  # m/s
    
    def generate_observations(
        self, world_state: WorldState, current_time: float
    ) -> list[SensorObservation]:
        """Generate observations from world state."""
        observations = []
        
        if not self.config.enabled:
            return observations
        
        # Check for dropout
        if self.rng.random() < self.config.dropout_prob:
            return observations
        
        observer_pos = world_state.observer_pose.position.to_array()
        observer_heading = world_state.observer_pose.heading
        
        for obj_id, obj_state in world_state.objects.items():
            # Check detection probability
            if self.rng.random() > self.config.detection_probability:
                continue
            
            obj_pos = obj_state.position.to_array()
            obj_vel = obj_state.velocity.to_array()
            
            # Vector from observer to object in world frame
            rel_pos = obj_pos - observer_pos
            range_true = np.linalg.norm(rel_pos)
            
            if range_true < 1e-6:  # Too close
                continue
            
            # Bearing in world frame
            bearing_world = np.arctan2(rel_pos[1], rel_pos[0])
            # Bearing in sensor frame
            bearing_sensor = bearing_world - observer_heading
            # Normalize to [-pi, pi]
            bearing_sensor = np.arctan2(np.sin(bearing_sensor), np.cos(bearing_sensor))
            
            # Radial velocity (range rate)
            # v_r = (rel_pos/range) . rel_vel
            unit_range = rel_pos / range_true
            range_rate_true = np.dot(unit_range, obj_vel)
            
            # Add noise
            range_meas = range_true + self.rng.normal(0, self.range_noise_std)
            range_meas = max(range_meas, 0.1)  # Minimum range
            
            bearing_meas = bearing_sensor + self.rng.normal(0, self.bearing_noise_std)
            bearing_meas = np.arctan2(np.sin(bearing_meas), np.cos(bearing_meas))
            
            range_rate_meas = range_rate_true + self.rng.normal(0, self.range_rate_noise_std)
            
            # Add bias if configured
            range_meas += self.config.bias.get("range", 0.0)
            bearing_meas += self.config.bias.get("bearing", 0.0)
            range_rate_meas += self.config.bias.get("range_rate", 0.0)
            
            # Compute measurement covariance
            R = np.diag([
                self.range_noise_std**2,
                self.bearing_noise_std**2,
                self.range_rate_noise_std**2,
            ])
            
            # Compute delivery time with delay
            delay_mean = self.config.delivery_delay_mean
            delay_std = self.config.delivery_delay_std
            if delay_std > 0:
                delay = max(0, self.rng.normal(delay_mean, delay_std))
            else:
                delay = delay_mean
            
            obs = SensorObservation(
                observation_id=str(uuid.uuid4()),
                sensor_id=self.config.sensor_id,
                sensor_type=self.config.sensor_type,
                capture_time=current_time,
                delivery_time=current_time + delay,
                coordinate_frame=CoordinateFrame.SENSOR,
                measurement_model="range_bearing_nonlinear",
                measurements={
                    "range": float(range_meas),
                    "bearing": float(bearing_meas),
                    "range_rate": float(range_rate_meas),
                },
                measurement_covariance=R.tolist(),
            )
            # Store true object id for evaluation only (will be stripped)
            obs._true_object_id = obj_id
            observations.append(obs)
        
        # Add false alarms if configured
        false_alarm_rate = self.config.false_alarm_rate
        if false_alarm_rate > 0:
            # Simple Poisson model
            expected_false = false_alarm_rate * self.rng.uniform(0, 1)  # rough approximation
            num_false = self.rng.poisson(expected_false)
            for _ in range(num_false):
                range_meas = self.rng.uniform(5, 50)
                bearing_meas = self.rng.uniform(-np.pi, np.pi)
                range_rate_meas = self.rng.uniform(-5, 5)
                
                R = np.diag([self.range_noise_std**2, self.bearing_noise_std**2, self.range_rate_noise_std**2])
                
                delay = max(0, self.rng.normal(delay_mean, delay_std) if delay_std > 0 else delay_mean)
                
                obs = SensorObservation(
                    observation_id=str(uuid.uuid4()),
                    sensor_id=self.config.sensor_id,
                    sensor_type=self.config.sensor_type,
                    capture_time=current_time,
                    delivery_time=current_time + delay,
                    coordinate_frame=CoordinateFrame.SENSOR,
                    measurement_model="range_bearing_nonlinear",
                    measurements={
                        "range": float(range_meas),
                        "bearing": float(bearing_meas),
                        "range_rate": float(range_rate_meas),
                    },
                    measurement_covariance=R.tolist(),
                )
                obs._true_object_id = None  # False alarm
                observations.append(obs)
        
        return observations
