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
    import_step, export_stl, export_step, Solid, Box, Cylinder, Pos, Rot,
    Plane, Polygon, extrude, Axis,
)

HERE = os.path.dirname(os.path.abspath(__file__))
MICRO = os.path.join(HERE, "vendor", "micro")

# ---- micro actuator (20:1) + beam params (match arm_section.scad) ----
ACT_R   = 21.0          # housing outer radius
HOUS_H  = 18.2          # housing height (along its axis)
BASE_H  = 9.0           # NEMA17 plate thickness
BORE_R  = 17.0          # housing inner bore (disc cavity) radius
SEG_LEN = 150.0         # housing center -> base center
BEAM_H  = 28.0          # beam height (Z) -- the stiff (anti-sag) direction
BEAM_W  = 20.0          # beam width (Y) -- ~ actuator width
WALL    = 4.0           # collar/gusset wall


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
    housing = _axis_to_y(_load("housing"))                 # proximal output, X=0
    base = Pos(length, 0, 0) * _axis_to_y(_load("base_nema17"))  # distal motor mount

    # collar: grips the housing wall (inner bites to BORE_R+2, keeping the disc
    # cavity clear), outer proud for the beam to fuse onto. Axis along Y.
    collar = Rot(90, 0, 0) * (Cylinder(ACT_R + WALL, HOUS_H) - Cylinder(BORE_R + 2, HOUS_H))

    # beam: from the bore wall to the base center, tall in Z, centered on Y.
    beam = Pos((BORE_R + length) / 2, 0, 0) * Box(length - BORE_R, BEAM_W, BEAM_H)

    # gusset: triangular brace blending the beam down onto the base face.
    tri = Polygon((length, -BEAM_H/2), (length, BEAM_H/2), (length - BEAM_H, -BEAM_H/2),
                  align=None)
    gusset = extrude(Plane.XZ * tri, BEAM_W/2, both=True)

    return housing + collar + beam + gusset + base


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


if __name__ == "__main__":
    main()
