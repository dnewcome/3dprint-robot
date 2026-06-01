// ============================================================
//  arm_assembly.scad — WHOLE-ARM VISUALIZATION (standalone)
//
//  6-DOF cable-driven arm, posed. Stylized for overview — dimensions
//  follow the specs, but gears/cords are simplified. Open in OpenSCAD,
//  F5 to preview, drag to orbit. Edit q1..q6 + grip to pose it.
//
//  Architecture shown:
//    fixed BASE ─ J1 yaw ─ TURNTABLE (6 motors ride here) ─ shoulder mast
//    ─ J2 shoulder ─ upper arm ─ J3 elbow ─ forearm ─ J4 roll
//    ─ wrist DIFFERENTIAL (J5 pitch + J6 roll) ─ GRIPPER
//
//  Colors: gray=structure, green=joint drums/sectors, blue=motors,
//          orange=idlers/differential, red=cord-bundle hint.
//  Cords are only HINTED (red) — real routing is the stacked idler
//  trunk described in turntable_spec.md.
// ============================================================

$fn = 64;

// ---- link lengths (mm) ----
H_mast = 70;     // turntable top -> J2 axis
a1 = 200;        // upper arm  (J2 -> J3)
a2 = 200;        // forearm    (J3 -> J4/wrist)
a3 = 90;         // wrist      (J5 -> tool)
tube_od = 40;

// ---- pose (deg) ----
q1 = 25;   // base yaw
q2 = 35;   // shoulder
q3 = -62;  // elbow
q4 = 15;   // forearm roll
q5 = 40;   // wrist pitch
q6 = 0;    // tool roll
grip = 16; // gripper opening

// ---------- primitives ----------
module nema(h=40){ color("steelblue") translate([-21,-21,0]) cube([42,42,h]); }

module link(L, od){
    color("gainsboro") difference(){
        cylinder(h=L, d=od);
        translate([0,0,-1]) cylinder(h=L+2, d=od-6);
    }
    color("indianred") cylinder(h=L, d=3);        // cord-bundle hint
}
module drum_pitch(d){ color("seagreen") rotate([90,0,0]) cylinder(h=20, d=d, center=true); }
module drum_roll(d){  color("seagreen") cylinder(h=20, d=d, center=true); }
module idler_stack(grv=8){
    for(i=[0:grv-1]) color("orange")
        rotate([90,0,0]) translate([0,0,i*2.4-grv*1.2]) cylinder(h=1.8, d=22);
}

module base(){
    color([0.3,0.3,0.32]) cylinder(h=40, d=130);
}
module turntable(){
    color("gainsboro") cylinder(h=8, d=210);
    for(i=[0:5]){ a=i*60;
        translate([80*cos(a),80*sin(a),8]) rotate([0,0,a]) nema(); }
    color([0.7,0.7,0.72]) translate([0,0,8]) cylinder(h=H_mast, d=46);  // shoulder mast
}
module differential(){
    for(s=[-1,1]) translate([0,s*22,0]) rotate([90,0,0])    // side pulleys on pitch(Y)
        color("orange") cylinder(h=8, d=30, center=true);
    color("seagreen") cylinder(h=42, d=26);                  // roll output along Z (tool)
    color([0.7,0.7,0.7]) translate([0,-26,0]) cube([16,52,16], center=true); // carrier yoke
}
module gripper(g){
    color("dimgray") cylinder(h=12, d=30);
    for(s=[-1,1]) translate([s*7,0,12]) rotate([0,s*g,0])
        color([0.4,0.4,0.45]) translate([-2.5,-4,0]) cube([5,8,42]);
}

// ---------- kinematic chain ----------
module arm(){
    base();
    translate([0,0,40]) rotate([0,0,q1]){          // J1 base yaw
        turntable();
        translate([0,0,8+H_mast]) rotate([0,q2,0]){ // J2 shoulder (pitch)
            drum_pitch(120); idler_stack(10);
            link(a1, tube_od);
            translate([0,0,a1]) rotate([0,q3,0]){    // J3 elbow (pitch)
                drum_pitch(110); idler_stack(8);
                link(a2, 38);
                translate([0,0,a2]) rotate([0,0,q4]){ // J4 forearm roll
                    drum_roll(64);
                    translate([0,0,28]) rotate([0,q5,0]){ // J5 wrist pitch
                        differential();
                        link(a3, 24);                         // wrist -> tool tube
                        translate([0,0,a3]) rotate([0,0,q6]) // J6 tool roll
                            gripper(grip);
                    }
                }
            }
        }
    }
}

arm();

echo(str("Reach from shoulder = ", a1+a2+a3, " mm ; shoulder height ~ ",
         40+8+H_mast, " mm ; max tip height ~ ", 40+8+H_mast+a1+a2+a3, " mm"));
