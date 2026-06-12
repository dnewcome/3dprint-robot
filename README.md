# 3D-Printed Cycloidal Robot Arm

A 3D-printable cycloidal robot arm, designed for **low backlash**, **commodity
parts** (NEMA17, 608 bearings, magnets), and **fast iteration** on a home
printer. Two design tracks live here:

- **Integrated-actuator arm (current direction).** A **5-DOF** arm built from
  printed **sections** that fuse directly to off-the-shelf
  [Sweep Dynamics](https://www.sweepdynamics.com) **20:1 Micro Cycloidal**
  drives (a larger cycloidal at the base slew). Each section integrates one
  half of a joint at each end — the rotating cyclo **body** (upstream joint
  output) on one end, the **NEMA17 motor plate** (downstream motor mount) on
  the other — so the link *is* the actuator mount. See `arm_section.scad`.
- **From-scratch parametric joint (original track).** A **3-DOF** positioning
  trunk built around **one parametric cycloidal joint** (`cycloid_joint.scad`)
  used three times — no bought actuators. Kept as the ground-up alternative.

![integrated arm section](images/arm_section.png)

**Full design rationale → [DESIGN.md](DESIGN.md).** This README is the map.

## Status
Active. **Current focus:** the integrated-actuator arm — the long arm section
is modeled and prints as one fused solid; the two 90° end sections (base→slew,
wrist→tool-roll) are next. No part is finalized for print yet.
**In progress:** migrating the CAD from OpenSCAD to **[build123d](https://build123d.readthedocs.io)**
(Python + OCC) — it imports the vendor STEP files as exact solids, a better fit
for the fused-actuator parts than mesh import. `arm_section.py` is the ported
long section (the `.scad` stays as the no-dependency reference).

## Headline specs
| | |
|---|---|
| Near-term DOF | **3** (positioning trunk: J1 yaw + J2 shoulder + J3 elbow) |
| Future DOF | 5–6 via parked wrist / BLDC upgrades |
| Payload | 250 g |
| Reach | ~480 mm from shoulder |
| Print volume target | 250 mm cube |
| Joint drive | NEMA17 → 2:1 GT2 belt → cycloid (18:1) = **36:1** |
| Output bearing | large BB crossed-roller, **outboard of the gears** (J1's = the moment bearing) |
| Feedback | output-side absolute magnetic encoder per joint |

## Key decisions (the short version)
- **One cycloidal joint, three sizes** — build/tune once, reprint to scale.
- **Floating-roller cycloid** — nylon rollers, clearance sets backlash, SLA
  bearing surfaces for finish. No steel dowels required.
- **Bearing outboard of the gearset** (clevis-free stator/rotor cartridge) →
  carries the cantilever moment; **J1 = same cartridge vertical**, bearing sized up.
- **3 DOF is useful** — three joints position the tool point; bolt on a fixed
  gripper or manual wrist. Extra DOF is a deliberate later step, not v1.
- **Explorations parked, not deleted** — cable drive, wrist, BLDC, harmonic
  all live in [`parked/`](parked/) for when the trunk proves out.

## Repo map
**Build path (root)**
- `arm_section.scad` — **the integrated-actuator links** (current direction).
  Parametric; `PART=` selects `base` / `upper` / `forearm` / `wrist`. Fuses the
  Sweep Dynamics micro-cyclo body + NEMA17 plate into one printable section.
- `arm_section.py` — the **build123d** port of the above (exact STEP solids →
  `out/`). Needs `pip install build123d` + `extract_vendor_steps.py` (pulls the
  two parts out of your purchased assembly STEP). Generated STL/STEP land in `out/`.
- `cycloid_joint.scad` — **the from-scratch joint.** Parametric cartridge;
  `which=` selects J1/J2/J3, `part=` selects disc / ring / cam / flange / stator.
- `arm_trunk.scad` — the 3-DOF from-scratch assembly (pose-able).
- `vendor/` — the two Sweep Dynamics input parts + how to get the rest
  ([`vendor/README.md`](vendor/README.md)). Paid geometry — read [`NOTICE`](NOTICE).
- `encoder_joint_spec.md` — integrated output-side encoder.
- `DESIGN.md` — source of truth.

**Simulation & analysis** → [`sim/`](sim/README.md) — MuJoCo model + tools to
pose it, size the motors (torque/reach/motor-catalog), budget backlash, watch it
hold/sag under gravity, and run a closed-loop reach controller (the digital-twin
foundation). Where the motor/reduction/backlash trade-offs were quantified.

**Parked explorations** → [`parked/`](parked/README.md) — cable/capstan drive,
wrist mechanisms, harmonic ring, BLDC motor options + integrated actuator,
and the now-merged joint-source files.

## Viewing the CAD
[OpenSCAD](https://openscad.org). Render a part to PNG:
```bash
# an integrated-actuator arm section (current direction)
openscad -o images/arm_section.png -D 'PART="upper"' arm_section.scad

# the from-scratch 3-DOF trunk
openscad -o images/arm_trunk.png --imgsize=850,1000 arm_trunk.scad

# the J2 cycloid disc (the actual printable part)
openscad -o images/disc.png -D 'which="J2"' -D 'part="disc"' cycloid_joint.scad
```
> `arm_section.scad` imports `vendor/micro/*.stl`. The two tracked parts are
> enough to render the link; the full actuator you supply from your Sweep
> Dynamics purchase (see [`vendor/README.md`](vendor/README.md)).

## Prototype plan
1. **One joint (J2)** — print the disc, pin ring, cam, flange + BB race;
   assemble with a NEMA17 + belt; measure backlash, repeatability, friction.
2. **J1 base** — same cartridge vertical; load-test the moment bearing.
3. **Trunk** — J1+J2+J3 + links; verify reach, stiffness, repeatability.
4. Then revisit a wrist (from `parked/`) for 5–6 DOF.

## References
- Cable-transmission arms (Barrett WAM, UC Berkeley Blue) — remote-cable inspiration.
- [Mishin Machine](https://youtube.com/@MishinMachine) — printed cable/wave-gear robotics.
- [Morse Dynamics](https://instagram.com/morsedynamics) — related printed robotics / drivetrains.
- [Skyentific](https://youtube.com/@Skyentific) — printed BLDC + cycloidal joint actuators.

## License & attribution
This project's own work (CAD source, simulation, docs) is **MIT** licensed
([`LICENSE`](LICENSE)). It is **not** affiliated with Sweep Dynamics. The two
bundled actuator meshes under `vendor/` are Sweep Dynamics' paid geometry,
included as derivative-design input with attribution — see [`NOTICE`](NOTICE).
Buy the actuators at [sweepdynamics.com](https://www.sweepdynamics.com).

---
*Developed iteratively; see DESIGN.md for the full reasoning and the parked alternatives.*
