// ============================================================
//  bldc_2204.scad — 2204-class outrunner BLDC (e.g. C2204-1400KV)
//
//  Parametric model from the vendor spec drawing:
//    bell OD .......... 27.8 mm        body height ...... 18 mm
//    shaft ............ Ø3              rear shaft stub .. 10.5 mm (below mount)
//    front thread ..... M5             (prop / adapter end, top of bell)
//    mount holes ...... 4 × Ø3.2 on a 16 × 19 rectangle
//    mount arms ....... ~34 mm across the diagonal
//
//  Two bodies are colored separately so you can see what spins:
//    STATOR + base (fixed)  = dark gray
//    BELL/can (rotor)       = light  — rotate it with `roll` to animate
//
//  This is a fit/clearance model (envelope, mount pattern, shaft), not a
//  magnetic/winding-accurate one. Slots & windings are stylized.
//
//  Origin: motor axis = Z. z=0 is the MOUNTING FACE (bottom of base
//  plate). Bell sits above; rear shaft stub points down (-Z).
// ============================================================

$fn = 96;

// ---- key dimensions (mm) ----
bell_d     = 27.8;    // rotating can OD
body_h     = 18;      // mount face → top of bell
shaft_d    = 3;       // motor shaft
shaft_rear = 10.5;    // shaft protrusion below the mount face
thread_d   = 5;       // M5 front (prop) shaft / nut adapter
mount_x    = 19;      // mounting-hole spacing (one axis)
mount_y    = 16;      // mounting-hole spacing (other axis)
mount_hole = 3.2;     // Ø of the 4 mount holes
arm_span   = 34;      // overall span across mount arms (diagonal-ish)

// ---- derived structure ----
base_h     = 2.2;     // mount plate thickness
stator_d   = bell_d - 4;   // stator OD (rotor gap ~1mm shown as 2)
stator_h   = body_h - 6;   // visible stator stack height
bell_wall  = 1.2;
bell_lip   = 2;       // bell sits this far down over the stator
eps        = 0.02;

roll = 0;             // spin the bell/rotor (deg) for animation

// ------------------------------------------------------------
//  FIXED part: mount base + stator stack + rear shaft stub
// ------------------------------------------------------------
module mount_base() {
    difference() {
        union() {
            // 4-arm cross plate (the cast/CNC spider)
            for (s = [[1,1],[1,-1],[-1,1],[-1,-1]])
                hull() {
                    cylinder(h=base_h, d=9);                       // hub
                    translate([s[0]*mount_x/2, s[1]*mount_y/2, 0])
                        cylinder(h=base_h, d=7);                   // arm pad
                }
            cylinder(h=base_h, d=14);                              // center boss
        }
        // 4 mounting holes
        for (s = [[1,1],[1,-1],[-1,1],[-1,-1]])
            translate([s[0]*mount_x/2, s[1]*mount_y/2, -eps])
                cylinder(h=base_h+2*eps, d=mount_hole);
        // center relief / shaft clearance
        translate([0,0,-eps]) cylinder(h=base_h+2*eps, d=shaft_d+1.5);
    }
}

module stator_stack() {
    // bearing tube / mount riser
    translate([0,0,base_h]) cylinder(h=body_h-bell_lip-base_h, d=10);
    // stylized 12-slot stator laminations
    translate([0,0,base_h+1.5])
        for (i = [0:11]) rotate([0,0,i*30])
            translate([stator_d/2 - 1.6, 0, 0])
                cube([3.2, 4.4, stator_h], center=true);
    // copper windings hint (a torus-ish band)
    color([0.72,0.45,0.2])
        translate([0,0,base_h + 1.5 + stator_h/2])
            rotate_extrude() translate([stator_d/2-2.2,0,0]) circle(d=4.5);
}

module rear_shaft() {
    translate([0,0,-shaft_rear]) cylinder(h=shaft_rear+base_h, d=shaft_d);
    // E-clip groove hint near the tip
    translate([0,0,-shaft_rear+2])
        rotate_extrude() translate([shaft_d/2,0,0]) circle(d=0.6);
}

module stator_assembly() {
    color([0.22,0.22,0.24]) { mount_base(); rear_shaft(); }
    color([0.30,0.30,0.33]) stator_stack();
}

// ------------------------------------------------------------
//  ROTOR: bell/can + vented top + M5 front shaft/nut
// ------------------------------------------------------------
module bell() {
    // outer can
    difference() {
        cylinder(h=body_h-bell_lip, d=bell_d);
        translate([0,0,-eps])
            cylinder(h=body_h-bell_lip-1.2, d=bell_d-2*bell_wall);  // hollow
    }
    // top cap with vent holes + spokes
    translate([0,0,body_h-bell_lip-1.2])
        difference() {
            cylinder(h=1.2, d=bell_d);
            // 6 vent holes
            for (i=[0:5]) rotate([0,0,i*60])
                translate([bell_d/4, 0, -eps])
                    cylinder(h=1.2+2*eps, d=4);
            // center bore for the shaft
            translate([0,0,-eps]) cylinder(h=1.2+2*eps, d=shaft_d+0.3);
        }
}

module front_shaft() {
    // M5 prop-end: shaft section + nut adapter sitting proud of the bell
    translate([0,0,body_h-bell_lip-1.2]) {
        cylinder(h=3, d=shaft_d);                     // exposed shaft
        translate([0,0,3]) cylinder(h=4, d=thread_d); // M5 adapter / collet
    }
}

module rotor_assembly() {
    rotate([0,0,roll]) {
        color([0.78,0.80,0.82]) bell();
        color([0.62,0.63,0.66]) front_shaft();
    }
}

// ------------------------------------------------------------
//  full motor
// ------------------------------------------------------------
module bldc_2204() {
    translate([0,0,bell_lip]) rotor_assembly();   // bell rides down over stator
    stator_assembly();
}

bldc_2204();

echo(str("BLDC 2204: bell Ø", bell_d, " | body ", body_h,
         " mm | mount ", mount_x, "×", mount_y,
         " (Ø", mount_hole, ") | shaft Ø", shaft_d,
         " rear ", shaft_rear, " mm | front M", thread_d));
