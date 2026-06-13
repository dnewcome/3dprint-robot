#!/usr/bin/env python3
"""
wrist_bracket.py — the wrist 90-degree section: holds the TOOL-ROLL actuator (J5).

Like the base bracket it turns 90 degrees, but instead of bolting the motor to a
flat plate, the NEMA17 stepper SLIDES INTO a box/socket. The box's front wall is
the cyclo mount (NEMA17 bolt pattern + shaft bore) -- the cyclo body/plate
integrates here as the final wrist drive, output along +X (the tool). A 4x4 grid
flange (same idea as the base) mounts the whole thing to the wrist-pitch output.

    python wrist_bracket.py    ->  out/wrist_bracket.stl + .step

Frame: tool-roll axis = +X (motor slides in from -X, cyclo/tool on +X). The
flange is horizontal (mounts to the wrist-pitch output); box stands at 90 deg.
"""
import os
from build123d import (Box, Cylinder, Pos, Rot, export_stl, export_step)

# ---- motor box (NEMA17 slides in along -X; cyclo on the +X face) ----
ML    = 40.0    # motor body length = pocket depth
MS    = 42.6    # NEMA17 body + slide clearance (pocket cross-section)
WALL  = 3.0     # box wall
NBOLT = 31.0    # NEMA17 bolt square
NHOLE = 3.4     # M3 clearance (shared: motor front + cyclo base)
BORE  = 23.0    # center bore (motor boss + shaft / cyclo input)
# ---- flange to the wrist-pitch output ----
FLW   = 66.0
FLT   = 6.0
GN, PITCH, FHOLE = 4, 13.0, 4.5
GUSSET = 22.0
GUSSET_W = 8.0


def bracket():
    # horizontal flange -> bolts to the wrist-pitch output. 4x4 adjustable grid.
    flange = Pos(0, 0, FLT/2) * Box(FLW, FLW, FLT)
    g = [(i-(GN-1)/2)*PITCH for i in range(GN)]
    for x in g:
        for y in g:
            flange -= Pos(x, y, FLT/2) * Cylinder(FHOLE/2, FLT+2)

    # motor box on top, axis +X. Open at the back (-X) so the stepper slides in;
    # the front wall (X in [0,WALL]) is the cyclo mount.
    bz = FLT + (MS + 2*WALL)/2
    box = Pos((WALL-ML)/2, 0, bz) * Box(ML+WALL, MS+2*WALL, MS+2*WALL)
    box -= Pos(-ML/2, 0, bz) * Box(ML+1, MS, MS)               # motor cavity (open -X)
    box -= Pos(-(ML+WALL)/2, 0, bz) * Box(WALL+1, MS-8, MS-8)  # lighten the back lip
    # front wall: NEMA17 bolt pattern (motor + cyclo) + center bore
    for sy in (1, -1):
        for sz in (1, -1):
            box -= Pos(WALL/2, sy*NBOLT/2, bz + sz*NBOLT/2) * Rot(0, 90, 0) * Cylinder(NHOLE/2, WALL+2)
    box -= Pos(WALL/2, 0, bz) * Rot(0, 90, 0) * Cylinder(BORE/2, WALL+2)

    # EXTERNAL side braces tying the box down to the flange (on the OUTSIDE of the
    # box side walls, so the motor pocket stays clear for the stepper to slide in)
    gy = (MS + 2*WALL)/2 + GUSSET_W/2 - 0.5     # just outside the box wall
    gus = None
    for s in (1, -1):
        wedge = Pos(WALL - GUSSET, s*gy, FLT) * Box(GUSSET, GUSSET_W, GUSSET)
        cut = Pos(WALL - GUSSET, s*gy, FLT + GUSSET) * Rot(0, 45, 0) * Box(GUSSET*1.6, GUSSET_W+2, GUSSET*1.6)
        wedge -= cut
        gus = wedge if gus is None else gus + wedge

    return flange + box + gus


def main():
    os.makedirs("out", exist_ok=True)
    b = bracket()
    export_stl(b, "out/wrist_bracket.stl")
    export_step(b, "out/wrist_bracket.step")
    print(f"wrist_bracket: vol {b.volume:.0f} mm^3  bbox {b.bounding_box().size}")
    print(f"  motor box: {MS}mm pocket, stepper slides in from -X")
    print(f"  front face: NEMA17 pattern + {BORE}mm bore (cyclo mount, tool-roll out +X)")


if __name__ == "__main__":
    main()
