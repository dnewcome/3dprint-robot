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

MLEN     = 38.0       # motor length (legs span this)
FLANGE_T = 4.85       # vendor plate FLAT flange thickness (the boss rises above it)
LEGR     = 26.0       # leg centre: outboard of the motor's flat face (42 sq)
EAR_IN   = 18.0       # ear reaches IN to this radius (clean flange, clear of bolts)
EAR_W    = 16.0       # ear width (clears the NEMA bolt holes at +/-15.5)
# legs sit at the MID-SIDES (not corners) so the ears land on clear flange between
# the motor and the bolt circle, and the diagonal NEMA bolt holes stay accessible.
SIDES = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def cage():
    # vendor cyclo plate: native z 0..9, bearing boss UP (output), motor-side
    # (pilot bore) DOWN. Motor bolts to the bottom face and hangs to z = -MLEN.
    # Everything we add stays at/below the FLANGE top (z=FLANGE_T): the top is
    # FLUSH and the rotating output (the boss above FLANGE_T) is left clear.
    out = A._load("base_nema17")
    leg_h = FLANGE_T + MLEN
    for dx, dy in SIDES:
        leg = Pos(dx * LEGR, dy * LEGR, (FLANGE_T - MLEN) / 2) * Box(MC.LEG, MC.LEG, leg_h)
        # ear: radial bridge from the flange edge out to the leg, FLUSH with the
        # flange top (z 0..FLANGE_T). Lands at the mid-side, clear of the bolts.
        out_r = LEGR + MC.LEG / 2
        span = out_r - EAR_IN
        if dx:
            ear = Pos(dx * (EAR_IN + out_r) / 2, 0, FLANGE_T / 2) * Box(span, EAR_W, FLANGE_T)
        else:
            ear = Pos(0, dy * (EAR_IN + out_r) / 2, FLANGE_T / 2) * Box(EAR_W, span, FLANGE_T)
        # foot on the base plate, outboard, with a vertical bolt hole
        foot = Pos(dx * MC.FOOTR, dy * MC.FOOTR, -MLEN + MC.FOOT_T / 2) * Box(MC.FOOT_W, MC.FOOT_W, MC.FOOT_T)
        foot -= Pos(dx * MC.HOLER, dy * MC.HOLER, -MLEN + MC.FOOT_T / 2) * Cylinder(MC.FBOLT / 2, MC.FOOT_T + 2)
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
