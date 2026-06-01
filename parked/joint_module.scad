// ============================================================
//  Joint module input/output stack — completes cycloidal_disc.scad
//
//  Power path:
//    NEMA17 (5mm) --20T-- GT2 belt 2:1 --40T-- input shaft (8mm)
//      input shaft runs on 2x 608 in the housing  (proper support!)
//        -> double eccentric cam (2x 6802) -> two cycloidal discs
//          -> 6 steel output pins -> output flange
//            -> main output bearing (6810 or BB crossed-roller)
//              -> magnet on flange end -> encoder PCB on housing
//
//  Net ratio: 2 (belt) x 18 (cycloidal) = 36:1
//
//  The belt pre-stage does triple duty: gets ratio to 36:1, puts
//  the cam on its OWN supported shaft (not the motor stub), and
//  lets the NEMA17 sit offset for packaging / relocation.
// ============================================================

use <cycloidal_disc.scad>   // pulls in disc + pin_ring + params

// ---- shared with cycloidal_disc.scad (keep in sync) ----
E   = 1.5;     // eccentricity
T   = 8;       // disc thickness
n_out   = 6;   // output pins
out_bc  = 18;  // output bolt-circle radius
out_pin_d = 6; // steel output dowel diameter

// ---- input side ----
shaft_d      = 8;    // ground steel input shaft
cam_jrnl_d   = 15;   // 6802 bore -> cam journal OD
cam_jrnl_w   = 5;    // 6802 width
gap          = 0.5;  // axial clearance between discs

// ---- double eccentric cam (the part you print/turn) ----
// Two journals 180deg apart (+E and -E), stacked axially so each
// carries one disc.  Discs end up 180deg out of phase -> balanced.
module double_eccentric_cam() {
    difference() {
        union() {
            translate([ E,0,0])
                cylinder(h=cam_jrnl_w, d=cam_jrnl_d, $fn=96);
            translate([-E,0,cam_jrnl_w + gap])
                cylinder(h=cam_jrnl_w, d=cam_jrnl_d, $fn=96);
            // crescent counterweights cancel residual disc-orbit mass
            translate([-E,0,0])
                cylinder(h=cam_jrnl_w, d=cam_jrnl_d-2, $fn=96);
            translate([ E,0,cam_jrnl_w+gap])
                cylinder(h=cam_jrnl_w, d=cam_jrnl_d-2, $fn=96);
        }
        // through bore for the input shaft + radial set-screw flat
        translate([0,0,-1])
            cylinder(h=2*cam_jrnl_w+gap+2, d=shaft_d, $fn=64);
        translate([0,-shaft_d/2-2,cam_jrnl_w])      // set-screw access
            rotate([90,0,0]) cylinder(h=6, d=3, $fn=24);
    }
}

// ---- output flange: 6 steel pins + on-axis magnet pocket ----
flange_d = 56;
flange_t = 6;
pin_len  = 2*T + gap + 4;     // pins span both discs + clearance

module output_flange() {
    difference() {
        union() {
            cylinder(h=flange_t, d=flange_d, $fn=160);
            for (a=[0:360/n_out:359])               // output pins
                translate([out_bc*cos(a), out_bc*sin(a), flange_t])
                    cylinder(h=pin_len, d=out_pin_d, $fn=48);
        }
        translate([0,0,-0.01]) cylinder(h=2.6, d=6.2, $fn=48); // magnet pocket
        // 4x M3 to bolt onto the output link / bearing inner ring
        for (a=[45:90:359])
            translate([22*cos(a),22*sin(a),-1]) cylinder(h=flange_t+2,d=3.2,$fn=24);
    }
}

// ---- exploded section view to check the stack ----
module stack_demo() {
    color("dimgray")  output_flange();
    color("orange")   translate([ E,0,flange_t+pin_len-2*T-gap-2])
                          rotate([0,0,0])  /* disc1 */ children(0);
    // (use assembly() in cycloidal_disc.scad for disc+ring fit;
    //  this file focuses on cam + flange geometry)
    color("steelblue") translate([0,0,flange_t+12]) double_eccentric_cam();
}

// ---- pick one to render ----
double_eccentric_cam();
// output_flange();
