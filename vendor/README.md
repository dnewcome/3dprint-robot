# vendor/ — third-party actuator geometry

The arm is built around the **[Sweep Dynamics](https://www.sweepdynamics.com)
cycloidal drives**. The printed arm sections (`../arm_section.scad`) fuse
directly to these actuators' interfaces, so a little of the vendor geometry is
needed as design input.

## What's tracked here (and why)
Only the **two interface parts** of the **20:1 Micro Cycloidal Drive** that the
arm sections are designed around:

| file | what it is |
|---|---|
| `micro/housing.stl` | the rotating cyclo **body** — fused into a section as the joint output |
| `micro/base_nema17.stl` | the **NEMA17 motor plate** — fused into a section as the motor mount |

These are included as derivative-design input only, with attribution — see
[`../NOTICE`](../NOTICE). They are **not** the product.

## What you supply (purchase from Sweep Dynamics)
Everything else is `.gitignore`d and not redistributed — you provide it from
your own purchase:

- the rest of the **Micro Cycloidal** (discs ×9 tolerances, shaft, end cap),
- the larger **base-slew** cycloidal drive (used for J1),
- all **STEP** sources.

Drop your purchased files in alongside (`micro/`, `slew/`); the `.scad` and the
sim will pick them up locally.
