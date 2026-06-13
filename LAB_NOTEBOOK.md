# Lab Notebook — Process Variables

Running log of the **process variables** that affect how this design prints,
assembles, and performs — kept so the eventual write-up has the real history,
not a reconstruction. Two parts: a **variable catalog** (the systematic list,
updated in place) and a dated **log** (observations as they happen).

Convention: dates absolute (YYYY-MM-DD). Record the *observation* and the
*conditions* even when you don't yet know the cause — correlations emerge later.

---

## Variable catalog

### Print / process
| Variable | Why it matters | Current / baseline | Status |
|---|---|---|---|
| **Filament brand** | Shrinkage, melt viscosity, diameter tolerance differ brand-to-brand even within PLA; a flow calibration doesn't transfer | Bambu PLA (baseline prints) → **Elegoo black PLA** (new) | switching; needs recal |
| **Color / pigment** | Carbon black shifts thermal absorption + flow; black often runs oozier, loses a touch more dimension on small features | black | suspected fit shift |
| **Print orientation** | Hole axis **vertical** → round, slightly undersize; **horizontal** → top sags, undersize + egg-shaped (tighter, out-of-round) | per-part, see notes | key var for the angle part |
| **Flow rate / extrusion mult.** | Directly sets hole/bore size; per-material | calibrated on Bambu | re-cal for Elegoo |
| **Pressure advance** | Corner/seam dimensional accuracy | (record per material) | — |
| **First-layer elephant's foot** | Squishes the bed-facing face → that face's holes/edges shrink | slicer compensation? | enable for seating face |
| **Nozzle temp** | Flow, ooze, small-feature fidelity | (record) | — |
| **Layer height / nozzle Ø** | Small-feature resolution (e.g. countersink chamfers, thin walls) | (record) | — |

### CAD clearances (design levers — see `angle_drive.py`, `arm_section.py`)
| Variable | Meaning | Current |
|---|---|---|
| `GAP` | body OD → mounting plate clearance | 2.0 mm (angle_drive, tuned) |
| `CLEAR` | motor-to-cap gap (sets plate lift `PLATE_Z`) | tuned per drive |
| `CAP` | cyclo end-cap height allowance | tuned per drive |
| `CAP_R` | cap-lip relief radius in the web (= body OD + margin) | `BR + 1.5` |
| bore clear | web cut to open the body interior; r18.0 (wall is r18.5) | 18.0 mm |
| `WEB_T` | hull-web thickness (Y) | 28.0 mm |
| *(proposed)* `FIT` | single per-part print-fit offset for all holes/bores | not yet added |

### Measured hardware (calibration anchors for the model)
| Quantity | Value | Notes |
|---|---|---|
| Holding torque (slip onset) | 1.8 kg @ 75 mm ≈ **1.32 N·m** | limited by **stepper missing steps**, not the printed cyclo slipping (electrically tunable) |
| Static push, measured | 250 g @ 75 mm ≈ **0.18 N·m** | on a scale, arm pushing down |
| Actuator mass | 188 g | full micro actuator |
| Segment length | 75 mm | joint-to-joint (short test build) |

---

## Open questions
- How much of the angle-part fit shift is **material (Elegoo black)** vs
  **orientation**? → isolate by printing the same part in Bambu at the same
  orientation, and the Elegoo at two orientations.
- Is a single `FIT` clearance constant enough, or do the two orthogonal faces of
  the L-part need **independent** offsets (because one prints vertical, one
  horizontal)?
- Does the NURBS-healed countersink print cleanly, or does the chamfer still need
  a slicer-side tweak?

---

## Log

### 2026-06-13 — angle_drive fits differ from the straight sections
- Observation: tolerances on the right-angle part (`angle_drive`) feel "a little
  different" than the straight arm sections.
- Two changes coincided: (1) **material** switched Bambu → Elegoo black PLA;
  (2) the part is an **L** with mating features on two orthogonal faces.
- Hypothesis (orientation): no single bed orientation puts both the cyclo
  bore/boss *and* the NEMA plate holes in the favorable **vertical** axis — so
  one set always prints in the saggy **horizontal** orientation (undersize,
  egg-shaped). The straight sections don't have this conflict, which is likely
  why their fits were fine.
- Hypothesis (material): flow calibrated on Bambu; Elegoo black likely needs its
  own flow / temp cal — expect ~0.05–0.15 mm size drift on holes until redone.
- Next: print a **tolerance ladder** (holes at +0.0/+0.1/+0.2/+0.3 mm) in Elegoo
  black; measure which drops onto the hardware. That offset = the per-material
  `FIT`. Orient with the tightest-tolerance feature (bore/boss) vertical.
- CAD status: `angle_drive` geometry frozen for now (hull web + cap relief +
  web-only bore clear, committed `19f0802`). No `FIT` param added yet.
