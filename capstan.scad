// ============================================================
//  capstan.scad — PARAMETRIC capstan drum + driven pulley
//
//  Set cord dia, ratio, and joint range; the file SIZES the drum and
//  driven pulley and reports travel/tension/idler-load in the console
//  (F5 → see ECHO output). Tune inputs to minimize size.
//
//  Size logic (read this — it answers "how small can it go?"):
//   • Drum radius is floored by the cord BEND radius: r_drum ≥
//     bend_factor·cord_d (Dyneema ~3–5×). Smaller also raises cable
//     tension (T = motor_T / r_drum) → idler load + creep.
//   • Driven pulley radius = ratio · r_drum.  ← shrinks with thinner
//     cord or lower ratio. This is the knob for "don't want it too big."
//   • Drum height = (turns for full travel + anchor turns) · groove pitch.
//
//  Trade: thin cord → small drum/pulley BUT tiny drum = hard to print +
//  high tension. 2 mm cord with ~8 mm drum is a robust, printable balance.
// ============================================================

$fn = 72;

// ===================== INPUTS =====================
cord_d        = 2.0;    // cord diameter (mm)
ratio         = 6;      // reduction N = R_driven / r_drum
out_range     = 270;    // total driven travel (deg) e.g. ±135° = 270
motor_T       = 0.45;   // motor torque at the drum (N·m) — for tension calc
cord_MBL      = 2000;   // cord min breaking load (N) — DM20-class
bend_factor   = 4;      // min drum radius = bend_factor · cord_d (Dyneema 3–5)
pitch_factor  = 1.15;   // helical groove pitch = pitch_factor · cord_d
anchor_turns  = 2;      // extra drum wraps for a no-slip anchor
drum_r_override = 0;    // 0 = auto (bend minimum); else force a radius (mm)

// build params
end_pad  = 1.5;         // small plain land at each groove end (no flanges —
                        // the groove already captures the cord)
shaft_d  = 5;           // motor shaft (drum bore)
driven_bore = 8;        // driven pulley shaft
mag_d    = 6.2;
groove_depth_f = 0.55;  // groove cuts this · cord_d deep

// ===================== DERIVED =====================
function r2(x) = floor(x*100+0.5)/100;

r_drum_min = bend_factor*cord_d;
r_drum     = (drum_r_override>0) ? drum_r_override : r_drum_min;
R_driven   = ratio*r_drum;
groove_p   = pitch_factor*cord_d;

drum_revs    = ratio*out_range/360;          // drum turns for full output range
groove_turns = drum_revs + anchor_turns;
groove_len   = groove_turns*groove_p;
drum_h       = groove_len + 2*end_pad;

cable_T   = motor_T*1000/r_drum;             // N at the cord (motor-limited)
travel_mm = drum_revs*2*PI*r_drum;           // linear cord paid out over range
idler90   = 2*cable_T*sin(45);               // idler load at a 90° turn

// ===================== REPORT =====================
echo("================ CAPSTAN SIZING ================");
echo(str("cord dia          : ", cord_d, " mm"));
echo(str("ratio             : ", ratio, " : 1"));
echo(str("drum radius        : ", r2(r_drum), " mm  (bend min = ", r2(r_drum_min),
         drum_r_override>0 ? "  [OVERRIDDEN]" : "  [auto]", ")"));
echo(str("driven pulley dia  : ", r2(2*R_driven), " mm  (radius ", r2(R_driven), ")"));
echo(str("output range       : ", out_range, " deg  →  drum spins ", r2(drum_revs), " rev"));
echo(str("drum groove        : ", r2(groove_turns), " turns @ ", r2(groove_p),
         " mm pitch  →  drum height ", r2(drum_h), " mm"));
echo(str("linear cord travel : ", r2(travel_mm), " mm"));
echo(str("cable tension      : ", r2(cable_T), " N  (", r2(100*cable_T/cord_MBL), "% MBL)"));
echo(str("idler load @90turn : ", r2(idler90), " N"));
if (r_drum < r_drum_min)
    echo("!! WARNING: drum radius below cord bend limit → cord fatigue");
if (cable_T > 0.25*cord_MBL)
    echo("!! WARNING: tension >25% MBL → bigger drum, thicker cord, or less load");
if (out_range > 340)
    echo("!! NOTE: driven travel >340° → driven pulley needs a helix/2nd layer too");
echo("================================================");

// ===================== GEOMETRY =====================
// helical-groove capstan drum (no flanges — groove captures the cord)
module capstan_drum() {
    difference() {
        cylinder(h=drum_h, r=r_drum);
        // helix groove
        sps = max(1, round(groove_turns*48));
        for (i=[0:sps]) {
            a = i*360/48;
            z = end_pad + i*groove_p/48;
            rotate([0,0,a]) translate([r_drum, 0, z])
                sphere(d = cord_d + 0.3);
        }
        translate([0,0,-1]) cylinder(h=drum_h+2, d=shaft_d+0.2);     // shaft bore
        // ---- CENTER ANCHOR (positive — don't trust Dyneema friction) ----
        // Put ~1-2 wraps each side so the capstan effect shields this anchor;
        // it then only holds a small residual. Method: cord into the radial
        // hole, then crimp/splice-on-pin/clamp in the pocket.
        translate([0,0,drum_h/2]) rotate([0,90,0])
            cylinder(h=r_drum+0.5, d=cord_d+0.4);                    // radial cord lead-in
        translate([r_drum-4,-3.5,drum_h/2-3.5]) cube([4.5,7,7]);     // crimp/clamp pocket
        translate([r_drum+0.5,0,drum_h/2]) rotate([0,-90,0])
            cylinder(h=4, d=2.5);                                    // optional M3 grub (heat-set)
        // drum-to-shaft set screw (near base, clear of the anchor)
        translate([0,-r_drum,end_pad+2]) rotate([90,0,0])
            cylinder(h=2*r_drum, d=2.6);
    }
}

// driven pulley: single circumferential groove (out_range < 1 rev),
// 2 anchors (pull-pull), hub + magnet pocket
module driven_pulley() {
    h = max(cord_d+6, 12);
    difference() {
        union() {
            cylinder(h=h, r=R_driven);
            translate([0,0,h]) cylinder(h=4, r=14);                  // hub
        }
        translate([0,0,h/2]) rotate_extrude()
            translate([R_driven,0]) circle(d=cord_d+0.3);            // groove
        for (s=[-1,1]) translate([0, s*(cord_d/2+1), h/2]) rotate([0,90,0])
            cylinder(h=R_driven+1, d=cord_d+0.5);                    // 2 anchor channels
        translate([0,0,-1]) cylinder(h=h+6, d=driven_bore+0.2);      // shaft bore
        translate([0,0,h+4-2.7]) cylinder(h=2.8, d=mag_d);           // magnet pocket
    }
}

// ===================== RENDER =====================
// side-by-side to compare sizes
capstan_drum();
translate([r_drum + R_driven + 15, 0, 0]) driven_pulley();
// capstan_drum();
// driven_pulley();
