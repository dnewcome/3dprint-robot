#!/usr/bin/env python3
"""
shoulder_bracket.py — the base 90-degree section (right-angle slew->shoulder mount).

Bolts to the base slew's output on its horizontal face and presents the shoulder
joint on the vertical face, axis horizontal -- so the whole arm yaws with the
slew (like the cricket drive's base). Both faces carry a 4x4 ADJUSTABLE bolt grid
so it mates to whatever base cyclo / shoulder actuator you use (set PITCH). Pure
parametric -- no vendor geometry, so it builds without the STEP files.

    python shoulder_bracket.py     ->  out/shoulder_bracket.stl + .step
"""
import os
from build123d import (Box, Cylinder, Pos, Rot, Plane, Polygon, extrude,
                       export_stl, export_step)

# ---- adjustable params ----
T       = 6.0      # plate thickness, mm
W       = 60.0     # plate width (square), mm
H       = 56.0     # shoulder-plate height, mm
GRID_N  = 4        # 4 x 4 bolt grid
PITCH   = 14.0     # grid pitch -- ADJUST to your base cyclo / shoulder actuator
HOLE_D  = 4.5      # bolt clearance (M4)
SHAFT_D = 16.0     # center clearance bore on the shoulder face (cyclo shaft)
GUSSET  = 26.0     # corner gusset leg length
GW      = 40.0     # gusset width (along the joint axis)


def _grid():
    return [(i - (GRID_N - 1) / 2) * PITCH for i in range(GRID_N)]


def bracket():
    g = _grid()
    # base plate (horizontal): bolts DOWN to the slew output. 4x4 grid through Z.
    base = Pos(0, 0, T / 2) * Box(W, W, T)
    for x in g:
        for y in g:
            base -= Pos(x, y, T / 2) * Cylinder(HOLE_D / 2, T + 2)

    # shoulder plate (vertical, normal +/-Y, standing at the -Y edge): the shoulder
    # actuator bolts here with its axis horizontal (Y = pitch). 4x4 grid + center bore.
    wy = -W / 2 + T / 2
    wall = Pos(0, wy, T + H / 2) * Box(W, T, H)
    wall -= Pos(0, wy, T + H / 2) * Rot(90, 0, 0) * Cylinder(SHAFT_D / 2, T + 2)
    for x in g:
        for z in g:
            wall -= Pos(x, wy, T + H / 2 + z) * Rot(90, 0, 0) * Cylinder(HOLE_D / 2, T + 2)

    # gusset filling the inner corner (triangle in the Y-Z plane, extruded along X)
    inner_y = -W / 2 + T
    tri = Plane.YZ * Polygon((inner_y, T), (inner_y + GUSSET, T), (inner_y, T + GUSSET),
                             align=None)
    gusset = extrude(tri, GW / 2, both=True)

    return base + wall + gusset


def main():
    os.makedirs("out", exist_ok=True)
    b = bracket()
    export_stl(b, "out/shoulder_bracket.stl")
    export_step(b, "out/shoulder_bracket.step")
    print(f"shoulder_bracket: vol {b.volume:.0f} mm^3  bbox {b.bounding_box().size}")
    print(f"  base face: 4x4 grid @ {PITCH}mm pitch (slew mount)")
    print(f"  shoulder face: 4x4 grid + {SHAFT_D}mm bore (actuator mount), axis horizontal")


if __name__ == "__main__":
    main()
