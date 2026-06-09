#!/usr/bin/env python3
"""
view.py — load the cycloid trunk in the MuJoCo interactive viewer for
reach / workspace / posing exploration.

    pip install mujoco
    python sim/view.py

In the viewer: drag the joint sliders (or the body) to pose the arm, watch
the tool tip sweep its workspace, and eyeball self-collision. Gravity is on,
so with the placeholder inertials it will also sag toward a rest pose — that's
expected at this stage (real torque/sag work comes with proper inertias).

MuJoCo reads the URDF directly. The <mujoco><compiler> block inside
arm_trunk.urdf keeps the visual geoms and auto-balances inertia on import.
"""
import os
import mujoco
import mujoco.viewer

HERE = os.path.dirname(os.path.abspath(__file__))
URDF = os.path.join(HERE, "arm_trunk.urdf")


def main():
    model = mujoco.MjModel.from_xml_path(URDF)
    data = mujoco.MjData(model)

    # report the kinematic chain + reach at zero pose
    print(f"loaded {URDF}")
    print(f"  joints: {model.njnt}   bodies: {model.nbody}")
    mujoco.mj_forward(model, data)
    tcp_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "tcp_link")
    tip = data.xpos[tcp_id]
    print(f"  TCP world pos @ zero pose: "
          f"({tip[0]:.3f}, {tip[1]:.3f}, {tip[2]:.3f}) m")

    mujoco.viewer.launch(model, data)


if __name__ == "__main__":
    main()
