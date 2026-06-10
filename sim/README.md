# Arm Simulation & Analysis Suite

A MuJoCo model of the arm plus a set of small, focused tools to **pose it, size
the motors, budget backlash, watch it behave under gravity, and close a control
loop** — built up as a learning/validation layer before anything is printed.

Everything here is plain Python + [MuJoCo](https://mujoco.readthedocs.io)
(`pip install mujoco`). Each script has its assumptions as editable constants at
the top — change a number, re-run, see the effect.

```
pip install mujoco
python sim/view.py          # pose it (kinematic)
python sim/gravity.py       # watch it hold/sag under gravity
python sim/sizing.py        # torque / reach / motor catalog
python sim/backlash.py      # backlash -> tool-tip error budget
python sim/twin_demo.py     # closed-loop reach-to-target (digital twin)
python sim/twin_demo.py fidelity   # measure sim-vs-"real" fidelity
python sim/gcode.py         # exact-path mode: draw a G-code shape
python sim/plan.py          # autonomy mode: collision-free pick around an obstacle
```

> **Display note:** MuJoCo's bundled GLFW here is Wayland-only, and its in-window
> UI sliders don't take mouse drags under native Wayland. The viewers therefore
> also accept **keyboard** control (`Q/A W/S E/D R/F T/G`, `X`=reset). Camera
> orbit/zoom with the mouse works fine.

---

## The model

`arm_trunk.urdf` — a **5-DOF arm**: J1 base yaw, J2 shoulder pitch, J3 elbow
pitch (all the larger **R20 cycloidal** drive), J4 wrist pitch + J5 tool roll
(the smaller **20:1 Micro cycloidal**). Reach ~0.49 m. The drives are real
geometry: each R20 is split into a fixed motor half (motor plate + the actual
stepper from the STEP) and a rotating output body, so the joints articulate like
the hardware. Arm segments are flat plate members; round mounting plates match
the round output faces.

- **Meshes** (`meshes/`): `r20_motor.stl` / `r20_body.stl` (split R20),
  `micro20.stl` (wrist drive) — converted from the vendor STEP files via gmsh.
- **Transmissions**: the URDF carries ROS `<transmission>` blocks recording each
  joint's reduction (20:1). `ros2_control` reads these; MuJoCo ignores them and
  the sim scripts inject their own actuators (see "Gotchas").

---

## The tools

### `view.py` — kinematic poser
Drag the joints (sliders or keys); the arm follows exactly, no gravity. Best for
checking reach, workspace, and self-clearance. Prints live tip position + radial
reach.

### `sweep.py` — animated workspace
Hands-free: sweeps the joints through a choreographed motion so you can see the
envelope. `--pose q1 q2 q3 …` holds a static pose.

### `gravity.py` — dynamics: hold or sag
Real physics. Gravity on, realistic link masses, and each joint is a position
servo whose force is **clamped to the actuator's real output torque**. So if a
pose needs more torque than the motor can make, the joint visibly sags. The
console prints per-joint torque and flags any joint over its **continuous
(thermal)** limit (`!`) — it can hold there briefly but it's cooking the motor.
Also models **friction / non-backdrivability** (`frictionloss`), so reaction
torques don't back-drive the joints like free pivots.

### `sizing.py` — torque, reach, motor catalog
A lumped-mass model + MuJoCo **inverse dynamics**: how much holding torque each
joint needs at worst case (arm horizontal, extended, with payload), vs what a
motor-on-cycloidal can deliver. The `MOTORS` catalog ranks bare steppers, geared
steppers, gimbal/pancake BLDCs — each at 20:1 vs 36:1 — by the longest members
they can hold continuously.

### `backlash.py` — backlash → tool-tip error
Per-joint backlash spec (`BACKLASH_DEG`) → worst-case slop at the tool tip, using
the translational Jacobian as each joint's lever arm. Shows which joints' lash
matters most and compares drive types.

### `robot.py` / `control.py` / `twin_demo.py` — the digital-twin foundation
- `robot.py` — **`RobotInterface`**, the one abstraction both sim and hardware
  implement (positions in, targets out). `SimRobot` wraps the MuJoCo model;
  `RealRobot` is a stub to wire to your encoders + drivers.
- `control.py` — a model-based **closed-loop IK** controller (damped least
  squares, integral feedback on the measured tip, anti-windup).
- `twin_demo.py` — drives the tool tip to a sequence of XYZ targets through the
  interface (`reach_demo`), and measures **fidelity** (`fidelity` arg) by
  replaying identical commands on a "truth" model and a mismatched "twin" and
  comparing tip paths.

### The two task modes
- `gcode.py` — **exact-path mode** (drawing / adhesive / paint): parse G-code
  (`G0/G1 X Y Z F`), map it onto a work plane in the robot's reach, and stream it
  through the controller so the tool tip traces the path (~0.7 mm). `--check`
  reports drawing-line accuracy; pass a `.gcode` file to run your own toolpath.
- `plan.py` — **autonomy mode** ("pick it up, don't collide"): give a grasp
  pose; an RRT-Connect planner finds a **collision-free joint path** (world
  obstacles + self-collision, checked in MuJoCo) and the arm executes it. Object
  poses in `OBJECTS` are the seam a perception module (webcam → pose) or an LLM
  ("pick the red block") would set. Key modeling point: the gripper is allowed to
  contact the object it's grasping; everything else must avoid everything.

---

## What the analysis found (the design conclusions)

These came out of `sizing.py` / `backlash.py` / `gravity.py` and drive the build:

1. **The shoulder is the binding joint, and reduction is the dominant lever.**
   At 20:1, almost no motor holds the arm extended *continuously*; going to 36:1
   (a belt pre-stage) roughly doubles the member length. Reduction beats motor
   upgrades for reach.
2. **Wrist-motor mass hurts twice** — its own weight loads the shoulder. Keep the
   wrist motors as light as possible; the tip-mass lever dwarfs the 250 g payload.
3. **Don't buy a geared motor — the metal planetary gearbox is the ~300 g.** A
   geared NEMA14 is 411 g, geared NEMA11 is 349 g; the gearbox dominates. Build
   the reduction in your **printed cycloidal** (light, ~0 backlash) and keep the
   motor bare.
4. **"Pancake" only helps as a BLDC outrunner.** Stepper torque ∝ stack *length*,
   so a flat stepper is just weaker (same torque/gram). BLDC outrunner torque ∝
   *radius²*, so a flat-and-wide pancake outrunner is genuinely torque-dense.
   Pancake BLDC 8108 @36:1 → ~0.62 m reach vs NEMA17's ~0.48 m. Cost: FOC +
   encoder per joint.
5. **Backlash budget: the base joints dominate.** At 0.2°/joint, J1/J2 (~470 mm
   lever) contribute ~1.6 mm of tip slop each; the tool-roll joint contributes ~0
   (tip on its axis). Spend tight tolerances on the base. Cycloidal (0.1–0.2°) →
   2–5 mm tip slop; a planetary geared stepper (1°) → ~24 mm. Hard number for
   "why cycloidal."

---

## Concepts (the things worth knowing)

- **Inverse dynamics** — given a pose (and zero acceleration), solve for the
  joint torques needed to hold it. How `sizing.py` and `gravity.py` get torques.
- **Jacobian** — the matrix mapping joint speeds to tip motion. Its column for a
  joint is also that joint's *lever arm to the tip* — used for both IK and the
  backlash budget.
- **Damped least squares IK** — invert the Jacobian to turn a desired tip move
  into joint moves, with a damping term for stability near singularities.
- **Three distinct "give" effects** (don't conflate them):
  - *Inertial coupling* — moving one link reacts a torque on the parent (load- &
    speed-dependent). Real, in the sim.
  - *Compliance* — elastic flex under load (modeled by servo stiffness `KP`).
  - *Friction / non-backdrivability* — the geartrain resists being back-driven
    (modeled by `frictionloss`). A high-reduction cyclo+stepper barely
    back-drives.
  - *Backlash* — a fixed dead-band, **load-independent** (so *not* the twitch you
    see when snapping a joint). `backlash.py` budgets it; it isn't in the dynamic
    sim yet.
- **Continuous vs holding torque** — a stepper holds near its full holding torque
  briefly, but only ~60% continuously before it overheats. The continuous number
  is what sizes a pose-holding arm.
- **FOC** (field-oriented control) — the closed-loop current control a BLDC needs
  to act like a servo; pairs with an encoder per joint.
- **Gymnasium** — just a standard *interface* (`reset()`/`step(action)`) so RL
  libraries can talk to any environment. Optional; only needed if you do RL.
- **Digital twin / fidelity** — run identical commands on sim and real arm,
  compare logged positions; tune the sim's params (friction, mass, stiffness) to
  minimize the difference (*system identification*). That difference is your
  fidelity number.

---

## Architecture: where the "brain" goes

Keep MuJoCo **dumb** — it only steps physics and reports state. Everything smart
lives above `RobotInterface`, which both `SimRobot` and (later) `RealRobot`
implement, so the same control/AI code runs against sim or hardware:

- **Classical IK + trajectory control** first — deterministic, debuggable (this
  is `control.py`). Good enough for positioning/pick-place.
- **LLM/VLM as a planner** on top — turns goals/language into target poses for
  the classical executor. (Doesn't run the fast loop.)
- **RL** only for genuinely hard skills (contact-rich, dynamic, learned
  compliance). Overkill for basic operation.
- **Transport**: in-process Python to start; add RPC (ZMQ/gRPC) or **ROS 2**
  (`mujoco_ros2_control` reads the transmissions) when you need cross-process or
  the real hardware.

---

## Gotchas / caveats

- **MuJoCo ignores URDF `<transmission>` and `<gazebo>` tags** — it has no
  actuators from the URDF (`nu=0`). The sim scripts add position-servo actuators
  via `MjSpec`. The transmissions are there for `ros2_control` / documentation.
- **Servo gains must scale with joint inertia.** A uniform stiff gain explodes on
  the near-zero-inertia wrist-roll joint (`KV·dt/I` blows past the explicit-
  integration limit). `gravity.py` scales per-joint gains to a common bandwidth
  and uses the implicit integrator.
- **Numbers are estimates.** Motor torques, efficiencies (0.70), masses,
  frictions are editable placeholders. They get *real* when you weigh printed
  parts and read motor datasheets — or, best, when you measure fidelity against
  the built arm.
- **What's modeled:** rigid-body dynamics, gravity, force-limited servos,
  joint friction/non-backdrivability, kinematic backlash budget.
  **Not yet:** dynamic backlash dead-band, gear/structural elasticity, thermal
  models, sensor noise.
