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
import angle_mount as AM                                             # noqa: E402
import cyclo_cage as CC                                              # noqa: E402
from build123d import (export_stl, export_step, Compound, Pos, Box, Cylinder,  # noqa: E402
                       CenterOf)


def angle_mount_solid():
    """The 90deg connection as one solid: body_boss (cyclo body) + mount_plate
    bolted to it. The SAME part is used at the base (slew->shoulder) and the wrist
    (pitch->roll), just bolted in different orientations."""
    return Compound(children=[AM.body_boss(), AM.mount_plate()])

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


# ---- mate-composed CHAIN: the assembly is built by MATING parts (every joint =
#      base-plate boss seated into the next body), so joint frames are DERIVED
#      from geometry, not typed. A per-joint CLOCK angle (about the joint axis)
#      sets the rest pose -- here, the arm standing straight up.
import numpy as np                                                  # noqa: E402
from build123d import Location                                      # noqa: E402


def angle_mount_solid():
    """body_boss + mount_plate as one solid (the 90deg connection)."""
    return Compound(children=[AM.body_boss(), AM.mount_plate()])


def _loc_xyz_rpy(L):
    """build123d Location -> (xyz in m, rpy in rad) for URDF."""
    t = L.wrapped.Transformation()
    R = np.array([[t.Value(i + 1, j + 1) for j in range(3)] for i in range(3)])
    p = np.array([t.Value(i + 1, 4) for i in range(3)]) / 1000.0
    return (tuple(p), (float(np.arctan2(R[2, 1], R[2, 2])),
                       float(np.arctan2(-R[2, 0], np.hypot(R[0, 0], R[1, 0]))),
                       float(np.arctan2(R[1, 0], R[0, 0]))))


def _axis_of(L):
    """the connector's Z (the joint rotation axis) as a unit tuple."""
    z = (L * Location((0, 0, 1))).position - L.position
    v = np.array([z.X, z.Y, z.Z]); v = v / np.linalg.norm(v)
    return tuple(round(x, 4) for x in v)


# chain spec: (link, parent, joint, solid_fn, mate_fn, clock_deg, limit, effort, mass)
SPEC = [
    ("base_link", None, None, CC.cage, CC.mate_frames, None, None, None, 0.5),
    ("mast_link", "base_link", "j1_yaw", angle_mount_solid, AM.mate_frames,
     0, (-PI, PI), TORQUE_SLEW, ACT_48 + 0.063),
    ("upper_arm_link", "mast_link", "j2_shoulder", lambda: A.long_section(UPPER),
     lambda: A.mate_frames(UPPER), 90, (-1.92, 1.92), TQ_48, section_link(UPPER, ACT_38)[1]),
    ("forearm_link", "upper_arm_link", "j3_elbow", lambda: A.long_section(FORE),
     lambda: A.mate_frames(FORE), 180, (-2.62, 2.62), TQ_38, section_link(FORE, ACT_24)[1]),
    ("wrist_link", "forearm_link", "j4_wrist_pitch", angle_mount_solid, AM.mate_frames,
     0, (-1.92, 1.92), TQ_24, ACT_24 + 0.03),
]
MESH = {"base_link": "cyclo_cage.stl", "mast_link": "angle_mount.stl",
        "upper_arm_link": "arm_upper.stl", "forearm_link": "arm_fore.stl",
        "wrist_link": "angle_mount.stl"}


def compose():
    """Walk the spec, mating each part to the previous -> per-link dicts with the
    derived joint origin/axis (in the parent frame) and the world placement."""
    out = []
    for i, (link, parent, jn, bld, mfn, clk, lim, eff, mass) in enumerate(SPEC):
        prox, dist = mfn()
        if i == 0:
            loc, origin, axis = Location(), None, None
        else:
            rel = out[i - 1]["dist"] * Location((0, 0, 0), (0, 0, clk)) * prox.inverse()
            loc = out[i - 1]["loc"] * rel
            origin, axis = _loc_xyz_rpy(rel), _axis_of(prox)
        sol = bld()
        c = sol.center(CenterOf.MASS); bb = sol.bounding_box().size
        out.append(dict(link=link, parent=parent, jointname=jn, prox=prox, dist=dist,
                        loc=loc, solidfn=bld, mesh=MESH[link], mass=mass,
                        com=(c.X / 1000, c.Y / 1000, c.Z / 1000),
                        I=box_I(mass, bb.X / 1000, bb.Y / 1000, bb.Z / 1000),
                        origin=origin, axis=axis, limit=lim, effort=eff))
    return out


CHAIN = compose()
# the gripper rides on the wrist's DIST (mount-plate boss) -> j5 tool-roll
_wrist = CHAIN[-1]
_tool_origin = _loc_xyz_rpy(_wrist["dist"])
_tool_axis = _axis_of(_wrist["dist"])
TCP_FROM_TOOL = (0.08, 0, 0)        # fixed TCP offset in tool frame


# ---------------- URDF emission ----------------
def _link_xml(e):
    """A mesh link, placed at IDENTITY in its own frame (the mate gives the joint)."""
    cx, cy, cz = e["com"]; Ix, Iy, Iz = e["I"]
    vis = (f'<visual><geometry><mesh filename="{e["mesh"]}" '
           f'scale="0.001 0.001 0.001"/></geometry><material name="link"/></visual>')
    return (f'  <link name="{e["link"]}">\n    {vis}\n'
            f'    <inertial><origin xyz="{cx:.4f} {cy:.4f} {cz:.4f}"/>'
            f'<mass value="{e["mass"]:.4f}"/>'
            f'<inertia ixx="{Ix:.2e}" iyy="{Iy:.2e}" izz="{Iz:.2e}" '
            f'ixy="0" ixz="0" iyz="0"/></inertial>\n  </link>\n')


def _joint_xml(name, parent, child, origin, axis, limit, effort, damp=0.05):
    (xyz, rpy) = origin
    return (f'  <joint name="{name}" type="revolute">\n'
            f'    <parent link="{parent}"/><child link="{child}"/>\n'
            f'    <origin xyz="{xyz[0]:.5f} {xyz[1]:.5f} {xyz[2]:.5f}" '
            f'rpy="{rpy[0]:.5f} {rpy[1]:.5f} {rpy[2]:.5f}"/>'
            f'<axis xyz="{axis[0]} {axis[1]} {axis[2]}"/>\n'
            f'    <limit lower="{limit[0]:.4f}" upper="{limit[1]:.4f}" '
            f'effort="{effort}" velocity="3.0"/>\n'
            f'    <dynamics damping="{damp}"/>\n  </joint>\n')


def _transmission_xml(name):
    return (f'  <transmission name="tr_{name}"><type>transmission_interface/'
            f'SimpleTransmission</type>\n'
            f'    <joint name="{name}"><hardwareInterface>hardware_interface/'
            f'PositionJointInterface</hardwareInterface></joint>\n'
            f'    <actuator name="{name}_act"><mechanicalReduction>20'
            f'</mechanicalReduction></actuator></transmission>\n')


def _gripper_visuals():
    return ('<visual><origin xyz="0.006 0 0" rpy="0 1.5708 0"/><geometry>'
            '<cylinder radius="0.018" length="0.006"/></geometry><material name="link"/></visual>\n    '
            '<visual><origin xyz="0.022 0 0"/><geometry><box size="0.022 0.05 0.026"/>'
            '</geometry><material name="link"/></visual>\n    '
            '<visual><origin xyz="0.05 0.019 0"/><geometry><box size="0.05 0.008 0.024"/>'
            '</geometry><material name="tool"/></visual>\n    '
            '<visual><origin xyz="0.05 -0.019 0"/><geometry><box size="0.05 0.008 0.024"/>'
            '</geometry><material name="tool"/></visual>')


def build_urdf():
    parts = ['<?xml version="1.0"?>',
             '<!-- GENERATED by arm_assembly.py (mate-composed) - do not hand-edit. -->',
             '<robot name="micro_arm">',
             '  <mujoco><compiler balanceinertia="true" discardvisual="false" '
             'fusestatic="false" meshdir="meshes"/></mujoco>',
             '  <material name="link"> <color rgba="0.78 0.78 0.80 1"/></material>',
             '  <material name="tool"> <color rgba="0.27 0.51 0.71 1"/></material>']
    for e in CHAIN:
        if e["jointname"]:
            parts.append(_joint_xml(e["jointname"], e["parent"], e["link"],
                                    e["origin"], e["axis"], e["limit"], e["effort"]))
        parts.append(_link_xml(e))
    # j5 tool-roll + the gripper, on the wrist's mount-plate boss
    parts.append(_joint_xml("j5_tool_roll", "wrist_link", "tool_link",
                            _tool_origin, _tool_axis, (-PI, PI), TQ_24, 0.03))
    parts.append(f'  <link name="tool_link">\n    {_gripper_visuals()}\n'
                 f'    <inertial><origin xyz="0.03 0 0"/><mass value="{0.03+PAYLOAD:.4f}"/>'
                 f'<inertia ixx="2.0e-04" iyy="3.0e-04" izz="3.0e-04" ixy="0" ixz="0" iyz="0"/>'
                 f'</inertial>\n  </link>\n')
    parts.append('  <joint name="tcp_fixed" type="fixed"><parent link="tool_link"/>'
                 f'<child link="tcp_link"/><origin xyz="{TCP_FROM_TOOL[0]} '
                 f'{TCP_FROM_TOOL[1]} {TCP_FROM_TOOL[2]}"/></joint>')
    parts.append('  <link name="tcp_link"><inertial><mass value="0.001"/>'
                 '<inertia ixx="1e-6" iyy="1e-6" izz="1e-6" ixy="0" ixz="0" iyz="0"/>'
                 '</inertial></link>')
    for e in CHAIN:
        if e["jointname"]:
            parts.append(_transmission_xml(e["jointname"]))
    parts.append(_transmission_xml("j5_tool_roll"))
    parts.append('</robot>\n')
    return "\n".join(parts)


# ---------------- CAD preview (the mated arm, straight-up rest pose) ----------------
def assembly_solid():
    solids = [e["loc"] * e["solidfn"]() for e in CHAIN]
    tool = CHAIN[-1]["loc"] * CHAIN[-1]["dist"]            # gripper at the wrist output
    solids.append(tool * Pos(22, 0, 0) * Box(22, 50, 26))
    for s in (1, -1):
        solids.append(tool * Pos(50, s * 19, 0) * Box(50, 8, 24))
    return Compound(children=solids)


def main():
    os.makedirs(os.path.join(HERE, "sim", "meshes"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    export_stl(A.long_section(UPPER), os.path.join(HERE, "sim", "meshes", "arm_upper.stl"))
    export_stl(A.long_section(FORE), os.path.join(HERE, "sim", "meshes", "arm_fore.stl"))
    export_stl(CC.cage(), os.path.join(HERE, "sim", "meshes", "cyclo_cage.stl"))
    export_stl(angle_mount_solid(), os.path.join(HERE, "sim", "meshes", "angle_mount.stl"))
    with open(os.path.join(HERE, "sim", "arm_trunk.urdf"), "w") as f:
        f.write(build_urdf())
    try:
        export_step(assembly_solid(), os.path.join(HERE, "out", "arm_assembly.step"))
        prev = "out/arm_assembly.step"
    except Exception as ex:                          # preview is non-essential
        prev = f"(skipped: {ex})"
    print("regenerated (mate-composed, straight-up rest pose):")
    print(f"  {len(CHAIN)} mesh links + gripper; arm {UPPER}+{FORE}mm sections")
    print(f"  motor ladder: slew/elbow 38mm({TQ_38}N*m)  shoulder 48mm({TQ_48}N*m)  wrist 24mm({TQ_24}N*m)")
    print(f"  sim/arm_trunk.urdf  +  {prev}")
    if "--show" in sys.argv:                  # live VSCode OCP viewer of the full arm
        from preview import show
        show(assembly_solid())


if __name__ == "__main__":
    main()
