#!/usr/bin/env python3
"""
sweep_design.py — sweep segment length x NEMA17 motor size to find which arm
designs actually HOLD, and the reach/weight each buys.

Anchored to the MEASURED prototype: the pancake stepper realizes 1.32 N*m output
(1.8 kg on a scale at 75mm). So the effective drive factor -- cyclo efficiency x
open-loop step margin -- is 1.32 / (0.13 holding x 20 ratio) = 0.51. We apply
that to the standard NEMA17 body-length ladder.

The binding joint is the SHOULDER (J2, free weight at the base); the ELBOW (J3)
is the next limit, and a bigger elbow motor costs weight the shoulder must carry.
Equal segments assumed (modular: one printed section x2).

    python sim/sweep_design.py

CAVEAT: this is MOTOR-limited. The printed cyclo is only proven to 1.32 N*m so
far -- every cell above that assumes the small drive can transmit the torque.
Set CYCLO_CAP once you've measured where the drive (not the motor) gives out.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mujoco, numpy as np                                           # noqa: E402
import sizing                                                        # noqa: E402

RATIO     = 20
DRIVE     = 0.51        # cyclo eff x open-loop step margin (anchored to measured)
CYCLO_CAP = 99.0        # printed-cyclo torque ceiling, N*m (UNKNOWN; only 1.32 proven)
PANCAKE_M = 0.14        # the 24mm pancake's motor mass, kg (mass-delta baseline)

# standard NEMA17 by body length: (holding torque N*m, motor mass kg)
NEMA17 = {
    "24mm pancake": (0.13, 0.14),
    "34mm":         (0.28, 0.22),
    "40mm std":     (0.42, 0.28),
    "48mm":         (0.59, 0.36),
}

def cap(name):                         # practical joint output torque, N*m
    return min(NEMA17[name][0] * RATIO * DRIVE, CYCLO_CAP)

def act_mass(name):                    # full actuator mass, anchored to 188g pancake
    return 0.188 + (NEMA17[name][1] - PANCAKE_M)


def demands(L_mm, m_elbow, m_wrist):
    """shoulder + elbow holding torque (N*m) for equal segments L, arm horizontal."""
    m = mujoco.MjModel.from_xml_string(sizing.build(L_mm/1000, L_mm/1000, m_elbow, m_wrist))
    d = mujoco.MjData(m); d.qpos[:] = [np.pi/2, 0, 0, 0]
    mujoco.mj_inverse(m, d)
    return abs(d.qfrc_inverse[0]), abs(d.qfrc_inverse[1])

def reach_m(L_mm):
    return (2*L_mm + 50 + 78) / 1000.0     # 2 sections + wrist stub + tool/TCP


def grid(elbow="24mm pancake"):
    L_list = [75, 100, 125, 150, 175, 200]
    cols = list(NEMA17)
    m_el = act_mass(elbow); m_wr = act_mass("24mm pancake")
    print("="*86)
    print(f"WHICH (segment length x SHOULDER motor) HOLDS  -- elbow={elbow}, wrist=pancake")
    print("  cell: ok / shldr (shoulder over) / elbow (elbow over).  +250g payload, dead-horizontal")
    print("="*86)
    print(f"{'segment':>8}{'reach':>8}  " + "".join(f"{c:>14}" for c in cols))
    for L in L_list:
        sd, ed = demands(L, m_el, m_wr)
        cells = []
        for c in cols:
            if ed > cap(elbow):   cells.append("elbow")
            elif sd > cap(c):     cells.append("shldr")
            else:                 cells.append("ok")
        print(f"{L:>6}mm{reach_m(L):>7.2f}m  " + "".join(f"{x:>14}" for x in cells))
    print("-"*86)
    print("shoulder caps (N*m): " + ", ".join(f"{c.split()[0]}={cap(c):.1f}" for c in cols))


def main():
    grid(elbow="24mm pancake")             # lightest elbow -> shoulder/elbow frontier
    print()
    grid(elbow="34mm")                     # bump the elbow -> how much longer you can go
    print("\nNote: MOTOR-limited only. Every 'ok' above 1.32 N*m assumes the printed")
    print("cyclo transmits that torque -- measure CYCLO_CAP before trusting the long end.")


if __name__ == "__main__":
    main()
