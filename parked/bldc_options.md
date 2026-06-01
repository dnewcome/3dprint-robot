# BLDC motor options — comparison for a joint actuator

Working question: can a BLDC replace a NEMA 17 at a joint? Yes, as a *frame*
— but **KV (winding) decides how much reduction you need and how hot it runs
holding a pose.** This compares candidates across the markets, because the
low-KV motors you want are *not* in the drone catalog you've been browsing.

## Why you only ever see 2000+ KV
You've been searching the **RC / racing** market. Those motors swing small
props at huge rpm on 4S → few turns of fat wire → **high KV by design**.
Low-KV motors live in other markets and are often spec'd by *turns* (e.g.
"120T"), not KV:

| Market | Typical KV | Why |
|---|---|---|
| FPV / racing quad | 1700–2700 | speed, small props, low V |
| Cinelifter / big quad | 400–900 | bigger props |
| **Gimbal** | **~70–400** | hold a camera still at 0 rpm — *our problem* |
| **Robotics QDD / ODrive** | **80–270** | torque at low speed, legged robots |
| Hoverboard / e-bike hub | 8–30 | direct-drive traction |

**Physical coupling:** KV ∝ 1/turns, and a *small* frame can't fit many
turns → small frames are almost always high-KV. To get low KV you go
**bigger frame**, **rewind**, or **accept a large reduction** (see below).

## Key relation
`Kt [N·m/A] = 8.27 / KV`  → torque per amp. Low KV = high Kt = **less current
to make torque = less heat holding a pose** (the BLDC's weak spot).

Output torque per amp = `Kt × reduction × efficiency` (η≈0.7 assumed).

## Candidate comparison
Specs are **approximate / representative** — verify against the actual part
before committing. "Hold I" = motor current to hold **3 N·m at the joint**
(a realistic arm-joint gravity load) at the listed reduction.

| Motor | Market | OD×H (mm) | Mass | KV | Kt (mN·m/A) | Reduction | Out τ/A | Hold I for 3 N·m | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| Racerstar 2204-1400KV (linked) | racing | 28×18 | ~28 g | 1400 | 5.9 | 30:1 | 0.12 N·m/A | **24 A** ✗ | cooks at stall unless R≫100 |
| 2204 @ huge reduction | racing | 28×18 | ~28 g | 1400 | 5.9 | **360:1** | 1.49 N·m/A | ~2 A | works, but 2-stage gearbox |
| GBM2804 gimbal | gimbal | 28×15 | ~50 g | ~300 | 27.6 | 30:1 | 0.58 N·m/A | ~5.2 A | small but low-KV; modest hold |
| iPower GBM4108-120T | gimbal | 46×25 | ~110 g | ~110 | 75 | 30:1 | 1.58 N·m/A | ~1.9 A | **great holder**, light |
| ODrive D5065-270KV | robotics | 50×65 | ~420 g | 270 | 30.6 | 20:1 | 0.43 N·m/A | ~7 A | heavy; high speed |
| ODrive D6374-150KV | robotics | 63×74 | ~600 g | 150 | 55 | 20:1 | 0.77 N·m/A | ~3.9 A | strong, heavy |
| T-Motor U8-100KV | robotics QDD | 96×35 | ~240 g | 100 | 82.7 | **8:1** | 0.46 N·m/A | ~6.5 A | low-R direct-drive style |
| T-Motor U8 @ higher R | robotics QDD | 96×35 | ~240 g | 100 | 82.7 | 30:1 | 1.74 N·m/A | **~1.7 A** ✓ | ideal holder, but 96 mm OD |
| MAD M6C12-80KV | robotics | ~64×25 | ~200 g | 80 | 103 | 20:1 | 1.45 N·m/A | ~2.1 A | low-profile pancake-ish |
| — NEMA 17 (baseline) | stepper | 42×48 | ~280 g | — | — | 30:1 | — | holds w/ detent, ~0 active I | reference |

## The trade this exposes
There are two ways to make a BLDC hold a pose without overheating:

1. **Low-KV motor + modest reduction** (gimbal / robotics motors, ~20–30:1).
   Holding current ~2 A → manageable heat. Costs: motor is bigger/heavier
   and pricier, but the drivetrain stays simple (single cycloid stage).
2. **Cheap high-KV racer + big reduction** (e.g. 2204 at ~300–360:1).
   Motor is 28 g and \$15, but you need a **two-stage** reduction → more
   backlash sources, more mass/complexity in the gearbox, and the output
   bearing still governs. Against "simple to build/tune."

**Sweet spot for this arm:** a **low-KV gimbal motor (~46 mm, ~110 g, 120T)**
or a **flat robotics motor (MAD/CubeMars-class, ~80 KV)** at ~20–30:1 through
the existing cycloid. Roughly NEMA-17 mass or less, holds at ~2 A, single
reduction stage, and the bell gives a direct mount for the eccentric cam.
The 2204 is best kept for the **gripper / wrist-roll** (light, fast, low
holding load) where its high KV isn't a liability.

## What to check on any candidate
1. **KV** — want Kt high enough that holding current is ~1–3 A at your
   reduction (use the formula above).
2. **Stall thermal mass** — iron/copper mass + can area; gimbal/robotics
   motors are wound to survive 0-rpm current, racers assume propwash.
3. **Bell bolt circle** — outrunner: somewhere to bolt the eccentric cam.
4. **Bearing** — motor bearings are light; let the cycloid input bearing
   carry the eccentric load, motor supplies torque only.
5. **Hollow shaft / through-bore** — nice for routing the dress-pack on-axis.
