#!/usr/bin/env python3
"""
arm_section.py — the printable arm links, in build123d (port of arm_section.scad).

Same architecture as the OpenSCAD version: each SECTION integrates one half of a
joint at each end — the rotating cyclo HOUSING (upstream joint output) fused into
the print on one end, the NEMA17 BASE plate (downstream motor mount) on the other.
A joint forms in the gap between two sections.

What build123d buys over OpenSCAD here: the vendor parts come in as EXACT BREP
solids (from STEP), so the beam/collar/gusset fuse against precise geometry with
real solid booleans instead of mesh unions.

    python arm_section.py [upper|forearm]      # -> out/<part>.stl + .step

Vendor STEP parts are extracted by extract_vendor_steps.py (gitignored, paid).
Local frame: arm length +X; cyclo axes along Y (pitch axis); +Z up. The beam is
tall in Z (gravity sag bends it about Y; stiffness ~ height^2).
"""
import os, sys
from build123d import (
    import_step, export_stl, export_step, Box, Cylinder, Pos, Rot,
)

HERE = os.path.dirname(os.path.abspath(__file__))
MICRO = os.path.join(HERE, "vendor", "micro")

# ---- micro actuator (20:1) + arm params ----
ACT_R   = 21.0          # housing outer radius
HOUS_H  = 18.2          # housing height (along its axis)
BASE_H  = 9.0           # NEMA17 plate thickness (= the mount-plate edge)
BORE_R  = 17.0          # housing inner bore (disc cavity) radius
SEG_LEN = 75.0          # housing center -> base center (short test-print length)
# The arm is the NEMA plate EXTENDED to the body: same thickness as the plate
# edge (flush + centered on Y, so the plate edge stays clear and the body end is
# flush, never proud), and tall in Z so it resists gravity sag (stiffness ~ Z^2).
ARM_T   = 4.9           # arm thickness (Y) = the NEMA-plate flange (~4.85mm)
ARM_Z   = 36.0          # arm height (Z), the stiff anti-sag direction (< body OD)
WALL    = 4.0           # body saddle wall
WELD    = 2.0           # arm overlap into the plate edge for a solid butt joint
CLEAR_R = BORE_R + 2     # disc-cavity clearance radius: arm end is radiused to
                         # this so it never pokes toward the rotating internals
# Flat-print alignment: the arm sits FLUSH with one face of the round body
# (its -Y face) instead of centered, so that face is a flat print bed. The
# plate is shifted in Y to share the same plane (its axis stays at Z=0).
ARM_FACE = -HOUS_H / 2          # the body's -Y face = the flat print plane
ARM_YC   = ARM_FACE + ARM_T/2   # arm Y-center so its outer face is on that plane


def _load(name):
    p = os.path.join(MICRO, f"{name}.step")
    if not os.path.exists(p):
        sys.exit(f"missing {p} — run extract_vendor_steps.py (needs your "
                 f"purchased Sweep Dynamics assembly STEP). See NOTICE.")
    return import_step(p).solids()[0]


def _axis_to_y(solid):
    """Rotate a Z-axis vendor part so its cyclo axis lies on the Y axis,
    centered on Y=0 (X,Z stay centered on the axis)."""
    s = Rot(90, 0, 0) * solid
    bb = s.bounding_box()
    return Pos(0, -(bb.min.Y + bb.max.Y) / 2, 0) * s


def long_section(length=SEG_LEN):
    # Both actuator AXES on the same center (Z=0); the plate is shifted in Y so
    # its near face is coplanar with the body's -Y face (flat print bed).
    housing = _axis_to_y(_load("housing"))                 # proximal output, X=0
    # flip the plate (Rot about X) so its FLANGE faces the print plane (-Y),
    # right-side-up, with the boss facing up where the next joint mounts.
    base = Pos(length, ARM_FACE + BASE_H/2, 0) * Rot(180, 0, 0) * _axis_to_y(_load("base_nema17"))

    # the arm is a flat blade ARM_T thick (Y) sitting FLUSH on the body's -Y face
    # (ARM_YC), tall in Z. It ENDS at the plate's near (-X) edge (plate is 42mm,
    # half = ACT_R) with a small weld overlap -- so it never covers the plate
    # face and the central boss stays fully clear for the next joint.
    plate_edge = length - ACT_R
    arm_end = plate_edge + WELD
    # arm blade to the plate edge, with its proximal end RADIUSED to the body's
    # clearance circle (CLEAR_R) -- carved by subtracting a Y-axis cylinder -- so
    # it wraps the body OD without poking into the disc cavity.
    clear = Pos(0, ARM_YC, 0) * Rot(90, 0, 0) * Cylinder(CLEAR_R, ARM_T + 2)
    arm = Pos(arm_end / 2, ARM_YC, 0) * Box(arm_end, ARM_T, ARM_Z) - clear

    # saddle: hugs the body OD over the arm's width only (flush, on the same -Y
    # face) to fair the flat arm into the round body. No bore intrusion.
    saddle = Pos(0, ARM_YC, 0) * Rot(90, 0, 0) * (Cylinder(ACT_R + WALL, ARM_T) - Cylinder(CLEAR_R, ARM_T))

    return housing + saddle + arm + base


def main():
    part = sys.argv[1] if len(sys.argv) > 1 else "upper"
    if part not in ("upper", "forearm"):
        sys.exit("only long sections (upper|forearm) implemented so far")
    sec = long_section()
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    stl = os.path.join(HERE, "out", f"{part}.stl")
    stp = os.path.join(HERE, "out", f"{part}.step")
    export_stl(sec, stl)
    export_step(sec, stp)
    print(f"{part}: volume={sec.volume:.0f} mm^3, "
          f"solids={len(sec.solids())} (want 1), bbox={sec.bounding_box().size}")
    print(f"  wrote {stl}\n  wrote {stp}")
    from preview import show       # live VSCode OCP viewer (no-op if not installed)
    show(sec)


if __name__ == "__main__":
    main()
