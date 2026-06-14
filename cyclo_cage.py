#!/usr/bin/env python3
"""
cyclo_cage.py — motor cage for a 38mm NEMA17, with the VENDOR CYCLO PLATE built in.

Like motor_cage.py, but the top isn't a plain parametric NEMA platform -- it's the
real Sweep cyclo mounting plate (vendor base_nema17): NEMA17 bolt pattern + pilot
bore on the motor side (down), bearing boss on the output side (up). The motor
bolts up to the plate, shaft up into the cyclo; 4 legs run down the motor's 38mm
length to feet that bolt the whole drive to a base plate. (This is the base-slew
drive mount.)

    python cyclo_cage.py        # -> out/cyclo_cage.stl + .step

Needs the vendor STEP (extract_vendor_steps.py). See NOTICE.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_section as A                                          # _load(vendor)  # noqa: E402
import motor_cage as MC                                          # leg/foot specs # noqa: E402
from build123d import Box, Cylinder, Pos, export_stl, export_step  # noqa: E402

MLEN    = 38.0        # motor length (legs span this)
PLATE_T = 9.0         # vendor plate thickness (z 0..9, boss up)
LEGR    = 24.0        # leg centre: in the corner chamfer gap (clears the 42mm motor)
EAR_W   = 14.0        # corner-ear square: bridges the chamfered plate to the leg


def cage():
    # vendor cyclo plate: native z 0..9, bearing boss UP, motor-side (pilot bore)
    # DOWN. Motor bolts to the bottom face and hangs below to z = -MLEN.
    out = A._load("base_nema17")
    for sx, sy in MC.CORNERS:
        lx, ly = sx * LEGR, sy * LEGR
        # leg: corner post from the base plate (z=-MLEN) up to the plate top
        leg = Pos(lx, ly, (PLATE_T - MLEN) / 2) * Box(MC.LEG, MC.LEG, PLATE_T + MLEN)
        # ear: corner gusset at plate height, bridging the chamfered plate to the leg
        ex, ey = sx * (LEGR - 3), sy * (LEGR - 3)
        ear = Pos(ex, ey, PLATE_T / 2) * Box(EAR_W, EAR_W, PLATE_T)
        # foot on the base plate, reaching outboard, with a vertical bolt hole
        foot = Pos(sx * MC.FOOTR, sy * MC.FOOTR, -MLEN + MC.FOOT_T / 2) * Box(MC.FOOT_W, MC.FOOT_W, MC.FOOT_T)
        foot -= Pos(sx * MC.HOLER, sy * MC.HOLER, -MLEN + MC.FOOT_T / 2) * Cylinder(MC.FBOLT / 2, MC.FOOT_T + 2)
        out += leg + ear + foot
    return out


def main():
    os.makedirs("out", exist_ok=True)
    c = cage()
    export_stl(c, "out/cyclo_cage.stl")
    export_step(c, "out/cyclo_cage.step")
    print(f"cyclo_cage: vol {c.volume:.0f} mm^3  bbox {c.bounding_box().size}  solids {len(c.solids())}")
    print(f"  vendor cyclo plate top (boss up); 4 legs x {MLEN}mm; 4x M{MC.FBOLT} feet")
    try:
        from preview import show
        show(c)
    except Exception:
        pass


if __name__ == "__main__":
    main()
