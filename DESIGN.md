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

## Design philosophy — complexity arbitrage
Spend the thing 3D printing makes free (arbitrary geometric complexity) to
buy down what's actually expensive: precision-machined/specialty parts,
money, and lead time. Prefer **clever printed shapes + commodity hardware**
(NEMA17, 608 bearings, steel dowels, nylon spacers, Dyneema, magnets) over
simple shapes that need bought precision. Higher *conceptual* complexity is
an acceptable price for *part availability* and fast iteration.

**The refinement that protects "iterate easily":** 3DP makes *fabrication*
complexity free — it does NOT make *assembly/tuning/debug* complexity free.
The real limit on iteration speed is part count, tolerances, and things you
must calibrate (cable tension, backlash, coupling), not print cost. So the
rule isn't "minimize complexity" — it's **push complexity into the printed
geometry, keep it out of the assembly/tuning loop: complex to print, simple
to build and tune.**

Tactics to keep the iteration loop cheap:
- **Modular swappable joints** — iterate by reprinting one part, not the arm.
- **Reuse hardware, reprint plastic** — a revision costs filament + an hour,
  never new bought parts.
- **Parametric files** (`capstan.scad` etc.) — a change is a number, not a remodel.
- **Engineer the tuning out** — constant-force tensioner (no re-tensioning),
  output encoders (calibrate coupling instead of building it out).

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

## v1 build configuration (the cohesive 6-DOF integration)
Per-joint calls for the first buildable arm:

| Joint | Drive | Motor | Notes |
|------|-------|-------|-------|
| **J1 base** | fixed internal ring (72T) + onboard pinion (18T) = **4:1**, on a ~116 mm BB moment bearing | onboard the turntable | gravity-neutral axis → low ratio fine; bearing is the real job. `base.scad` |
| **J2 shoulder** | coaxial stepper + cycloid; **drive body = the arm link** | coaxial at shoulder | clevis-free cantilever (`coaxial_joint.scad`, cycloidal internals) |
| **J3 elbow** | **FORK** (decide): (a) Dyneema remote capstan, or (b) remote cycloid via a long input shaft from a shoulder-mounted stepper | shoulder or upper-arm | (b) reuses the cycloid + no cable to tune; (a) is the zero-backlash but fiddlier path still to be prototyped |
| **J4/J5/J6 wrist** | **geared bevel differential** (no belts) | 2 steppers on forearm | differential = **2 DOF (pitch+roll)** only |

**Open decisions (pin before full integration):**
1. **DOF:** bevel differential is **2 axes** → 5 motors = **5-DOF v1**. The 3rd
   wrist axis (J4 forearm roll) needs a 6th motor — leave a mount, add later.
   (Matches "simple enough for now.")
2. **Shoulder structure drives J3:** the "J3 motor opposite J2 at the
   shoulder" idea needs a **two-sided yoke shoulder**, which conflicts with
   the **one-sided coaxial cantilever J2**. Pick one: clean cantilever J2
   *or* symmetric back-to-back motors. Recommendation: cantilever J2 +
   remote-cycloid J3 (long shaft up the upper arm); keep the Dyneema rig as
   a separate de-risking experiment.
3. **J1 is gravity-neutral** (vertical axis) → simple 4:1 internal-ring
   drive is sufficient; spend the effort on the moment bearing.

Reduction reuse: J1 and J2 are both cycloid/internal-ring coaxial drives —
share the cartridge design where possible (modularity, per the philosophy).

## 14. File index
**Current / canonical (cable-driven path):**
- `DESIGN.md` — this file.
- `capstan_drive.scad`, `capstan_spec.md` — cable reduction.
- `actuator_layout_spec.md` — distributed motor placement.
- `cable_wrist_spec.md`, `wrist_decision.md` — wrist (pure-cable).
- `encoder_joint_spec.md` — integrated encoder.
- `turntable.scad`, `turntable_spec.md` — base (also the remote-trunk
  upgrade path).
- `arm_v1.scad`/`.png` — **current top-level assembly** (v1 build config).
- `base.scad`/`.png` — J1 base (moment-bearing carrier + internal-ring drive).
- `arm_assembly.scad`/`.png`, `whole_arm.scad` — earlier cable-concept viz.

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
- **Morse Dynamics** (instagram.com/morsedynamics) — closely related
  printed robotics / actuator-drivetrain work; reference for joint, drive,
  and reducer techniques.
- **Skyentific** (youtube.com/@Skyentific) — printed **BLDC + cycloidal
  integrated robot-joint actuators** (frameless motor built into the
  reducer, FOC, dual encoders); closest existing work to the integrated-
  actuator idea below. Also covers inverted/decoupled cycloid topologies.

### Design idea (PARKED — not committed): pancake BLDC joint actuator
Replace the coaxial stepper with a low-profile **pancake BLDC** (~90 mm OD,
matching the cycloid ring) for a thin integrated actuator + backdrivable /
force-controllable motion. Key findings:
- **Don't look for an inrunner.** A 90 mm low-profile inrunner-with-shaft
  doesn't exist and is the wrong topology: torque ∝ rotor radius, so big
  pancakes put magnets at large radius = **outrunner or frameless**. An
  inrunner here = low torque + high Kv (wrong for a joint).
- **Two viable parts:**
  - *Gimbal outrunner* (T-Motor GB / iPower GBM / generic ~90 mm, low Kv,
    ~15–30 mm tall) — easiest, off-the-shelf. Mount the static core to the
    joint body, **bolt the eccentric cam to the rotating bell** (no shaft).
  - *Frameless BLDC kit* (rotor ring + stator ring) — build your own
    inrunner-style with a protruding shaft; max integration, more assembly.
- **Electronics:** needs FOC (ODrive / SimpleFOC / VESC) + commutation
  encoder — this is "building servo drives." Synergy: the planned magnetic
  encoder (AS5048/MT6701) **doubles as the FOC sensor**.
- **Still keep the cycloid reduction** — BLDC upgrades the motor, not the
  gearbox; and a low-ratio BLDC must draw current to hold a pose (heat) →
  meaningful reduction needed. BLDC **+ cycloid**, not direct-drive.
- **Don't load the motor's light bearings** with the eccentric — let the
  cycloid's own input bearing carry it; motor supplies torque only.
- **Sequencing:** design the joint cartridge **dual-use** (stepper+belt now
  / frameless BLDC stator bore later); prototype mechanics with cheap
  open-loop steppers first, swap to BLDC once compliance/smoothness is
  wanted. The 90 mm cycloid ring already matches a 90 mm motor → drop-in.
- **Status:** parked — adds electronics/tuning complexity (against
  "simple to build/tune"); revisit after the stepper+cable mechanics prove
  out. Capstan/stepper remains the committed path.

#### Sub-idea: small-frame BLDC + reduction as a NEMA-17 drop-in
Evaluating several off-the-shelf BLDC options (e.g. a 2204-class drone
outrunner, modeled in `bldc_2204.scad`, through to larger gimbal frames).
A small BLDC **+ reduction can stand in for a NEMA 17 at a fraction of the
mass** — the torque/speed numbers are easy; thermal-at-stall and control
are the real constraints.
- **Torque math (2204-1400KV example):** `Kt = 8.27/Kv ≈ 5.9 mN·m/A`.
  - 10 A burst → 59 mN·m → only **~7:1** to match a 0.4 N·m NEMA-17 hold.
  - 3 A sane-continuous → 18 mN·m → **~22:1** for 0.35 N·m output.
  - Our existing 4–36:1 reductions already cover this; ≥20:1 gives
    NEMA-17-class continuous torque and several × that on burst.
- **Speed is surplus:** ~15,000 rpm free-run on 3S → ~430 rpm output even
  at 36:1. You trade away speed to buy torque — exactly what's wanted.
- **Mass win:** 2204 ≈ **28 g** vs NEMA 17 ≈ **280 g**. Even with a printed
  cycloid stage, well under the stepper → big distal-link inertia drop
  (serves the "mass off the arm" goal). Good **wrist / gripper** candidate.
- **Catch 1 — holding against gravity is the BLDC weak spot:** ~zero detent
  torque, so holding a pose = servoing current at **zero rpm** = worst-case
  heat with no propwash. Fix with enough reduction (low holding current),
  a detent brake, or a self-locking-ish stage.
- **Catch 2 — commits to FOC:** ODrive / SimpleFOC + encoder. The planned
  output-side magnetic encoder **doubles as the commutation sensor**.
- **Catch 3 — 1400 KV is the wrong wind for a joint:** racing motors are
  wound for speed (need high current → stall heat) and their "continuous"
  rating assumes prop cooling we won't have. **Prefer a low-KV gimbal wind**
  (~100–200 KV, e.g. GB2208 / 4008-class) in the same frame: 7–14× the
  torque-per-amp, so holding current and heat drop hard. Same envelope /
  CAD, just rewound. **Spec gimbal-wound for any joint that holds load.**
- **Takeaway:** as a *frame*, a small BLDC is a viable drop-in for a distal
  joint at ≥20:1 with a derated thermal budget; as a *racing wind* it runs
  hot at stall. `bldc_2204.scad` is the fit/envelope model for trial fits.
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

### Design idea: integrated BLDC-cycloidal actuator (one drive unit)
Build a **frameless BLDC into the cycloidal reducer** so motor + gearbox +
encoders are a single sealed unit — the big payoff of going BLDC. Model:
`integrated_actuator.scad` (concept cross-section). Prior art: commercial
Harmonic Drive **FHA** / Nabtesco **RV** / **CubeMars AK** & T-Motor joints;
DIY/printed: **Skyentific** (closest existing work — printed BLDC-cycloidal
robot-joint actuators).

- **Frameless motor = stator ring + rotor ring, no housing/bearings.** You
  supply the structure, so the magnetics build directly into the cycloid's
  members instead of bolting on a separate motor.
- **Member mapping:**
  - rotor magnet ring → **eccentric carrier** (input, motor speed)
  - stator ring → **fixed** to the housing (alongside the pin ring)
  - output disc/plate → rides the big **moment bearing** (slow output)
  - This makes the earlier **bell-as-eccentric** idea concrete: the rotor
    *is* the bell; its eccentric crank drives the disc.
- **Reduction** unchanged — still set by lobe count (`cycloidal_disc.scad`
  math). The motor fills volume the reducer already had → ~zero extra axial
  space beyond the magnet zone.
- **Four integration-specific challenges** (don't exist for a bolt-on motor):
  1. **Air gap must stay concentric, isolated from the eccentric.** Magnet
     ring spins truly concentric on a **main bearing**; only a separate
     eccentric crank on the rotor drives the disc. If disc load deflects the
     magnets into the stator → cogging / rub / dead motor. Main bearing
     (thin-section ball or printed BB race) takes the cycloid side-load so
     the magnets never see it.
  2. **Heat path.** Windings buried in plastic (an insulator) + stall-hold
     current = cooking risk. Bond stator to a **metal insert** tied to the
     housing, run **low-KV** (~2 A hold), add a winding **thermistor**.
     This is the constraint that most often bites printed integrated actuators.
  3. **Two encoders.** Rotor-back magnet (AS5048, FOC/commutation) + output
     magnet (MT6701, absolute joint angle). Both sensors on the **static**
     housing → no wires cross a rotating interface, no motor slip ring.
  4. **Balance.** Eccentric orbiting mass shakes — use **twin discs 180°
     out of phase** (also wanted for smoothness).
- **Two forks:**
  - *Outrunner vs inrunner frameless* — outrunner (magnets at large radius)
    = more torque but magnet-zone and pin-ring-zone stack **axially** (a bit
    taller); inrunner is flatter but lower torque density. → **outrunner**.
  - *Cycloidal vs harmonic* — frameless integrates even more naturally into
    **harmonic** (wave generator = rotor, gap concentric by construction =
    the FHA architecture), but needs a durable **printed flexspline**.
    Cycloidal is the print-robust choice; harmonic the elegant one.
- **Status:** concept — same parked rationale (electronics/tuning vs "simple
  to build/tune"). The unit unifies low-KV motor + bell-as-eccentric + output
  moment bearing + dual encoders into one part; revisit after stepper+cable
  mechanics prove out.

## File index (cont.)
**Exploratory / fallback (gear-based path, kept for reference):**
- `cycloidal_disc.scad`, `joint_module*.{scad,md}`, `belt_stage.scad`,
  `arm_link*.{scad,md}` — cycloidal joint module.
- `harmonic_ring.scad`, `harmonic_drive_spec.md` — flat strain-wave.
- `coaxial_joint.scad`, `coaxial_joint_spec.md` — clevis-free cartridge.
- `wrist_differential.scad` — bevel differential (rejected for backlash).
- `bldc_2204.scad` — 2204-class outrunner BLDC fit/envelope model
  (parametric; candidate small-frame actuator, see parked-BLDC sub-idea).
- `bldc_options.md` — BLDC candidate comparison (KV markets, KV↔reduction
  trade, holding-current-at-stall) for picking a joint motor.
- `integrated_actuator.scad` — concept cross-section of a frameless BLDC
  built into the cycloid (one drive unit; see integrated-actuator idea).
