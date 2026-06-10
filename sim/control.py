#!/usr/bin/env python3
"""
control.py — model-based closed-loop IK (the "executor").

A damped-least-squares position controller: read the arm's MEASURED joint
angles, compute the tool Jacobian from a kinematic MODEL, and nudge the joints
to drive the tool tip toward an XYZ target. It talks only through
RobotInterface, so it drives SimRobot or RealRobot unchanged.

This is the classical layer. An LLM planner or RL policy plugs in ABOVE it by
choosing the targets (or, for RL, replacing step_toward with a learned action).
"""
import os
import numpy as np
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
URDF = os.path.join(HERE, "arm_trunk.urdf")


class IKController:
    """Owns a kinematic model (FK + Jacobian). Hardware-agnostic: works for sim
    and real, since it uses MEASURED joint angles, not the sim's internals."""

    def __init__(self, urdf=URDF, damping=0.05, gain=0.25, max_step=0.02):
        self.m = mujoco.MjModel.from_xml_path(urdf)   # massless kinematics only
        self.d = mujoco.MjData(self.m)
        self.n = self.m.nv
        self.tcp = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, "tcp_link")
        self.lo = self.m.jnt_range[:, 0].copy()
        self.hi = self.m.jnt_range[:, 1].copy()
        self.damping = damping        # DLS lambda (stability near singularities)
        self.gain = gain              # fraction of error to chase per step
        self.max_step = max_step      # max joint move per step (rad)

    def fk(self, q):
        self.d.qpos[:self.n] = q
        mujoco.mj_forward(self.m, self.d)
        return self.d.xpos[self.tcp].copy()

    def jac(self, q):
        self.d.qpos[:self.n] = q
        mujoco.mj_forward(self.m, self.d)
        Jp = np.zeros((3, self.n))
        mujoco.mj_jac(self.m, self.d, Jp, None, self.d.xpos[self.tcp], self.tcp)
        return Jp

    def reset(self, q0):
        """Seed the internal joint reference (the integrator state)."""
        self.q_ref = np.array(q0, float)

    def solve_ik(self, target, q_seed, iters=3000, tol=1e-4):
        """Absolute kinematic IK: joint config whose tip is at `target` (XYZ).
        Used by the planner to turn a grasp pose into a goal configuration."""
        q = np.array(q_seed, float)
        err = 1e9
        for _ in range(iters):
            x = self.fk(q)
            e = np.asarray(target, float) - x
            err = np.linalg.norm(e)
            if err < tol:
                break
            J = self.jac(q)
            JJt = J @ J.T + (self.damping ** 2) * np.eye(3)
            q = np.clip(q + J.T @ np.linalg.solve(JJt, e),
                        self.lo[:self.n], self.hi[:self.n])
        return q, float(err)

    def step_toward(self, q_meas, tcp_measured, x_target):
        """Integral feedback on the MEASURED tip: grow an internal joint
        reference until the real tool tip hits the target (absorbs gravity droop
        and disturbances without windup). Jacobian is taken at the ACTUAL pose.
        Returns (q_command, tip_error_m)."""
        err = np.asarray(x_target, float) - np.asarray(tcp_measured, float)
        J = self.jac(q_meas)
        JJt = J @ J.T + (self.damping ** 2) * np.eye(3)
        dq = np.clip(J.T @ np.linalg.solve(JJt, err) * self.gain,
                     -self.max_step, self.max_step)
        self.q_ref = np.clip(self.q_ref + dq, self.lo[:self.n], self.hi[:self.n])
        return self.q_ref.copy(), float(np.linalg.norm(err))


def reach(robot, controller, target, tol=0.002, max_ticks=800, dt=0.02,
          settle=10, cart_speed=0.15):
    """Closed loop: drive robot's TCP to `target` (XYZ) using MEASURED feedback.
    The Cartesian SETPOINT is ramped from the current tip to the target at
    cart_speed (m/s) so the arm moves smoothly instead of lurching -- which also
    keeps the tracking error small, so the integrator never winds up. Returns
    (reached, tip_error_m)."""
    target = np.asarray(target, float)
    controller.reset(robot.get_joint_positions())
    sp = robot.get_tcp_pose().copy()       # setpoint starts at the current tip
    good = 0
    for _ in range(max_ticks):
        d = target - sp                    # advance setpoint toward goal
        dist = np.linalg.norm(d)
        sp = target.copy() if dist <= cart_speed*dt else sp + d/dist*cart_speed*dt
        tcp = robot.get_tcp_pose()
        q_cmd, _ = controller.step_toward(robot.get_joint_positions(), tcp, sp)
        robot.set_joint_targets(q_cmd)
        robot.step(dt)
        err = float(np.linalg.norm(target - robot.get_tcp_pose()))
        good = good + 1 if (err < tol and np.array_equal(sp, target)) else 0
        if good >= settle:
            return True, err
    return False, float(np.linalg.norm(target - robot.get_tcp_pose()))


def trace_path(robot, controller, segments, dt=0.02, record=True):
    """Follow a CONTINUOUS Cartesian path (for drawing / dispensing / G-code).
    `segments` = list of (xyz_target, speed_m_s). The setpoint advances along the
    polyline at each segment's speed WITHOUT stopping at the waypoints, so the
    tip traces a smooth path. Returns the recorded tip trajectory (N,3) if
    `record`, for accuracy checking against the commanded path."""
    controller.reset(robot.get_joint_positions())
    sp = robot.get_tcp_pose().copy()
    traj = []
    def tick(setpoint):
        q_cmd, _ = controller.step_toward(robot.get_joint_positions(),
                                          robot.get_tcp_pose(), setpoint)
        robot.set_joint_targets(q_cmd)
        robot.step(dt)
        if record:
            traj.append(robot.get_tcp_pose().copy())
    for tgt, speed in segments:
        tgt = np.asarray(tgt, float)
        while np.linalg.norm(tgt - sp) > speed*dt:
            d = tgt - sp
            sp = sp + d/np.linalg.norm(d)*speed*dt
            tick(sp)
        sp = tgt.copy()
        tick(sp)
    for _ in range(15):                    # settle on the final point
        tick(sp)
    return np.array(traj) if record else None
