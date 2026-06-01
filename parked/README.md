# Parked explorations

These files are **not part of the current build path.** The near-term build
target is the 3-DOF cycloid trunk at the repo root (`cycloid_joint.scad` +
`arm_trunk.scad`). Everything here was option-generation that's been
superseded or deferred — kept for reference and likely future use.

See the root `DESIGN.md` for the full reasoning behind each.

## What's here

**Joint sources — merged into the root `cycloid_joint.scad`:**
- `cycloidal_disc.scad` — original validated cycloid profile math + pin ring.
- `joint_module.scad` / `_spec.md` — double-eccentric cam + output flange.
- `coaxial_joint.scad` / `_spec.md` — clevis-free stator/rotor cartridge
  (bearing outboard of the gears). The architecture the canonical joint uses.
- `belt_stage.scad`, `arm_link.scad` / `_spec.md` — belt pre-stage + link.
- `base.scad` / `.png` — superseded internal-ring (4:1) J1 base. J1 is now
  the cycloid cartridge stood vertical instead.

**Cable / capstan drive** (zero-backlash remote-tendon path; future experiment):
- `capstan.scad`, `capstan_drive.scad`, `capstan_spec.md`
- `capstan_teststand.scad` / `_spec.md` — remote-capstan test rig.
- `actuator_layout_spec.md` — distributed local-motor placement.

**Wrist** (for extending the trunk to 5–6 DOF later):
- `cable_wrist.scad` / `_spec.md` — pure-cable differential.
- `wrist_differential.scad` — bevel differential.
- `wrist_decision.md` — wrist mechanism trade study.

**Harmonic** (alternative reducer):
- `harmonic_ring.scad`, `harmonic_drive_spec.md` — flat strain-wave.

**BLDC** (motor upgrade path):
- `bldc_2204.scad` / `.png` — 2204-class outrunner fit model.
- `bldc_options.md` — KV-market breakdown + candidate comparison.
- `integrated_actuator.scad` / `.png` — frameless-motor-in-reducer concept.

**Earlier assemblies** (superseded by `arm_trunk.scad`):
- `arm_v1.scad` / `.png` — 5-DOF cycloid+bevel-wrist assembly.
- `arm_assembly.scad` / `.png`, `whole_arm.scad` — cable-architecture viz.
- `turntable.scad` / `_spec.md` — base layout.
