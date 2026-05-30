# Integrated flat strain-wave drive — one ring per link

A **flat (pancake) harmonic** drive split across two arm links. Each link
carries one rigid circular spline printed into it; the flexspline + wave
generator slot in between. Files: `harmonic_ring.scad`.

## Why the flat type (two circular splines)
Standard harmonic = 1 ring + cup flexspline → doesn't split across links.
The **flat type** has TWO rigid rings and a ring flexspline, so:
- **CS (N+2 teeth)** → built into the **housing link** (stationary).
- **DS (N teeth)**  → built into the **next link** (rotates = output).
- Flexspline (N) + wave generator → the slot-in cartridge.

Flexspline regresses 2 teeth/rev vs CS; DS (same count as flexspline)
follows it → **ratio = N/2**.

## Numbers
| Param | Value |
|------|-------|
| Flexspline / DS teeth | 36 |
| CS teeth | 38 |
| Module | 2.0 mm |
| Pitch dia (flexspline/DS) | 72 mm |
| Pitch dia (CS) | 76 mm |
| Ring OD | ~93 mm (fits the 98 mm housing) |
| Harmonic ratio | 18:1 |
| + 2:1 GT2 belt | **36:1 total** |
| Wave-gen radial deflection δ | ~1.8 mm (≈0.9·m) |

Keeping the belt pre-stage lets the harmonic do only 18:1 (36 teeth,
2.0 module — easy to print) instead of 72 teeth at ~1 mm module.

## How it slots into `arm_link.scad`
- `internal_ring_gear(N+2)` **replaces `pin_ring_bores()`** in the cup —
  i.e. the CS is the cup's inner wall. No dowels, no cycloidal disc.
- The **next link** prints `internal_ring_gear(N)` as its proximal face.
- The two links register on a **spigot** (see below) and bolt around the
  perimeter — the flexspline lives in the gap, the wave generator on the
  input shaft (same 8 mm shaft + 2:1 belt as before).
- Output-side encoder unchanged: magnet on the DS/output center, fixed
  bridge reads it.

## The two things that make or break a PRINTED strain wave
1. **Flexspline material & wall.** It flexes every rev — this is the wear/
   fatigue part and the reason we earlier preferred cycloidal.
   - **PP (polypropylene):** best fatigue life, flexes happily; hard to
     print (warping, bed adhesion) — use a PP-friendly sheet/glue.
   - **TPU (95A):** easy to print, very durable in flex, BUT high
     hysteresis → torsional wind-up & lost motion. Okay for a runner.
   - **Nylon (PA / PA-CF):** stiffer, decent fatigue; CF makes it too
     stiff — use unfilled nylon for the flexspline.
   - Wall ~1.5 mm at the root; thinner flexes easier but wears faster.
   - Expect **finite life** — design the flexspline as a cheap, fast-
     reprint consumable. This is the honest trade vs cycloidal's steel
     dowels.
2. **CS↔DS concentricity & alignment across the slot-join.** The two
   rings are on two *separate printed parts*. If they're not coaxial and
   square, teeth bind or skip. → a precise **register spigot**:
   - Housing link: a ~60 mm boss (h≈4 mm) concentric with the CS.
   - Next link: a matching bore. Print both vertical so they're round.
   - Bolt circle outside the spigot; the spigot does the centering, the
     bolts only clamp.

## Wave generator options (printed)
- **Roller type (recommended):** oval carrier + 2 ball bearings riding the
  flexspline bore. Lower friction, less heat than a plain oval.
- **Plain oval:** printed ellipse + PTFE/greased flexspline bore. Simpler,
  more friction, fine for a bench test.
- δ ≈ 0.9·m ≈ 1.8 mm radial. Too little → teeth don't engage; too much →
  over-strains the flexspline.

## Backlash / stiffness reality
- Strain wave's selling point is **near-zero backlash** — true if teeth
  fit well. That's the upside over a sloppy-printed cycloidal.
- Its weakness is **torsional wind-up** (the flexspline is a spring). The
  output-side encoder reads the wind-up, so it's great for static
  accuracy, poor for dynamic stiffness. Worse with TPU flexsplines.

## Fallback (don't delete the cycloidal files)
If the printed flexspline disappoints on life or wind-up, the **exact same
housing** takes the cycloidal internals — `pin_ring_bores()` instead of
`internal_ring_gear()`, steel dowels instead of a flexspline. Same 8 mm
input shaft, same belt, same output bearing, same encoder. Prototype both
discs/flexsplines on Proto 2 and keep whichever measures better.
