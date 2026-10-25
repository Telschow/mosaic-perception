"""
Synthetic world simulation with deterministic ground truth.
"""

from __future__ import annotations

import numpy as np

from ..domain.models import ObjectClass, ObjectState, Pose2D, Vector2, WorldState


class SyntheticWorld:
    """
    Deterministic 2D synthetic environment with known ground truth.
    """

    def __init__(
        self,
        seed: int = 42,
        duration: float = 10.0,
        dt: float = 0.1,
        num_objects: int = 3,
        observer_trajectory: str = "static",
    ):
        self.seed = seed
        self.duration = duration
        self.dt = dt
        self.num_objects = num_objects
        self.observer_trajectory = observer_trajectory

        self.rng = np.random.RandomState(seed)
        self.time_steps = np.arange(0, duration + dt, dt)

        # Generate trajectories
        self.object_trajectories = self._generate_trajectories()
        self.observer_trajectories = self._generate_observer_trajectory()

    def _generate_trajectories(self) -> dict[str, list[ObjectState]]:
        """Generate deterministic object trajectories."""
        trajectories = {}
        classes = [ObjectClass.UNKNOWN, ObjectClass.VEHICLE, ObjectClass.PEDESTRIAN]

        for i in range(self.num_objects):
            obj_id = f"obj_{i:03d}"
            states = []

            # Random initial position
            x0 = float(self.rng.uniform(-20, 20))
            y0 = float(self.rng.uniform(-20, 20))
            # Random initial velocity
            vx0 = float(self.rng.uniform(-2, 2))
            vy0 = float(self.rng.uniform(-2, 2))

            # Create different trajectory types
            traj_type = self.rng.choice(["constant_vel", "sinusoid", "turning"])
            obj_class = classes[self.rng.randint(0, len(classes))]

            for t in self.time_steps:
                if traj_type == "constant_vel":
                    x, y, vx, vy = x0 + vx0 * t, y0 + vy0 * t, vx0, vy0
                elif traj_type == "sinusoid":
                    x = x0 + vx0 * t
                    y = y0 + vy0 * t + 3.0 * np.sin(0.5 * t)
                    vx = vx0
                    vy = vy0 + 1.5 * np.cos(0.5 * t)
                elif traj_type == "turning":
                    omega = float(self.rng.uniform(-0.2, 0.2))
                    speed = np.sqrt(vx0**2 + vy0**2)
                    if speed < 0.5:
                        speed = 1.0
                        vx0_init = speed
                        vy0_init = 0.0
                    else:
                        vx0_init = vx0
                        vy0_init = vy0
                    angle = np.arctan2(vy0_init, vx0_init) + omega * t
                    vx = speed * np.cos(angle)
                    vy = speed * np.sin(angle)
                    # Integrate
                    x = x0
                    y = y0
                    for tt in np.arange(self.dt, t + self.dt, self.dt):
                        a_ang = np.arctan2(vy0_init, vx0_init) + omega * tt
                        vx_t = speed * np.cos(a_ang)
                        vy_t = speed * np.sin(a_ang)
                        x += vx_t * self.dt
                        y += vy_t * self.dt
                else:
                    x, y, vx, vy = x0 + vx0 * t, y0 + vy0 * t, vx0, vy0

                obj_state = ObjectState(
                    object_id=obj_id,
                    position=Vector2(x=float(x), y=float(y)),
                    velocity=Vector2(x=float(vx), y=float(vy)),
                    true_class=obj_class,
                    visible=True,
                )
                states.append(obj_state)

            trajectories[obj_id] = states

        return trajectories

    def _generate_observer_trajectory(self) -> list[Pose2D]:
        """Generate observer trajectory."""
        poses = []
        for t in self.time_steps:
            if self.observer_trajectory == "static":
                pose = Pose2D(position=Vector2(x=0.0, y=0.0), heading=0.0)
            elif self.observer_trajectory == "circle":
                radius = 10.0
                omega = 0.2
                x = radius * np.cos(omega * t)
                y = radius * np.sin(omega * t)
                heading = omega * t + np.pi / 2
                pose = Pose2D(position=Vector2(x=float(x), y=float(y)), heading=float(heading))
            else:
                pose = Pose2D(position=Vector2(x=0.0, y=0.0), heading=0.0)
            poses.append(pose)
        return poses

    def get_world_state(self, t_idx: int) -> WorldState:
        """Get world state at time step index."""
        t = self.time_steps[t_idx]
        objects = {}
        for obj_id, traj in self.object_trajectories.items():
            objects[obj_id] = traj[t_idx]
        observer_pose = self.observer_trajectories[t_idx]
        return WorldState(time=float(t), objects=objects, observer_pose=observer_pose)

    def get_all_states(self) -> list[WorldState]:
        """Get all world states."""
        return [self.get_world_state(i) for i in range(len(self.time_steps))]
