#!/usr/bin/env python3
"""
gravity.py — DYNAMICS view: watch the arm hold or sag under gravity.

Unlike view.py (kinematic posing), this steps real physics:
  * gravity ON
  * realistic link masses (actuators + members), set below
  * each joint = a position servo whose force is CLAMPED to the actuator's real
    output torque -- so if a pose needs more torque than the motor can make,
    the joint visibly sags, exactly like the real arm.

The console prints each joint's live torque and flags any joint pulling MORE
than its continuous (thermal) limit -- it can hold there briefly, but it's
cooking the motor. That's the line the sizing analysis is about.

    pip install mujoco
    python sim/gravity.py
Controls: sliders, or keys Q/A W/S E/D R/F T/G (target angles), X = reset.
"""
import os, math, time
import numpy as np
import mujoco, mujoco.viewer

HERE = os.path.dirname(os.path.abspath(__file__))
URDF = os.path.join(HERE, "arm_trunk.urdf")

# ---- realistic config: current build = R20 (NEMA17,20:1) joints + Micro wrists ----
# link: (mass kg, COM [x,y,z] m)  -- dominant mass is each link's distal motor
LINKS = {
    "base_link":      (1.00, [0, 0,      0.030]),
    "mast_link":      (0.50, [0, 0,      0.050]),
    "upper_arm_link": (0.54, [0,  0.018, 0.150]),
    "forearm_link":   (0.52, [0, -0.018, 0.120]),
    "wrist_link":     (0.37, [0, -0.018, 0.030]),
    "tool_link":      (0.28, [0, 0,      0.040]),   # includes 250 g payload
    "tcp_link":       (0.001,[0, 0,      0]),
}
# per-joint actuator output torque (N*m): [J1,J2,J3,J4,J5]
TAU_PEAK = [6.16, 6.16, 6.16, 6.16, 6.16]   # holding/stall (NEMA17 x20 x0.7eff)
TAU_CONT = [3.70, 3.70, 3.70, 3.70, 3.70]   # continuous (thermal) limit
W0, ZETA = 30.0, 1.2                         # servo bandwidth rad/s, damping
STEP = math.radians(3.0)


def build():
    spec = mujoco.MjSpec.from_file(URDF)
    for b in spec.bodies:
        if b.name in LINKS:
            m, com = LINKS[b.name]
            b.mass = m
            b.ipos = com                           # COM; inertia left as imported
            # (inertia irrelevant for static gravity hold)
    for i, j in enumerate(spec.joints):
        a = spec.add_actuator()
        a.name, a.target = j.name, j.name
        a.trntype = mujoco.mjtTrn.mjTRN_JOINT
        a.gaintype = mujoco.mjtGain.mjGAIN_FIXED
        a.biastype = mujoco.mjtBias.mjBIAS_AFFINE             # gains set per-joint below
        a.forcelimited = mujoco.mjtLimited.mjLIMITED_TRUE     # <-- the real torque clamp
        a.forcerange[0] = -TAU_PEAK[i]; a.forcerange[1] = TAU_PEAK[i]
        a.ctrllimited = mujoco.mjtLimited.mjLIMITED_TRUE
        a.ctrlrange[0] = j.range[0]; a.ctrlrange[1] = j.range[1]
    m = spec.compile()
    m.opt.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST
    # per-joint servo gains scaled to each joint's inertia (uniform bandwidth =
    # stable even for the near-zero-inertia wrist-roll joint).
    d = mujoco.MjData(m); d.qpos[:m.nu] = [0, 0.6, -1.0, 0, 0]
    mujoco.mj_forward(m, d)
    Mfull = np.zeros((m.nv, m.nv)); mujoco.mj_fullM(m, Mfull, d.qM)
    for i in range(m.nu):
        Ii = max(Mfull[i, i], 2e-4)
        kp = Ii * W0**2; kv = 2 * ZETA * Ii * W0
        m.actuator_gainprm[i, 0] = kp
        m.actuator_biasprm[i, 1] = -kp; m.actuator_biasprm[i, 2] = -kv
    return m


def main():
    m = build(); d = mujoco.MjData(m)
    n = m.nu
    lo = m.jnt_range[:, 0].copy(); hi = m.jnt_range[:, 1].copy()
    d.qpos[:n] = [0, 0.6, -1.0, 0, 0]    # start folded (stable)
    d.ctrl[:n] = d.qpos[:n]

    BIND = {ord('Q'):(0,1),ord('A'):(0,-1),ord('W'):(1,1),ord('S'):(1,-1),
            ord('E'):(2,1),ord('D'):(2,-1),ord('R'):(3,1),ord('F'):(3,-1),
            ord('T'):(4,1),ord('G'):(4,-1)}
    def on_key(k):
        if k == ord('X'): d.ctrl[:n] = d.qpos[:n]
        elif k in BIND:
            i,s = BIND[k]
            if i < n: d.ctrl[i] = max(lo[i], min(hi[i], d.ctrl[i] + s*STEP))

    print(f"loaded {URDF}  (gravity ON, force-limited servos)")
    print("  keys Q/A W/S E/D R/F T/G set targets, X=reset. Watch it hold or sag.")
    sub = max(1, int(round(0.02 / m.opt.timestep)))
    with mujoco.viewer.launch_passive(m, d, key_callback=on_key) as v:
        while v.is_running():
            t0 = time.time()
            for _ in range(sub): mujoco.mj_step(m, d)
            v.sync()
            f = d.actuator_force[:n]
            flags = "".join(("!" if abs(f[i]) > TAU_CONT[i] else ".") for i in range(n))
            tq = " ".join(f"{f[i]:+5.1f}" for i in range(n))
            print(f"\r  torque[Nm] {tq}  thermal {flags}  (! = over continuous)   ",
                  end="", flush=True)
            dt = 0.02 - (time.time() - t0)
            if dt > 0: time.sleep(dt)


if __name__ == "__main__":
    main()
