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
GAP   = 3.0                       # clearance from body OD to the NEMA plate
# NEMA17 plate (the next motor's mount), face perpendicular to the body axis
NS, NT = 47.0, 6.0               # plate size, thickness
NBOLT, NHOLE, NBORE = 31.0, 3.4, 23.0
GUS, GW = 22.0, 8.0              # gusset leg, gusset width


def part():
    body = A._load("housing")                       # axis Z, centered XY, z 0..18.2
    zc = BH / 2                                      # body mid-height

    # NEMA plate at 90 deg: stood off in +X, face normal = X (next motor axis = X)
    px = BR + GAP + NT / 2
    plate = Pos(px, 0, zc) * Box(NT, NS, NS)
    plate -= Pos(px, 0, zc) * Rot(0, 90, 0) * Cylinder(NBORE / 2, NT + 2)   # shaft bore
    for sy in (1, -1):
        for sz in (1, -1):
            plate -= Pos(px, sy*NBOLT/2, zc + sz*NBOLT/2) * Rot(0, 90, 0) * Cylinder(NHOLE/2, NT+2)

    # web tying the body OD to the plate, then keep the cyclo bore clear
    web = Pos((BR + px) / 2, 0, zc) * Box(px - BR + 4, NS - 2*GW, BH)

    # side gussets (triangles in the X-Z plane at the Y edges)
    gy = NS / 2 - GW / 2
    tri = Plane.XZ * Polygon((px, zc - NS/2), (px, zc + NS/2), (BR - 2, zc - NS/2),
                             align=None)
    gus = (Pos(0, gy, 0) * extrude(tri, GW/2, both=True)
           + Pos(0, -gy, 0) * extrude(tri, GW/2, both=True))

    out = body + web + plate + gus
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
