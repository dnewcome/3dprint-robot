#!/usr/bin/env python3
"""
pivot_link.py — the LAST pivot link of the arm (the wrist attaches here).

A short arm section, 46mm joint-to-joint: the cyclo HOUSING on the proximal end
(the wrist-pitch output) and, instead of the NEMA17 base, a THICKENED END BOSS
carrying 2 axial heat-set inserts in the SAME 2-bolt pattern as angle_mount's
body_boss. So the wrist (angle_mount.mount_plate) bolts straight onto this end --
inserts come in from the end face, blind back (so inserts, not nuts).

    python pivot_link.py        # -> out/pivot_link.stl + .step

The end is thickened (END_T > the thin arm blade) to house the inserts, just like
the boss that sticks off the body piece in angle_mount.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_section as A                                          # noqa: E402
import angle_mount as AM                                         # fastener specs # noqa: E402
from build123d import Box, Cylinder, Pos, Rot, export_stl, export_step  # noqa: E402

SEG     = 52.0        # joint-to-joint: housing axis -> end attach face
END_LEN = 12.0        # X length of the thickened end boss (insert depth + wall)
END_T   = 10.0        # Y thickness of the end boss (> ARM_T; houses the inserts)


def pivot_link(length=SEG):
    housing = A._axis_to_y(A._load("housing"))            # proximal output, X=0

    # flat arm blade (flush on the body's -Y print face, tall in Z), proximal end
    # radiused to the body clearance circle so it wraps the OD without poking in.
    clear = Pos(0, A.ARM_YC, 0) * Rot(90, 0, 0) * Cylinder(A.CLEAR_R, A.ARM_T + 2)
    arm = Pos(length / 2, A.ARM_YC, 0) * Box(length, A.ARM_T, A.ARM_Z) - clear
    saddle = (Pos(0, A.ARM_YC, 0) * Rot(90, 0, 0)
              * (Cylinder(A.ACT_R + A.WALL, A.ARM_T) - Cylinder(A.CLEAR_R, A.ARM_T)))

    # thickened end boss: flush on the -Y face, thicker in +Y to hold the inserts.
    by = A.ARM_FACE + END_T / 2
    boss = Pos(length - END_LEN / 2, by, 0) * Box(END_LEN, END_T, A.ARM_Z)

    out = housing + saddle + arm + boss
    # 2 heat-set inserts from the END face (+X), drilled -X, spaced in Z (the
    # tall direction) at the angle_mount bolt pattern -- blind back. Cut from the
    # FINAL solid so the blade (which overlaps the boss in Y) can't plug them.
    for s in (1, -1):
        out -= (Pos(length - AM.INSERT_DP / 2 + 0.1, by, s * AM.BOLT_SP / 2)
                * Rot(0, 90, 0) * Cylinder(AM.INSERT_D / 2, AM.INSERT_DP + 0.2))
    return out


def main():
    os.makedirs("out", exist_ok=True)
    p = pivot_link()
    export_stl(p, "out/pivot_link.stl")
    export_step(p, "out/pivot_link.step")
    print(f"pivot_link: vol {p.volume:.0f} mm^3  bbox {p.bounding_box().size}  solids {len(p.solids())}")
    print(f"  {SEG}mm joint-to-joint; end boss {END_T}mm thick, 2x M3 inserts @ {AM.BOLT_SP}mm (Z)")
    try:
        from preview import show
        show(p)
    except Exception:
        pass


if __name__ == "__main__":
    main()
