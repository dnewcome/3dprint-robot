#!/usr/bin/env python3
"""
gen_meshes.py — generate the sim's arm-section meshes from the build123d CAD.

The sim links ARE the printed arm sections (arm_trunk.urdf references
meshes/arm_long.stl). Those meshes embed the paid vendor geometry, so they're
.gitignore'd and you regenerate them locally:

    python extract_vendor_steps.py     # once: pull the 2 vendor parts (your STEP)
    python sim/gen_meshes.py           # -> sim/meshes/arm_long.stl

Needs build123d + your purchased Sweep Dynamics assembly STEP. See ../NOTICE.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))           # repo root (for arm_section)
import arm_section as A                              # noqa: E402
from build123d import export_stl                     # noqa: E402

MESHES = os.path.join(HERE, "meshes")
SECTIONS = {"arm_long": A.long_section(150)}         # full-length long section


def main():
    os.makedirs(MESHES, exist_ok=True)
    for name, sec in SECTIONS.items():
        path = os.path.join(MESHES, f"{name}.stl")
        export_stl(sec, path)
        print(f"wrote {os.path.relpath(path, os.path.dirname(HERE))} "
              f"(vol {sec.volume:.0f} mm^3)")


if __name__ == "__main__":
    main()
