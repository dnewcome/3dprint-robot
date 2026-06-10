#!/usr/bin/env python3
"""
view.py — interactive KEYBOARD poser for the 3-DOF cycloid trunk.

    pip install mujoco
    python sim/view.py

Why keyboard, not sliders: MuJoCo's bundled GLFW here is a Wayland-only build,
and its in-window UI slider widgets don't accept mouse drags under native
Wayland (camera orbit works, sliders don't). Keyboard events DO go through, so
we pose the joints with keys instead — reliable on this setup.

CONTROLS (focus the viewer window):
    J1 base yaw :  Q / A   (+ / -)
    J2 shoulder :  W / S
    J3 elbow    :  E / D
    reset pose  :  R
    mouse       :  orbit / pan / zoom the camera (works fine)

Joints are posed kinematically (qpos set directly), so motion is exact and
nothing sags — ideal for reach / workspace / posing. The live tip position and
radial reach print to the console as you move.
"""
import os, math
import mujoco
import mujoco.viewer

HERE = os.path.dirname(os.path.abspath(__file__))
URDF = os.path.join(HERE, "arm_trunk.urdf")

KP, KV = 40.0, 2.0          # servo gains (used if you step physics instead)
STEP = math.radians(3.0)    # keypress increment


def build_model():
    """Load the URDF and graft a position servo onto each joint."""
    spec = mujoco.MjSpec.from_file(URDF)
    for j in spec.joints:
        a = spec.add_actuator()
        a.name, a.target = j.name, j.name
        a.trntype = mujoco.mjtTrn.mjTRN_JOINT
        a.gaintype = mujoco.mjtGain.mjGAIN_FIXED
        a.gainprm[0] = KP
        a.biastype = mujoco.mjtBias.mjBIAS_AFFINE
        a.biasprm[1], a.biasprm[2] = -KP, -KV
        a.ctrllimited = mujoco.mjtLimited.mjLIMITED_TRUE
        a.ctrlrange[0], a.ctrlrange[1] = j.range[0], j.range[1]
    return spec.compile()


def main():
    model = build_model()
    data = mujoco.MjData(model)
    tcp = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "tcp_link")
    lo = model.jnt_range[:, 0].copy()
    hi = model.jnt_range[:, 1].copy()

    # The joint TARGET lives in data.ctrl (length nu=3). The Control-tab sliders
    # write it; the keys below also write it. The loop never overwrites it, so
    # sliders no longer snap back. data.qpos just mirrors the target (kinematic
    # posing — no gravity sag, exact).
    BIND = {ord('Q'): (0, +1), ord('A'): (0, -1),   # GLFW: uppercase ASCII
            ord('W'): (1, +1), ord('S'): (1, -1),
            ord('E'): (2, +1), ord('D'): (2, -1),
            ord('R'): (3, +1), ord('F'): (3, -1),   # J4 wrist pitch
            ord('T'): (4, +1), ord('G'): (4, -1)}   # J5 tool roll

    def on_key(keycode):
        if keycode == ord('X'):
            data.ctrl[:model.nu] = 0.0
        elif keycode in BIND:
            i, s = BIND[keycode]
            if i < model.nu:
                data.ctrl[i] = max(lo[i], min(hi[i], data.ctrl[i] + s * STEP))

    print(f"loaded {URDF}  (joints {model.njnt}, actuators {model.nu})")
    print("  sliders OR keys: Q/A=J1 W/S=J2 E/D=J3 R/F=J4(wrist) T/G=J5(roll) X=reset")

    with mujoco.viewer.launch_passive(model, data, key_callback=on_key) as viewer:
        n = model.nu
        while viewer.is_running():
            data.qpos[:n] = data.ctrl[:n]     # mirror target -> pose (no clobber)
            mujoco.mj_forward(model, data)
            viewer.sync()
            tip = data.xpos[tcp]
            reach = math.hypot(tip[0], tip[1])
            angs = ",".join(f"{math.degrees(data.ctrl[i]):.0f}" for i in range(n))
            print(f"\r  J=[{angs}]deg  tip=({tip[0]:.3f},{tip[1]:.3f},{tip[2]:.3f})m"
                  f"  radial={reach:.3f}m   ", end="", flush=True)


if __name__ == "__main__":
    main()
