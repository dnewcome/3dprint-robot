# Wrist mechanism — trade study & decision

Goal: provide the end-of-arm orientation DOF for a printed, cable-driven
arm (250 g payload), driven by simple remote capstans.

## Options evaluated
| Mechanism | Input/actuator | Range | Backlash | Sensing | Printable | Verdict |
|-----------|----------------|-------|----------|---------|-----------|---------|
| **Bevel differential** | **1-DOF capstan pulley** | large | gear lash (small, low-load joint) | per-axis encoder (easy) | yes | **CHOSEN** |
| ABENICS cross-spherical | **2-DOF articulated drive** | full/continuous | gear lash | 3-DOF (hard) | no (lab part) | rejected |
| Roller-driven sphere | 1-DOF | full/continuous | none | 3-DOF + slip (hard) | preload-sensitive | rejected |
| Agile Eye (spherical parallel) | 1-DOF | limited tilt cone | none | coupled legs | precise curved links | rejected |

## Why bevel differential wins for THIS build
- Each input is a plain spinning cord pulley (single DOF) — drivable by
  two simple forearm capstans, no drive element has to reorient.
- Backlash is only at the wrist (lowest load, output encoder watches it) —
  the one place the zero-backlash rule can be relaxed.
- Per-axis absolute encoders → no exotic orientation sensing.

## Why ABENICS was rejected (record so we don't revisit)
Each CS-gear drive module is itself ~2-DOF: the drive gear must tilt to
stay meshed as the ball reorients (differential pinion + helical linkage
per module). No off-the-shelf 2-DOF drive exists; building two of them to
power one ball defeats the purpose. Brilliant mechanism, not DIY-buildable.

## U-joint roll shaft — CONSIDERED & REJECTED (backlash)
A driveshaft + Cardan through the hollow central bevel would give a
positive, full-range 3rd axis — BUT it stacks bevel-mesh lash + printed
Cardan lash right at the tool. That betrays the project's zero-backlash
premise. Rejected.

## Wrist trilemma: zero-backlash · 3-DOF · simple — pick 2
- bevel + U-joint = 3-DOF + simple, but BACKLASH (rejected).
- The zero-backlash way to cross the bend is ANOTHER TENDON, not a shaft:
  a cord over an idler CONCENTRIC with the pitch axis (no length change
  with pitch, always in tension, full range).

## Direction: drop the bevel gears → PURE-CABLE wrist (zero backlash)
- **Cable differential (2 cords) → pitch + yaw** (no gears → no gear lash).
- **3rd cord pair over the pitch-concentric idler → roll** = full 3-DOF,
  zero lash, all forearm-driven (the WAM wrist). Cost vs bevel+U-joint is
  +1 cord pair, +1 idler, +1 coupling term — NOT backlash.

## Open sub-decisions
1. **6-DOF (3 cord pairs) vs 5-DOF (2 cord pairs, add 3rd later)** — same
   pure-cable mechanism; the third axis is incremental.
2. Pure-cable differential routing detail (fleet angle, anchor/tension).

## Industrial reference (why we still chose cable)
Classic industrial wrists (e.g. FANUC) use **concentric coaxial drive
tubes + spiral bevel gears**: wrist motors on the forearm, power
transmitted out to the 3 wrist axes through nested shafts; hollow center
for the dress-pack. Same architecture as ours (proximal motors → concentric
transmission → 3-DOF wrist). But their near-zero backlash comes from
**precision-ground hardened steel** bevels — not reproducible in print.
Cables are our spiral-bevel substitute: low backlash from tension instead
of from grinding. Confirms the topology; reaffirms cable over printed gears.

## Status
Mechanism: LOCKED = cable-driven bevel differential.
Geometry skeleton: `wrist_differential.scad`.
Remaining: resolve the two sub-decisions above, then detail real bevel
teeth (gear library), yoke, bearings, encoder mounts.
