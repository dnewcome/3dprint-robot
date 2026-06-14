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
# legs at the CORNERS (the motor's wire connector lives on an edge face, so the
# mid-sides are blocked). Corner = the flange chamfer gap (clears the 42mm motor).
LEGR     = 24.0       # leg centre offset (X=Y): in the corner chamfer gap
EAR_LEN  = 11.0       # diagonal ear length (radial): grabs the corner flange sliver
EAR_W    = 18.0       # diagonal ear width (tangential, along the chamfer)
EAR_R    = 22.0       # diagonal ear centre offset (X=Y)
FOOTR    = 28.0       # foot pad centre (X=Y), outboard of the leg
HOLER    = 32.0       # foot bolt-hole centre (X=Y): OUTBOARD of the leg, clear


def cage():
    # vendor cyclo plate: native z 0..9, bearing boss UP (output), motor-side
    # (pilot bore) DOWN. Motor bolts to the bottom face and hangs to z = -MLEN.
    # Everything we add stays at/below the FLANGE top (z=FLANGE_T): the top is
    # FLUSH and the rotating output (the boss above FLANGE_T) is left clear.
    out = A._load("base_nema17")
    leg_h = FLANGE_T + MLEN
    holes = []
    for sx, sy in MC.CORNERS:
        leg = Pos(sx * LEGR, sy * LEGR, (FLANGE_T - MLEN) / 2) * Box(MC.LEG, MC.LEG, leg_h)
        # diagonal ear: a 45-deg gusset along the chamfer, grabbing only the corner
        # flange sliver OUTBOARD of the bolt heads, flush with the flange top.
        ang = math.degrees(math.atan2(sy, sx))
        ear = (Pos(sx * EAR_R, sy * EAR_R, FLANGE_T / 2)
               * Rot(0, 0, ang) * Box(EAR_LEN, EAR_W, FLANGE_T))
        # foot on the base plate, outboard, hole cut from the FINAL solid (below)
        foot = Pos(sx * FOOTR, sy * FOOTR, -MLEN + MC.FOOT_T / 2) * Box(MC.FOOT_W, MC.FOOT_W, MC.FOOT_T)
        out += leg + ear + foot
        holes.append((sx * HOLER, sy * HOLER))
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
