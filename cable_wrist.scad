// ============================================================
//  cable_wrist.scad — cord-driven differential wrist (SCHEMATIC)
//
//  Two cords A,B (from base motors) turn two side bevels on the PITCH
//  axis; a central bevel on the ROLL axis is the differential output.
//    A,B same dir -> ROLL (J6) ;  A,B opposite -> PITCH (J5)
//  Carrier yoke = pitch axis. Cords route down the forearm centerline,
//  redirect idlers set the pull-pull tangent points.
//
//  Schematic only: bevels shown as cylinders; cords not drawn.
//  See cable_wrist_spec.md.
// ============================================================

Rside = 22;   // side bevel/pulley radius (cord wraps here)
Rcap  = 18;   // central (roll output) bevel radius
yoke  = 60;   // pitch-axis span
 id_R  = 8;    // redirect idler radius

module bevel(r) { color("steelblue") cylinder(h=8, r=r, center=true, $fn=64); }

module differential() {
    // pitch axis = X ; side bevels A/B at +/-yoke/2
    for (s=[-1,1]) translate([s*yoke/2,0,0]) rotate([0,90,0]) bevel(Rside);
    // central roll output on Z (tool axis), meshing both sides
    color("seagreen") cylinder(h=40, r=Rcap, $fn=64);
    // carrier yoke (pitch frame)
    color("gainsboro") difference() {
        translate([-yoke/2-6,0,0]) rotate([0,90,0]) cylinder(h=yoke+12, r=10,$fn=8);
        translate([-yoke/2-7,0,0]) rotate([0,90,0]) cylinder(h=yoke+14, r=6,$fn=8);
    }
}

module redirect_idlers() {
    // two idlers on the forearm bringing cords A,B to side-bevel tangents
    color("orange") for (s=[-1,1])
        translate([s*Rside, 0, -50]) rotate([90,0,0]) cylinder(h=6,r=id_R,center=true,$fn=48);
}

module forearm_stub() {
    color([.8,.8,.8,.5]) translate([0,0,-90]) cylinder(h=80, d=42, $fn=48);
}

differential();
redirect_idlers();
forearm_stub();
