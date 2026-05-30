# 3D-Printed Cable-Driven 6-DOF Robot Arm — Design

**Status:** architecture converged on a remote, cable-driven (Dyneema
capstan) arm with distributed local motors and a pure-cable wrist.
Prototyping not yet started. This file is the single source of truth;
per-subsystem detail lives in the referenced `*_spec.md` files.

---

## 1. Goals & constraints
- **6-DOF** articulated arm (full dexterity), with a clean **5-DOF**
  fallback (drop forearm roll).
- **Payload:** 250 g at the tool.
- **Print volume:** 250 mm cube. One-piece links ≤ ~180 mm; larger split
  and bolt.
- **Reach:** ~490 mm from the shoulder.
- **Low backlash** is the governing value — it drove every major choice
  (cable over printed gears, Dyneema, output-side encoders).
- **Commonly available actuators:** NEMA17 steppers, open-loop to start;
  no servo drives required initially.
- **Cost/printability** over precision-machined parts.

## 2. Architecture at a glance
```
 fixed base ─ J1 yaw ─ TURNTABLE ─ J2 shoulder ─ upper arm ─ J3 elbow
   ─ forearm ─ [wrist: pitch + yaw + roll, pure-cable] ─ gripper
```
- **Drive:** Dyneema capstan (cable) reduction. Zero backlash, light arm,
  motors kept off the distal links.
- **Motors:** distributed — each joint's motor sits on the link just
  distal to the upstream joint (see §6), so no tendon crosses a joint →
  **no inter-joint coupling.**
- **Bends (J2/J3 + wrist pitch/yaw):** capstan to an output sector/drum.
- **Rolls (J1, optional J4):** continuous-rotation; capstan can't do
  continuous travel, so these stay geared/direct or are provided by the
  wrist's cabled roll.
- **Every joint:** large crossed-roller output bearing + output-side
  absolute magnetic encoder.

## 3. Governing design principles
1. **Cable, not printed gears, for low backlash.** Cables are always in
   tension → no lash; printed strain-wave/cycloidal/bevel all carry lash.
2. **Output-side absolute encoder on every joint.** True joint angle,
   immune to upstream slop; enables homing without limit switches and
   makes any residual coupling calibratable.
3. **The output moment bearing is the real bottleneck**, not the
   reduction. Size it big, concentric, outboard. Validate it first.
4. **Mount each motor just distal to its joint's predecessor** → tendon
   stays in one moving frame → no coupling matrix.
5. **Prove one joint before replicating.** De-risk on the bench.

## 4. Joint drive — Dyneema capstan
- **Reduction (bends J2/J3):** 2-stage capstan, 6:1 × 6:1 = **36:1**.
  Drum r=10 mm, pulley/sector R=60 mm.
- **Cord:** **Dyneema DM20 (UHMWPE)**, anchored both ends (terminated
  capstan = zero slip). Bends to ~5× dia.
- **Cord sizing by CREEP, not strength:** keep pretension + peak load
  < ~25% MBL → target MBL ≥ ~1050 N for J2. Use SK78/SK99, pre-stretch.
- **Constant-force spring tensioner per cord** — non-negotiable: takes up
  creep automatically and preserves pretension (a fixed turnbuckle goes
  slack and reintroduces lash).
- **Terminations:** splice (Brummel/locked bury) or anchored wraps + clamp.
  **No knots** (slip, −50% strength). Radius all groove/anchor edges.
- **Helical groove, pitch = cord dia**, on every drum (prevents wrap
  climbing).
- Detail: `capstan_spec.md`, `capstan_drive.scad`.

## 5. Output bearing & encoder (shared by all joints)
- **Bearing:** large crossed-roller — printed **airsoft-BB race
  (~90–104 mm)** or a bought thin-section (6810, 50×65×7). Single bearing
  reacts the full cantilever moment; bigger + outboard = stiffer.
  **This is Proto 1 — validate before anything else.**
- **Encoder:** diametric 6×2.5 mm magnet on the output + magnetic IC.
  **AS5600** (12-bit I²C, $3) for prototyping → **MT6701** (14-bit SSI)
  for production. Same magnet/mount, drop-in upgrade.
  - Keep steel (bearing, fasteners) ≥ ~8 mm from the magnet.
  - AS5600 address fixed (0x36) → one per bus; use a TCA9548A mux or one
    MCU per joint on a shared bus.
- Detail: `encoder_joint_spec.md`.

## 6. Actuator layout — distributed local cable drive
Each joint's motor on the link just distal to the upstream joint → no
tendon crosses a joint → no coupling. Supersedes the all-on-turntable
cable-trunk idea for v1.

| Motor | Mounted on | Drives |
|------|-----------|--------|
| J1 | ground (fixed, zero inertia cost) | base yaw → turntable |
| J2 | turntable | shoulder |
| J3 | upper-arm proximal | elbow |
| wrist (2–3) | forearm proximal (just after elbow) | wrist DOF |
| gripper | forearm (Bowden) | gripper |

- Mass stays near each carrying joint's axis (low moment); J2 lands
  ~5–7 N·m worst case — within budget.
- **Electrical crosses J1**: slip ring (many conductors) or service loop
  if J1 ≤ ±180°.
- **Upgrade path:** to chase distal mass later, move motors proximal and
  re-introduce through-joint routing (concentric idler trunk + coupling
  matrix, per `turntable_spec.md`). Joints/tendons unchanged.
- Detail: `actuator_layout_spec.md`, `turntable_spec.md`.

## 7. Wrist — pure-cable differential (zero backlash)
Trade study (`wrist_decision.md`) rejected every geared/exotic option for
backlash or buildability; **landed on an all-cable wrist.**

- **Cable differential (2 cords) → pitch + yaw** (no gears → no gear lash).
- **3rd cord pair over a pitch-axis-concentric idler → roll** (the
  zero-backlash way to carry rotation across the bend — a tendon, not a
  U-joint/shaft). = full 3-DOF, zero lash, all forearm-driven (WAM-style).
- Each cord pair routes down the forearm centerline over the pitch-axis
  idler; the third axis is **incremental** (one more cord pair + idler +
  one calibratable coupling term).
- **Rejected options (do not revisit):**
  - **ABENICS cross-spherical:** each drive module is ~2-DOF (gears must
    tilt to stay meshed); no off-the-shelf 2-DOF drive → not DIY-buildable.
  - **Roller-driven sphere:** slip + 3-DOF orientation sensing.
  - **Agile Eye (spherical parallel):** limited tilt + precise curved
    links.
  - **Bevel differential:** gear backlash at the tool.
  - **U-joint roll shaft through the bevel:** stacks bevel + Cardan lash —
    betrays the zero-backlash premise.
- Detail: `wrist_decision.md`, `cable_wrist_spec.md`, `wrist_differential.scad`
  (note: the bevel `.scad` is now a rejected reference).

## 8. Gripper
- **Single-acting Bowden tendon + spring return:** one cord pulls to close,
  spring opens. Grip force = motor current.
- Holding 250 g needs ~10–20 N grip → ~30 N cord tension → trivial (0.5 mm
  Dyneema). Bowden lets the motor sit back; sheath friction adds
  hysteresis (fine for grasping, not precise force control).

## 9. Geometry & reach
| Param | Value |
|------|-------|
| Base column / shoulder height | ~118–150 mm |
| Upper arm (J2→J3) `a1` | 200 mm |
| Forearm (J3→wrist) `a2` | 200 mm |
| Wrist→tool `a3` | 90 mm |
| Reach from shoulder | ~490 mm |
| Max tip height | ~610 mm |
- Visualize/pose: `arm_assembly.scad` (→ `arm_assembly.png`),
  `whole_arm.scad`.

## 10. Torque / sizing budget
- **NEMA17 throughout** (run ≤ ~50% holding open-loop). No NEMA23 needed.
- Bend joints at 36:1: ~24 N·m available vs ~11 N·m worst-case demand.
- **Capstan torque ceiling** = working tension × sector radius ≈ **16 N·m**
  at R=60 mm (bump J2 sector to 80 mm for margin).
- **Cable is inherently protected:** NEMA17 stall × ratio can't exceed the
  cord's working load → set stepper run-current as an electronic torque
  limit.
- Wrist & gripper loads are < ~0.5 N·m — trivial.
- **Counterbalancing: deliberately omitted.** The arm is light enough that
  gravity comp isn't needed. A J2 spring/gas strut is a known bolt-on
  (lowers holding torque + cable pretension) if it's ever wanted — no
  architecture change to add it.

## 11. Control
- Open-loop steppers + output-side absolute encoders for homing and
  position readout (closed loop later if wanted).
- Distributed motor layout → **no inter-joint coupling** to compensate in
  v1. The only coupling is the wrist's 3rd-axis cord crossing the pitch
  axis → one calibratable term (move the joint, log the encoders).
- One MCU per joint (or per cluster) on a shared bus is the cleanest given
  the AS5600 single-address constraint.

## 12. Open decisions
1. **6-DOF vs 5-DOF:** 6-DOF = 3 wrist cord pairs (pitch+yaw+roll);
   5-DOF = 2 pairs, add the 3rd later. Same pure-cable mechanism.
2. **Single vs per-cluster MCU / bus topology.**
3. **Output bearing:** printed BB race vs bought thin-section (decide on
   Proto 1 results).

## 13. Prototype / de-risk plan
1. **Proto 1 — output bearing coupon.** Printed BB crossed-roller race;
   hang 250 g at 450 mm, measure wobble (<0.5 mm). Decides BB vs bought.
2. **Proto 2 — one capstan joint.** Motor + 2-stage capstan + Dyneema +
   sector on the Proto-1 bearing + AS5600. Measure **backlash (~0 is the
   whole point), repeatability, cable creep/tension hold** over cycling.
3. **Proto 3 — pure-cable wrist (2-DOF first).** Cable differential
   pitch+yaw on the bench; validate zero backlash and routing/fleet angle
   before adding the 3rd cord.
4. Then replicate + integrate the full arm.

## 14. File index
**Current / canonical (cable-driven path):**
- `DESIGN.md` — this file.
- `capstan_drive.scad`, `capstan_spec.md` — cable reduction.
- `actuator_layout_spec.md` — distributed motor placement.
- `cable_wrist_spec.md`, `wrist_decision.md` — wrist (pure-cable).
- `encoder_joint_spec.md` — integrated encoder.
- `turntable.scad`, `turntable_spec.md` — base (also the remote-trunk
  upgrade path).
- `arm_assembly.scad`/`.png`, `whole_arm.scad` — visualization.

## 15. Candidate parts / references
- **Roll-joint reducer (OPTIONAL, post-capstan):** Mishin Machine's
  **rolling-element wave gear** (strain-wave/cycloidal hybrid with steel
  balls/rollers — printed profiles, steel does the wear/precision).
  Better printable reducer than the cycloidal/harmonic fallback; good
  candidate for **J1 (and optional J4/J6)** continuous-rotation joints
  where capstan's finite travel doesn't work. Parametric OnShape model +
  NEMA17 housing + generator available. NOT for the bend joints (those
  stay cable). Print + measure backlash before trusting it. Decision:
  deferred — **capstan drive is being prototyped first.**
  Channel: youtube.com/@MishinMachine (similar printed cable/gear robotics).
- **Mishin techniques worth borrowing:**
  - *Belt pre-stage* — already used (2:1 GT2 into the reduction).
  - *Right-angle cycloid* — reduction + 90° axis turn in one unit; tucks a
    motor along a link to drive a perpendicular joint. Gear-path only
    (relevant if a bend joint ever goes geared).
  - *Through-bore / decoupled-center cycloid* — hollow joint center to
    route the dress-pack + downstream tendons ON the rotation axis. Useful
    regardless of drive type — carry into the joint housings.
  - His cycloidal cartridge ≈ our `cycloidal_disc.scad` (steel dowels,
    eccentric cam, output-pin disc) — validates the fallback joint design.

## File index (cont.)
**Exploratory / fallback (gear-based path, kept for reference):**
- `cycloidal_disc.scad`, `joint_module*.{scad,md}`, `belt_stage.scad`,
  `arm_link*.{scad,md}` — cycloidal joint module.
- `harmonic_ring.scad`, `harmonic_drive_spec.md` — flat strain-wave.
- `coaxial_joint.scad`, `coaxial_joint_spec.md` — clevis-free cartridge.
- `wrist_differential.scad` — bevel differential (rejected for backlash).
