// ============================================================
//  arm_link.scad — structural housing/link the 36:1 drive fits into
//
//  One printable arm segment =
//    [ JOINT CUP ]  houses the drive for THIS joint:
//        - integral pin ring (19 dowel holes)
//        - twin-608 back boss (cantilevers the cam, frees center)
//        - 6810 main output bearing seat at the front lip
//        - offset motor pad + belt window (belt_stage.scad)
//        - open center -> encoder bridge + cable pass-through
//    [ LINK TUBE ] structural span of `link_len`
//    [ PROX FACE ] bolts to the PREVIOUS joint's output ring (yoke)
//
//  Parametric: set link_len / which features per joint. Print the cup
//  with the joint axis VERTICAL so the output-bearing seat and pin-ring
//  bores come out round (no support inside the bore).
//
//  Keep the first block in sync with cycloidal_disc.scad / joint_module.scad
// ============================================================

// ---- synced drive params ----
ring_R    = 36;     // pin circle radius
Rr        = 3;      // roller (dowel) radius
ring_wall = 5;      // wall outside the pins
N_pins    = 19;
T         = 8;      // disc thickness
gap       = 0.5;

// ---- derived joint sizes ----
ring_Ro = ring_R + Rr + ring_wall;      // 44  outer radius of pin ring
hood_OD = 2*ring_Ro + 10;               // ~98 housing OD at the joint
wall    = 4;                            // structural wall thickness
cup_d   = 46;                           // axial depth of the cup interior

// ---- bearings ----
in_brg_OD  = 22;  in_brg_W = 7;         // 608 (x2 in back boss)
in_brg_gap = 18;  // spacing between the 608 pair (cantilever stiffness)
out_brg_OD = 65;  out_brg_W = 7;        // 6810 main output bearing
out_brg_ID = 50;

// ---- belt / motor ----
C_nom = 30;  nema = 42.3;  nema_holes = 31.0;

// ---- link ----
link_len = 160;   // <-- set per joint (upper arm / forearm)
link_OD  = 42;
bolt_bc  = 56;    // bolt-circle dia where the next yoke / prev face mates

eps = 0.01;
// ------------------------------------------------------------

// integral pin ring: the cup's inner cylinder carries the dowel holes
module pin_ring_bores(h) {
    for (i = [0:N_pins-1]) {
        a = i*360/N_pins;
        translate([ring_R*cos(a), ring_R*sin(a), -eps])
            cylinder(h = h, r = Rr + 0.10, $fn = 40);   // press fit dowels
    }
}

// the joint cup (drive lives inside; output bearing at +Z front lip)
module joint_cup() {
    difference() {
        union() {
            // outer hood
            cylinder(h = cup_d, d = hood_OD, $fn = 200);
            // back wall + central boss for the 608 pair
            cylinder(h = 2*in_brg_W + in_brg_gap + wall,
                     d = in_brg_OD + 2*wall, $fn = 96);
        }
        // ---- interior cavity for discs + output ring ----
        translate([0,0, wall])
            cylinder(h = cup_d, r = ring_R - Rr - 0.3, $fn = 200);
        // ---- integral pin-ring dowel holes ----
        translate([0,0, wall]) pin_ring_bores(2*T + gap + 1);
        // ---- 6810 output bearing seat at the front lip ----
        translate([0,0, cup_d - out_brg_W])
            cylinder(h = out_brg_W + eps, d = out_brg_OD, $fn = 160);
        // bore through the lip so the output ring's center stays open
        translate([0,0, cup_d - out_brg_W - eps])
            cylinder(h = out_brg_W + 2*eps, d = out_brg_ID - 6, $fn = 160);
        // ---- twin 608 seats in the back boss ----
        translate([0,0, wall])
            cylinder(h = in_brg_W + eps, d = in_brg_OD, $fn = 80);
        translate([0,0, wall + in_brg_W + in_brg_gap])
            cylinder(h = in_brg_W + eps, d = in_brg_OD, $fn = 80);
        // shaft clearance through the boss
        translate([0,0,-eps])
            cylinder(h = cup_d, d = 9, $fn = 48);
    }
}

// offset motor pad + belt window (motor + pulleys live OUTSIDE the back)
module motor_pad() {
    translate([C_nom, 0, -wall]) {
        difference() {
            translate([-nema/2-3, -nema/2-3, 0])
                cube([nema+6, nema+6, wall]);
            // M3 brass-insert bosses on the NEMA17 pattern (slots live
            // in the belt_stage.scad plate that bolts on top of this)
            for (sx=[-1,1], sy=[-1,1])
                translate([sx*nema_holes/2, sy*nema_holes/2, -eps])
                    cylinder(h = wall+2*eps, d = 4.2, $fn = 24);
            translate([0,0,-eps]) cylinder(h = wall+2*eps, d = 24, $fn = 64);
        }
    }
    // belt window: clearance between motor pad and the 40T input pulley
    // (left open by construction — pad sits proud of the back wall)
}

// fixed encoder bridge: 2 legs from the front lip span the open center,
// holding the AS5600/MT6701 PCB ~1.5mm above the magnet on the output.
module encoder_bridge() {
    leg = (out_brg_ID-6)/2;
    color("dimgray")
    translate([0,0, cup_d]) {
        for (s=[-1,1])
            translate([0, s*leg, 0]) cube([8, 3, 6], center=true);
        // PCB pad over center
        translate([0,0,2]) cube([16, 16, 2], center=true);
    }
}

// structural link tube + proximal mounting face to the PREVIOUS joint
module link(L = link_len) {
    // tube sweeps off the side of the cup, along -Y, then a flat face
    rotate([90,0,0]) {
        difference() {
            cylinder(h = L, d = link_OD, $fn = 96);
            translate([0,0,-eps]) cylinder(h = L+2*eps, d = link_OD-2*wall, $fn=96);
        }
        // proximal face: bolt ring that mates to prev output ring
        translate([0,0,L]) difference() {
            cylinder(h = wall, d = bolt_bc+12, $fn=120);
            for (a=[0:60:359])
                translate([bolt_bc/2*cos(a), bolt_bc/2*sin(a), -eps])
                    cylinder(h=wall+2*eps, d=3.4, $fn=24);
            translate([0,0,-eps]) cylinder(h=wall+2*eps, d=link_OD-2*wall, $fn=96);
        }
    }
}

module arm_link() {
    joint_cup();
    motor_pad();
    translate([0, -hood_OD/2 + wall, cup_d/2]) link();   // tube off the cup side
    // encoder_bridge();   // enable to view the sensor mount
}

arm_link();
// joint_cup();            // <- isolate the cup
// encoder_bridge();       // <- print separately
