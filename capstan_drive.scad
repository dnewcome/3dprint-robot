// ============================================================
//  capstan_drive.scad — remote 2-stage capstan reduction (WAM-style)
//
//  Motors live on the J1 turntable; cables route out to the bend
//  joints (J2/J3/J5). Each joint = output SECTOR on the same big
//  crossed-roller bearing + encoder. Reduction is two cable stages.
//
//    motor ─ grooved DRUM (r=10) ──cable 6:1──► STAGE-1 PULLEY (R=60)
//                                                 │ shares shaft with
//                                              STAGE-2 DRUM (r=10)
//                                                 │ cable routed over
//                                                 │ idlers to the joint
//                                                 ▼
//                                       OUTPUT SECTOR (R=60) 6:1 = 36:1
//
//  Cable: 1mm 7x19 stainless, ANCHORED both ends (zero slip).
//  Groove pitch = cable dia; drum r=10 ≈ 10x cable dia -> finite cable
//  life (treat cable as a consumable, or use Dyneema for tighter bends).
//
//  SKELETON: grooves shown as flanged drums (cut the real helical groove
//  in CAD); cable paths are not drawn. Bearing/encoder reuse the
//  coaxial_joint cartridge.
// ============================================================

cable_d = 1.0;
r_drum  = 10;     // capstan drum radius (both stages)
R_pull  = 60;     // stage-1 pulley radius
R_sect  = 60;     // output sector radius  -> 6:1 x 6:1 = 36:1
sect_sweep = 270; // sector arc (deg) -> ~±135 deg travel
brg_OD  = 104;    // crossed-roller output bearing (Proto 1 race)
wall=4; eps=0.01;

// grooved capstan drum (flanged; cut helical groove pitch=cable_d in CAD)
module grooved_drum(r=r_drum, turns=12) {
    h = turns*cable_d + 3;
    fl = 2;                                  // flange
    color("dimgray") {
        cylinder(h=h, r=r, $fn=64);
        cylinder(h=fl, r=r+2.5, $fn=64);                 // bottom flange
        translate([0,0,h-fl]) cylinder(h=fl, r=r+2.5, $fn=64);
    }
}

// stage-1 pulley sharing a shaft with the stage-2 drum
module reduction_block() {
    color("steelblue") difference() {
        cylinder(h=10, r=R_pull, $fn=160);               // stage-1 pulley
        translate([0,0,-eps]) cylinder(h=12, d=8, $fn=48);
        // rim cable groove (single wrap + 2 anchor holes)
        translate([0,0,5]) rotate_extrude($fn=200)
            translate([R_pull,0,0]) circle(d=cable_d+0.4,$fn=20);
    }
    translate([0,0,10]) grooved_drum();                  // stage-2 drum on top
}

// output sector: partial pulley on the joint's big bearing
module output_sector() {
    color("seagreen") difference() {
        union() {
            // sector arc
            rotate_extrude(angle=sect_sweep, $fn=200)
                translate([R_sect-6,0,0]) square([6,12]);
            cylinder(h=12, d=brg_OD-6, $fn=160);          // hub -> bearing inner
        }
        translate([0,0,-eps]) cylinder(h=14, d=24, $fn=96);   // open center
        // rim groove for the cable + anchor pockets at the ends
        translate([0,0,6]) rotate_extrude(angle=sect_sweep,$fn=200)
            translate([R_sect-3,0,0]) circle(d=cable_d+0.4,$fn=20);
        // magnet pocket on hub face (output-side encoder)
        translate([0,0,12-2.6]) cylinder(h=2.7,d=6.2,$fn=48);
    }
}

// routing idler (concentric with an intervening joint axis -> decouples
// length change into a known coupling term)
module idler(R=18) {
    color("orange") difference() {
        cylinder(h=10, r=R, $fn=96);
        translate([0,0,5]) rotate_extrude($fn=160)
            translate([R,0,0]) circle(d=cable_d+0.6,$fn=20);
        translate([0,0,-eps]) cylinder(h=12,d=8,$fn=48);
    }
}

// ---- demo: one joint's two stages (cables omitted) ----
module demo() {
    translate([0,0,0]) grooved_drum(turns=14);     // motor drum (stage 1 in)
    translate([90,0,0]) reduction_block();          // stage-1 pulley + stage-2 drum
    translate([260,0,0]) output_sector();           // at the joint
    translate([175,40,0]) idler();                  // routing over a joint axis
}

// ---- render one ----
output_sector();
// reduction_block();
// grooved_drum();
// demo();
