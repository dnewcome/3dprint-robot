#!/usr/bin/env python3
"""
sweep.py — animated workspace demo for the 3-DOF cycloid trunk.

Use this when the interactive Control sliders won't cooperate (e.g. MuJoCo's
in-window UI under native Wayland). It drives the joints through a smooth
choreographed motion so you can SEE the arm articulate and sweep its reach
envelope — no slider dragging required. You can still orbit/zoom with the mouse.

    pip install mujoco
    python sim/sweep.py            # forces XWayland for reliable input
    python sim/sweep.py --pose 20 45 -65   # hold one static pose (degrees)

Joints are posed kinematically (qpos set directly + mj_forward), so the motion
is exact and independent of mass/servo tuning.
"""
import os, sys, math, time
import mujoco
import mujoco.viewer
from view import build_model, URDF  # reuse the same model (URDF + servos)


def main():
    args = sys.argv[1:]
    model = build_model()
    data = mujoco.MjData(model)
    tcp = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "tcp_link")

    static = None
    if args and args[0] == "--pose":
        static = [math.radians(float(x)) for x in args[1:4]]

    with mujoco.viewer.launch_passive(model, data) as viewer:
        t = 0.0
        while viewer.is_running():
            if static is not None:
                q = static
            else:
                # gentle Lissajous-style sweep within each joint's range
                q = [1.4 * math.sin(t * 0.40),
                     0.9 * math.sin(t * 0.61) + 0.3,
                    -1.3 * math.sin(t * 0.83)]
            data.qpos[:3] = q
            data.ctrl[:3] = q          # keep servos in sync if physics steps
            mujoco.mj_forward(model, data)
            viewer.sync()
            tip = data.xpos[tcp]
            reach = math.hypot(tip[0], tip[1])
            print(f"\r  q=({math.degrees(q[0]):6.1f},{math.degrees(q[1]):6.1f},"
                  f"{math.degrees(q[2]):6.1f})deg  tip=({tip[0]:.3f},{tip[1]:.3f},"
                  f"{tip[2]:.3f})  radial={reach:.3f}m   ", end="", flush=True)
            if static is not None:
                time.sleep(0.05)
                continue
            t += 0.02
            time.sleep(0.02)


if __name__ == "__main__":
    main()
