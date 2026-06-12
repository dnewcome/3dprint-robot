# legacy/ — deprecated OpenSCAD sources

OpenSCAD is **no longer the CAD toolchain** for this project — the CAD has moved
to **[build123d](https://build123d.readthedocs.io)** (Python + OCC), which
imports the vendor STEP files as exact solids instead of meshes. These `.scad`
files are kept for reference only and are **not maintained**.

| file | status |
|---|---|
| `arm_section.scad` | superseded by [`../arm_section.py`](../arm_section.py) |
| `cycloid_joint.scad` | the from-scratch parametric cyclo joint (3-DOF track); no build123d port yet |
| `arm_trunk.scad` | the 3-DOF from-scratch assembly; uses `cycloid_joint.scad` |

To render the legacy parts you still need [OpenSCAD](https://openscad.org), e.g.
`openscad -o /tmp/x.png -D 'PART="upper"' legacy/arm_section.scad` (it imports
`../vendor/micro/*.stl`).

Older exploration `.scad` (cable drive, wrist, BLDC, harmonic) lives separately
in [`../parked/`](../parked/) and is also OpenSCAD-era.
