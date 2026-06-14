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
import math                                                      # noqa: E402
import arm_section as A                                          # _load(vendor)  # noqa: E402
import motor_cage as MC                                          # leg/foot specs # noqa: E402
from build123d import Box, Cylinder, Pos, Rot, export_stl, export_step  # noqa: E402

MLEN     = 38.0       # motor length (legs span this)
FLANGE_T = 4.85       # vendor plate FLAT flange thickness (the boss rises above it)
MOTOR    = 42.3       # NEMA17 body square
CHAMF    = 38.0       # corner chamfer line (|x|+|y| = CHAMF) on motor + plate
MCLR     = 0.6        # clearance around the motor envelope
# legs at the CORNERS, ROTATED 45deg so a face mates the chamfer flat directly.
LEG      = 9.0        # leg square side
LEGC     = 21.5       # leg centre offset (X=Y): face overlaps the corner flange
# diagonal feet (same 45deg) hanging off the leg bottoms
FOOT_L   = 18.0       # foot length (radial), FOOT_W width, on the diagonal
FOOT_W   = 14.0
FOOTC    = 30.0       # foot centre offset (X=Y), outboard of the leg
HOLEC    = 33.0       # foot bolt-hole offset (X=Y), outboard of the leg


def _motor_envelope():
    # the NEMA17 body: a 42.3 square with the corners chamfered at |x|+|y|=CHAMF,
    # as a prism over the motor length (+clearance). Subtracted from the legs so
    # they hug the corner without biting into the motor.
    sq = Box(MOTOR + 2 * MCLR, MOTOR + 2 * MCLR, MLEN + 1)
    diag = (CHAMF + MCLR) * math.sqrt(2)             # 45deg box -> chamfer faces
    oct_ = sq & (Rot(0, 0, 45) * Box(diag, diag, MLEN + 1))
    return Pos(0, 0, -MLEN / 2) * oct_


def cage():
    # vendor cyclo plate: native z 0..9, bearing boss UP (output), motor-side
    # (pilot bore) DOWN. Motor bolts to the bottom face and hangs to z = -MLEN.
    # Everything we add stays at/below the FLANGE top (z=FLANGE_T): FLUSH top.
    out = A._load("base_nema17")
    env = _motor_envelope()
    leg_h = FLANGE_T + MLEN
    holes = []
    for sx, sy in MC.CORNERS:
        ang = math.degrees(math.atan2(sy, sx))
        # 45deg leg: one face parallel to the chamfer, overlapping the corner
        # flange above (fuses to the plate) and clipped to the motor below.
        leg = (Pos(sx * LEGC, sy * LEGC, (FLANGE_T - MLEN) / 2)
               * Rot(0, 0, ang) * Box(LEG, LEG, leg_h)) - env
        # 45deg foot tab hanging off the bottom on the diagonal
        foot = (Pos(sx * FOOTC, sy * FOOTC, -MLEN + MC.FOOT_T / 2)
                * Rot(0, 0, ang) * Box(FOOT_L, FOOT_W, MC.FOOT_T))
        out += leg + foot
        holes.append((sx * HOLEC, sy * HOLEC))
    for hx, hy in holes:        # cut AFTER union so nothing plugs them
        out -= Pos(hx, hy, -MLEN + MC.FOOT_T / 2) * Cylinder(MC.FBOLT / 2, MC.FOOT_T + 2)
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
