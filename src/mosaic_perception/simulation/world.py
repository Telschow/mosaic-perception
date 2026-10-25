"""
Synthetic world simulation with deterministic ground truth.
"""

from __future__ import annotations

import math

import numpy as np

from ..domain.models import ObjectClass, ObjectState, Pose2D, Vector2, WorldState


class SyntheticWorld:
    """
    Deterministic 2D synthetic environment with known ground truth.

    Object trajectories are piecewise-analytic so position and velocity are
    consistent at every sampled time. The observer pose includes both heading
    and world-frame velocity; sensors use the pose at capture time.
    """

    def __init__(
        self,
        seed: int = 42,
        duration: float = 10.0,
        dt: float = 0.1,
        num_objects: int = 3,
        observer_trajectory: str = "static",
        target_layout: str = "random",
    ):
        if target_layout not in ("random", "crossing"):
            raise ValueError(f"unknown target_layout {target_layout!r}")
        if dt <= 0:
            raise ValueError("dt must be positive")
        if duration < 0:
            raise ValueError("duration must be non-negative")
        self.seed = seed
        self.duration = duration
        self.dt = dt
        self.num_objects = num_objects
        self.observer_trajectory = observer_trajectory
        self.target_layout = target_layout

        self.rng = np.random.RandomState(seed)
        # Number of steps: inclusive of t=0 and the final step <= duration.
        n_steps = int(math.floor(duration / dt + 1e-9)) + 1
        self.time_steps = np.arange(n_steps) * dt

        self.object_trajectories = self._generate_trajectories()
        self.observer_trajectories = self._generate_observer_trajectory()

    def _generate_trajectories(self) -> dict[str, list[ObjectState]]:
        """Generate deterministic object trajectories."""
        if self.target_layout == "crossing":
            return self._generate_crossing_trajectories()
        trajectories: dict[str, list[ObjectState]] = {}
        classes = [ObjectClass.UNKNOWN, ObjectClass.VEHICLE, ObjectClass.PEDESTRIAN]

        for i in range(self.num_objects):
            obj_id = f"obj_{i:03d}"
            states: list[ObjectState] = []

            x0 = float(self.rng.uniform(-20, 20))
            y0 = float(self.rng.uniform(-20, 20))
            vx0 = float(self.rng.uniform(-2, 2))
            vy0 = float(self.rng.uniform(-2, 2))

            traj_type = str(self.rng.choice(["constant_vel", "sinusoid", "turning"]))
            obj_class = classes[int(self.rng.randint(0, len(classes)))]

            speed = float(np.hypot(vx0, vy0))
            omega = float(self.rng.uniform(-0.2, 0.2))
            if speed < 0.5:
                speed = 1.0
                heading0 = 0.0
            else:
                heading0 = float(np.arctan2(vy0, vx0))

            for t in self.time_steps:
                tf = float(t)
                if traj_type == "constant_vel":
                    x, y, vx, vy = x0 + vx0 * tf, y0 + vy0 * tf, vx0, vy0
                elif traj_type == "sinusoid":
                    x = x0 + vx0 * tf
                    y = y0 + vy0 * tf + 3.0 * np.sin(0.5 * tf)
                    vx = vx0
                    vy = vy0 + 1.5 * np.cos(0.5 * tf)
                elif traj_type == "turning":
                    angle = heading0 + omega * tf
                    vx = speed * np.cos(angle)
                    vy = speed * np.sin(angle)
                    # Closed-form integral of the constant-turn velocity.
                    x = x0 + (speed / omega) * (np.sin(angle) - np.sin(heading0))
                    y = y0 - (speed / omega) * (np.cos(angle) - np.cos(heading0))
                else:  # pragma: no cover - defensive
                    raise ValueError(f"unknown trajectory type {traj_type!r}")

                states.append(
                    ObjectState(
                        object_id=obj_id,
                        position=Vector2(x=float(x), y=float(y)),
                        velocity=Vector2(x=float(vx), y=float(vy)),
                        true_class=obj_class,
                        visible=True,
                    )
                )

            trajectories[obj_id] = states

        return trajectories

    def _generate_crossing_trajectories(self) -> dict[str, list[ObjectState]]:
        """Constant-velocity targets whose paths cross at mid-run.

        Every target moves at 2 m/s on its own heading (headings spaced by
        pi / num_objects) and passes the seeded crossing point at
        ``duration / 2``. Target ``i`` is offset by ``0.5 * (i - (n - 1) / 2)``
        m along the x axis at that instant, so adjacent targets are 0.5 m
        apart there and targets ``k`` apart are ``0.5 * k`` m apart, all inside
        the 2 m matching gate for up to five targets. With one target this is
        just a straight line.
        """
        speed = 2.0
        crossing_time = self.duration / 2.0
        centre = self.rng.uniform(-10.0, 10.0, size=2)
        classes = [ObjectClass.VEHICLE, ObjectClass.PEDESTRIAN, ObjectClass.UNKNOWN]
        trajectories: dict[str, list[ObjectState]] = {}
        n = self.num_objects
        for i in range(n):
            heading = i * math.pi / max(n, 1)
            vx, vy = speed * math.cos(heading), speed * math.sin(heading)
            offset_x = 0.5 * (i - (n - 1) / 2.0)
            cross_x, cross_y = float(centre[0]) + offset_x, float(centre[1])
            states = [
                ObjectState(
                    object_id=f"obj_{i:03d}",
                    position=Vector2(
                        x=cross_x + vx * (float(t) - crossing_time),
                        y=cross_y + vy * (float(t) - crossing_time),
                    ),
                    velocity=Vector2(x=vx, y=vy),
                    true_class=classes[i % len(classes)],
                    visible=True,
                )
                for t in self.time_steps
            ]
            trajectories[f"obj_{i:03d}"] = states
        return trajectories

    def _generate_observer_trajectory(self) -> list[Pose2D]:
        """Generate observer poses, including world-frame velocity."""
        poses: list[Pose2D] = []
        if self.observer_trajectory == "static":
            for _ in self.time_steps:
                poses.append(
                    Pose2D(
                        position=Vector2(x=0.0, y=0.0),
                        heading=0.0,
                        velocity=Vector2(x=0.0, y=0.0),
                    )
                )
        elif self.observer_trajectory == "circle":
            radius = 10.0
            omega = 0.2
            for t in self.time_steps:
                tf = float(t)
                heading = omega * tf + np.pi / 2
                poses.append(
                    Pose2D(
                        position=Vector2(
                            x=float(radius * np.cos(omega * tf)),
                            y=float(radius * np.sin(omega * tf)),
                        ),
                        heading=float(np.arctan2(np.sin(heading), np.cos(heading))),
                        velocity=Vector2(
                            x=float(-radius * omega * np.sin(omega * tf)),
                            y=float(radius * omega * np.cos(omega * tf)),
                        ),
                    )
                )
        else:
            raise ValueError(
                f"unknown observer_trajectory {self.observer_trajectory!r}; "
                "available: static, circle"
            )
        return poses

    def get_world_state(self, t_idx: int) -> WorldState:
        """Get world state at time step index."""
        t = self.time_steps[t_idx]
        objects = {obj_id: traj[t_idx] for obj_id, traj in self.object_trajectories.items()}
        observer_pose = self.observer_trajectories[t_idx]
        return WorldState(time=float(t), objects=objects, observer_pose=observer_pose)

    def get_all_states(self) -> list[WorldState]:
        """Get all world states."""
        return [self.get_world_state(i) for i in range(len(self.time_steps))]
