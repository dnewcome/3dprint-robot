#!/usr/bin/env python3
"""
plan.py — collision-aware motion planning: "pick it up, don't care how, don't hit
anything."

The autonomy layer. You give a GOAL (a grasp pose); the planner finds a
collision-FREE joint path from the current configuration to it, avoiding world
obstacles AND self-collision, using a sampling-based planner (RRT-Connect) with
MuJoCo as the collision checker. The controller then executes it.

    python sim/plan.py            # plan a pick around an obstacle, play it in the viewer
    python sim/plan.py --check    # headless: report whether a collision-free plan was found

Object poses are set in OBJECTS below — that's the exact seam a perception
module (webcam -> detector/pose) or an LLM ("pick the red block") would feed.

Collision model: the visual drive meshes are too heavy/irregular to collide
against, so each link gets a simple capsule; world items are boxes. Adjacent
links are excluded (they share joints). Planning is purely kinematic (set a
configuration, check contacts) — no dynamics.
"""
import sys, os
import numpy as np
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from control import IKController                                   # noqa: E402

URDF = os.path.join(HERE, "arm_trunk.urdf")

# link capsules: name -> (fromto xyz->xyz in link frame, radius)  [meters]
CAPSULES = {
    "mast_link":      ((0, 0, -0.04, 0, 0, 0.078), 0.040),
    "upper_arm_link": ((0, 0.018, 0.0, 0, 0.018, 0.210), 0.030),
    "forearm_link":   ((0, -0.018, 0.0, 0, -0.018, 0.160), 0.028),
    "wrist_link":     ((0, -0.018, 0.0, 0, -0.018, 0.050), 0.030),
    "tool_link":      ((0, 0, 0.0, 0, 0, 0.085), 0.012),
}
EXCLUDE = [("base_link", "mast_link"), ("mast_link", "upper_arm_link"),
           ("upper_arm_link", "forearm_link"), ("forearm_link", "wrist_link"),
           ("wrist_link", "tool_link"), ("tool_link", "tcp_link"),
           ("base_link", "upper_arm_link")]

# world (set by perception/LLM in real use). pos in base frame, half-sizes.
OBJECTS = {
    "object":   dict(pos=(0.25, 0.10, 0.34), size=(0.014, 0.014, 0.020),
                     rgba=(0.85, 0.2, 0.2, 1)),       # the thing to pick (red)
    "obstacle": dict(pos=(0.20, 0.10, 0.40), size=(0.025, 0.04, 0.10),
                     rgba=(0.3, 0.3, 0.35, 1)),       # a block in the direct path
}
GRASP = (0.25, 0.10, 0.355)                            # grasp pose just above the object


def build_scene():
    spec = mujoco.MjSpec.from_file(URDF)
    for g in spec.geoms:                               # visual meshes don't collide
        g.contype = 0; g.conaffinity = 0
    for body in spec.bodies:
        if body.name in CAPSULES:
            ft, r = CAPSULES[body.name]
            g = body.add_geom()
            g.type = mujoco.mjtGeom.mjGEOM_CAPSULE
            g.fromto = ft; g.size = [r, 0, 0]
            g.contype = 1; g.conaffinity = 1
            g.rgba = [0.2, 0.6, 1.0, 0.25]             # faint collision capsule
    world = spec.worldbody
    for name, o in OBJECTS.items():
        b = world.add_body(name=name, pos=o["pos"])
        g = b.add_geom()
        g.type = mujoco.mjtGeom.mjGEOM_BOX
        g.size = o["size"]; g.rgba = o["rgba"]
        g.contype = 1; g.conaffinity = 1
    for a, b in EXCLUDE:
        e = spec.add_exclude(); e.bodyname1 = a; e.bodyname2 = b
    # the gripper is ALLOWED to contact the object it's grasping (but nothing
    # else may hit the object, and the gripper must still avoid everything else).
    for link in ("tool_link", "wrist_link"):
        e = spec.add_exclude(); e.bodyname1 = link; e.bodyname2 = "object"
    m = spec.compile()
    return m


def collision_free(m, d, q):
    d.qpos[:m.nv] = q
    mujoco.mj_forward(m, d)
    return d.ncon == 0


def _edge_free(m, d, a, b, res=0.04):
    n = max(2, int(np.linalg.norm(b - a) / res))
    return all(collision_free(m, d, a + t*(b-a)) for t in np.linspace(0, 1, n))


def rrt_connect(m, d, q0, qg, lo, hi, step=0.15, max_iter=4000, seed=1):
    if not collision_free(m, d, q0): return None, "start in collision"
    if not collision_free(m, d, qg): return None, "goal in collision"
    rng = np.random.RandomState(seed)
    Ta, Tb = [q0.copy()], [qg.copy()]            # two trees: parents tracked separately
    Pa, Pb = [-1], [-1]
    def extend(T, P, target):
        i = int(np.argmin([np.linalg.norm(n - target) for n in T]))
        dirn = target - T[i]; dist = np.linalg.norm(dirn)
        qn = target.copy() if dist < step else T[i] + dirn/dist*step
        if _edge_free(m, d, T[i], qn):
            T.append(qn); P.append(i); return qn, len(T)-1
        return None, None
    for it in range(max_iter):
        qr = rng.uniform(lo, hi)
        qn, ia = extend(Ta, Pa, qr)
        if qn is None:
            Ta, Tb, Pa, Pb = Tb, Ta, Pb, Pa
            continue
        qn2, ib = extend(Tb, Pb, qn)              # try to connect other tree to qn
        if qn2 is not None and np.linalg.norm(qn2 - qn) < 1e-6:
            pa = _backtrace(Ta, Pa, ia); pb = _backtrace(Tb, Pb, ib)
            path = pa + pb[::-1]
            # make sure tree A is the one rooted at start
            if np.linalg.norm(path[0] - q0) > 1e-6: path = path[::-1]
            return _shorten(m, d, path), f"found in {it} iters"
        Ta, Tb, Pa, Pb = Tb, Ta, Pb, Pa
    return None, "no path (max_iter)"


def _backtrace(T, P, i):
    path = []
    while i != -1:
        path.append(T[i]); i = P[i]
    return path[::-1]


def _shorten(m, d, path, iters=200, seed=2):
    rng = np.random.RandomState(seed)
    path = [p.copy() for p in path]
    for _ in range(iters):
        if len(path) <= 2: break
        i = rng.randint(0, len(path)-1); j = rng.randint(i+1, len(path))
        if j - i >= 2 and _edge_free(m, d, path[i], path[j]):
            path = path[:i+1] + path[j:]
    return path


def plan_pick(grasp=GRASP):
    m = build_scene(); d = mujoco.MjData(m)
    lo, hi = m.jnt_range[:, 0].copy(), m.jnt_range[:, 1].copy()
    ik = IKController()
    q0 = np.array([0, 0.6, -1.0, 0, 0])               # start folded
    qg, err = ik.solve_ik(grasp, q0)
    if err > 0.01:
        return m, d, None, f"grasp pose unreachable (IK err {err*1000:.0f}mm)"
    path, msg = rrt_connect(m, d, q0, qg, lo, hi)
    return m, d, path, msg


def main():
    check = "--check" in sys.argv[1:]
    m, d, path, msg = plan_pick()
    print(f"plan: {msg}")
    if path is None:
        print("  no collision-free path."); return
    # densify for smooth playback
    dense = []
    for a, b in zip(path[:-1], path[1:]):
        for t in np.linspace(0, 1, max(2, int(np.linalg.norm(b-a)/0.01))):
            dense.append(a + t*(b-a))
    print(f"  {len(path)} waypoints -> {len(dense)} steps, all collision-free")
    if check:
        bad = sum(0 if collision_free(m, d, q) else 1 for q in dense)
        print(f"  collision-check along path: {bad} colliding states (want 0)")
        return
    import mujoco.viewer, time
    with mujoco.viewer.launch_passive(m, d) as v:
        print("playing the pick path (close window to exit)...")
        while v.is_running():
            for q in dense + dense[::-1]:              # forward then back, loop
                if not v.is_running(): break
                d.qpos[:m.nv] = q; mujoco.mj_forward(m, d); v.sync()
                time.sleep(0.02)


if __name__ == "__main__":
    main()
