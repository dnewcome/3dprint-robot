// ============================================================
//  Parametric cycloidal drive — disc + pin ring
//  Joint module for 3D-printed 6-axis arm (250 g payload)
//
//  Reduction (ring fixed, output via disc holes):
//      ratio = number of lobes = (N_pins - 1)
//  Here: N=19 pins -> 18 lobes -> 18:1.  Add a 2:1 GT2 belt
//  pre-stage upstream for 36:1 total at the shoulder.
//
//  IMPORTANT build notes:
//   * Use STEEL DOWEL PINS (or 6mm ball bearings on pins) as the
//     rollers — never printed-on-printed, it wears in hours.
//   * Single disc is unbalanced; for the real joint use TWO discs
//     180° out of phase (see assembly() ) to cancel the shake.
//   * Validity requires  E < R/N_pins  (keeps the profile from
//     self-intersecting).  Checked with assert() below.
// ============================================================

// ---------------- Parameters ----------------
N_pins = 19;      // ring pins  -> lobes = N_pins-1, ratio = lobes
R      = 36;      // pin circle radius (mm)
Rr     = 3;       // roller / pin radius (mm)  -> 6mm dowels
E      = 1.5;     // eccentricity (mm)   MUST be < R/N_pins
T      = 8;       // disc thickness (mm)
steps  = 720;     // profile resolution

bore_r     = 12;  // disc center bore = OD/2 of the cam bearing.
                  //   Matches 6802-2RS (24mm OD) on the double eccentric cam.
                  //   See joint_module.scad for the input/cam/output stack.
n_out      = 6;   // number of output-pin holes
out_bc     = 18;  // output-pin bolt-circle radius (mm)
out_pin_r  = 3;   // output pin radius (6mm pins)
// output holes are oversized by E so the eccentric disc clears them:
out_hole_r = out_pin_r + E;

assert(E < R/N_pins, "Invalid: eccentricity E must be < R / N_pins");

// ---------------- Cycloid math ----------------
// (degrees — OpenSCAD trig is in degrees)
function psi(t) = atan2( sin((1-N_pins)*t),
                         (R/(E*N_pins)) - cos((1-N_pins)*t) );
function px(t)  =  R*cos(t) - Rr*cos(t + psi(t)) - E*cos(N_pins*t);
function py(t)  = -R*sin(t) + Rr*sin(t + psi(t)) + E*sin(N_pins*t);

disc_pts = [ for (i=[0:steps-1]) let(t = i*360/steps) [px(t), py(t)] ];

// ---------------- Modules ----------------
module cycloidal_disc() {
    linear_extrude(height=T)
    difference() {
        polygon(disc_pts);
        circle(r = bore_r, $fn=96);                 // eccentric-cam bearing
        for (a = [0 : 360/n_out : 359])             // output-pin holes
            translate([out_bc*cos(a), out_bc*sin(a)])
                circle(r = out_hole_r, $fn=64);
    }
}

module pin_ring(wall = 5, flange = 4) {
    Ro = R + Rr + wall;                              // outer radius
    difference() {
        cylinder(h = T + flange, r = Ro, $fn = 220);
        // inner running cavity (disc spins here)
        translate([0,0,flange])
            cylinder(h = T + 1, r = R - Rr + E + 0.4, $fn = 220);
        // pin holes (press steel dowels here)
        for (i = [0 : N_pins-1]) {
            a = i*360/N_pins;
            translate([R*cos(a), R*sin(a), flange - 1])
                cylinder(h = T + 2, r = Rr + 0.10, $fn = 48);  // +0.1 fit
        }
    }
}

// Two discs, 180° apart, each shifted by the eccentricity in its
// own direction — this is what you actually print for the joint.
module assembly() {
    color("silver") pin_ring();
    color("orange")  translate([ E, 0, 6]) cycloidal_disc();
    color("teal")    translate([-E, 0, 6 + T + 0.5])
                         rotate([0,0,180]) cycloidal_disc();
}

// ---------------- Output select ----------------
// Render ONE of these (comment the rest), or use the demo.
cycloidal_disc();           // <- the part to STL for printing
// pin_ring();
// assembly();              // <- view fit/clearance before printing
