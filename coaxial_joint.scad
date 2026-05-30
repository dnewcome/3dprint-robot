// ============================================================
//  coaxial_joint.scad — CLEVIS-FREE modular actuator joint
//  (UR/cobot-style cartridge). Motor coaxial, shaft pointing IN.
//
//  STATOR (link N side): geared stepper bolts to the back, shaft
//    enters on-axis carrying the wave generator. Integral CS (N+2).
//    Holds the OUTER race of the big crossed-roller output bearing.
//  ROTOR (link N+1 side): integral DS (N), rides the bearing INNER
//    race, presents a front bolt-face for the (offset) moving link.
//    Open center = encoder magnet + cable pass-through.
//
//  No fork, no clevis: ONE big crossed-roller bearing, concentric and
//  OUTBOARD of the gears, carries the whole cantilever moment.
//
//  Reduction = (geared-stepper ratio) x (N/2). e.g. 5 x 18 = 90:1.
//  Pre-stage lives in the geared stepper -> no belt, fully inline.
//
//  NOTE: layout SKELETON — correct architecture, sizes & seats; fillet
//  / lighten / detail the gear bores in real CAD. Pulls the gearset
//  from harmonic_ring.scad (swap to cycloidal by editing the rings).
// ============================================================

use <harmonic_ring.scad>     // internal_ring_gear(teeth, m, h)

// ---- gearset (sync with harmonic_ring.scad) ----
N   = 36;          // flexspline / DS teeth ; CS = N+2
m   = 2.0;         // module
Hg  = 8;           // gear ring height

// ---- coaxial geared-stepper output (the "shaft pointing in") ----
gshaft_d   = 8;    // geared NEMA17 output shaft
gflange_bc = 31;   // geared stepper output bolt circle dia

// ---- big crossed-roller output bearing (OUTBOARD of the gears) ----
// modeled as an annular ball groove; use airsoft BBs (Proto 1) or a
// bought thin-section slewing ring.
ball_d   = 6;      // 6mm airsoft BB
Rrace    = 52;     // ball pitch radius (race centerline) -> ~104mm bearing
brg_W    = 10;

wall = 4; eps = 0.01;

Rg_out  = m*(N+2)/2 + 1.25*m + 5;   // CS outer radius (~45.5)
Rhood   = Rrace + ball_d/2 + wall;   // stator outer radius

// ---- ball groove (shared race shape, cut into both parts) ----
module ball_groove(z) {
    translate([0,0,z]) rotate_extrude($fn=220)
        translate([Rrace,0,0]) circle(d=ball_d+0.4, $fn=32);
}

// ---- STATOR: motor mount + integral CS + outer race ----
module stator() {
    difference() {
        cylinder(h = wall + Hg + brg_W, r = Rhood, $fn=240);
        // gear + rotor cavity
        translate([0,0,wall]) cylinder(h = Hg+brg_W+1, r = Rrace-2, $fn=240);
        // geared-stepper shaft entry + bolt circle at back
        translate([0,0,-eps]) cylinder(h = wall+2*eps, d = gshaft_d+1.5, $fn=48);
        for (a=[0:90:359])
            translate([gflange_bc/2*cos(a), gflange_bc/2*sin(a), -eps])
                cylinder(h = wall+2*eps, d=3.4, $fn=24);
        // outer half of the ball race
        ball_groove(wall + Hg + brg_W/2);
    }
    // integral CS (fixed) at the back of the cavity
    translate([0,0,wall]) internal_ring_gear(N+2, m, Hg);
}

// ---- ROTOR: integral DS + inner race + front bolt-face ----
module rotor() {
    difference() {
        union() {
            // ring that becomes the bearing inner race, spanning to gears
            cylinder(h = Hg+brg_W, r = Rrace-2.2, $fn=240);
            // front flange for the moving link
            translate([0,0,Hg+brg_W])
                cylinder(h = wall, r = Rrace-2.2, $fn=240);
            translate([0,0,Hg]) internal_ring_gear(N, m, brg_W); // DS (output)
        }
        // open center: encoder magnet web + cable pass-through
        translate([0,0,-eps]) cylinder(h = Hg+brg_W+wall+2*eps, d=24, $fn=120);
        // inner half of the ball race
        ball_groove(Hg + brg_W/2 - wall);   // aligns with stator groove on assembly
        // moving-link bolt circle on the front face
        for (a=[0:60:359])
            translate([(Rrace-12)*cos(a), (Rrace-12)*sin(a), Hg+brg_W])
                cylinder(h = wall+eps, d=3.4, $fn=24);
        // magnet pocket on the center web (output-side encoder)
        translate([0,0,Hg+brg_W+wall-2.6]) cylinder(h=2.7, d=6.2, $fn=48);
    }
}

// ---- assembly preview ----
module demo() {
    color("steelblue") stator();
    color("seagreen")  translate([0,0,wall]) rotor();
    color("orange")    translate([0,0,wall]) flexspline();
    color("dimgray")   translate([0,0,wall]) wave_generator(shaft_d=gshaft_d);
}

// ---- render one ----
stator();
// rotor();
// demo();
