#!/usr/bin/env python3
"""
sizing.py — weight & torque analysis for the cycloid arm.

Answers: "how long can the members be?" and "which motor?" The limit is the
gravity moment at the shoulder (J2): it must HOLD everything beyond it at full
horizontal extension. Heavy motors out near the wrist hurt twice — their own
weight loads the shoulder. We build a lumped-mass model, use MuJoCo inverse
dynamics for the required holding torque, and compare to what each motor (on
the printed cycloidal) can deliver continuously.

    pip install mujoco
    python sim/sizing.py

KEY PRINCIPLE the catalog encodes: the *reduction* should come from the printed
cycloidal (light, ~0 backlash), NOT a metal planetary gearbox (~250-300 g).
So the motor should be BARE and light. Torque scaling:
  * stepper torque ~ stack LENGTH  -> a "pancake" stepper is just weaker, same
    torque/gram. Not a win.
  * BLDC outrunner torque ~ radius^2 -> a flat, wide pancake outrunner is the
    torque-dense flat motor. That's the real lever (needs FOC + encoder).
All numbers are editable estimates — plug in datasheet values to sharpen.
"""
import mujoco, numpy as np

g = 9.81

# ---------------- the printed reduction (shared) ----------------
RATIO = 20          # cycloidal reduction
EFF   = 0.70        # cycloidal efficiency (printed, conservative)
CONT  = 0.60        # stepper usable continuous fraction (thermal); BLDC similar
CYCLO_PRINTED = 0.15  # printed cycloidal stage per joint (body+plates+bearings), kg

# ---------------- MOTOR CATALOG ----------------
# name: dict(t=continuous torque at the MOTOR shaft [N*m], m=bare motor mass [kg],
#            kind, note). 'geared' kind already includes its gearbox (t=output, no cyclo).
MOTORS = {
 "NEMA8 stepper":      dict(t=0.015, m=0.060, kind="step", note="tiny, weak"),
 "NEMA11 stepper":     dict(t=0.060, m=0.095, kind="step", note="bare, simple"),
 "NEMA14 stepper":     dict(t=0.120, m=0.140, kind="step", note="bare"),
 "NEMA17 stepper":     dict(t=0.260, m=0.300, kind="step", note="cont=0.6x0.44 hold"),
 "geared NEMA14 19:1": dict(t=1.68,  m=0.411, kind="geared", note="metal gearbox; 1deg backlash"),
 "gimbal BLDC GBM2804":dict(t=0.030, m=0.055, kind="bldc", note="FOC+enc; torque-weak"),
 "gimbal BLDC GBM4108":dict(t=0.080, m=0.110, kind="bldc", note="FOC+enc"),
 "pancake BLDC 5208":  dict(t=0.180, m=0.175, kind="bldc", note="FOC+enc; flat outrunner"),
 "pancake BLDC 8108":  dict(t=0.350, m=0.230, kind="bldc", note="FOC+enc; flat, torque-dense"),
}

def joint_out_cont(mo, ratio=RATIO):
    """Continuous output torque at the JOINT for a motor at a given reduction.
    'geared' motors carry their own fixed gearbox (ratio arg ignored)."""
    if mo["kind"] == "geared":
        return mo["t"] * CONT
    return mo["t"] * ratio * EFF * CONT

def joint_mass(mo):
    """Mass of the whole joint actuator (motor + printed cyclo, or geared as-is)."""
    return mo["m"] if mo["kind"] == "geared" else mo["m"] + CYCLO_PRINTED

# ---------------- lumped-mass arm ----------------
M_OUTBODY = 0.06    # printed output body at each joint (small lever, proximal)
PAYLOAD   = 0.25
M_TOOL    = 0.03
RHO_PLA   = 700.0; MEM_W, MEM_T = 0.044, 0.010
def member_mass(L): return RHO_PLA * MEM_W * MEM_T * L
H_SH = 0.15
L1d, L2d, L3, L4 = 0.210, 0.160, 0.050, 0.078   # default member lengths


def build(L1, L2, m_elbow, m_wrist=None, payload=PAYLOAD):
    """Planar chain. m_elbow = J3 (elbow) actuator mass; m_wrist = J4/J5 wrist
    actuator mass (defaults to m_elbow). Each actuator sits at the DISTAL joint
    of its link (worst lever); each link also has its member + output body."""
    if m_wrist is None: m_wrist = m_elbow
    m_ua = M_OUTBODY + member_mass(L1) + m_elbow
    c_ua = (member_mass(L1)*L1/2 + m_elbow*L1) / m_ua
    m_fa = M_OUTBODY + member_mass(L2) + m_wrist
    c_fa = (member_mass(L2)*L2/2 + m_wrist*L2) / m_fa
    m_wr = m_wrist + 0.02
    m_to = M_TOOL + payload
    def I(m): return max(m*4e-4, 1e-5)
    return f"""
<mujoco><option gravity="0 0 -{g}"/><worldbody>
 <body name="ua" pos="0 0 {H_SH}"><joint type="hinge" axis="0 1 0"/>
  <inertial pos="0 0 {c_ua}" mass="{m_ua}" diaginertia="{I(m_ua)} {I(m_ua)} {I(m_ua)}"/>
  <body name="fa" pos="0 0 {L1}"><joint type="hinge" axis="0 1 0"/>
   <inertial pos="0 0 {c_fa}" mass="{m_fa}" diaginertia="{I(m_fa)} {I(m_fa)} {I(m_fa)}"/>
   <body name="wr" pos="0 0 {L2}"><joint type="hinge" axis="0 1 0"/>
    <inertial pos="0 0 {L3/2}" mass="{m_wr}" diaginertia="{I(m_wr)} {I(m_wr)} {I(m_wr)}"/>
    <body name="to" pos="0 0 {L3}"><joint type="hinge" axis="0 0 1"/>
     <inertial pos="0 0 {L4}" mass="{m_to}" diaginertia="{I(m_to)} {I(m_to)} {I(m_to)}"/>
    </body></body></body></body></worldbody></mujoco>"""


def j2_demand(L1, L2, m_elbow, m_wrist=None, **kw):
    m = mujoco.MjModel.from_xml_string(build(L1, L2, m_elbow, m_wrist, **kw))
    d = mujoco.MjData(m); d.qpos[:] = [np.pi/2, 0, 0, 0]
    mujoco.mj_inverse(m, d)
    return abs(d.qfrc_inverse[0])

def max_member(out_cont, m_act):
    """Largest equal member length (L1=L2=L) within continuous shoulder torque."""
    best = 0
    for L in range(50, 421, 5):
        if j2_demand(L/1000, L/1000, m_act) <= out_cont: best = L
    return best


def catalog():
    print("="*96)
    print("MOTOR CATALOG — same motor at every joint, on the printed cycloidal.")
    print("max member = longest equal limbs the SHOULDER can hold continuously, at 20:1 vs 36:1.")
    print("="*96)
    print(f"{'motor':<22}{'joint':>7}{'wrist pr':>9}{'mem@20:1':>10}{'mem@36:1':>10}  note")
    print("-"*96)
    for name, mo in MOTORS.items():
        jm = joint_mass(mo)
        m20 = max_member(joint_out_cont(mo, 20), jm)
        m36 = max_member(joint_out_cont(mo, 36), jm)
        f20 = f"{m20}mm" if m20 else "TOO WEAK"
        f36 = f"{m36}mm" if m36 else "TOO WEAK"
        print(f"{name:<22}{jm*1000:6.0f}g{2*jm*1000:8.0f}g{f20:>10}{f36:>10}  {mo['note']}")
    print("-"*96)
    print(f"payload {PAYLOAD*1000:.0f}g | reach = 2*member + {1000*(L3+L4):.0f}mm wrist/tool. "
          f"36:1 = your belt pre-stage. geared NEMA14 fixed at 19:1 (can't add reduction).")


def mixed():
    print("\n" + "="*96)
    print("RECOMMENDED MIXED BUILD — torque-dense where it lifts, lightest where it hangs")
    print("="*96)
    # different motor per role: shoulder/elbow carry load; wrist just needs to be light
    for sh_name, sh_ratio in [("NEMA17 stepper", 36), ("pancake BLDC 8108", 36)]:
        sh = MOTORS[sh_name]; wmo = MOTORS["gimbal BLDC GBM2804"]
        oc = joint_out_cont(sh, sh_ratio)
        # elbow motor mass = shoulder-class; wrist motors = light gimbal
        m_elbow = joint_mass(sh); m_wrist = joint_mass(wmo)
        best = 0
        for L in range(50, 421, 5):
            if j2_demand(L/1000, L/1000, m_elbow, m_wrist) <= oc: best = L
        print(f"  shoulder/elbow {sh_name} @{sh_ratio}:1 (out {oc:.1f}Nm) + wrist gimbal 2804 "
              f"({m_wrist*1000:.0f}g) -> {best}mm members, reach ~{(2*best)/1000+L3+L4:.2f}m")
    print("  all reduction from printed cycloidal (~0 backlash). BLDC cost: FOC+encoder x5.")


if __name__ == "__main__":
    catalog()
    mixed()
