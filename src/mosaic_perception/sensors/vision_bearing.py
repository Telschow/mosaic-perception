"""
Vision-like bearing sensor model.

This represents the output of an upstream vision detector: bearing relative to
the observer heading plus generic class probabilities and a detection
confidence. Raw pixels are intentionally not simulated.

The class scores are detector outputs, not calibrated probabilities; they are
carried as metadata and are not fused into the kinematic state in v0.1.
"""

from __future__ import annotations

import numpy as np

from ..domain.models import (
    CoordinateFrame,
    ObjectClass,
    Pose2D,
    SensorConfig,
    SensorObservation,
    Vector2,
    WorldState,
    wrap_angle,
)


class VisionBearingSensor:
    """Simplified vision-detector output model (bearing only)."""

    def __init__(self, config: SensorConfig, rng: np.random.RandomState | None = None):
        self.config = config
        self.rng = rng if rng is not None else np.random.RandomState(42)
        self.bearing_noise_std = config.noise_std.get("bearing", 0.005)
        self._last_emit_time: float | None = None
        self._next_observation_id = 0

    def _due(self, current_time: float) -> bool:
        period = 1.0 / self.config.frame_rate
        if self._last_emit_time is None:
            self._last_emit_time = current_time
            return True
        if current_time - self._last_emit_time < period - 1e-9:
            return False
        self._last_emit_time = current_time
        return True

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
        """Generate vision-like observations from world state."""
        observations: list[SensorObservation] = []

        if not self.config.enabled:
            return observations
        if not self._due(float(current_time)):
            return observations
        if self.rng.random() < self.config.dropout_prob:
            return observations

        pose = world_state.observer_pose
        observer_pos = pose.position.to_array()
        observer_heading = float(pose.heading)

        for obj_id, obj_state in world_state.objects.items():
            if not obj_state.visible:
                continue
            if self.rng.random() > self.config.detection_probability:
                continue

            obj_pos = obj_state.position.to_array()
            rel_pos = obj_pos - observer_pos
            range_true = float(np.linalg.norm(rel_pos))
            if range_true < 1e-6:
                continue

            bearing_world = float(np.arctan2(rel_pos[1], rel_pos[0]))
            bearing_sensor = wrap_angle(bearing_world - observer_heading)

            bearing_meas = wrap_angle(
                bearing_sensor
                + float(self.rng.normal(0, self.bearing_noise_std))
                + float(self.config.bias.get("bearing", 0.0))
            )

            reported_var = self.bearing_noise_std**2 * float(self.config.reported_cov_scale)
            reported_cov = np.array([[reported_var]])

            # Detector-like class scores. These are softmax-style outputs with
            # noise; they are not claimed to be calibrated probabilities.
            true_class = obj_state.true_class
            class_probs: dict[str, float] = {}
            for c in ObjectClass:
                if c == true_class:
                    value = 0.75 + float(self.rng.normal(0, 0.05))
                else:
                    value = 0.06 + float(self.rng.normal(0, 0.02))
                class_probs[c.value] = max(1e-3, value)
            total = sum(class_probs.values())
            class_probs = {k: float(v / total) for k, v in class_probs.items()}

            observations.append(
                SensorObservation(
                    observation_id=self._new_id(),
                    sensor_id=self.config.sensor_id,
                    sensor_type=self.config.sensor_type,
                    capture_time=float(current_time),
                    delivery_time=self._delivery_time(current_time),
                    coordinate_frame=CoordinateFrame.SENSOR,
                    measurement_model="bearing_sensor_frame",
                    measurements={"bearing": float(bearing_meas)},
                    measurement_covariance=reported_cov.tolist(),
                    class_probs=class_probs,
                    detection_confidence=float(self.rng.uniform(0.7, 0.95)),
                    observer_pose=Pose2D(
                        position=Vector2(x=float(observer_pos[0]), y=float(observer_pos[1])),
                        heading=observer_heading,
                        velocity=Vector2(x=float(pose.velocity.x), y=float(pose.velocity.y)),
                    ),
                )
            )
            observations[-1]._true_object_id = obj_id

        observations.extend(self._false_alarms(current_time, pose))
        return observations

    def _false_alarms(self, current_time: float, pose: Pose2D) -> list[SensorObservation]:
        rate = float(self.config.false_alarm_rate)
        if rate <= 0.0:
            return []
        num_false = int(self.rng.poisson(rate))
        reported_var = self.bearing_noise_std**2 * float(self.config.reported_cov_scale)
        out: list[SensorObservation] = []
        for _ in range(num_false):
            class_probs = {c.value: 1.0 / len(ObjectClass) for c in ObjectClass}
            out.append(
                SensorObservation(
                    observation_id=self._new_id(),
                    sensor_id=self.config.sensor_id,
                    sensor_type=self.config.sensor_type,
                    capture_time=float(current_time),
                    delivery_time=self._delivery_time(current_time),
                    coordinate_frame=CoordinateFrame.SENSOR,
                    measurement_model="bearing_sensor_frame",
                    measurements={"bearing": float(self.rng.uniform(-np.pi, np.pi))},
                    measurement_covariance=[[float(reported_var)]],
                    class_probs=class_probs,
                    detection_confidence=float(self.rng.uniform(0.3, 0.6)),
                    observer_pose=Pose2D(
                        position=pose.position,
                        heading=float(pose.heading),
                        velocity=pose.velocity,
                    ),
                )
            )
        return out
