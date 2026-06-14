#!/usr/bin/env python3
"""
arm_assembly.py — the fully assembled robot: the SINGLE SOURCE OF TRUTH.

Part geometry lives in arm_section.py (build123d). This file assembles those
parts into the robot: it defines the kinematic CHAIN (joints + links) once and
DERIVES each joint frame from the part geometry (e.g. a section's distal joint
is at its base, which is set by the section length). From that one definition it
generates everything downstream:

    python arm_assembly.py        # regenerate:
      sim/meshes/arm_long.stl     # the section mesh(es) for the sim
      sim/arm_trunk.urdf          # the robot model (GENERATED -- do not hand-edit)
      out/arm_assembly.step       # a CAD preview of the whole arm at q=0

So changing a section length / joint offset / motor here flows to the part, the
sim, and the analysis scripts at once -- no hand-syncing the URDF.

Needs build123d + the vendor STEP (extract_vendor_steps.py). See NOTICE.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_section as A                                              # noqa: E402
import shoulder_bracket as SB                                        # noqa: E402
import angle_drive as AD                                             # noqa: E402
from build123d import (export_stl, export_step, Compound, Pos, Box, Cylinder,  # noqa: E402
                       CenterOf)

PI = 3.14159265

# ---- physical params (MEASURED where noted; edit as parts are weighed) ----
PLA      = 1.24e-6      # kg/mm^3 (PLA ~1.24 g/cc) -> section plastic mass
PAYLOAD  = 0.25         # tool payload, kg
UPPER    = 75           # upper-arm section length, mm (shoulder J2 -> elbow J3)
FORE     = 52           # forearm / last pivot link (pivot_link.py), elbow -> wrist
#
# MOTOR LADDER (the build's NEMA17 plan: slew 38 / shoulder 48 / elbow 38 / wrist 24).
# Output torque is anchored to the MEASURED 24mm-pancake limit (1.8 kg @ 75mm =
# 1.32 N*m, where the OPEN-LOOP stepper starts MISSING STEPS -- the printed cyclo
# does NOT slip), then scaled by motor holding torque (~ stack length). These are
# the CURRENT step-loss caps; tunable up with more current / closed-loop.
#                  full actuator (stepper+cyclo), kg     output torque, N*m
ACT_24, TQ_24 = 0.188, 1.32      # 24mm pancake  -- MEASURED actuator + torque
ACT_38, TQ_38 = 0.29,  3.6       # 38mm
ACT_48, TQ_48 = 0.39,  5.5       # 48mm
TORQUE_SLEW   = TQ_38            # base slew driven by the 38mm (vertical axis: easy)


def distal(length_mm):
    """A section's DISTAL joint frame (its base), in the section's own frame,
    in METERS. Derived from the section geometry -> this is what makes the CAD
    the source of truth for the next joint's location."""
    return (length_mm / 1000.0, (A.ARM_FACE + A.BASE_H / 2) / 1000.0, 0.0)


def box_I(m, dx, dy, dz):
    """diagonal inertia of a solid box (kg*m^2), dims in meters."""
    return (m * (dy*dy + dz*dz) / 12, m * (dx*dx + dz*dz) / 12,
            m * (dx*dx + dy*dy) / 12)


def section_link(length_mm, act_mass):
    """Build a long section solid and return (solid, mass, com_m, inertia).
    Mass = the section's BLADE plastic (the printed structure, EXCLUDING the
    housing + base -- those are part of the measured full actuator, so counting
    the whole section here would double-count them) + the DISTAL actuator (the
    next joint's motor, whose size depends on where this section sits)."""
    sec = A.long_section(length_mm)
    blade_vol = max(sec.volume - A._load("housing").volume
                    - A._load("base_nema17").volume, 0.0)
    m_blade = blade_vol * PLA
    c = sec.center(CenterOf.MASS)                           # mm
    com_blade = (c.X/1000, c.Y/1000, c.Z/1000)
    d = distal(length_mm)                                   # actuator at the distal joint
    mass = m_blade + act_mass
    com = tuple((m_blade*com_blade[i] + act_mass*d[i]) / mass for i in range(3))
    bb = sec.bounding_box().size
    I = box_I(mass, bb.X/1000, bb.Y/1000, bb.Z/1000)
    return sec, mass, com, I


# ---- the CHAIN: the one definition. Each entry = a LINK + the JOINT that
#      drives it (origin in the PARENT link frame). Geometry is a section or a
#      primitive stand-in. Joint origins for section-driven joints are derived. -
# upper arm carries the ELBOW motor (38mm) at its distal joint; the forearm (the
# last pivot link) carries the WRIST-PITCH motor (24mm pancake).
_up, _upm, _upc, _upI = section_link(UPPER, ACT_38)
_fo, _fom, _foc, _foI = section_link(FORE,  ACT_24)

CHAIN = [
    dict(link="base_link", parent=None,
         geom=("cyl", 0.045, 0.06, (0, 0, 0.03)),
         mass=1.0, com=(0, 0, 0.03), I=box_I(1.0, 0.09, 0.09, 0.06)),

    dict(link="mast_link", parent="base_link",
         joint=dict(name="j1_yaw", axis=(0, 0, 1), origin=(0, 0, 0.065),
                    limit=(-PI, PI), effort=TORQUE_SLEW, vel=3.0, damp=0.05),
         geom=("mesh", "shoulder_bracket.stl"),
         mass=ACT_48 + 0.063, com=(0, -0.015, 0.030),       # 48mm shoulder motor sits here
         I=box_I(0.45, 0.06, 0.06, 0.062)),

    dict(link="upper_arm_link", parent="mast_link",
         joint=dict(name="j2_shoulder", axis=(0, 1, 0), origin=(0, -0.027, 0.034),
                    limit=(-1.92, 1.92), effort=TQ_48, vel=3.0, damp=0.05),
         geom=("mesh", "arm_upper.stl"), section=UPPER,
         mass=_upm, com=_upc, I=_upI),

    dict(link="forearm_link", parent="upper_arm_link",
         joint=dict(name="j3_elbow", axis=(0, 1, 0), origin=distal(UPPER),
                    limit=(-2.62, 2.62), effort=TQ_38, vel=3.0, damp=0.05),
         geom=("mesh", "arm_fore.stl"), section=FORE,
         mass=_fom, com=_foc, I=_foI),

    dict(link="wrist_link", parent="forearm_link",
         joint=dict(name="j4_wrist_pitch", axis=(0, 1, 0), origin=distal(FORE),
                    limit=(-1.92, 1.92), effort=TQ_24, vel=3.0, damp=0.03),
         geom=("mesh", "angle_drive.stl", (0, 0, 0), (PI/2, 0, 0)),
         mass=ACT_24 + 0.03, com=(0.02, -0.006, 0),
         I=box_I(0.22, 0.05, 0.05, 0.05)),

    dict(link="tool_link", parent="wrist_link",
         joint=dict(name="j5_tool_roll", axis=(1, 0, 0), origin=(0.0285, -0.0487, 0),
                    limit=(-PI, PI), effort=TQ_24, vel=3.0, damp=0.03),
         geom=("tool",),
         mass=0.03 + PAYLOAD, com=(0.03, 0, 0), I=box_I(0.28, 0.06, 0.04, 0.04)),
]
TCP_FROM_TOOL = (0.08, 0, 0)        # fixed TCP offset in tool frame


# ---------------- URDF emission ----------------
def _geom_xml(geom):
    k = geom[0]
    if k == "mesh":
        return (f'<mesh filename="{geom[1]}" scale="0.001 0.001 0.001"/>', None)
    if k == "cyl":
        r, h, off = geom[1], geom[2], geom[3]
        return (f'<cylinder radius="{r}" length="{h}"/>', off)
    if k == "box":
        s, off = geom[1], geom[2]
        return (f'<box size="{s[0]} {s[1]} {s[2]}"/>', off)
    return (None, None)            # "tool" handled specially


def _link_xml(e):
    name = e["link"]; m = e["mass"]; cx, cy, cz = e["com"]; Ix, Iy, Iz = e["I"]
    if e["geom"][0] == "tool":
        vis = ('<visual><origin xyz="0.02 0 0" rpy="0 1.5708 0"/><geometry>'
               '<cylinder radius="0.02" length="0.006"/></geometry>'
               '<material name="link"/></visual>\n    '
               '<visual><origin xyz="0.05 0 0" rpy="0 1.5708 0"/><geometry>'
               '<cylinder radius="0.006" length="0.06"/></geometry>'
               '<material name="tool"/></visual>')
    elif e["geom"][0] == "mesh":
        fn = e["geom"][1]
        off = e["geom"][2] if len(e["geom"]) > 2 else (0, 0, 0)
        rpy = e["geom"][3] if len(e["geom"]) > 3 else (0, 0, 0)
        o = (f'<origin xyz="{off[0]} {off[1]} {off[2]}" '
             f'rpy="{rpy[0]} {rpy[1]} {rpy[2]}"/>')
        vis = (f'<visual>{o}<geometry><mesh filename="{fn}" '
               f'scale="0.001 0.001 0.001"/></geometry><material name="link"/></visual>')
    else:
        g, off = _geom_xml(e["geom"])
        o = f'<origin xyz="{off[0]} {off[1]} {off[2]}"/>' if off else ""
        vis = f'<visual>{o}<geometry>{g}</geometry><material name="motor"/></visual>'
    return (f'  <link name="{name}">\n    {vis}\n'
            f'    <inertial><origin xyz="{cx:.4f} {cy:.4f} {cz:.4f}"/>'
            f'<mass value="{m:.4f}"/>'
            f'<inertia ixx="{Ix:.2e}" iyy="{Iy:.2e}" izz="{Iz:.2e}" '
            f'ixy="0" ixz="0" iyz="0"/></inertial>\n  </link>\n')


def _joint_xml(e):
    j = e["joint"]; o = j["origin"]; a = j["axis"]
    return (f'  <joint name="{j["name"]}" type="revolute">\n'
            f'    <parent link="{e["parent"]}"/><child link="{e["link"]}"/>\n'
            f'    <origin xyz="{o[0]:.4f} {o[1]:.4f} {o[2]:.4f}"/>'
            f'<axis xyz="{a[0]} {a[1]} {a[2]}"/>\n'
            f'    <limit lower="{j["limit"][0]:.4f}" upper="{j["limit"][1]:.4f}" '
            f'effort="{j["effort"]}" velocity="{j["vel"]}"/>\n'
            f'    <dynamics damping="{j["damp"]}"/>\n  </joint>\n')


def _transmission_xml(name):
    return (f'  <transmission name="tr_{name}"><type>transmission_interface/'
            f'SimpleTransmission</type>\n'
            f'    <joint name="{name}"><hardwareInterface>hardware_interface/'
            f'PositionJointInterface</hardwareInterface></joint>\n'
            f'    <actuator name="{name}_act"><mechanicalReduction>20'
            f'</mechanicalReduction></actuator></transmission>\n')


def build_urdf():
    parts = ['<?xml version="1.0"?>',
             '<!-- GENERATED by arm_assembly.py - do not hand-edit. -->',
             '<!-- 5-DOF micro-cyclo arm: every joint 20:1 Micro except the base',
             '     slew. upper_arm + forearm links ARE the printed arm sections',
             '     (meshes/arm_long.stl); base + wrist 90deg sections are stand-ins. -->',
             '<robot name="micro_arm">',
             '  <mujoco><compiler balanceinertia="true" discardvisual="false" '
             'fusestatic="false" meshdir="meshes"/></mujoco>',
             '  <material name="motor"><color rgba="0.13 0.13 0.15 1"/></material>',
             '  <material name="link"> <color rgba="0.78 0.78 0.80 1"/></material>',
             '  <material name="tool"> <color rgba="0.27 0.51 0.71 1"/></material>']
    for e in CHAIN:
        if e.get("joint"):
            parts.append(_joint_xml(e))
        parts.append(_link_xml(e))
    # TCP
    parts.append(f'  <joint name="tcp_fixed" type="fixed"><parent link="tool_link"/>'
                 f'<child link="tcp_link"/><origin xyz="{TCP_FROM_TOOL[0]} '
                 f'{TCP_FROM_TOOL[1]} {TCP_FROM_TOOL[2]}"/></joint>')
    parts.append('  <link name="tcp_link"><inertial><mass value="0.001"/>'
                 '<inertia ixx="1e-6" iyy="1e-6" izz="1e-6" ixy="0" ixz="0" iyz="0"/>'
                 '</inertial></link>')
    for e in CHAIN:
        if e.get("joint"):
            parts.append(_transmission_xml(e["joint"]["name"]))
    parts.append('</robot>\n')
    return "\n".join(parts)


# ---------------- CAD preview (whole arm at q=0) ----------------
def assembly_solid():
    """Place each link's solid at its q=0 forward-kinematics pose (origins are
    pure translations at q=0) into one Compound."""
    pos = {None: (0, 0, 0)}
    solids = []
    for e in CHAIN:
        p = pos[e["parent"]] if e["parent"] else (0, 0, 0)
        o = e["joint"]["origin"] if e.get("joint") else (0, 0, 0)
        xyz = tuple(p[i] + o[i] for i in range(3))
        pos[e["link"]] = xyz
        g = e["geom"]
        if g[0] == "mesh":
            part = {"shoulder_bracket.stl": SB.bracket,
                    "angle_drive.stl": AD.part}.get(g[1])
            part = part() if part else A.long_section(e["section"])  # arm_upper/arm_fore
            solids.append(Pos(xyz[0]*1000, xyz[1]*1000, xyz[2]*1000) * part)   # mm frame
        elif g[0] == "box":
            s, off = g[1], g[2]
            solids.append(Pos((xyz[0]+off[0])*1000, (xyz[1]+off[1])*1000,
                              (xyz[2]+off[2])*1000) * Box(s[0]*1000, s[1]*1000, s[2]*1000))
        elif g[0] == "cyl":
            r, h, off = g[1], g[2], g[3]
            solids.append(Pos((xyz[0]+off[0])*1000, (xyz[1]+off[1])*1000,
                              (xyz[2]+off[2])*1000) * Cylinder(r*1000, h*1000))
    return Compound(children=solids)


def main():
    os.makedirs(os.path.join(HERE, "sim", "meshes"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    # 1) section + bracket meshes
    export_stl(_up, os.path.join(HERE, "sim", "meshes", "arm_upper.stl"))
    export_stl(_fo, os.path.join(HERE, "sim", "meshes", "arm_fore.stl"))
    export_stl(SB.bracket(), os.path.join(HERE, "sim", "meshes", "shoulder_bracket.stl"))
    export_stl(AD.part(), os.path.join(HERE, "sim", "meshes", "angle_drive.stl"))
    # 2) the URDF (the generated robot model)
    with open(os.path.join(HERE, "sim", "arm_trunk.urdf"), "w") as f:
        f.write(build_urdf())
    # 3) CAD assembly preview
    try:
        export_step(assembly_solid(), os.path.join(HERE, "out", "arm_assembly.step"))
        prev = "out/arm_assembly.step"
    except Exception as ex:                          # preview is non-essential
        prev = f"(skipped: {ex})"
    print("regenerated:")
    print(f"  arm_upper.stl {UPPER}mm ({_upm*1000:.0f} g) + arm_fore.stl {FORE}mm ({_fom*1000:.0f} g) incl. motors")
    print(f"  sim/arm_trunk.urdf       ({len(CHAIN)} links, "
          f"reach ~{((UPPER+FORE)/1000 + 0.05 + TCP_FROM_TOOL[0]):.2f} m)")
    print(f"  motor ladder: slew/elbow 38mm({TQ_38}N*m)  shoulder 48mm({TQ_48}N*m)  wrist 24mm({TQ_24}N*m)")
    print(f"  {prev}")
    if "--show" in sys.argv:                  # live VSCode OCP viewer of the full arm
        from preview import show
        show(assembly_solid())


if __name__ == "__main__":
    main()
