#!/usr/bin/env python3
"""
angle_drive.py — right-angle drive part: a cyclo BODY (cylindrical output) with a
NEMA17 plate attached at 90 degrees. One joint's cylindrical output carries the
NEXT joint's motor on a perpendicular axis -- e.g. the forearm-roll motor stacked
on the elbow output (the 6-DOF stack), or any right-angle joint transition.

Integrates the real cyclo body (vendor housing) and adds a NEMA17 mount plate at
90 deg, joined by a web + side gussets (like the Sweep right-angle mount).

    python angle_drive.py     ->  out/angle_drive.stl + .step

Needs build123d + the vendor STEP (extract_vendor_steps.py). See NOTICE.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_section as A                                              # noqa: E402
from build123d import (Box, Cylinder, Pos, Rot, Plane, Polygon, extrude,  # noqa: E402
                       export_stl, export_step)

# cyclo body (vendor housing): axis Z, r ~21, height 18.2, bore r17
BR, BH, BORE = 21.0, 18.2, 17.0
GAP    = 3.0                      # clearance from body OD to the mounting plate
BASE_T = 9.0                      # vendor base-plate thickness
NS     = 42.0                     # vendor base footprint (NEMA17 square)
GW     = 8.0                      # side-gusset width


def part():
    body = A._load("housing")                       # axis Z, centered XY, z 0..18.2
    zc = BH / 2                                      # body mid-height

    # the REAL cyclo mounting plate (vendor base_nema17: NEMA17 bolt pattern +
    # main bearing boss + bore), stood at 90 deg -- rotate its axis Z -> X and
    # set it beside the body in +X. The next motor bolts to it.
    base = Pos(BR + GAP, 0, zc) * Rot(0, 90, 0) * A._load("base_nema17")

    # web tying the body OD to the plate
    web = Pos(BR + GAP/2, 0, zc) * Box(GAP + 6, NS - 2*GW, BH)

    # side gussets (triangles in the X-Z plane at the Y edges)
    gy = NS / 2 - GW / 2
    xb = BR + GAP + BASE_T
    tri = Plane.XZ * Polygon((xb, zc - NS/2), (xb, zc + NS/2), (BR - 2, zc - NS/2),
                             align=None)
    gus = (Pos(0, gy, 0) * extrude(tri, GW/2, both=True)
           + Pos(0, -gy, 0) * extrude(tri, GW/2, both=True))

    out = body + web + base + gus
    out -= Pos(0, 0, zc) * Cylinder(BORE, BH + 4)   # reopen the disc cavity
    return out


def main():
    os.makedirs("out", exist_ok=True)
    p = part()
    export_stl(p, "out/angle_drive.stl")
    export_step(p, "out/angle_drive.step")
    print(f"angle_drive: vol {p.volume:.0f} mm^3  bbox {p.bounding_box().size}")
    print(f"  cyclo body axis Z; NEMA17 plate face normal X (next motor at 90 deg)")


if __name__ == "__main__":
    main()
