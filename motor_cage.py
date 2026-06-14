#!/usr/bin/env python3
"""
motor_cage.py — a cage that drops over a NEMA17 stepper to bolt it to a plate.

The motor stands VERTICAL, shaft UP. The cage's top plate carries the NEMA17
bolt pattern (bolts up into the motor's shaft-end face) with a centre bore for
the shaft + pilot boss. Four legs run DOWN the motor's chamfered corners to the
base plate, each ending in a foot with a vertical bolt hole to fasten the whole
thing down.

    python motor_cage.py        # -> out/motor_cage.stl + .step

Pure parametric -- no vendor geometry, prints flat-ish (legs need light support).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build123d import Box, Cylinder, Pos, export_stl, export_step    # noqa: E402

# ---- NEMA17 motor ----
NEMA    = 42.3        # motor body square
BOLT_SQ = 31.0        # NEMA17 bolt-hole square
MBOLT   = 3.4         # M3 clearance (cage -> motor face)
PILOT   = 24.0        # centre bore Ø: clears shaft (Ø5) + pilot boss (Ø22)
MLEN    = 48.0        # motor length the legs span

# ---- cage ----
TOP_T   = 5.0         # top plate thickness
TOP_SQ  = 54.0        # top plate square (overhangs the motor to reach the legs)
LEG     = 8.0         # leg cross-section (square)
LEGR    = 23.0        # leg centre offset (X=Y): outside the chamfered corner
# ---- feet ----
FOOT_W  = 14.0        # foot pad square
FOOT_T  = 5.0         # foot thickness (sits on the plate)
FOOTR   = 29.0        # foot centre offset (outboard of the leg)
FBOLT   = 4.5         # M4 clearance (foot -> base plate)
HOLER   = 30.0        # bolt-hole offset (outboard of the leg, accessible)

CORNERS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def cage():
    top_z = MLEN                                   # underside of the top plate
    # top plate: NEMA17 pattern + shaft/boss bore, bolts up to the motor face
    plate = Pos(0, 0, top_z + TOP_T / 2) * Box(TOP_SQ, TOP_SQ, TOP_T)
    plate -= Pos(0, 0, top_z + TOP_T / 2) * Cylinder(PILOT / 2, TOP_T + 2)
    for sx, sy in CORNERS:
        plate -= (Pos(sx * BOLT_SQ / 2, sy * BOLT_SQ / 2, top_z + TOP_T / 2)
                  * Cylinder(MBOLT / 2, TOP_T + 2))
    out = plate

    for sx, sy in CORNERS:
        # leg: corner post from the base plate up to the top plate
        leg = Pos(sx * LEGR, sy * LEGR, MLEN / 2) * Box(LEG, LEG, MLEN)
        # foot: pad on the base plate, reaching outboard, with a vertical bolt hole
        foot = Pos(sx * FOOTR, sy * FOOTR, FOOT_T / 2) * Box(FOOT_W, FOOT_W, FOOT_T)
        foot -= Pos(sx * HOLER, sy * HOLER, FOOT_T / 2) * Cylinder(FBOLT / 2, FOOT_T + 2)
        out += leg + foot
    return out


def main():
    os.makedirs("out", exist_ok=True)
    c = cage()
    export_stl(c, "out/motor_cage.stl")
    export_step(c, "out/motor_cage.step")
    print(f"motor_cage: vol {c.volume:.0f} mm^3  bbox {c.bounding_box().size}  solids {len(c.solids())}")
    print(f"  top NEMA17 pattern @ {BOLT_SQ}mm, Ø{PILOT} shaft bore; 4 legs x {MLEN}mm; 4x M4 feet")
    try:
        from preview import show
        show(c)
    except Exception:
        pass


if __name__ == "__main__":
    main()
