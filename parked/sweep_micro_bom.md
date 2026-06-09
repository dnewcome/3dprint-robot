# Sweep Dynamics — 20:1 Micro Cycloidal — parts list

Reference actuator being evaluated as a buildable cycloidal drive (NEMA17-mount,
~20:1, 3D-printed body + commodity bearings/bolts). Files downloaded as STEP +
print-ready STL (9-disc clearance ladder). This is the **hardware shopping list**.

> Source: Sweep Dynamics (sweepdynamics.com). Drive uses a paired thin-section
> ball bearing for the output (not a crossed-roller), 6 shoulder-bolt output
> pins riding aluminium rollers, and a printed lobed pin-ring. The disc ships in
> 9 clearance variants (−0.1 … Nul … +0.1 mm in 0.025 steps) — print the set,
> fit-test, keep the backlash you want. (Independent confirmation of our own
> clearance-sets-backlash strategy.)

## Bearings — need to buy
Clean `amazon.com/dp/<ASIN>` links (affiliate/tracking stripped); click → **Add to List**.

| Bearing | Designation | Qty | ASIN | Link |
|---|---|---|---|---|
| 30×37×4 mm 2RS | uxcell **6706-2RS** | 2 | B0D6WDB21H | https://www.amazon.com/dp/B0D6WDB21H |
| 7×13×4 mm 2RS  | uxcell **687-2RS**  | 2 | B0D2LBCKP2 | https://www.amazon.com/dp/B0D2LBCKP2 |
| 8×12×3.5 mm 2RS| uxcell **MR128-2RS**| 2 | B0CM6R2Z75 | https://www.amazon.com/dp/B0CM6R2Z75 |

- **30×37×4 (6706)** — main output bearing (×2, likely paired to take the moment).
- **7×13×4 (687)** — eccentric-cam / input support.
- **8×12×3.5 (MR128)** — secondary cam / support.

## Output-pin rollers — substituted to nylon
BOM calls for **M3 × 5mm OD × 10mm aluminium rollers** (×6). The exact
3mm-bore × 5mm-OD × 10mm *plain-bore* aluminium part is an AliExpress
specialty — US retail only stocks threaded (won't spin) or 6mm-OD (wrong
pin diameter). Substituted to **nylon**, which matches our floating-roller
design decision and spins freely on the M3 shank:

| Part | Spec | ASIN | Link |
|---|---|---|---|
| Nylon round spacer, **unthreaded** PA66 | OD 5mm · ID 3.2mm · L 10mm (×6) | B074N5HD42 | https://www.amazon.com/dp/B074N5HD42 |

Electronics-Salon assortment box (2–20mm lengths; use the 10mm). 5mm OD is the
functional dimension (fits disc output holes); 3.2mm bore = ~0.2mm clearance on
the M3 shank so it rolls. Bulk single-length alt: VXB 300-pc M3 unthreaded kit.

## Bolts — already have / per BOM
- M3×20 mm button-head ×6 — output pin bolts (rollers ride on these)
- M3×8 mm countersunk ×4
- M3 nuts ×6

## Print settings (from Sweep instructions)
0.20 mm layer (0.25 initial) · 3–4 walls · 7/7 top/bottom · 25–30% gyroid/grid infill.

---
*Files in `~/Downloads/cad-files/sweep-micro-cycloidal.zip`. The 26:1 High-Torque
variant (62 mm, 40×52×7 output bearings) is in `sweep-cycloidal.zip`.*
