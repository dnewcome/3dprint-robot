// ============================================================
//  DEPRECATED (2026-06) — superseded by ../arm_section.py (build123d).
//  OpenSCAD is no longer the toolchain; this is kept for reference only and
//  is not maintained. The build123d port imports the vendor STEP as exact
//  solids; this version imports the STL meshes.
//
//  arm_section.scad — the printable arm links for the cycloidal arm.
//
//  ARCHITECTURE (decided 2026-06): the arm is built from SECTIONS that each
//  integrate one half of a joint at each end. The Sweep Dynamics actuators
//  have a ROTATING BODY (the cyclo Housing is the output) and a fixed motor
//  mount (the NEMA17 Base), and ship with NO external mounting pattern -- so
//  the mount is designed straight into the printed section (fused, not bolted):
//      - one end: the rotating HOUSING (output of the UPSTREAM joint) FUSED
//        into the print  -> this end pivots with the joint.
//      - other end: the NEMA17 BASE plate (motor mount for the DOWNSTREAM
//        joint), also fused in.
//  A joint forms in the gap between two sections: motor on section N's Base
//  -> cyclo internals (discs/shaft/endcap) -> Housing fused into section N+1
//  -> N+1 swings.   Every joint = the 20:1 Micro Cycloidal (42x42, NEMA17)
//  EXCEPT the base slew (the larger 26:1, 62x62), which the base section
//  bolts onto through a right-angle flange.
//
//  FOUR sections (set PART below):
//    "base"    90deg: NEMA17 plate (shoulder motor) + 4-bolt flange -> slew
//    "upper"   long : Housing (shoulder out) ---150mm--- Base (elbow motor)
//    "forearm" long : Housing (elbow out)   ---150mm--- Base (wrist motor)
//    "wrist"   90deg: Housing (wrist-pitch out) + tool-roll actuator mount
//
//  Vendor geometry imported from vendor/micro/*.stl. Native parts sit at
//  XY=(75,0), z=0..h; helpers recenter them on the origin and on Y.
//
//  Local frame: arm length runs +X. Joint (cyclo) axes run along Y (pitch
//  axis). +Z = up; gravity sag bends the beam about Y, so the beam is TALL
//  in Z (stiffness ~ height^2) and only actuator-wide in Y.
// ============================================================

PART = "upper";          // "base" | "upper" | "forearm" | "wrist"

// ---- vendor micro actuator (20:1) ----
ACT      = 42;           // actuator footprint (square, mm)
ACT_R    = 21;           // housing outer radius (round body)
HOUS_H   = 18.2;         // housing height (along its axis)
BASE_H   = 9.0;          // base plate thickness
VC       = 75;           // vendor parts centered at X=VC in their STL

// ---- structural beam (tall in Z to fight gravity sag) ----
SEG_LEN  = 150;          // long-section length (housing center -> base face)
BEAM_H   = 28;           // beam height (along Z) -- the stiff direction
BEAM_W   = 20;           // beam width (along Y) -- ~ actuator width
WALL     = 4;            // collar/gusset wall

$fn = 64;

// ---------- vendor parts, recentered to origin (axis = +Z) ----------
module v_housing() translate([-VC,0,0]) import("../vendor/micro/housing.stl");
module v_base()    translate([-VC,0,0]) import("../vendor/micro/base_nema17.stl");

// Housing as a joint OUTPUT: cyclo axis along Y, centered on Y=0.
// native (after recenter) z:0..HOUS_H about origin -> rotate so axis=Y, then
// shift so the body straddles Y=0.
module housing_end() translate([0, HOUS_H/2, 0]) rotate([-90,0,0]) v_housing();

// Base as a motor mount: motor axis along Y, plate centered on Y=0.
module base_end() translate([0, -BASE_H/2, 0]) rotate([90,0,0]) v_base();

// flat tall beam from x0 to x1, centered on Y=0
module beam(x0, x1)
    translate([x0, -BEAM_W/2, -BEAM_H/2]) cube([x1-x0, BEAM_W, BEAM_H]);

// collar that grips the housing wall (annulus biting 2mm into the 4mm wall,
// outer face proud for the beam to fuse onto). Bore (r<BORE_R) stays clear.
BORE_R = 17;             // housing inner bore (disc cavity) radius
module housing_collar() {
    rotate([-90,0,0]) translate([0,0,-HOUS_H/2])
    difference() {
        cylinder(h=HOUS_H, r=ACT_R+WALL);
        translate([0,0,-0.5]) cylinder(h=HOUS_H+1, r=BORE_R+2);   // keep cavity clear
    }
}

// triangular gusset blending the beam down onto the base plate face
module base_gusset(xface) {
    hull() {
        translate([xface-0.1, -BEAM_W/2, -BEAM_H/2]) cube([0.1, BEAM_W, BEAM_H]);
        translate([xface-BEAM_H, -BEAM_W/2, -BEAM_H/2]) cube([0.1, BEAM_W, 0.1]);
    }
}

// ---------------- sections ----------------

// LONG section: housing (proximal, X=0) --beam--> base (distal)
module long_section(len=SEG_LEN) {
    xbase = len;                       // base plate face sits at X=len
    union() {
        housing_end();
        housing_collar();
        beam(BORE_R, xbase);           // beam starts at the bore wall (clears the disc cavity)
        base_gusset(xbase);
        translate([xbase, 0, 0]) base_end();
    }
}

if (PART == "upper" || PART == "forearm")
    long_section();
