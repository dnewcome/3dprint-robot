#!/usr/bin/env python3
"""
twin_demo.py — the digital-twin foundation, end to end.

    python sim/twin_demo.py            # closed-loop reach-to-target, in the viewer
    python sim/twin_demo.py fidelity   # measure sim-vs-"real" fidelity (headless)

REACH demo: a classical IK controller drives the tool tip to a sequence of XYZ
targets using POSITION FEEDBACK, under real gravity/friction physics. This is
the loop an LLM (choosing targets) or an RL policy (replacing the controller)
plugs into -- everything talks through RobotInterface, so swapping in RealRobot
later changes nothing above it.

FIDELITY demo: the honest version of "how close is the sim to reality." We treat
one model as the TRUTH (the real arm) and another as our TWIN with mismatched
parameters (friction, mass), replay the SAME joint commands open-loop on both,
and measure how far their tool tips drift apart. On real hardware you'd do
exactly this -- command a trajectory, compare to logged encoder positions -- and
then tune the twin's params to shrink the error (system identification).
"""
import sys
import numpy as np
import gravity
from robot import SimRobot
from control import IKController, reach

TARGETS = [
    [0.25,  0.00, 0.35],
    [0.20,  0.12, 0.40],
    [0.15, -0.12, 0.45],
    [0.28,  0.00, 0.30],
    [0.05,  0.00, 0.55],
]


def reach_demo():
    robot = SimRobot(render=True, realtime=True)
    ctrl = IKController()
    print("Closed-loop reach. Tool tip chases each target using feedback.\n")
    try:
        while robot.viewer is None or robot.viewer.is_running():
            for tgt in TARGETS:
                ok, err = reach(robot, ctrl, np.array(tgt), max_ticks=800)
                tcp = robot.get_tcp_pose()
                print(f"  target {np.round(tgt,2)} -> reached={ok}  "
                      f"err={err*1000:4.1f}mm  tip={np.round(tcp,3)}")
                if robot.viewer is not None and not robot.viewer.is_running():
                    break
    finally:
        robot.close()


def _record_commands(target_seq):
    """Closed-loop on the TRUTH model; log the joint command trajectory."""
    gravity.FRICTION[:] = [1.0, 1.0, 1.0, 0.5, 0.5]
    truth = SimRobot(render=False)
    ctrl = IKController()
    cmds = []
    for tgt in target_seq:
        ctrl.reset(truth.get_joint_positions())
        for _ in range(400):
            tcp = truth.get_tcp_pose()
            q_cmd, _ = ctrl.step_toward(truth.get_joint_positions(), tcp, np.array(tgt))
            truth.set_joint_targets(q_cmd); truth.step(0.02)
            cmds.append(q_cmd.copy())
    return np.array(cmds)


def _replay(cmds, friction, mass_scale):
    """Open-loop replay of the same commands on a model with given params; log tip."""
    gravity.FRICTION[:] = friction
    base = dict(gravity.LINKS)
    for k in ("upper_arm_link", "forearm_link", "wrist_link"):
        m, com = base[k]; gravity.LINKS[k] = (m * mass_scale, com)
    robot = SimRobot(render=False)
    tips = []
    for q in cmds:
        robot.set_joint_targets(q); robot.step(0.02)
        tips.append(robot.get_tcp_pose())
    gravity.LINKS.update(base)            # restore
    return np.array(tips)


def fidelity_demo():
    print("="*60)
    print("FIDELITY: replay identical commands, compare tool-tip paths")
    print("="*60)
    cmds = _record_commands(TARGETS)
    truth = _replay(cmds, [1.0, 1.0, 1.0, 0.5, 0.5], 1.00)     # the "real" arm
    print(f"recorded {len(cmds)} command steps on the truth model\n")
    print(f"{'twin parameter error':<34}{'RMS tip':>10}{'max tip':>10}")
    for label, fr, ms in [
            ("perfect twin (same params)",       [1.0,1.0,1.0,0.5,0.5], 1.00),
            ("friction +50%",                    [1.5,1.5,1.5,0.75,0.75],1.00),
            ("links +15% mass",                  [1.0,1.0,1.0,0.5,0.5], 1.15),
            ("friction +50% AND +15% mass",      [1.5,1.5,1.5,0.75,0.75],1.15)]:
        twin = _replay(cmds, fr, ms)
        d = np.linalg.norm(truth - twin, axis=1)
        print(f"{label:<34}{d.mean()*1000:8.1f}mm{d.max()*1000:8.1f}mm")
    print("\nOn real hardware: 'truth' = logged encoder positions; you TUNE the")
    print("twin's params to drive RMS toward zero. That number is your fidelity.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fidelity":
        fidelity_demo()
    else:
        reach_demo()
