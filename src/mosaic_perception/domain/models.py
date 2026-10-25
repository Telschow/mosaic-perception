"""
Domain models and data contracts for Mosaic.

All data structures follow explicit contracts to prevent mixing ground truth
with estimator inputs and to clearly distinguish timing, uncertainty, and metadata.
"""

from __future__ import annotations

import time
from enum import StrEnum
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    """2D vector representation."""

    x: float = 0.0
    y: float = 0.0

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> Vector2:
        return cls(x=float(arr[0]), y=float(arr[1]))


class Pose2D(BaseModel):
    """2D pose with position and heading."""

    position: Vector2 = Field(default_factory=Vector2)
    heading: float = 0.0  # radians

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
    sensor_type: str  # "range_bearing", "vision_bearing", etc.
    frame_rate: float = 10.0  # Hz
    noise_std: dict[str, float] = Field(default_factory=dict)
    detection_probability: float = 1.0
    false_alarm_rate: float = 0.0
    bias: dict[str, float] = Field(default_factory=dict)
    dropout_prob: float = 0.0
    delivery_delay_mean: float = 0.0
    delivery_delay_std: float = 0.0
    enabled: bool = True

    @field_validator("detection_probability")
    @classmethod
    def validate_detection_prob(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("detection_probability must be in [0,1]")
        return v


class ScenarioConfig(BaseModel):
    """Configuration for a simulation scenario."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str = ""
    seed: int = 42
    duration: float = 10.0  # seconds
    dt: float = 0.1  # time step
    num_objects: int = 3
    observer_trajectory: str = "static"

    # Degradation settings
    vision_dropout_rate: float = 0.0
    range_dropout_rate: float = 0.0
    measurement_bias_scale: float = 0.0
    delivery_delay_scale: float = 1.0
    false_observation_rate: float = 0.0
    uncertainty_miscalibration: float = 1.0  # scale factor for reported uncertainty

    # Sensor configurations
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
    delivery_time: float = Field(description="Time when observation was delivered to tracker")

    # Metadata
    coordinate_frame: CoordinateFrame = CoordinateFrame.SENSOR
    measurement_model: str = Field(description="Identifier for measurement model used")

    # Measurements (sensor-specific)
    measurements: dict[str, float] = Field(default_factory=dict)

    # Uncertainty
    measurement_covariance: list[list[float]] | None = None

    # Classification (for vision-like sensors)
    class_probs: dict[str, float] | None = None
    detection_confidence: float | None = None

    # Association (set by tracker, not by sensor)
    associated_track_id: str | None = None

    # Observer pose context for the estimator
    observer_pose: Pose2D | None = Field(
        default=None, description="Observer pose at capture time for estimation"
    )

    # For debugging/evaluation only - NEVER used by tracker
    _true_object_id: str | None = None  # Private, evaluation only

    def get_measurement_cov(self) -> np.ndarray | None:
        if self.measurement_covariance is None:
            return None
        return np.array(self.measurement_covariance)

    def age_of_information(self) -> float:
        """Time between capture and delivery."""
        return self.delivery_time - self.capture_time


class TrackEstimate(BaseModel):
    """Track estimate from the tracker."""

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
    hits: int = 0  # Number of successful updates
    misses: int = 0  # Number of missed updates/opportunities
    age: int = 0  # Track age in frames/epochs
    associated_observations: list[str] = Field(default_factory=list)

    # Metadata
    initiating_sensor: str | None = None
    class_estimate: ObjectClass = ObjectClass.UNKNOWN
    class_confidence: float = 0.0

    def state_array(self) -> np.ndarray:
        return np.array(self.state)

    def cov_array(self) -> np.ndarray:
        return np.array(self.covariance)

    def position(self) -> np.ndarray:
        return self.state_array()[:2]

    def velocity(self) -> np.ndarray:
        return self.state_array()[2:]

    def position_cov(self) -> np.ndarray:
        P = self.cov_array()
        return P[:2, :2]


class EvaluationResult(BaseModel):
    """Evaluation results for a run."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    scenario_name: str
    seed: int
    method_name: str
    timestamp: float = Field(default_factory=time.time)

    # Accuracy metrics
    position_rmse: float | None = None
    velocity_rmse: float | None = None

    # Detection/association metrics
    precision: float | None = None
    recall: float | None = None
    identity_switches: int = 0
    track_fragmentation: float | None = None

    # Timing
    mean_age_of_information: float | None = None

    # Uncertainty calibration
    position_coverage_95: float | None = None  # empirical coverage
    position_coverage_68: float | None = None

    # Track statistics
    num_tracks: int = 0
    num_confirmed_tracks: int = 0
    num_false_tracks: int = 0

    # Raw data for detailed analysis
    per_frame_metrics: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    config: dict[str, Any] = Field(default_factory=dict)
    git_commit: str | None = None
    notes: list[str] = Field(default_factory=list)


# Update forward references
WorldState.model_rebuild()
