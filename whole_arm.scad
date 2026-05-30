// ============================================================
//  whole_arm.scad — 6-axis layout: stacked roll + bend cartridges
//
//  Visualizes link lengths, joint placement, and the reach envelope.
//  Each joint is a coaxial clevis-free cartridge (coaxial_joint.scad);
//  here drawn as stylized drums so you can check the kinematics & fit.
//
//  Joint map (articulated arm, ~spherical wrist):
//    J1 base   ROLL  (axis vertical)      big drum, 90:1
//    J2 shoulder BEND (axis horizontal)   big drum, 90:1
//    J3 elbow  BEND                       big drum, 90:1
//    J4 forearm ROLL (axis along link)    med drum, ~36:1
//    J5 wrist  BEND                       small drum, 18:1
//    J6 tool   ROLL                       small drum, 18:1
//
//  Change the q1..q6 to pose the arm; change link lengths to retune.
// ============================================================

// ---- link lengths (mm) — all one-piece printable on a 250 bed ----
H1 = 150;   // base column: J1 top -> J2 axis
a1 = 200;   // upper arm: J2 -> J3
a2 = 200;   // forearm:   J3 -> wrist point (J5)
a3 = 90;    // wrist:     J5 -> tool flange (J6)

// ---- pose (deg) ----
q1=20; q2=40; q3=-55; q4=0; q5=35; q6=0;

// ---- drum sizes (od, thickness) ----
BIG=[110,30]; MED=[78,26]; SML=[64,22];
tube_od=42; tube_id=34;

module drum(s) {
    od=s[0]; th=s[1];
    color("steelblue") cylinder(h=th, d=od, center=true, $fn=80);
    color("dimgray")   translate([0,0,-th/2-22]) cylinder(h=44,d=42,$fn=48); // motor
}
module tube(L) {
    color("gainsboro") difference(){
        cylinder(h=L, d=tube_od, $fn=60);
        translate([0,0,-1]) cylinder(h=L+2, d=tube_id, $fn=60);
    }
}
module flange(){ color("orange") cylinder(h=4,d=40,$fn=48); }

// reach envelope: sphere about the shoulder, R = a1+a2+a3
module envelope() {
    color([1,0.6,0.1,0.06])
        translate([0,0,30/2+H1]) sphere(r=a1+a2+a3, $fn=64);
}

// ---- kinematic chain (link dir = local +Z, pitch=about Y, roll=about Z)
rotate([0,0,q1]) {
    rotate([90,0,0]) drum(BIG);                 // J1 roll, axis vertical
    translate([0,0,30/2]) tube(H1);             // base column
    translate([0,0,30/2+H1]) rotate([0,q2,0]) { // J2 shoulder bend
        rotate([90,0,0]) drum(BIG);
        tube(a1);                               // upper arm
        translate([0,0,a1]) rotate([0,q3,0]) {  // J3 elbow bend
            rotate([90,0,0]) drum(BIG);
            tube(a2);                            // forearm
            translate([0,0,a2]) rotate([0,0,q4]) {   // J4 forearm roll
                drum(MED);
                translate([0,0,13]) rotate([0,q5,0]) {   // J5 wrist bend
                    rotate([90,0,0]) drum(SML);
                    translate([0,0,a3]) rotate([0,0,q6]) {  // J6 tool roll
                        drum(SML);
                        translate([0,0,11]) flange();
                    }
                }
            }
        }
    }
}

envelope();
echo(str("Max reach from shoulder = ", a1+a2+a3, " mm"));
echo(str("Shoulder height ~ ", 30/2+H1, " mm ; max tip height ~ ",
         30/2+H1 + a1+a2+a3, " mm"));
