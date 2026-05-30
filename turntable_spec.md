# Turntable motor-plate layout

J1 motor is fixed to the base and rotates the TURNTABLE. All other motors
ride the turntable, so their cords never cross J1 (no J1 coupling for
J2–J6). Files: `turntable.scad`.

## Motor census
| On | Motor | Drives | Notes |
|----|-------|--------|-------|
| **Fixed base** | J1 | turntable rotation | geared cartridge; vertical axis, inertia-limited only |
| Turntable | J2 | shoulder | 2-stage capstan |
| Turntable | J3 | elbow | cord crosses J2 |
| Turntable | J4 | forearm roll | cord crosses J2, J3 |
| Turntable | W1 | wrist diff A | crosses J2, J3, (J4) |
| Turntable | W2 | wrist diff B | crosses J2, J3, (J4) |
| Turntable | Grip | gripper tendon | crosses all |
→ 6 motors on the turntable + 1 fixed = **7 actuators**.

## Why motors-on-turntable (the deliberate trade)
- PRO: nothing crosses J1 → no J1 coupling, no fleet angle at the base.
- CON: J1 must accelerate ~6 motors of inertia. Fine — J1 is vertical
  (no gravity torque) and heavily geared; size it for base slew rate,
  not holding torque.
- v2 option: move J2/J3 motors to the fixed base, route their cords over a
  J1-concentric idler. J1 coupling is a single linear term (`+k·θ1`) →
  cheap to compensate. Defer until inertia actually bites.

## Plate arrangement
- 6 steppers in a ring (~80 mm radius → ~200 mm plate). Each has its
  2-stage reducer block (stage-1 pulley + stage-2 drum, `capstan_drive`).
- Stage-2 cords exit upward/inward toward a central **shoulder mast**
  carrying the J2 axis.
- Constant-force **spring tensioner per cord** on the plate (Dyneema creep
  — non-negotiable, see capstan_spec). Long runs (J4/W1/W2/grip span the
  whole arm) creep most → these tensioners matter most.

## The cable trunk = stacked concentric idlers (this is the WAM bit)
Every cord is a pull–pull LOOP (2 runs). Run count crossing each joint:
```
cross J2:  J3,J4,W1,W2,grip = 5 loops = 10 runs  (+ J2 itself wraps here)
cross J3:  J4,W1,W2,grip   = 4 loops = 8 runs
cross J4:  W1,W2,grip      = 3 loops = 6 runs
```
At J2 and J3, route every passing run over an idler **concentric with
that joint axis** → the crossing becomes a known linear coupling term, not
slack. In practice that's a **stacked idler pack** on the J2 axis (≈10
grooves) and on the J3 axis (≈8 grooves), one groove per run. Keep groove
order consistent so runs don't cross/rub.

## Coupling (lower-triangular, calibrate with output encoders)
```
θ2 = k·φ2
θ3 = k·φ3 − c32·θ2
θ4 = k·φ4 − c42·θ2 − c43·θ3
[θ5;θ6] = M·[φW1;φW2] − (wrist crossing terms)
```
Calibrate c_ij by moving one joint and logging the others' encoders.

## Electrical
- Motors rotate with the turntable → their wires cross J1. Use a **slip
  ring** (7+ motors × steps/enc = many conductors → a capsule slip ring)
  or a generous **service loop** if J1 travel ≤ ±180°. Encoders are on the
  joints (also cross J1) — same slip-ring/loop.

## Sizing notes
- Long cords (whole-arm runs) → more total creep elongation (∝ length) →
  consider a slightly heavier Dyneema for W1/W2/J4 and definitely the
  spring tensioners.
- Idler count on the long runs adds friction + compliance; W1/W2 (wrist)
  are the softest joints. Acceptable at 250 g.
- J1 inertia: ~6 × NEMA17 (~1.7 kg) at ~80 mm radius + arm. Geared
  cartridge ~90:1 handles it; don't expect fast base slews.
