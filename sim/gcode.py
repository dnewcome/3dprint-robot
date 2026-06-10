#!/usr/bin/env python3
"""
gcode.py — run a G-code path on the arm (drawing / dispensing / painting).

The exact-path layer: parse G0/G1 moves, map the G-code coordinate frame onto a
work plane in the robot's reach, and stream the path through the closed-loop
controller so the tool tip traces it. This is how you'd drive a pen, a glue
nozzle, or a paint head from CAM / plotter output.

    python sim/gcode.py            # draw a built-in demo (square + circle), in viewer
    python sim/gcode.py file.gcode # run your own G-code file
    python sim/gcode.py --check    # headless: report path-tracking accuracy

Supported: G0 (rapid), G1 (feed), X Y Z F, G20/G21 (in/mm), G90/G91 (abs/rel),
comments (;... and (...)). Unknown codes are ignored. G-code Z is "pen height":
Z>0 lifts off the work plane (pen up), Z<=0 draws on it.

Frame mapping (edit WORK): G-code (x,y) mm -> robot work plane; the tool traces
on a plane at height PLANE_Z, centered at (ORIGIN_X, ORIGIN_Y) in the base frame.
"""
import sys, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- where the drawing lives in the robot's workspace (meters) ----
ORIGIN_X, ORIGIN_Y, PLANE_Z = 0.20, 0.0, 0.34   # work-plane center + height
SCALE = 0.001                                   # G-code mm -> robot m (1:1 real size)
DRAW_SPEED, RAPID_SPEED = 0.02, 0.08            # m/s (pen-down feed cap / travel)


def parse_gcode(text):
    """-> list of (x,y,z, feed_mm_min, rapid) absolute moves, in G-code mm."""
    x = y = z = 0.0; feed = 600.0
    unit = 1.0       # 1=mm, 25.4=inch
    absolute = True
    moves = []
    for raw in text.splitlines():
        line = re.sub(r"\(.*?\)", "", raw)      # strip (...) comments
        line = line.split(";")[0].strip().upper()
        if not line:
            continue
        words = dict(re.findall(r"([GXYZF])\s*(-?\d*\.?\d+)", line))
        if "G" in words:
            g = int(float(words["G"]))
            if g == 20: unit = 25.4
            elif g == 21: unit = 1.0
            elif g == 90: absolute = True
            elif g == 91: absolute = False
        def upd(cur, key):
            if key not in words: return cur
            v = float(words[key]) * unit
            return v if absolute else cur + v
        gnum = int(float(words.get("G", "-1")))
        if gnum in (0, 1) or ("X" in words or "Y" in words or "Z" in words):
            x, y, z = upd(x, "X"), upd(y, "Y"), upd(z, "Z")
            if "F" in words: feed = float(words["F"])
            moves.append((x, y, z, feed, gnum == 0))
    return moves


def to_segments(moves):
    """G-code moves -> [(robot_xyz_m, speed_m_s)] for control.trace_path."""
    segs = []
    for x, y, z, feed, rapid in moves:
        p = [ORIGIN_X + x*SCALE, ORIGIN_Y + y*SCALE, PLANE_Z + max(z, 0.0)*SCALE]
        spd = RAPID_SPEED if rapid else min(DRAW_SPEED, feed/60.0*SCALE*1000)
        segs.append((p, spd))
    return segs


def demo_gcode():
    """A 80mm square then a 35mm-radius circle, pen up between (Z lift)."""
    g = ["G21", "G90", "G0 Z5"]
    sq = [(-40, -40), (40, -40), (40, 40), (-40, 40), (-40, -40)]
    g += [f"G0 X{sq[0][0]} Y{sq[0][1]}", "G1 Z0 F300"]
    g += [f"G1 X{a} Y{b} F600" for a, b in sq[1:]]
    g += ["G0 Z5"]
    pts = [(35*np.cos(t), 35*np.sin(t)) for t in np.linspace(0, 2*np.pi, 60)]
    g += [f"G0 X{pts[0][0]:.2f} Y{pts[0][1]:.2f}", "G1 Z0 F300"]
    g += [f"G1 X{a:.2f} Y{b:.2f} F600" for a, b in pts[1:]]
    g += ["G0 Z5"]
    return "\n".join(g)


def run(gcode_text, render=True, check=False):
    sys.path.insert(0, HERE)
    from robot import SimRobot
    from control import IKController, trace_path
    segs = to_segments(parse_gcode(gcode_text))
    robot = SimRobot(render=render, realtime=render)
    ctrl = IKController()
    print(f"G-code: {len(segs)} moves on work plane z={PLANE_Z} m")
    traj = trace_path(robot, ctrl, segs, record=check)
    if check and traj is not None:
        # densify the commanded path to ~1mm so we measure distance-to-LINE, not
        # distance-to-waypoint; only score pen-down (drawing) portions.
        dense = []
        prev = np.array(segs[0][0])
        draw_lo, draw_hi = PLANE_Z - 0.002, PLANE_Z + 0.003   # on the work plane
        for p, _ in segs:
            p = np.array(p)
            n = max(1, int(np.linalg.norm(p-prev)/0.001))
            for a in np.linspace(0, 1, n):
                q = prev + a*(p-prev)
                if q[2] <= draw_hi: dense.append(q)
            prev = p
        dense = np.array(dense)
        drawn = np.array([t for t in traj if draw_lo <= t[2] <= draw_hi])
        errs = [np.min(np.linalg.norm(dense - t, axis=1)) for t in drawn[::4]]
        print(f"drawing-line tracking error: mean {np.mean(errs)*1000:.2f} mm  "
              f"max {np.max(errs)*1000:.2f} mm  ({len(drawn)} pen-down samples)")
    if render and robot.viewer is not None:
        print("done — close the window to exit.")
        while robot.viewer.is_running():
            robot.step(0.05)
    robot.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    check = "--check" in args
    files = [a for a in args if not a.startswith("--")]
    text = open(files[0]).read() if files else demo_gcode()
    run(text, render=not check, check=check)
