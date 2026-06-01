# Joint module — mechanical stack, BOM & fits

36:1 module = 2:1 GT2 belt pre-stage + 18:1 cycloidal (19 pins / 18 lobes).
Files: `cycloidal_disc.scad` (disc + ring), `joint_module.scad` (cam,
flange), `encoder_joint_spec.md` (sensor).

## Axial stack-up (motor end → output end)
```
 NEMA17 (5mm shaft) ── 20T GT2 pulley
        │  belt, 2:1
        ▼
 40T GT2 pulley ─ INPUT SHAFT (8mm ground rod)
   ├─ 608 + 608 PAIR in the back-wall boss (~18mm apart)
   │       └─ takes the cam cantilever moment AND frees the output
   │          center for the encoder + cable pass-through
   ├─ DOUBLE ECCENTRIC CAM (cantilevered forward off the boss)
   │     ├─ 6802 + DISC 1   (offset +E)
   │     └─ 6802 + DISC 2   (offset −E, 180°)   ← balanced pair
 PIN RING (19× 6mm steel dowels, INTEGRAL to the housing cup wall)
 6× 6mm steel OUTPUT PINS ─ OUTPUT RING (rotates with the next link)
   └─ MAIN OUTPUT BEARING (6810 thin-section, or BB crossed-roller race)
 Next link = YOKE bolted to the output ring's perimeter (center open)
 MAGNET (6×2.5 diametric) on output center ─ fixed ENCODER BRIDGE over it
```

## Bearing / hardware BOM (per joint)
| Qty | Part | Size (mm) | Role |
|----:|------|-----------|------|
| 2 | 608-2RS | 8×22×7 | input shaft support in housing |
| 2 | 6802-2RS | 15×24×5 | cam journals → disc bores |
| 1 | 6810-2RS *or* BB race | 50×65×7 | **main output (moment) bearing** |
| 19 | dowel pin | 6 Ø × (T+2) | ring rollers (the gear "teeth") |
| 6 | dowel pin | 6 Ø × ~22 | output pins through disc holes |
| 1 | ground rod | 8 Ø input shaft | cam carrier |
| 1 set | GT2 20T + 40T + belt | — | 2:1 pre-stage |
| 1 | NEMA17 | — | motor (run ≤50% holding) |
| 1 | magnet N35 | 6 Ø × 2.5 | encoder target |

Per arm (J1–J3 as this module): ×3. Wrist (J4–J6) uses the lighter
differential — separate spec.

## Critical fits / clearances
- **Cam journal ↔ 6802 bore:** print journal at 15.0; bore is steel.
  Printed-on-steel press is unreliable — add a **0.1 mm shim/CA-glue**
  or model journal at 15.15 and sand to fit.
- **Disc bore ↔ 6802 OD (24):** light slip fit; model `bore_r=12.1`
  if your printer runs tight. Disc must spin freely on the bearing.
- **Ring dowel holes:** `Rr+0.10` in the .scad → press fit for 6 mm
  dowels. The disc rides on the dowels' *inner* faces.
- **Output pin holes in disc:** oversized by E (radius `out_pin_r+E`)
  so the orbiting disc clears the fixed pins. Do **not** tighten these.
- **Backlash budget:** belt (~0.05°), cycloidal (≤0.3° if fits good),
  output-pin clearance (keep pins+holes concentric). Output-side
  encoder reads through all of it — that's the point.

## Balance & assembly notes
- Two discs **180° out of phase** (cam journals at +E / −E) cancel the
  orbital shake; the crescent counterweights in the cam trim the rest.
  Single-disc is fine for a slow bench test, bad above ~60 rpm output.
- Press dowels into the ring first, then drop disc 1 on its 6802, rotate
  cam 180°, drop disc 2. Slide output pins through *both* discs' holes.
- Torque path is shaft→cam→bearing→disc→**output pins**→flange. The cam
  bearing only transmits the small radial orbit force, so a printed cam
  is fine; the output pins see the real tangential load → **steel**.

## Belt pre-stage (`belt_stage.scad`)
2:1 via **20T → 40T GT2 (6 mm)**. Pitch diameters 12.73 / 25.46 mm.

| Closed belt | Center distance C |
|------------|-------------------|
| 110 mm | ~24 mm (tight, pulleys nearly touch) |
| **122 mm** | **~30 mm (recommended — compact)** |
| 158 mm | ~49 mm (roomy for tensioner) |
| 200 mm | ~70 mm |

- **Tension by sliding the motor:** the mount has 4 bolt slots + a pilot
  slot along the center-distance axis. Install the belt at the short end
  (slack), slide the motor away, lock the M3s. ~8 mm travel brackets the
  122 mm belt.
- **Belt force check:** motor 0.45 N·m / 6.37 mm pinion radius ≈ **71 N**
  — well within 6 mm GT2's working tension. No need for GT3/3 mm here.
- Buy the pulleys (5 mm bore for the motor, 8 mm bore for the input
  shaft); printing GT2 teeth accurately is not worth it.
- Keep the belt run clear of the encoder magnet — steel belt cords near
  the field skew readings.

## Sanity numbers (shoulder, J2)
- NEMA17 holding ~0.45 N·m × 36 × 0.7 eff ≈ **11 N·m** output.
- Demand ~6 N·m → motor runs ~30% holding → safe open-loop, no skips.
- Output pin tangential force ≈ 11 N·m / (6 pins × 0.018 m) ≈ **100 N**
  per pin → 6 mm steel dowel in shear, trivial.
