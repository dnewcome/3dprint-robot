# 3D-Printed Cable-Driven Robot Arm

A 6-DOF (5-DOF fallback) 3D-printable robot arm built around **remote
Dyneema capstan drives** — the goal is **low backlash, light links, and
motors kept off the arm**, using commonly available NEMA17 steppers.

> **Design intent:** cables (always in tension) replace printed gears for
> zero backlash; motors live near the base/proximal links and drive the
> joints through cord over idlers; every joint carries an absolute
> magnetic encoder.

**Full design rationale lives in [DESIGN.md](DESIGN.md)** — this README is
the quick map.

## Status
Architecture converged; **prototyping the capstan drive first.** No part
is finalized for print yet.

## Headline specs
| | |
|---|---|
| DOF | 6 (full dexterity) / 5-DOF fallback |
| Payload | 250 g |
| Reach | ~490 mm from shoulder |
| Print volume target | 250 mm cube |
| Drive | 2-stage Dyneema capstan (~36:1 on bend joints) |
| Wrist | pure-cable differential (pitch+yaw) + cabled roll |
| Motors | NEMA17, distributed: each on the link just distal to its upstream joint |
| Feedback | output-side absolute magnetic encoders (AS5600 → MT6701) |

## Key decisions (the short version)
- **Cable, not printed gears** — zero backlash from tension.
- **Output bearing is the bottleneck** — large crossed-roller (BB race / 6810); validate first.
- **Motor just distal to the upstream joint** → tendons stay in one frame → **no inter-joint coupling**.
- **Pure-cable wrist** — rejected ABENICS (2-DOF drives), roller sphere, Agile Eye, bevel+U-joint (all backlash/buildability). See [wrist_decision.md](wrist_decision.md).
- **Roll joints stay geared** (capstan can't do continuous rotation) — optional rolling-element wave gear candidate.
- **No counterbalancing** — arm is light enough.

## Repo map
**Design docs**
- `DESIGN.md` — source of truth.
- `wrist_decision.md` — wrist mechanism trade study.
- `actuator_layout_spec.md` — distributed motor placement.
- `capstan_spec.md`, `cable_wrist_spec.md`, `encoder_joint_spec.md`, `turntable_spec.md` — subsystem detail.

**Parametric CAD (OpenSCAD)** — current / cable path
- `capstan.scad` — **parametric capstan + driven pulley sizer** (set cord dia + ratio → reports drum/pulley size, travel, tension).
- `capstan_drive.scad` — 2-stage capstan reduction.
- `capstan_teststand.scad` + `_spec.md` — **remote-capstan test rig** (next build).
- `cable_wrist.scad` — differential wrist schematic.
- `arm_v1.scad` — **current top-level assembly** (v1: cycloid joints, bevel-diff wrist, 5-DOF, pose-able).
- `base.scad` — J1 base: moment-bearing carrier + internal-ring drive.
- `arm_assembly.scad` — earlier cable-architecture concept render (superseded by arm_v1).
- `whole_arm.scad`, `turntable.scad` — layout.

**Exploratory / fallback (gear-based, kept for reference)**
- `cycloidal_disc.scad`, `joint_module*.{scad,md}`, `belt_stage.scad`, `arm_link*.{scad,md}` — cycloidal joint module.
- `harmonic_ring.scad`, `harmonic_drive_spec.md` — flat strain-wave.
- `coaxial_joint.scad`, `coaxial_joint_spec.md` — clevis-free cartridge.
- `wrist_differential.scad` — bevel differential (rejected for backlash).

## Viewing the CAD
[OpenSCAD](https://openscad.org). `capstan.scad` prints a sizing report to
the console (F5). Render a part to PNG:
```bash
openscad -o out.png --imgsize=900,900 capstan.scad
```

## Prototype plan
1. **Output bearing coupon** — printed BB crossed-roller race; load test for wobble.
2. **One capstan joint** — motor + 2-stage capstan + Dyneema + encoder; measure backlash, repeatability, creep.
3. **Pure-cable wrist (2-DOF)** — validate zero backlash + routing before the 3rd cord.
4. Replicate + integrate.

## References
- Cable-transmission arms (Barrett WAM, UC Berkeley Blue) — remote-cable inspiration.
- [Mishin Machine](https://youtube.com/@MishinMachine) — printed cable/wave-gear robotics; rolling-element wave gear is the optional roll-joint reducer candidate.
- [Morse Dynamics](https://instagram.com/morsedynamics) — closely related printed robotics / actuator-drivetrain work.

---
*Design developed iteratively; see DESIGN.md for the full reasoning and rejected alternatives.*
