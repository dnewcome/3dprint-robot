#!/usr/bin/env python3
"""
extract_vendor_steps.py — pull the two interface parts (housing body + NEMA17
plate) out of the Sweep Dynamics 20:1 Micro Cycloidal assembly STEP as exact
BREP solids, for the build123d arm sections to fuse against.

These two parts are vendor (paid) geometry; the outputs are .gitignore'd. Point
ASSEMBLY at your own purchased file. See NOTICE.

    python extract_vendor_steps.py [path/to/20-1 Micro Cycloidal.step]
"""
import sys, os
import build123d as bd

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.expanduser(
    "~/Downloads/cad-files/sweepdynamics/micro-cycloidal/20-1 Micro Cycloidal.step")
OUT = os.path.join(HERE, "vendor", "micro")


def pick(solids, h):
    """the 42x42 solid whose Z-height ~ h (mm)."""
    for s in solids:
        sz = s.bounding_box().size
        if abs(sz.X-42) < 1 and abs(sz.Y-42) < 1 and abs(sz.Z-h) < 0.5:
            return s
    raise SystemExit(f"no 42x42 solid of height {h} found")


def main():
    asm = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    sols = bd.import_step(asm).solids()
    parts = {"housing": pick(sols, 18.2), "base_nema17": pick(sols, 9.0)}
    os.makedirs(OUT, exist_ok=True)
    for name, s in parts.items():
        # recenter on origin, sitting on z=0 (print/native orientation)
        bb = s.bounding_box()
        s = s.translate((-(bb.min.X+bb.max.X)/2, -(bb.min.Y+bb.max.Y)/2, -bb.min.Z))
        bd.export_step(s, os.path.join(OUT, f"{name}.step"))
        print(f"  wrote {name}.step  vol={s.volume:.0f}  size={s.bounding_box().size}")


if __name__ == "__main__":
    main()
