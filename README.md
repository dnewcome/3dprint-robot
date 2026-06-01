# 3D-Printed Cycloidal Robot Arm

A 3D-printable robot arm built around **one parametric cycloidal joint**,
used three times. The near-term build target is a **3-DOF positioning
trunk** (base + shoulder + elbow); a wrist and/or BLDC actuators are parked
upgrades. Designed for **low backlash**, **commodity parts** (NEMA17, 608
bearings, magnets), and **fast iteration** on a home printer.

> **One joint, three instances.** J1/J2/J3 are the same cartridge
> (`cycloid_joint.scad`) at three sizes. J1 is that cartridge stood
> vertical, its output bearing sized up to carry the arm's tipping moment.

**Full design rationale → [DESIGN.md](DESIGN.md).** This README is the map.

## Status
Architecture converged and **pared down to a buildable 3-DOF trunk.** No
part is finalized for print yet — next step is a single-joint prototype.

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
- `cycloid_joint.scad` — **THE joint.** Parametric cartridge; `which=` selects
  J1/J2/J3, `part=` selects disc / ring / cam / flange / stator / assembly.
- `arm_trunk.scad` — **the build-target assembly** (3-DOF, pose-able).
- `encoder_joint_spec.md` — integrated output-side encoder.
- `DESIGN.md` — source of truth.

**Parked explorations** → [`parked/`](parked/README.md) — cable/capstan drive,
wrist mechanisms, harmonic ring, BLDC motor options + integrated actuator,
and the now-merged joint-source files.

## Viewing the CAD
[OpenSCAD](https://openscad.org). Render a part to PNG:
```bash
# the 3-DOF trunk
openscad -o arm_trunk.png --imgsize=850,1000 arm_trunk.scad

# the J2 cycloid disc (the actual printable part)
openscad -o disc.png -D 'which="J2"' -D 'part="disc"' cycloid_joint.scad

# a joint assembly / a different joint
openscad -o j1.png -D 'which="J1"' -D 'part="assembly"' cycloid_joint.scad
```
Each joint echoes its ratio, bearing OD, and ring OD to the console.

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

---
*Developed iteratively; see DESIGN.md for the full reasoning and the parked alternatives.*
