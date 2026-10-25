"""
Range-bearing sensor model.

Measurement frame: bearings are reported relative to the observer heading at
capture time (sensor frame). Range rate is the line-of-sight closing rate
relative to the observer, so observer velocity is modelled explicitly.
"""

from __future__ import annotations

import numpy as np

from ..domain.models import (
    CoordinateFrame,
    Pose2D,
    SensorConfig,
    SensorObservation,
    Vector2,
    WorldState,
    wrap_angle,
)


class RangeBearingSensor:
    """
    Abstract range-bearing sensor producing noisy range, bearing, and radial
    velocity in the sensor frame.
    """

    def __init__(self, config: SensorConfig, rng: np.random.RandomState | None = None):
        self.config = config
        self.rng = rng if rng is not None else np.random.RandomState(42)

        self.range_noise_std = config.noise_std.get("range", 0.5)  # metres
        self.bearing_noise_std = config.noise_std.get("bearing", 0.01)  # radians
        self.range_rate_noise_std = config.noise_std.get("range_rate", 0.1)  # m/s
        self._last_emit_time: float | None = None
        self._next_observation_id = 0

    def _due(self, current_time: float) -> bool:
        """Respect the configured frame rate."""
        period = 1.0 / self.config.frame_rate
        if self._last_emit_time is None:
            self._last_emit_time = current_time
            return True
        if current_time - self._last_emit_time < period - 1e-9:
            return False
        self._last_emit_time = current_time
        return True

    def _reported_cov(self, covariance: np.ndarray) -> np.ndarray:
        return covariance * float(self.config.reported_cov_scale)

    def _new_id(self) -> str:
        observation_id = f"{self.config.sensor_id}-{self._next_observation_id:06d}"
        self._next_observation_id += 1
        return observation_id

    def _delivery_time(self, current_time: float) -> float:
        delay_mean = float(self.config.delivery_delay_mean)
        delay_std = float(self.config.delivery_delay_std)
        if delay_std > 0:
            delay = max(0.0, float(self.rng.normal(delay_mean, delay_std)))
        else:
            delay = max(0.0, delay_mean)
        return float(current_time) + delay

    def generate_observations(
        self, world_state: WorldState, current_time: float
    ) -> list[SensorObservation]:
        """Generate observations from world state."""
        observations: list[SensorObservation] = []

        if not self.config.enabled:
            return observations
        if not self._due(float(current_time)):
            return observations

        # Sensor-level dropout for the whole frame.
        if self.rng.random() < self.config.dropout_prob:
            return observations

        pose = world_state.observer_pose
        observer_pos = pose.position.to_array()
        observer_vel = pose.velocity.to_array()
        observer_heading = float(pose.heading)

        for obj_id, obj_state in world_state.objects.items():
            if not obj_state.visible:
                continue
            if self.rng.random() > self.config.detection_probability:
                continue

            obj_pos = obj_state.position.to_array()
            obj_vel = obj_state.velocity.to_array()

            rel_pos = obj_pos - observer_pos
            range_true = float(np.linalg.norm(rel_pos))
            if range_true < 1e-6:
                continue

            bearing_world = float(np.arctan2(rel_pos[1], rel_pos[0]))
            bearing_sensor = wrap_angle(bearing_world - observer_heading)

            # Closing rate relative to the observer.
            unit_range = rel_pos / range_true
            rel_vel = obj_vel - observer_vel
            range_rate_true = float(np.dot(unit_range, rel_vel))

            range_meas = range_true + float(self.rng.normal(0, self.range_noise_std))
            range_meas = max(range_meas, 0.1) + float(self.config.bias.get("range", 0.0))

            bearing_meas = wrap_angle(
                bearing_sensor
                + float(self.rng.normal(0, self.bearing_noise_std))
                + float(self.config.bias.get("bearing", 0.0))
            )

            range_rate_meas = range_rate_true + float(self.rng.normal(0, self.range_rate_noise_std))
            range_rate_meas += float(self.config.bias.get("range_rate", 0.0))

            r_true = np.diag(
                [
                    self.range_noise_std**2,
                    self.bearing_noise_std**2,
                    self.range_rate_noise_std**2,
                ]
            )

            obs = SensorObservation(
                observation_id=self._new_id(),
                sensor_id=self.config.sensor_id,
                sensor_type=self.config.sensor_type,
                capture_time=float(current_time),
                delivery_time=self._delivery_time(current_time),
                coordinate_frame=CoordinateFrame.SENSOR,
                measurement_model="range_bearing_sensor_frame",
                measurements={
                    "range": float(range_meas),
                    "bearing": float(bearing_meas),
                    "range_rate": float(range_rate_meas),
                },
                measurement_covariance=self._reported_cov(r_true).tolist(),
                observer_pose=Pose2D(
                    position=Vector2(x=float(observer_pos[0]), y=float(observer_pos[1])),
                    heading=observer_heading,
                    velocity=Vector2(x=float(observer_vel[0]), y=float(observer_vel[1])),
                ),
            )
            obs._true_object_id = obj_id  # evaluation only; stripped by caller
            observations.append(obs)

        observations.extend(self._false_alarms(current_time, pose))
        return observations

    def _false_alarms(self, current_time: float, pose: Pose2D) -> list[SensorObservation]:
        rate = float(self.config.false_alarm_rate)
        if rate <= 0.0:
            return []
        # Poisson false alarms per frame.
        num_false = int(self.rng.poisson(rate))
        out: list[SensorObservation] = []
        r_true = np.diag(
            [
                self.range_noise_std**2,
                self.bearing_noise_std**2,
                self.range_rate_noise_std**2,
            ]
        )
        for _ in range(num_false):
            out.append(
                SensorObservation(
                    observation_id=self._new_id(),
                    sensor_id=self.config.sensor_id,
                    sensor_type=self.config.sensor_type,
                    capture_time=float(current_time),
                    delivery_time=self._delivery_time(current_time),
                    coordinate_frame=CoordinateFrame.SENSOR,
                    measurement_model="range_bearing_sensor_frame",
                    measurements={
                        "range": float(self.rng.uniform(5, 50)),
                        "bearing": float(self.rng.uniform(-np.pi, np.pi)),
                        "range_rate": float(self.rng.uniform(-5, 5)),
                    },
                    measurement_covariance=self._reported_cov(r_true).tolist(),
                    observer_pose=Pose2D(
                        position=pose.position,
                        heading=float(pose.heading),
                        velocity=pose.velocity,
                    ),
                )
            )
        return out
