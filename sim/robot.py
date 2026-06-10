#!/usr/bin/env python3
"""
robot.py — the digital-twin seam.

ONE interface (RobotInterface) that both the simulator and the real arm
implement. Control / IK / AI code talks only to this interface, so the SAME
code drives the sim today and the hardware later -- and running both against
the same commands is exactly how you measure sim-to-real fidelity.

    RobotInterface   - abstract contract (positions in, targets out)
    SimRobot         - MuJoCo implementation (uses gravity.py's physics model)
    RealRobot        - stub: implement against your drivers + output encoders

Keep MuJoCo "dumb": it only steps physics and reports state. The brain lives
above this interface.
"""
from abc import ABC, abstractmethod
import time
import numpy as np
import mujoco
import mujoco.viewer


class RobotInterface(ABC):
    """Position-controlled arm. Units: radians, meters, seconds."""
    n_joints: int
    joint_names: list

    @abstractmethod
    def get_joint_positions(self) -> np.ndarray: ...
    @abstractmethod
    def get_joint_velocities(self) -> np.ndarray: ...
    @abstractmethod
    def set_joint_targets(self, q: np.ndarray) -> None: ...
    @abstractmethod
    def get_tcp_pose(self) -> np.ndarray:
        """World XYZ of the tool tip (3,)."""
    def step(self, dt: float = 0.02) -> None:
        """Advance/refresh by ~dt seconds (sim: integrate; real: just wait)."""
    def close(self) -> None: ...


class SimRobot(RobotInterface):
    """MuJoCo twin. Reuses gravity.py's model (real masses, force-limited
    position servos, friction/non-backdrivability)."""

    def __init__(self, render=False, realtime=True):
        import gravity
        self.m = gravity.build()
        self.d = mujoco.MjData(self.m)
        self.n_joints = self.m.nu
        self.joint_names = [mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
                            for i in range(self.m.nu)]
        self._tcp = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, "tcp_link")
        self._lo = self.m.jnt_range[:, 0].copy()
        self._hi = self.m.jnt_range[:, 1].copy()
        # start folded & stable
        self.d.qpos[:self.n_joints] = [0, 0.6, -1.0, 0, 0][:self.n_joints]
        self.d.ctrl[:self.n_joints] = self.d.qpos[:self.n_joints]
        mujoco.mj_forward(self.m, self.d)
        self._sub = max(1, int(round(0.02 / self.m.opt.timestep)))
        self._realtime = realtime
        self.viewer = None
        if render:
            self.viewer = mujoco.viewer.launch_passive(self.m, self.d)

    def get_joint_positions(self): return self.d.qpos[:self.n_joints].copy()
    def get_joint_velocities(self): return self.d.qvel[:self.n_joints].copy()

    def set_joint_targets(self, q):
        self.d.ctrl[:self.n_joints] = np.clip(q, self._lo, self._hi)

    def get_tcp_pose(self): return self.d.xpos[self._tcp].copy()

    def step(self, dt=0.02):
        t0 = time.time()
        for _ in range(int(round(dt / self.m.opt.timestep))):
            mujoco.mj_step(self.m, self.d)
        if self.viewer is not None:
            self.viewer.sync()
            if self._realtime:
                lag = dt - (time.time() - t0)
                if lag > 0: time.sleep(lag)

    def close(self):
        if self.viewer is not None: self.viewer.close()


class RealRobot(RobotInterface):
    """STUB for the physical arm. Implement each method against your stack:

      get_joint_positions -> read the output-side magnetic encoders (AS5048/
                             MT6701), convert counts -> radians.
      get_joint_velocities-> differentiate encoders, or read driver velocity.
      set_joint_targets   -> command each motor driver to a joint angle
                             (step/dir target for steppers, or FOC position).
      get_tcp_pose        -> forward kinematics from the encoder angles, using
                             the SAME kinematic model the IK controller uses.
      step                -> sleep to the control period (the real world
                             integrates itself).

    Because it satisfies RobotInterface, the IK/AI code above it is unchanged.
    """
    def __init__(self, *a, **k):
        raise NotImplementedError(
            "RealRobot is a stub — wire it to your encoders + motor drivers. "
            "It just has to satisfy RobotInterface; nothing above it changes.")
