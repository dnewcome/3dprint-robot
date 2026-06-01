// ============================================================
//  wrist_differential.scad — cable-driven BEVEL differential wrist
//
//  A car-differential repurposed: two SIDE bevels on the pitch axis are
//  the INPUTS (each driven by a capstan cord on its back pulley); the
//  PINION bevel on the roll/tool axis is the ROLL output; the YOKE
//  (carrier) pivoting on the pitch axis is the PITCH output.
//
//    cordA → side bevel A ┐
//                         ├ pinion (roll/tool) — meshes both sides
//    cordB → side bevel B ┘
//    yoke = pitch
//      A,B same dir → ROLL ;  A,B opposite → PITCH   (bidirectional both)
//
//  Bevels here are SMOOTH 45° miter cones (schematic). Generate real
//  bevel teeth with a gear library — params in wrist_differential_spec.md.
// ============================================================

$fn = 48;

m   = 1.5;   // gear module
Nt  = 20;    // teeth per miter (all equal → 1:1 symmetric diff)
PD  = m*Nt;  // pitch dia = 30
fw  = 6;     // face width
S   = PD/2 + 2;   // side-gear offset from center along pitch axis
pulley_d = 50;    // capstan cord pulley on each side bevel back
tool_len = 30;

// 45° miter as a truncated cone (large end = mesh end, toward center)
module miter() { cylinder(h=fw, r1=PD/2, r2=PD/2-fw); }

module side_bevel() {           // bevel + back cord pulley + bore
    color("seagreen") rotate([0,-90,0]) miter();        // large end toward +X(center)
    color("orange") translate([-fw-6,0,0]) rotate([0,90,0]) {  // cord pulley outboard
        difference(){
            cylinder(h=8, d=pulley_d);
            translate([0,0,4]) rotate_extrude() translate([pulley_d/2,0]) circle(d=1.4);
        }
    }
}

module pinion() {               // roll output + tool stub
    color("steelblue") miter();
    color("dimgray") translate([0,0,fw]) cylinder(h=tool_len, d=10);
    color([.4,.4,.45]) translate([0,0,fw+tool_len]) cylinder(h=4, d=26); // tool flange
}

module yoke() {                 // carrier: fork on pitch axis holds pinion
    color("gainsboro") {
        for (s=[-1,1]) translate([s*(S+4),0,0]) rotate([0,90,0])
            cylinder(h=4, d=22);                 // pitch-axis pivot hubs
        translate([-S-4,0,-PD/2-6]) cube([2*(S+4), 14, 8], center=false); // yoke base
    }
}

module wrist_differential() {
    translate([-S,0,0]) side_bevel();            // side A
    translate([ S,0,0]) mirror([1,0,0]) side_bevel();   // side B
    pinion();                                    // roll/tool, meshing both
    yoke();
}

wrist_differential();
