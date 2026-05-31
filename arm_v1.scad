// ============================================================
//  arm_v1.scad — TOP-LEVEL v1 assembly (matches the build config)
//
//  J1 base : bearing-carrier turntable + onboard stepper (internal ring)
//  J2 shldr: coaxial stepper + CYCLOID, body = arm link
//  J3 elbow: CYCLOID (coaxial stepper shown; remote-shaft is an option)
//  wrist   : geared BEVEL DIFFERENTIAL → pitch + roll  (5-DOF v1)
//  gripper : tendon (shown closed-ish)
//
//  Stylized for overview (drums stand in for cycloid internals). Pose
//  with q1..q6. F5 in OpenSCAD.
//  Colors: gray=structure, dark=steppers, green=cycloid/joint,
//          orange=differential, steel=tool.
// ============================================================

$fn = 64;

// link lengths (mm)
H_base = 20;     // base carrier + deck
H_sh   = 60;     // turntable deck → J2 axis
a1 = 200;        // upper arm  (J2→J3)
a2 = 200;        // forearm    (J3→wrist)
a3 = 80;         // wrist → tool

// pose (deg)
q1=25; q2=42; q3=-62; q5=35; q6=0; grip=15;

module stepper(h=36){ color([.25,.25,.27]) translate([-21,-21,0]) cube([42,42,h]); }
module cyc_joint(d){ color("seagreen") rotate([90,0,0]) cylinder(h=26,d=d,center=true); } // pitch drum (axis Y)
module link(L,od){
    color("gainsboro") difference(){
        cylinder(h=L,d=od); translate([0,0,-1]) cylinder(h=L+2,d=od-8);
    }
}
module base_carrier(){
    color([.3,.3,.32]) cylinder(h=14,d=124);              // moment-bearing carrier ring
    color("gainsboro") translate([0,0,14]) cylinder(h=6,d=150);  // turntable deck
    translate([42,0,20]) stepper(34);                     // onboard J1 stepper
}
module bevel_diff(){
    for(s=[-1,1]) translate([0,s*22,0]) rotate([90,0,0])
        color("orange") cylinder(h=9,d=30,center=true);   // side bevels (cord pulleys)
    color("seagreen") cylinder(h=34,d=24);                // roll output (tool axis)
    color([.7,.7,.7]) translate([0,-26,0]) cube([16,52,16],center=true); // pitch yoke
}
module gripper(g){
    color([.3,.3,.32]) cylinder(h=12,d=28);
    for(s=[-1,1]) translate([s*7,0,12]) rotate([0,s*g,0])
        color([.45,.45,.5]) translate([-2.5,-4,0]) cube([5,8,40]);
}

// ---- kinematic chain ----
rotate([0,0,q1]) {                                  // J1 base yaw
    base_carrier();
    color("gainsboro") translate([0,0,H_base]) cylinder(h=H_sh, d=44);   // shoulder mast
    translate([0,0,H_base+H_sh]) rotate([0,q2,0]) {  // J2 shoulder (cycloid)
        cyc_joint(96);
        translate([0,40,0]) rotate([90,0,0]) stepper(36);  // coaxial J2 stepper
        link(a1, 42);
        translate([0,0,a1]) rotate([0,q3,0]) {       // J3 elbow (cycloid)
            cyc_joint(88);
            translate([0,38,0]) rotate([90,0,0]) stepper(32);  // coaxial J3 stepper
            link(a2, 38);
            translate([0,0,a2]) {                    // forearm end / wrist base
                for(s=[-1,1]) translate([s*20,0,-34]) stepper(26);  // 2 wrist steppers
                rotate([0,q5,0]) {                   // wrist pitch (differential)
                    bevel_diff();
                    translate([0,0,a3]) rotate([0,0,q6]) gripper(grip);  // tool roll + gripper
                }
            }
        }
    }
}

echo(str("v1: 5-DOF | reach from shoulder ~", a1+a2+a3, " mm | shoulder height ~",
         H_base+H_sh, " mm"));
