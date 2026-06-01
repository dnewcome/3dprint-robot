# Actuator layout — distributed local cable drive (v1)

Supersedes the all-on-turntable cable-trunk plan (`turntable_spec.md`) for
v1. Core principle below eliminates inter-joint coupling.

## Principle: motor on the link just DISTAL to its joint's predecessor
Each joint's motor mounts on the proximal end of the link it drives, just
past the upstream joint. The tendon then stays entirely within ONE moving
frame and never crosses a joint → **no kinematic coupling, no concentric-
idler trunk, no coupling matrix.** Trade: more distal mass than all-at-
base, but each motor sits near its carrying joint's axis (low moment arm).

## Motor placement
| Motor | Mounted on | Drives | Tendon path |
|------|-----------|--------|-------------|
| 0 | ground (fixed, no inertia) | J1 base yaw | direct/geared |
| 1 | turntable | J2 shoulder | short |
| 2 | upper-arm proximal (after J2) | J3 elbow | along upper arm |
| 3,4 | forearm proximal (after J3) | wrist differential | along forearm to wrist |
| (5) | forearm proximal (after J3) | **J4 forearm roll — OPTIONAL** | see DOF note |
| grip | forearm (Bowden) | gripper | Bowden sheath to tool |

## Mass / torque check
- J3 motor at upper-arm proximal: ~near J2 axis → negligible J2 moment.
- 2 (or 3) wrist motors at elbow (~200 mm from shoulder): ~1.1 N·m (2) or
  ~1.6 N·m (3) added to J2. Within budget; J2 lands ~5–7 N·m.
- No motor is out at the wrist → distal mass stays low, joints stay light.

## DOF decision (OPEN)
The 5-motor list above is **5-DOF** (J1,J2,J3 + wrist pitch/roll); it drops
**J4 forearm roll**.
- **5-DOF:** position + 2 orientations. Simpler, lighter — strong v1.
- **6-DOF:** add motor 5 (J4) at the forearm proximal with the wrist pair.
  Restores full dexterity; forearm carries 3 motors.
Both obey the placement principle. J4, if added, mounts BEFORE the wrist
diff — then the wrist-diff motors should ride the rolling forearm section
to avoid crossing J4 (or accept one forgiving linear J4 coupling term).

## Gripper
- **Single-acting Bowden + spring return:** one cord pulls to close, spring
  opens. Grip force = motor current.
- Motor sits back on the forearm; Bowden sheath routes the cord to the
  tool. Caveat: sheath friction adds hysteresis → fine for grasping, not
  for precise force control.

## Reduction per joint (local capstan)
- Tendons are short (one link), so single- or 2-stage capstan as needed.
- J2/J3: 2-stage ~36:1 (load joints). Wrist: lower ratio, low load.
- Output-side absolute encoder at each joint (no coupling to untangle now,
  but still wanted for homing + zero backlash readout).

## Upgrade path
To chase distal mass later: move motors further proximal and re-introduce
through-joint routing (concentric idlers + coupling matrix per
`turntable_spec.md`). Joints, sectors, and tendons are unchanged — only
routing and firmware. Defer until mass actually bites.
