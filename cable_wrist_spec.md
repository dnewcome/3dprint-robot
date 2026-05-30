# Fully cable-driven wrist — zero motors past the shoulder

Goal: minimal distal mass. ALL six motors on the J1 turntable; the arm is
structure + Dyneema + idlers. Wrist = a cord-driven differential.
Files: `cable_wrist.scad`. Builds on `capstan_spec.md`.

## Motor census (all on the turntable / base)
| Joint | DOF | Drive | Travel |
|------|-----|-------|--------|
| J1 base | roll | geared cartridge (fixed base) → turntable | continuous |
| J2 shoulder | bend | capstan cord | ±135° |
| J3 elbow | bend | capstan cord (over J2) | ±135° |
| J4 forearm | roll | capstan cord to a forearm sector | ±135° |
| J5 wrist pitch | bend | **differential cord A/B** | ±100° |
| J6 tool roll | roll | **differential cord A/B** | ±135° |
→ 6 steppers, **none in the arm**. Forearm + wrist carry no motors.

## Weight reality (spend complexity where it pays)
- Removing the **J2/J3 NEMA17s** (~0.28 kg each @ 200–400 mm) is ~90% of
  the moment win — the capstan plan already does this.
- A fully cable wrist removes only the small J4/J6 motors (~0.7 N·m of
  shoulder torque) at the cost of +3 cords, +6 idlers, and full wrist
  coupling. Worth it only if you truly want nothing in the arm.

## The differential (J5 pitch + J6 roll from 2 cords)
Bevel differential, cords turn the side bevels instead of motors:
```
 cord A → side bevel A ┐
                       ├ central bevel on the J6 ROLL (tool) axis
 cord B → side bevel B ┘
 carrier yoke = J5 PITCH axis
   A,B same dir  → ROLL    A,B opposite → PITCH
 firmware:  roll=(a+b)/2   pitch=(a−b)/2     (CoreXY sum/difference)
```
- Side bevels can be printed bevel gears OR cord-and-pulley crosses.
- Each of A, B is a pull-pull loop (two runs) anchored on its side pulley.

## Routing (the 90° conversions)
```
turntable → [J2-concentric idler] → upper arm → [J3-concentric idler]
          → forearm CENTERLINE (on J4 axis, decouples forearm roll)
          → wrist redirect idlers → side bevels / pitch sector
```
- On the **forearm centerline** so J4 roll barely disturbs the wrist cords.
- Pitch sector plane CONTAINS the forearm axis → final turn is mostly
  in-plane; redirect idlers just set the pull-pull tangent points.
- J4 cord taps off earlier to a forearm-base sector (its own ±135°).

## Coupling matrix (output-side encoders calibrate it)
Lower-triangular; each downstream joint picks up upstream terms:
```
θ2 = k·φ2
θ3 = k·φ3 − c32·θ2
θ4 = k·φ4 − c42·θ2 − c43·θ3
[θ5;θ6] = M·[φA;φB] − C45·[θ2..θ4]   (M = differential sum/diff)
```
Calibrate c_ij empirically: move one joint, log the others' encoders.
This is why output-side absolute encoders are non-negotiable here.

## Gotchas specific to the cable wrist
- **Fleet angle:** as the pitch carrier swings, cord entry angle into the
  redirect idlers changes → keep idlers far / use self-aligning (pivoting)
  idlers, or accept reduced pitch range (±100°).
- **Idler count = friction + compliance.** J5/J6 are the least stiff
  joints (most crossings). Fine at 250 g; don't expect machine-tool rigor.
- **Tension coupling:** the differential shares cords A/B between pitch and
  roll — a pretension change affects both DOF. Tension both runs equally.
- **Cable count:** 5 capstan cords (each a pull-pull loop) + terminations
  + tensioners. This is the bulk of the build effort now — plan a tidy
  cable plate on the turntable.

## Pragmatic fallback
If 5-cord routing is too much for v1: cable J2/J3 only (the big win),
keep J4/J5/J6 as small local pancake steppers (NEMA11). Captures most of
the mass benefit; defer the differential + wrist routing to v2.
