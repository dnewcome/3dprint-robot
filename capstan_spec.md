# Remote 2-stage capstan arm (WAM-class)

Motors on the J1 turntable; steel cables drive the bend joints (J2/J3/J5)
through two capstan stages. Zero backlash, light arm, motors off the
distal links. Files: `capstan_drive.scad`.

## Arm architecture
| Joint | Type | Drive |
|------|------|-------|
| J1 base | roll (continuous) | geared cartridge (fixed base), output = TURNTABLE |
| **J2 shoulder** | bend | **remote 2-stage capstan** from turntable |
| **J3 elbow** | bend | **remote capstan**, cable routed over J2 |
| **J5 wrist** | bend | **remote capstan**, cable routed over J2+J3 |
| J4 forearm | roll (continuous) | small roll cartridge on the arm |
| J6 tool | roll (continuous) | small roll cartridge on the arm |

Motors for J2/J3/J5 ride the turntable → **J1 never enters the cable
coupling.** Arm links carry no bend-joint motors → very light.

## Reduction & cable
- 2 stages, **6:1 × 6:1 = 36:1**. Drum r=10 mm, pulley/sector R=60 mm.
- Stage-1 pulley shares a shaft with the stage-2 drum (compound stage).
- Cable: **Dyneema DM20 (UHMWPE), anchored both ends** (terminated
  capstan = zero slip). 5–6 wraps/drum. Confirm cord dia + MBL to finalize
  drum/sector sizes and pretension (see sizing below).
- Dyneema bends to ~5× dia → drums can SHRINK: r_drum 6 mm → sector R 36 mm
  still gives 6:1, so **sector dia ~72 mm** (vs 120 mm with steel). More
  compact joints, smaller footprint. Optional — keep 60 mm for stiffness.
- Output sector arc 270° → **±135° travel**.
- Same big crossed-roller output bearing + output-side encoder as the
  coaxial cartridge — only the reduction element changes.

## Tension / sizing (J2 worst case ~11 N·m) — size by CREEP, not strength
- Stage-2 cable tension = T_out/R_sect = 11/0.06 = **183 N** (at 60 mm
  sector). Stage-1 cable sees ~1/6 (~30 N).
- **Dyneema is plenty strong** — the limit is creep, not break. UHMWPE
  creep accelerates above ~20–30% of MBL, so size the cord so
  **pretension + peak load stays under ~25% MBL**. For ~183 N peak +
  ~80 N pretension ≈ 263 N → want **MBL ≥ ~1050 N** (≈ 100 kg cord).
- Use a **creep-improved grade (SK78/SK99)** and **pre-stretch / heat-set**
  the cord before final tensioning — most of the creep happens early.
- Hub & bearing react ~263 N; solid printed hub fine.

## HARD PART 1 (rewritten for Dyneema) — CREEP, not bend radius
Dyneema bends happily at ~5× dia, so the small-drum fatigue problem is
gone. The new problem is **creep**: under constant pretension the cord
slowly lengthens → pretension drops → slack appears → **lost motion
returns**, killing the zero-backlash benefit you chose capstan for.
Mitigations, in order:
1. **Constant-force tensioner** (spring or weighted) on each cable instead
   of a fixed turnbuckle — it takes up creep automatically and holds
   pretension. This is the single most important change vs steel.
2. **Pre-stretch / heat-set** the cord and run a break-in cycle; re-tension
   once after break-in.
3. Keep working load <25% MBL (above).
4. Output-side encoder still reads true angle, so creep doesn't lose you
   *position* — but slack costs *stiffness*, hence the spring tensioner.
- Still cut a **helical groove, pitch = cord dia**, on every drum.

## HARD PART 2 — routing & kinematic coupling
Cables for J3/J5 cross intervening joints. Route each over an **idler
concentric with the crossed joint's axis** so the joint's rotation maps
to a *known* cable-length change (a coupling term), not slack.

Coupling (output-side, calibrate coefficients from idler/sector radii):
```
θ_J2 = (1/36)·φ_motor2
θ_J3 = (1/36)·φ_motor3  −  c32·θ_J2
θ_J5 = (1/36)·φ_motor5  −  c52·θ_J2  −  c53·θ_J3
```
- This is the CoreXY decoupling problem again — solved in firmware.
- **Output-side absolute encoders make it robust:** they read true joint
  angle regardless of routing, so calibrate `c` empirically (move one
  joint, watch the others' encoders) rather than deriving exactly.
- Idlers add friction & a little compliance per crossing → J5 (2
  crossings) is the least stiff joint. Acceptable for 250 g.

## Tensioning & terminations (Dyneema-specific)
- **Do NOT knot Dyneema** — knots slip and lose ~50% strength. Terminate
  by **splice** (Brummel/locked bury — Dyneema splices beautifully) or by
  **several anchored wraps + a clamp plate / set-screw** in a drum slot.
- One end fixed; the other on a **constant-force spring tensioner** so it
  takes up creep automatically (vs a fixed turnbuckle that goes slack).
- Pre-stretch the cord, run a break-in cycle, re-tension once.
- Radius every groove and anchor edge — Dyneema is abrasion/edge
  sensitive; sharp corners cut it.

## Where capstan does NOT go
Continuous-rotation joints (J1, J4, J6). Anchored cable = finite travel.
Keep those as geared/harmonic cartridges.

## Recommended first prototype (de-risk before the whole arm)
**One remote capstan joint + coupling firmware**, on a bench:
1. Build J3-like: motor + 2-stage on a fixed plate, cable over ONE
   concentric idler (mock J2 axis), to a sector on a crossed-roller race.
2. Verify: backlash (~0, the selling point), output range ±135°,
   cable life under cycling, pretension hold.
3. Mount the idler on a movable "J2" and **calibrate c32** by rotating it
   and logging the sector encoder — proves the decoupling firmware.
Get this one joint right and the arm is just replication + routing.
```
```
