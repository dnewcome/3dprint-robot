// ============================================================
//  arm_trunk.scad — THE near-term build target: 3-DOF cycloid trunk.
//
//  J1 (base yaw) + J2 (shoulder) + J3 (elbow), ALL the same cartridge
//  from cycloid_joint.scad at three sizes. No wrist, no cables, no BLDC —
//  those are parked/ explorations. Three joints position the TOOL POINT in
//  space; bolt a fixed gripper or a manual wrist onto the forearm flange.
//
//  J1's output bearing IS the moment bearing (sized up) — the base is just
//  this cartridge stood vertical on a pedestal.
//
//  Joint envelopes are derived from cycloid_joint.scad's cfg() so sizes
//  stay in sync with the real parts. Pose with q1/q2/q3. F5 in OpenSCAD.
// ============================================================

use <cycloid_joint.scad>     // cfg() + accessors + (modules)

$fn = 72;

// ---- link lengths (mm) ----  reach from shoulder ~= a1+a2+tool
H_ped = 40;     // base pedestal height (table -> J1)
H_mast= 70;     // J1 deck -> J2 axis
a1    = 210;    // upper arm  (J2 -> J3)
a2    = 210;    // forearm    (J3 -> tool flange)
tool  = 60;     // forearm flange -> tool point

// ---- pose (deg) ----
q1 = 20; q2 = 45; q3 = -65;

// joint envelope drawn from its real config (bearing OD + ring + motor)
module joint_envelope(j) {
    c = cfg(j);
    brgOD = 2*(c_raceR(c)+c_ball(c)/2)+2;
    ringOD= 2*(c_R(c)+c_Rr(c)+4);
    H = c_T(c)*2 + 0.5 + 6 + c_brgW(c) + 8;
    color("dimgray")  cylinder(h=H, d=brgOD, center=true);            // cartridge body
    color("seagreen") cylinder(h=H+1, d=ringOD, center=true);          // gear ring band
    color([.18,.18,.2]) translate([0,0,-H/2-19]) cube([42.3,42.3,38],center=true); // NEMA17
}
module link(L, od) {
    color("gainsboro") difference() {
        cylinder(h=L, d=od); translate([0,0,-1]) cylinder(h=L+2, d=od-7); }
}

// ---- kinematic chain ----
// base pedestal
color([.35,.35,.38]) cylinder(h=H_ped, d=2*(c_raceR(cfg("J1"))+8));

translate([0,0,H_ped]) rotate([0,0,q1]) {           // ---- J1 base yaw (vertical axis)
    rotate([0,0,0]) joint_envelope("J1");
    color("gainsboro") translate([0,0,8]) cylinder(h=H_mast, d=46);    // shoulder mast
    translate([0,0,8+H_mast]) rotate([0,q2,0]) {     // ---- J2 shoulder (axis = Y)
        rotate([90,0,0]) joint_envelope("J2");
        link(a1, 42);
        translate([0,0,a1]) rotate([0,q3,0]) {       // ---- J3 elbow
            rotate([90,0,0]) joint_envelope("J3");
            link(a2, 36);
            translate([0,0,a2]) {                    // ---- forearm tool flange
                color([.5,.5,.55]) cylinder(h=6, d=44);
                color("steelblue") translate([0,0,6]) cylinder(h=tool, d=12);  // tool stub
            }
        }
    }
}

echo(str("trunk: 3-DOF | reach from shoulder ~", a1+a2+tool,
         " mm | shoulder height ~", H_ped+8+H_mast, " mm"));
