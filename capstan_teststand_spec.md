# Remote capstan test stand — build & test

Purpose: measure whether Dyneema routed **over idlers** ("remote" capstan)
transmits force with ~zero backlash, vs the adjacent capstan→pulley
baseline. Decides the whole arm's cable architecture. File:
`capstan_teststand.scad`.

## Layout
```
 [NEMA17 under plate → helical capstan DRUM (r=8)]
        │ 2 cable runs (pull-pull), Dyneema DM20
        ▼ over
 [2 idler 608s in clevises]  ← position-adjustable (turn angle = the variable)
        │
 [DRIVEN PULLEY r=48 (6:1) + magnet/encoder + load arm]
```

## Idler load — why 608, double-supported
Cable turning angle θ over an idler → bearing radial load **F = 2·T·sin(θ/2)**.
At a J2-class run tension T ≈ 260 N (80 N pretension + ~183 N load):
| θ | F_idler |
|---|---------|
| 30° | 135 N |
| 60° | 260 N |
| 90° | 370 N |
| 180° | 520 N |
- **608** static rating ~1.4 kN → comfortable even at 90°. (A 623 ~180 N
  static would fail — do not use small bearings here.)
- **Shaft in double shear** (clevis, both arms) — never a cantilevered
  shoulder screw at these loads.
- **Design lever:** keep turn angles small (two gentle idlers beat one
  sharp one). The slots let you vary θ and watch the load/friction.
- 608 radius 11 mm = 11× cord dia → also good for Dyneema bend life.

## BOM
| Qty | Item |
|----:|------|
| 1 | NEMA17 stepper + driver (TMC2209 / any) |
| 1 | printed capstan drum (helical groove, anchor hole) |
| 1 | printed driven pulley (groove, 2 anchors, magnet pocket, load arm) |
| 1 | printed pulley post + 2× 608 (driven shaft) |
| 2 | idler clevis + 608 + 8 mm shaft (ground rod) + retainers |
| 1 | AS5600 board + 6×2.5 mm diametric magnet |
| 1 | MCU (read AS5600 over I²C, step the motor) |
| — | Dyneema DM20, splice tools / crimp ferrules |
| 1 | constant-force spring (or screw tensioner) |
| — | M3 heat-set inserts + screws; baseplate (printed or ply/alu) |
| — | hook weights (load arm) |

## Lacing the cable (pull-pull, no slip)
1. Anchor cord mid-drum (anchor hole), lay ~6–8 helical wraps.
2. Take both ends off the drum, run each to the pulley **over its own
   idler** (one run per idler, or both over a wide idler).
3. Splice/clamp each end into the pulley's two anchor channels, on
   opposite sides, so winding one run unwinds the other.
4. One end terminates on the **constant-force spring** → sets pretension,
   absorbs Dyneema creep. Pre-stretch the cord first.
5. **No knots** — splice or ferrule.

## Test procedure
**A. Backlash (the headline number)**
- Power the motor holding (or lock the drum). Apply a small ± torque at
  the load arm; read the AS5600 deflection. That angle = backlash +
  compliance. Target: **< ~0.3°** referred to the output.
- **Baseline:** remove idlers, move pulley adjacent to the drum (direct
  capstan), repeat. The *difference* is the idlers' contribution — the
  whole point of the test.

**B. Friction / efficiency**
- Hang known weights on the load arm (torque = W·arm). Note motor current
  / steps to lift vs lower. Compare with/without idlers and at different
  idler turn angles.

**C. Creep & tension hold**
- Tension, run 100s of cycles, re-measure backlash and pretension over
  time. Confirm the constant-force spring holds it (no slack return).

**D. Idler load sanity**
- At max test tension, check idler shaft deflection / bearing feel and
  that the clevis isn't flexing. Vary θ via the slots; watch friction rise
  with angle.

## Targets (go/no-go for the arm)
- Backlash (remote) < ~0.3°, and not dramatically worse than baseline.
- No cord slip (anchored → should be zero).
- Pretension holds over cycling (spring works).
- Idler friction acceptable at the turn angles the arm will actually use.

If remote-capstan backlash ≈ baseline → the architecture is proven, scale
to a real joint (Proto on the crossed-roller bearing). If idlers add
significant lash/friction → reconsider turn angles or fall back to
adjacent capstans per joint.
