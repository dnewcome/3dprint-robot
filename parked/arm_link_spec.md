# Arm link / drive housing — structure, loads, printing

`arm_link.scad` = one printable arm segment: a **joint cup** that the
36:1 drive drops into, a **link tube**, and a **proximal face** that
bolts to the previous joint's output ring. Parametric on `link_len` so
the same model makes upper arm, forearm, etc.

## What the cup carries (load path)
```
 payload + arm weight
      │  (bending moment)
      ▼
 next link (YOKE) ── bolted to ── OUTPUT RING
      │
   6810 main output bearing  ←── THE stiffness bottleneck. Its seat in
      │                            the front lip must be round & snug.
 housing cup wall  ── hoop + bending ──►  link tube  ──►  prox face
                                                           │
                                              previous joint output ring
```
The gear torque reacts through the **integral pin ring** (dowels in the
cup wall) → the cup hoop. The bending moment reacts through the **6810
seat** → cup wall → tube. Keep these two paths stiff; everything else is
packaging.

## Key dimensions (derived, all parametric)
| Feature | Value | From |
|--------|-------|------|
| Housing OD at joint | ~98 mm | `2·(ring_R+Rr+ring_wall)+10` |
| Cup interior depth | 46 mm | disc stack + flange + bearing |
| Structural wall | 4 mm | `wall` (≥3 perimeters) |
| Output bearing seat | 65 mm (6810) | `out_brg_OD` |
| Back boss | twin 608, 18 mm apart | `in_brg_gap` |
| Motor pad offset | 30 mm | `C_nom` (belt center dist) |
| Link tube | 42 mm OD × `link_len` | per joint |

## Print strategy
- **Orient the cup with the joint axis VERTICAL.** Then the output-
  bearing seat, the pin-ring bores, and the 608 seats all print as round
  holes with no support inside them — bore roundness drives backlash.
- Print the **link tube** as part of the same body if `link_len` ≤ ~180 mm
  (fits the 250 mm bed on the diagonal); longer links → split and bolt at
  the prox face.
- **PETG or PA-CF**, 4 perimeters / ≥40% infill in the cup, gyroid in the
  tube. The cup is the loaded part; the tube mostly just needs to not
  twist.
- **Heat-set brass inserts** for every M3 (motor pad, prox face, encoder
  bridge). Don't tap plastic for fasteners that get reworked.

## Bearing seat fits
- **6810 seat (65 mm):** model at 65.0; PETG shrinks slightly → usually a
  light press. If loose, add a 0.1 mm shim or a smear of retaining
  compound. A loose output seat = a wobbly arm, so check this first.
- **608 seats (22 mm):** light press; the pair must be **coaxial** — print
  vertical so they share the same Z axis.
- **Pin-ring dowel holes:** `Rr+0.10` = press fit for 6 mm dowels.

## Encoder bridge & cabling
- The output center is **open by design**. A 2-leg `encoder_bridge()`
  bolts to the front lip and holds the AS5600/MT6701 PCB ~1.5 mm above
  the magnet glued to the output ring's center web.
- The same open bore is the **cable pass-through** — run motor + encoder
  wires of the *downstream* joints through the joint center near the
  rotation axis so they barely flex as the joint moves. Leave a service
  loop; don't pull them taut.
- Keep the steel output bearing and dowels ≥8 mm from the magnet (the
  open center naturally gives this clearance).

## To refine in real CAD (this .scad is the skeleton)
1. Fillet the cup-to-tube junction (stress riser) and the motor pad root.
2. Real belt window cut + a finger slot to seat/tension the belt.
3. Output ring + yoke bolt detail (this file stubs the ring as the
   bearing bore; model the 6× output-pin holes to match `out_bc`).
4. Wire channels / strain-relief clips along the tube.
5. Lightening pockets once the load path is confirmed on Proto 2.
```
```
