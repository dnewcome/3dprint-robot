#!/usr/bin/env python3
"""
angle_mount.py — the right-angle joint as TWO bolt-together, flat-printing pieces
(replaces the fused angle_drive). See LAB_NOTEBOOK.md: flat parts hit nominal
dims, so we split the L instead of printing it as one un-flat part.

  body_boss()   : the cyclo body + a BOSS sticking off its side, carrying 2
                  heat-set inserts. The boss's back is the body (a blind hole),
                  so heat-set inserts (melted in from the outer face), not nuts.
  mount_plate() : the vendor NEMA17 base + a short flat TAB (arm-style, but
                  stubby) with 2 clearance holes -- bolts flat onto the boss at
                  90 deg. Plate + tab coplanar => prints flat.

Frame: body axis Z (native housing). Boss sticks out +X; its mounting face is
the +X plane at x = OD + BOSS_OUT, normal +X; the 2 inserts are spaced in Z and
drilled -X into the boss.

    python angle_mount.py            # show + export
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arm_section as A                                          # noqa: E402
from build123d import (Box, Cylinder, Pos, Rot,                  # noqa: E402
                       export_stl, export_step)

# ---- fasteners ----
INSERT_D  = 4.6        # M3 heat-set insert hole (per the rest of the design)
INSERT_DP = 5.0        # insert depth into the boss
SCREW_CLR = 3.4        # M3 screw clearance (through the mount-plate tab)
BOLT_SP   = 12.0       # spacing between the 2 fasteners (along Z)

# ---- body ----
OD = A.ACT_R           # 21.0  body outer radius
BH = A.HOUS_H          # 18.2  body height

# ---- boss ----
BOSS_OUT = 8.0         # how far the mounting face sits beyond the OD
BOSS_W   = 20.0        # boss width (Y) -- holds the 2 horizontal inserts + margin
BORE_R   = 18.5        # body inner bore (teeth live at/inside this radius)
BOSS_IN  = BORE_R + 0.5  # boss inner face x: clears the bore + teeth, bonds to wall
FACE_X   = OD + BOSS_OUT       # x of the mounting face
ZC       = BH / 2             # fasteners centered on body mid-height


def body_boss():
    body = A._load("housing")                       # axis Z, OD r21, z 0..18.2
    # boss inner face at BOSS_IN (>bore), so it bonds to the body WALL only and
    # never reaches into the bore / internal teeth.
    boss = Pos((BOSS_IN + FACE_X) / 2, 0, ZC) * Box(FACE_X - BOSS_IN, BOSS_W, BH)
    out = body + boss
    # 2 heat-set inserts, drilled -X into the boss face, spaced HORIZONTALLY (Y),
    # blind back (the body)
    for s in (1, -1):
        out -= (Pos(FACE_X - INSERT_DP / 2 + 0.1, s * BOLT_SP / 2, ZC)
                * Rot(0, 90, 0) * Cylinder(INSERT_D / 2, INSERT_DP + 0.2))
    return out


# ---- mount plate (piece 2) ----
TAB_T  = 6.0           # tab thickness (X) -- the flange that seats on the boss
TAB_W  = BOSS_W        # tab width (Y), matches the boss
# the NEMA plate rides ABOVE the body so its central bore clears the boss; a
# short tab drops from its lower edge down over the boss face to carry the bolts.
PLATE_ZC = BH + 21 + 3        # plate center (its bottom edge ~ body top + 3)


def mount_plate():
    # NEMA17 base, face-normal +X (90 deg to the body's Z axis). The vendor plate
    # has its bearing BOSS on one face -- orient so the boss faces OUTWARD (+X,
    # away from the body) and the FLAT flange face seats inward (x=FACE_X) on the
    # body boss, so the mating surface is completely flush. Lifted so its bore
    # clears the body.
    base = Pos(FACE_X, 0, PLATE_ZC) * Rot(0, 90, 0) * A._load("base_nema17")

    # flush flat tab: a coplanar extension of the inner mating face (its inner
    # face on x=FACE_X, same plane as the flange) dropping down to the boss. Low
    # in Z, so it clears the bearing boss (which sits high + outboard).
    tab_lo = ZC - BOLT_SP / 2 - 5
    tab_hi = PLATE_ZC - 21 + 3                     # overlap into the plate bottom
    tab = (Pos(FACE_X + TAB_T / 2, 0, (tab_lo + tab_hi) / 2)
           * Box(TAB_T, TAB_W, tab_hi - tab_lo))
    out = base + tab
    # 2 clearance holes through the tab, HORIZONTAL (Y), aligned to the inserts
    for s in (1, -1):
        out -= (Pos(FACE_X + TAB_T / 2, s * BOLT_SP / 2, ZC)
                * Rot(0, 90, 0) * Cylinder(SCREW_CLR / 2, TAB_T * 3))
    return out


def main():
    os.makedirs("out", exist_ok=True)
    bb, mp = body_boss(), mount_plate()
    export_stl(bb, "out/body_boss.stl");   export_step(bb, "out/body_boss.step")
    export_stl(mp, "out/mount_plate.stl"); export_step(mp, "out/mount_plate.step")
    print(f"body_boss:   vol {bb.volume:.0f}  bbox {bb.bounding_box().size}")
    print(f"mount_plate: vol {mp.volume:.0f}  bbox {mp.bounding_box().size}")
    print(f"  boss face x={FACE_X}  2x M3 inserts (Ø{INSERT_D} hole) @ horizontal spacing {BOLT_SP}")
    try:
        from preview import show
        show(bb, mp)              # both, in assembled position
    except Exception:
        pass


if __name__ == "__main__":
    main()
