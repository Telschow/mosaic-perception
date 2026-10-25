"""Shared hand-constructed fixtures for unit and integration tests."""

from __future__ import annotations

import numpy as np

from mosaic_perception.domain.models import (
    ObjectState,
    Pose2D,
    SensorObservation,
    TrackEstimate,
    TrackSnapshot,
    TrackStatus,
    Vector2,
    WorldState,
)


def make_pose(heading: float = 0.0) -> Pose2D:
    return Pose2D(
        position=Vector2(x=0.0, y=0.0),
        heading=heading,
        velocity=Vector2(x=0.0, y=0.0),
    )


def make_track(
    track_id: str = "track_0000",
    position: tuple[float, float] = (10.0, 0.0),
    velocity: tuple[float, float] = (0.0, 0.0),
    *,
    status: TrackStatus = TrackStatus.TENTATIVE,
    hits: int = 0,
    misses: int = 0,
) -> TrackEstimate:
    return TrackEstimate(
        track_id=track_id,
        status=status,
        time=0.0,
        last_update_time=0.0,
        state=[position[0], position[1], velocity[0], velocity[1]],
        covariance=np.eye(4).tolist(),
        hits=hits,
        misses=misses,
    )


def make_observation(
    observation_id: str,
    sensor_type: str,
    measurements: dict[str, float],
    covariance: list[list[float]],
    capture_time: float = 0.0,
    delivery_time: float = 0.0,
    pose: Pose2D | None = None,
) -> SensorObservation:
    return SensorObservation(
        observation_id=observation_id,
        sensor_id="range1" if sensor_type == "range_bearing" else "vision1",
        sensor_type=sensor_type,
        capture_time=capture_time,
        delivery_time=delivery_time,
        measurement_model=(
            "range_bearing_sensor_frame"
            if sensor_type == "range_bearing"
            else "bearing_sensor_frame"
        ),
        measurements=measurements,
        measurement_covariance=covariance,
        observer_pose=pose or make_pose(),
    )


def range_observation(
    observation_id: str = "range-obs",
    distance: float = 10.0,
    bearing: float = 0.0,
    range_rate: float = 0.0,
    capture_time: float = 0.0,
    delivery_time: float = 0.0,
) -> SensorObservation:
    return make_observation(
        observation_id,
        "range_bearing",
        {"range": distance, "bearing": bearing, "range_rate": range_rate},
        [[0.25, 0.0, 0.0], [0.0, 1e-4, 0.0], [0.0, 0.0, 0.01]],
        capture_time,
        delivery_time,
    )


def vision_observation(
    observation_id: str = "vision-obs",
    bearing: float = 0.0,
    capture_time: float = 0.0,
    delivery_time: float = 0.0,
) -> SensorObservation:
    return make_observation(
        observation_id,
        "vision_bearing",
        {"bearing": bearing},
        [[2.5e-5]],
        capture_time,
        delivery_time,
    )


def make_snapshot(
    time: float,
    track_id: str,
    position: tuple[float, float],
    velocity: tuple[float, float] = (0.0, 0.0),
    *,
    status: TrackStatus = TrackStatus.CONFIRMED,
    covariance: np.ndarray | None = None,
) -> TrackSnapshot:
    state = [position[0], position[1], velocity[0], velocity[1]]
    return TrackSnapshot(
        time=time,
        track_id=track_id,
        status=status,
        state=state,
        covariance=(covariance if covariance is not None else np.eye(4)).tolist(),
    )


def make_world_state(
    time: float,
    objects: dict[str, tuple[tuple[float, float], tuple[float, float]]],
) -> WorldState:
    return WorldState(
        time=time,
        objects={
            object_id: ObjectState(
                object_id=object_id,
                position=Vector2(x=position[0], y=position[1]),
                velocity=Vector2(x=velocity[0], y=velocity[1]),
            )
            for object_id, (position, velocity) in objects.items()
        },
    )
