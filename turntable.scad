// ============================================================
//  turntable.scad — base motor-plate layout (SCHEMATIC)
//
//  J1 (fixed base) rotates this plate. 6 motors ride the plate, each
//  with a 2-stage capstan reducer; stage-2 cords converge on the central
//  shoulder mast (J2 axis) and route up the arm over stacked concentric
//  idlers. Constant-force tensioner per cord.
//
//  Schematic: motors = boxes, reducers = cylinders, cords not drawn.
//  See turntable_spec.md.
// ============================================================

n_mot   = 6;       // motors on the turntable (J2,J3,J4,W1,W2,grip)
ring_R  = 80;      // motor ring radius
plate_d = 210;
nema    = 42.3;

module nema17(){ color("dimgray") translate([-nema/2,-nema/2,0]) cube([nema,nema,40]); }
module reducer(){ // stage-1 pulley + stage-2 drum stack (schematic)
    color("steelblue") cylinder(h=10, r=30, $fn=64);
    color("dimgray")   translate([0,0,10]) cylinder(h=14, r=8, $fn=48);
}
module tensioner(){ color("orange") cube([10,24,8], center=true); } // constant-force spring

module idler_stack(grooves){       // concentric idler pack on a joint axis
    for (i=[0:grooves-1])
        color("orange") translate([0,0,i*2.2]) cylinder(h=1.6, r=10, $fn=48);
}

module turntable() {
    // plate
    color("gainsboro") cylinder(h=6, d=plate_d, $fn=160);
    // motor ring + reducers + tensioners
    for (i=[0:n_mot-1]) {
        a = i*360/n_mot;
        translate([ring_R*cos(a), ring_R*sin(a), 6]) {
            rotate([0,0,a]) {
                nema17();
                translate([ -50, 0, 0]) reducer();         // reducer inboard
                translate([ 22, 0, 4]) tensioner();         // tensioner outboard
            }
        }
    }
    // central shoulder mast carrying the J2 axis + first idler pack
    color([.7,.7,.7]) translate([0,0,6]) cylinder(h=70, d=46, $fn=64);
    translate([0,0,76]) rotate([90,0,0]) idler_stack(10);   // J2-axis idler pack (~10 runs)
}

turntable();
