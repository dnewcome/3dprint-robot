// ============================================================
//  2:1 GT2 belt pre-stage + slotted NEMA17 tensioning mount
//  Final piece of the joint module (cycloidal_disc + joint_module).
//
//  20T motor pinion -> 40T input-shaft pulley = 2:1
//  x 18:1 cycloidal = 36:1 total.
//
//  Pulleys are CHEAP — buy 20T & 40T GT2 6mm bore-5/8mm; the
//  cylinders below are just to visualise the center distance.
//  Tension by sliding the motor in the slots, then locking.
// ============================================================

PITCH  = 2;          // GT2 tooth pitch (mm)
Tm     = 20;         // motor pinion teeth
Ti     = 40;         // input-shaft pulley teeth
belt_w = 6;          // 6mm GT2

PD_m = Tm*PITCH/PI;  // motor pulley pitch dia  = 12.73
PD_i = Ti*PITCH/PI;  // input pulley pitch dia  = 25.46

C_nom  = 30;         // nominal center distance (fits 122mm closed belt)
travel = 8;          // tensioning slot length (install slack, slide to tension)

// NEMA17 frame
nema  = 42.3;        // body square
holes = 31.0;        // bolt-circle (square) spacing
pilot = 22;          // center pilot boss dia
boltD = 3.4;         // M3 clearance

// Belt pitch-length for a given center distance (mm)
function belt_len(C) = 2*C + PI*(PD_m+PD_i)/2 + pow(PD_i-PD_m,2)/(4*C);

// Slotted NEMA17 cut-out: 4 bolt slots + pilot slot, all along +X
// (the center-distance axis) so the motor slides to tension.
module nema17_slots() {
    for (sx=[-1,1], sy=[-1,1])
        hull() {
            translate([sx*holes/2,        sy*holes/2, 0]) cylinder(d=boltD, h=20, $fn=24);
            translate([sx*holes/2+travel, sy*holes/2, 0]) cylinder(d=boltD, h=20, $fn=24);
        }
    hull() {
        translate([0,0,0])      cylinder(d=pilot+0.5, h=20, $fn=72);
        translate([travel,0,0]) cylinder(d=pilot+0.5, h=20, $fn=72);
    }
}

module motor_plate(t=6) {
    difference() {
        translate([-nema/2-4, -nema/2-4, 0])
            cube([nema+travel+8, nema+8, t]);
        translate([0,0,-1]) nema17_slots();
    }
}

// Visual layout: motor pulley at origin, input pulley at C_nom
module layout() {
    color([.7,.7,.7,.45]) {
        cylinder(d=PD_m, h=2, $fn=72);
        translate([C_nom,0,0]) cylinder(d=PD_i, h=2, $fn=72);
    }
    translate([0,0,-7]) motor_plate();
}

echo(str("Nominal C=", C_nom, "mm  ->  belt pitch length = ",
         belt_len(C_nom), "mm  (use 122mm closed GT2)"));
echo(str("Tension range: C ", C_nom-3, "..", C_nom+travel-3, "mm"));

layout();
// motor_plate();   // <- the part to print
