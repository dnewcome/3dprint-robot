# Clevis-free coaxial joint (modular actuator cartridge)

Eliminates the fork/yoke. The whole drive sits in one drum; the moving
link cantilevers off the output face on ONE big crossed-roller bearing.
Cobot (Universal Robots) architecture. File: `coaxial_joint.scad`.

## Layout (along the joint axis)
```
[geared stepper] -> shaft IN -> [wave gen] inside [flexspline]
   STATOR carries CS (N+2, fixed)            ROTOR carries DS (N, output)
   STATOR holds outer race ─┐   ┌─ ROTOR is the inner race
                       big crossed-roller bearing (OUTBOARD of gears)
   stationary link on STATOR body     moving link bolts to ROTOR face
                                       (offset L-arm, single-sided)
```

## Reduction
`total = geared_stepper_ratio × (N/2)`
- Plain NEMA17 direct → 18:1 (roll joints, low load).
- NEMA17 + 5:1 planetary → **90:1** (bend joints). No belt, fully inline.
- This is the "commonly available geared stepper" path from day one.

## Roll vs bend joints (both clevis-free)
- **Roll (J1/J4/J6):** links coaxial with the drum → straight tube-in,
  tube-out. The cartridge is literally in line.
- **Bend (J2/J3/J5):** stationary link off the stator body, moving link
  is an offset arm off the rotor face → the drum becomes the elbow. No
  fork because the big bearing takes the cantilever moment.

## Why the output bearing grows (and goes outboard)
Single-sided support = this ONE bearing reacts the entire bending moment
in single shear. So:
- **Bigger** than in a clevis (two-bearing) design.
- **Concentric and OUTBOARD of the gears** for max moment arm → stiffest.
- Modeled here as a ~104 mm BB crossed-roller race (Proto 1 part), or a
  bought thin-section slewing ring. This is THE part to validate first.

Moment check (250 g @ 0.45 m ≈ 1.1 N·m payload + arm): a 100 mm race
puts the reaction couple on a 100 mm arm → low ball loads, easily within
a printed BB race. Bigger race = stiffer; cost is package diameter.

## The coaxial-motor tradeoff (read this)
Putting the motor on-axis removes the 2:1 belt pre-stage. Consequences:
1. The single gear stage must supply the whole ratio → use a **geared
   stepper** (above) rather than a 72-tooth/37-pin single stage.
2. The motor occupies the center, so the **output encoder** moves:
   - Keep the wave gen short (it lives in the gear plane only); the rotor
     center stays free at the FRONT → magnet on the rotor center web,
     IC on a thin 2-leg bridge from the stator front rim (NOT a clevis).
   - The moving link bolts on a bolt circle OUTSIDE the bridge, or read
     the magnet from the back if the link covers the front center.
   - Alternative: dual-shaft geared stepper → motor-side magnet on the
     rear stub for commutation; rim ring-magnet for absolute output.
3. Center bore still routes downstream cables near the axis.

## Gearset is swappable (same cartridge)
`coaxial_joint.scad` pulls harmonic rings from `harmonic_ring.scad`. To
run cycloidal instead: replace `internal_ring_gear()` with the pin ring +
disc and put the wave gen's job onto the eccentric cam. Same stator,
rotor, bearing, motor mount, encoder. Prototype both on Proto 2.

## Print / assembly
- Print stator and rotor with the **joint axis vertical** → round bearing
  races and gear bores (roundness drives backlash).
- BB race: load airsoft BBs into the groove on assembly; the rotor traps
  them against the stator. Grease lightly.
- Heat-set inserts for the geared-stepper bolts and the link bolt-face.
- Register the gearset concentricity via the bearing itself (rotor IS the
  inner race) — far better alignment than two bolted links.

## To refine in CAD (skeleton caveats)
1. The BB groove is a single torus here; real crossed-roller needs
   alternating ±45° V-grooves (or use two angular-contact thin-section
   bearings back-to-back instead).
2. Flexspline axial retention + the wave-gen-to-shaft coupling (flat/key).
3. Encoder bridge + magnet web detail; moving-link offset-arm geometry.
4. Seal/dust cover over the gear cavity.
