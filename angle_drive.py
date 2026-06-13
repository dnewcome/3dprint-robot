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
CAP    = 6.5                      # cyclo end-cap height on top of the housing
CLEAR  = 3.0                      # gap the motor must keep above the cap
# lift the plate in Z so a motor bolted to it (centered on the plate bore, NS
# tall) clears the top of the drive: bore center = housing + cap + CLEAR + NS/2.
PLATE_Z = BH + CAP + CLEAR + NS/2


def part():
    body = A._load("housing")                       # axis Z, centered XY, z 0..18.2

    # the REAL cyclo mounting plate (vendor base_nema17: NEMA17 bolt pattern +
    # main bearing boss + bore), at 90 deg (axis Z -> X), beside the body in +X
    # and lifted to PLATE_Z so the motor clears the drive cap.
    base = Pos(BR + GAP, 0, PLATE_Z) * Rot(0, 90, 0) * A._load("base_nema17")

    # riser tying the body up to the underside of the plate (stays BELOW the
    # motor; no gussets yet)
    z1 = PLATE_Z - NS / 2                            # plate bottom (= cap + CLEAR)
    rx0, rx1 = BR - 3, BR + GAP + BASE_T
    riser = Pos((rx0 + rx1) / 2, 0, z1 / 2) * Box(rx1 - rx0, 30, z1)

    out = body + riser + base
    out -= Pos(0, 0, BH / 2) * Cylinder(BORE, BH + 4)   # reopen the disc cavity
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
