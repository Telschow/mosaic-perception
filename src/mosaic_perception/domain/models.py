"""
Domain models and data contracts for Mosaic.

All data structures follow explicit contracts to prevent mixing ground truth
with estimator inputs and to clearly distinguish timing, uncertainty, and
metadata.

Coordinate and timing conventions
--------------------------------
* Positions are metres in a single right-handed world frame (x east, y north).
* Headings and bearings are radians, measured counter-clockwise from +x, and are
  wrapped to ``[-pi, pi]``.
* Sensor measurements are reported in the **sensor frame**: a bearing is the
  world-frame line-of-sight angle minus the observer heading at capture time.
* ``capture_time`` is when the measurement was taken; ``delivery_time`` is when
  the estimator may use it. Both are simulation seconds since t=0.
"""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Angular values closer than this are treated as identical after wrapping.
ANGLE_EPS = 1e-9


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the interval [-pi, pi]."""
    return float(math.atan2(math.sin(angle), math.cos(angle)))


class CoordinateFrame(StrEnum):
    """Coordinate frame identifiers."""

    WORLD = "world"  # Global/world frame
    SENSOR = "sensor"  # Sensor-local frame
    BODY = "body"  # Vehicle/body frame


class TrackStatus(StrEnum):
    """Track lifecycle status."""

    TENTATIVE = "tentative"  # Newly initiated, not yet confirmed
    CONFIRMED = "confirmed"  # Confirmed track with sufficient history
    COASTING = "coasting"  # Missing detections, coasting prediction
    DELETED = "deleted"  # Marked for deletion


class ObjectClass(StrEnum):
    """Generic object classes."""

    UNKNOWN = "unknown"
    VEHICLE = "vehicle"
    PEDESTRIAN = "pedestrian"
    CYCLIST = "cyclist"
    OTHER = "other"


class Vector2(BaseModel):
    """2D vector in metres or metres/second (context dependent)."""

    x: float = 0.0
    y: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> Vector2:
        return cls(x=float(arr[0]), y=float(arr[1]))


class Pose2D(BaseModel):
    """
    Planar pose of the observer/sensor platform at a simulation time.

    ``velocity`` is the world-frame platform velocity, needed to model radial
    velocity correctly for a moving observer. It defaults to zero.
    """

    position: Vector2 = Field(default_factory=Vector2)
    heading: float = 0.0  # radians, wrapped to [-pi, pi]
    velocity: Vector2 = Field(default_factory=Vector2)

    def to_array(self) -> np.ndarray:
        return np.array([self.position.x, self.position.y, self.heading])


class WorldState(BaseModel):
    """
    Ground truth world state at a given time.

    This represents the true state and must never leak into estimator inputs.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    time: float = Field(description="Simulation time in seconds")
    objects: dict[str, ObjectState] = Field(default_factory=dict)
    observer_pose: Pose2D = Field(default_factory=Pose2D)


class ObjectState(BaseModel):
    """Ground truth state of a single object."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    object_id: str = Field(description="Stable ground truth identity")
    position: Vector2 = Field(default_factory=Vector2)
    velocity: Vector2 = Field(default_factory=Vector2)
    true_class: ObjectClass = ObjectClass.UNKNOWN
    visible: bool = True  # For occlusion modeling if needed

    def state_vector(self) -> np.ndarray:
        """Get [x, y, vx, vy] state vector."""
        return np.array([self.position.x, self.position.y, self.velocity.x, self.velocity.y])


class SensorConfig(BaseModel):
    """Configuration for a sensor."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    sensor_id: str
    sensor_type: str  # "range_bearing", "vision_bearing"
    frame_rate: float = 10.0  # Hz; sensor emits at most this often
    noise_std: dict[str, float] = Field(default_factory=dict)
    detection_probability: float = 1.0
    false_alarm_rate: float = 0.0
    bias: dict[str, float] = Field(default_factory=dict)
    dropout_prob: float = 0.0
    delivery_delay_mean: float = 0.0
    delivery_delay_std: float = 0.0
    # Multiplies the covariance *reported to the estimator* without changing the
    # sampled measurement error. Used by the miscalibration scenario.
    reported_cov_scale: float = 1.0
    enabled: bool = True

    @field_validator("detection_probability")
    @classmethod
    def validate_detection_prob(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("detection_probability must be in [0,1]")
        return v

    @field_validator("frame_rate")
    @classmethod
    def validate_frame_rate(cls, v: float) -> float:
        if v <= 0.0:
            raise ValueError("frame_rate must be positive")
        return v

    @field_validator("reported_cov_scale")
    @classmethod
    def validate_cov_scale(cls, v: float) -> float:
        if v <= 0.0:
            raise ValueError("reported_cov_scale must be positive")
        return v


class ScenarioConfig(BaseModel):
    """
    Fully resolved configuration for one scenario.

    This is the effective configuration recorded with every run. Scenario
    presets are expanded into these values before simulation starts.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str = ""
    hypothesis: str = ""
    seed: int = 42
    duration: float = 10.0  # seconds
    dt: float = 0.1  # seconds
    num_objects: int = 3
    observer_trajectory: str = "static"
    sensors: dict[str, SensorConfig] = Field(default_factory=dict)


class SensorObservation(BaseModel):
    """
    Observation from a sensor.

    Must distinguish capture time from delivery time, include measurement model
    and coordinate frame, and represent uncertainty where applicable.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    observation_id: str
    sensor_id: str
    sensor_type: str

    # Timing
    capture_time: float = Field(description="Time when measurement was captured")
    delivery_time: float = Field(description="Time when observation is delivered to the tracker")

    # Metadata
    coordinate_frame: CoordinateFrame = CoordinateFrame.SENSOR
    measurement_model: str = Field(description="Identifier for measurement model used")

    # Measurements (sensor-specific, sensor frame)
    measurements: dict[str, float] = Field(default_factory=dict)

    # Uncertainty reported to the estimator (measurement units)
    measurement_covariance: list[list[float]] | None = None

    # Classification (for vision-like sensors)
    class_probs: dict[str, float] | None = None
    detection_confidence: float | None = None

    # Association (set by tracker, not by sensor)
    associated_track_id: str | None = None

    # Observer pose at capture time (position, heading, velocity)
    observer_pose: Pose2D | None = Field(
        default=None, description="Observer pose at capture time for estimation"
    )

    # For debugging/evaluation only - NEVER used by tracker
    _true_object_id: str | None = None  # Private, evaluation only

    def get_measurement_cov(self) -> np.ndarray | None:
        if self.measurement_covariance is None:
            return None
        return np.array(self.measurement_covariance, dtype=float)

    def age_of_information(self) -> float:
        """Time between capture and delivery."""
        return self.delivery_time - self.capture_time

    def measurement_group(self) -> str:
        """Group observations by the measurement model they carry."""
        if "range" in self.measurements:
            return "range_bearing"
        if "bearing" in self.measurements:
            return "vision_bearing"
        raise ValueError(f"observation {self.observation_id} has no recognised measurement group")


class TrackEstimate(BaseModel):
    """
    Current track estimate from the tracker.

    ``hits`` counts epochs in which at least one measurement was accepted.
    ``misses`` counts consecutive epochs with no accepted measurement.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    track_id: str
    status: TrackStatus = TrackStatus.TENTATIVE

    # Timing
    time: float
    last_update_time: float

    # State estimate (2D position and velocity)
    state: list[float] = Field(description="[x, y, vx, vy]")
    covariance: list[list[float]] = Field(description="4x4 state covariance")

    # Track management
    hits: int = 0  # epochs with at least one accepted measurement
    misses: int = 0  # consecutive epochs with no accepted measurement
    age: int = 0  # epochs since initiation
    associated_observations: list[str] = Field(default_factory=list)

    # Metadata
    initiating_sensor: str | None = None
    class_estimate: ObjectClass = ObjectClass.UNKNOWN
    class_confidence: float = 0.0

    def state_array(self) -> np.ndarray:
        return np.array(self.state, dtype=float)

    def cov_array(self) -> np.ndarray:
        return np.array(self.covariance, dtype=float)

    def position(self) -> np.ndarray:
        return self.state_array()[:2]

    def velocity(self) -> np.ndarray:
        return self.state_array()[2:]

    def position_cov(self) -> np.ndarray:
        covariance = self.cov_array()
        return covariance[:2, :2]


class TrackSnapshot(BaseModel):
    """
    Immutable per-epoch snapshot of a track, recorded during the run.

    Evaluation uses these snapshots rather than the final track dictionary so
    that estimates are scored at the epoch they actually describe.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    time: float
    track_id: str
    status: TrackStatus
    state: list[float]
    covariance: list[list[float]]
    hits: int = 0
    misses: int = 0
    age: int = 0
    updated_this_epoch: bool = False

    def state_array(self) -> np.ndarray:
        return np.array(self.state, dtype=float)

    def cov_array(self) -> np.ndarray:
        return np.array(self.covariance, dtype=float)

    def position(self) -> np.ndarray:
        return self.state_array()[:2]

    def velocity(self) -> np.ndarray:
        return self.state_array()[2:]

    def position_cov(self) -> np.ndarray:
        return self.cov_array()[:2, :2]


class ObservationStatistics(BaseModel):
    """Delivery statistics produced by the tracker for evaluation reporting."""

    delivered_observations: int = 0
    rejected_observations: int = 0
    rejected_out_of_sequence: int = 0
    rejected_invalid: int = 0
    pending_observations: int = 0
    age_samples: int = 0
    mean_age_of_information: float | None = None

    # Vision-specific observation acceptance (only populated when use_vision=True)
    vision_generated: int = 0
    vision_delivered: int = 0
    vision_gate_rejected: int = 0
    vision_lost_competition: int = 0
    vision_unassigned_other: int = 0
    vision_applied: int = 0
    # Delivered but rejected before/after association (stale, invalid, update failure)
    vision_invalid_or_stale: int = 0


class EvaluationResult(BaseModel):
    """
    Evaluation results for one method on one scenario/seed.

    Metric definitions are documented in ``docs/metrics.md``. A metric that is
    not defined for a run is ``None``; it is never silently reported as zero.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    scenario_name: str
    seed: int
    method_name: str

    # Accuracy metrics (matched track/object samples)
    position_rmse: float | None = None
    velocity_rmse: float | None = None

    # Track/object matching metrics (see docs/metrics.md)
    precision: float | None = None  # matched samples / confirmed track samples
    recall: float | None = None  # matched samples / ground-truth object samples
    identity_switches: int | None = None
    track_fragmentation: float | None = None  # unsupported in v0.1
    matched_samples: int = 0
    ground_truth_samples: int = 0
    confirmed_track_samples: int = 0
    unmatched_ground_truth_samples: int = 0
    unmatched_track_samples: int = 0
    coverage_samples: int = 0
    evaluated_frames: int = 0
    matching_gate_m: float = 2.0

    # Timing
    mean_age_of_information: float | None = None
    rejected_observations: int = 0
    rejected_out_of_sequence: int = 0
    rejected_invalid: int = 0
    delivered_observations: int = 0
    pending_observations: int = 0
    age_samples: int = 0

    # Vision-specific observation acceptance (only populated when use_vision=True)
    vision_generated: int = 0
    vision_delivered: int = 0
    vision_gate_rejected: int = 0
    vision_lost_competition: int = 0
    vision_unassigned_other: int = 0
    vision_applied: int = 0
    # Delivered but rejected before/after association (stale, invalid, update failure)
    vision_invalid_or_stale: int = 0

    # Uncertainty calibration
    position_coverage_95: float | None = None
    position_coverage_68: float | None = None

    # Track statistics
    num_tracks: int = 0
    num_confirmed_tracks: int = 0
    num_unmatched_confirmed_tracks: int = 0
    num_duplicate_tracks: int = 0
    duplicate_track_samples: int = 0

    # Raw data for detailed analysis
    per_frame_metrics: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    config: dict[str, Any] = Field(default_factory=dict)
    git_commit: str | None = None
    notes: list[str] = Field(default_factory=list)


# Update forward references
WorldState.model_rebuild()
