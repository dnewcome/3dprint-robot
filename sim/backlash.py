#!/usr/bin/env python3
"""
backlash.py — per-joint backlash -> tool-tip error budget.

Backlash isn't a native joint property in URDF/MuJoCo; you model its effect.
What matters for the arm is how each joint's lash shows up at the TOOL TIP:
a joint's backlash beta (deg) lets the tip wander by beta(rad) x (lever arm
from that joint's axis to the tip). The lever arm is exactly the translational
Jacobian column for that joint, so we read it straight from MuJoCo.

Worst case (all joints lash the same way) = sum of contributions. This is the
number that justifies low-backlash cycloidal drives over planetary gearboxes.

    pip install mujoco
    python sim/backlash.py

Set BACKLASH_DEG per joint below. Compare drive types at the bottom.
"""
import os, math
import numpy as np
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
URDF = os.path.join(HERE, "arm_trunk.urdf")

# ---- per-joint backlash spec (degrees at the joint output) ----
# printed cycloidal w/ tight roller clearance ~ 0.1-0.3 deg; planetary ~ 1 deg
BACKLASH_DEG = {
    "j1_yaw":         0.2,
    "j2_shoulder":    0.2,
    "j3_elbow":       0.2,
    "j4_wrist_pitch": 0.2,
    "j5_tool_roll":   0.2,
}
# worst-case pose for lever arms: arm reached out (it extends +X at q=0), with
# small bends so the tip is far from every joint axis -> biggest lever arms.
POSE_DEG = [0, 10, 20, 15, 0]


def tip_budget(backlash_deg, pose_deg=POSE_DEG, verbose=True):
    m = mujoco.MjModel.from_xml_path(URDF)
    d = mujoco.MjData(m)
    d.qpos[:m.nv] = np.radians(pose_deg)
    mujoco.mj_forward(m, d)
    tcp = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "tcp_link")
    point = d.xpos[tcp].copy()
    jacp = np.zeros((3, m.nv))
    mujoco.mj_jac(m, d, jacp, None, point, tcp)
    total = 0.0
    if verbose:
        print(f"{'joint':<16}{'backlash':>9}{'lever arm':>11}{'tip err':>10}")
    for i in range(m.nv):                               # one DOF per hinge joint
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.dof_jntid[i])
        arm = np.linalg.norm(jacp[:, i])               # m of tip motion per rad
        beta = math.radians(backlash_deg.get(name, 0))
        err = arm * beta * 1000                          # mm
        total += err
        if verbose:
            print(f"{name:<16}{backlash_deg.get(name,0):8.2f}d{arm*1000:9.0f}mm{err:9.2f}mm")
    if verbose:
        print(f"{'':16}{'':9}{'WORST-CASE TIP':>11}{total:9.2f}mm")
    return total


def main():
    print("="*52)
    print("BACKLASH -> TOOL-TIP ERROR BUDGET")
    print(f"pose (deg): {POSE_DEG}")
    print("="*52)
    print("\n[A] your spec (cycloidal, see BACKLASH_DEG):")
    tip_budget(BACKLASH_DEG)

    print("\n[B] compare drive types (same spec on all joints):")
    print(f"{'drive':<28}{'per-joint':>10}{'tip slop':>10}")
    for label, deg in [("printed cycloidal (tight)", 0.1),
                       ("printed cycloidal (loose)", 0.4),
                       ("planetary geared stepper", 1.0),
                       ("spur-gear / belt typical", 0.5)]:
        t = tip_budget({k: deg for k in BACKLASH_DEG}, verbose=False)
        print(f"{label:<28}{deg:8.2f}d{t:8.1f}mm")
    print("\n(worst case = all joints lash the same direction. RMS is ~2-3x smaller.)")


if __name__ == "__main__":
    main()
