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
                       BuildSketch, Locations, Rectangle, make_hull,
                       export_stl, export_step, GeomType)

# cyclo body (vendor housing): axis Z, r ~21, height 18.2, bore r17
BR, BH, BORE = 21.0, 8.2, 17.0
GAP    = 2.0                      # clearance from body OD to the mounting plate
BASE_T = 9.0                      # vendor base-plate thickness
NS     = 42.0                     # vendor base footprint (NEMA17 square)
CAP    = 6.5                      # cyclo end-cap height on top of the housing
CLEAR  = 5.0                     # gap the motor must keep above the cap
# lift the plate in Z so a motor bolted to it (centered on the plate bore, NS
# tall) clears the top of the drive: bore center = housing + cap + CLEAR + NS/2.
PLATE_Z = BH + CAP + CLEAR + NS/2
WEB_T   = 28.0                    # Y thickness of the hull web (body -> plate)
CAP_R   = BR + 1.5               # relief radius: cap lip (~body OD) + clearance

def part():
    body = A._load("housing")                       # axis Z, centered XY, z 0..18.2

    # the REAL cyclo mounting plate (vendor base_nema17: NEMA17 bolt pattern +
    # main bearing boss + bore), at 90 deg (axis Z -> X), beside the body in +X
    # and lifted to PLATE_Z so the motor clears the drive cap.
    base = Pos(BR + GAP, 0, PLATE_Z) * Rot(0, 90, 0) * A._load("base_nema17")

    # hull web tying the body up to the plate underside. Drawn as an X-Z
    # silhouette -- wide where it grips the body flank, tapering up to a pad
    # under the plate -- then given Y thickness. Replaces the blunt box riser so
    # the body blends into the plate (a convex hull, build123d's make_hull).
    z1 = PLATE_Z - NS / 2                            # plate underside z
    with BuildSketch(Plane.XZ) as sk:
        with Locations((BR + 1, BH)):           # grip the body's +X flank
           Rectangle(BR, BH)
        with Locations((BR + GAP * 2, z1)):             # pad under the plate
           Rectangle(BASE_T, 1)
        make_hull()
    web = extrude(sk.sketch, amount=WEB_T / 2, both=True)

    # relief pocket so the web clears the drive's end-cap LIP sitting on top of
    # the body. The cap is concentric with the body (axis Z), CAP tall, starting
    # at the real body top. Cut a cylinder of the cap lip radius + clearance.
    body_top = body.bounding_box().max.Z            # real housing top (~18.2)
    web -= Pos(0, 0, body_top + CAP / 2) * Cylinder(CAP_R, CAP + 4)

    # clear the web out of the body's interior bore -- on the WEB ONLY, before
    # unioning the body in, so we keep the housing's internal cycloidal teeth.
    # Cut to 18.0 (bore wall is r18.5): a 0.5mm margin that opens the cavity
    # while staying off the 18.5 face (cutting exactly on it hangs OCC).
    web -= Pos(0, 0, body_top / 2) * Cylinder(18.0, body_top + 8)

    out = body + web + base
    return out


def main():
    os.makedirs("out", exist_ok=True)
    p = part()
    export_stl(p, "out/angle_drive.stl")
    export_step(p, "out/angle_drive.step")
    print(f"angle_drive: vol {p.volume:.0f} mm^3  bbox {p.bounding_box().size}")
    print(f"  cyclo body axis Z; NEMA17 plate face normal X (next motor at 90 deg)")
    from preview import show       # live VSCode OCP viewer (no-op if not installed)
    show(p)


if __name__ == "__main__":
    main()
