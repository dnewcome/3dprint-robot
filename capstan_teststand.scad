// ============================================================
//  capstan_teststand.scad — REMOTE capstan drive test rig
//
//  Proves the core arm assumption: can Dyneema routed OVER IDLERS
//  transmit capstan force to a remote driven pulley with ~zero
//  backlash? Baseline = idlers removed, drum adjacent to pulley
//  ("normal" capstan). Compare the two.
//
//  Layout on one baseplate (all axes vertical, cable in a horizontal
//  plane just above the plate):
//    [NEMA17 under plate → helical capstan DRUM] --cable-- over
//    [2 IDLER bearings] --cable-- [DRIVEN PULLEY + encoder + load arm]
//
//  Cable: Dyneema DM20, anchored to the drum (no slip), 2 runs out to
//  the pulley (pull-pull). One run ends on a tensioner.
//
//  Render parts individually to print; layout() to check fit.
// ============================================================

$fn = 64;

// ---- cable / drive ----
cd       = 1.0;     // Dyneema dia
drum_r   = 8;       // capstan drum radius
groove_p = 1.3;     // helical groove pitch (≈ cd + clearance)
turns    = 8;
pulley_r = 48;      // driven pulley radius  → ratio = pulley_r/drum_r = 6:1

// ---- hardware ----
nema      = 42.3; nema_bolt = 31.0; nema_pilot = 24;
idler_od  = 22; idler_bore = 8;   // 608 idler, DOUBLE-SUPPORTED shaft (high side load)
idler_w   = 7;                    // 608 width
pulley_brg = 22;                  // 608 for the driven shaft
mag_d     = 6.2;

// ---- baseplate ----
bp = [300, 140, 6];
foot_h = 50;                      // standoff so NEMA17 hangs below
eps=0.01;

// positions (x along plate)
DRUM_X = 45;  PUL_X = 255;  IDL_X = 185;  CY = bp[1]/2;

// ---------- helical-groove capstan drum ----------
module capstan_drum() {
    h = turns*groove_p + 6;
    difference() {
        union() {
            cylinder(h=h, r=drum_r);
            cylinder(h=2.5, r=drum_r+3);              // bottom flange
            translate([0,0,h-2.5]) cylinder(h=2.5, r=drum_r+3); // top flange
        }
        // helical groove (carved by spheres along a helix)
        sps = turns*48;
        for (i=[0:sps]) {
            a = i*360/48;  z = 3 + i*groove_p/48;
            rotate([0,0,a]) translate([drum_r, 0, z]) sphere(d=cd+0.4);
        }
        translate([0,0,-eps]) cylinder(h=h+1, d=5.2);  // motor shaft bore
        translate([drum_r-2,0,3]) rotate([0,90,0]) cylinder(h=4,d=2.2); // anchor hole (mid)
        translate([0,-6,3]) rotate([90,0,0]) cylinder(h=12,d=3.2);      // M3 grub to shaft
    }
}

// ---------- driven pulley: groove + 2 anchors + magnet + load arm ----------
module driven_pulley() {
    h = 14;
    difference() {
        union() {
            cylinder(h=h, r=pulley_r);
            translate([0,0,h]) cylinder(h=4, r=12);            // hub for magnet/shaft
            translate([0,-6,0]) cube([pulley_r+60, 12, 6]);    // load arm
        }
        translate([0,0,5]) rotate_extrude() translate([pulley_r,0]) circle(d=cd+0.4); // groove
        for (s=[-1,1]) translate([0, s*4, 5]) rotate([0,90,0])
            cylinder(h=pulley_r+1, d=2.2);                     // 2 anchor channels
        translate([0,0,-eps]) cylinder(h=h+5, d=8.2);          // shaft bore
        translate([0,0,h+4-2.7]) cylinder(h=2.8, d=mag_d);     // magnet pocket (top)
        translate([pulley_r+52,0,-eps]) cylinder(h=8, d=5);    // weight-hang hole on arm
    }
}

// ---------- bearing post for the driven shaft ----------
module pulley_post() {
    difference() {
        union() {
            cylinder(h=40, d=pulley_brg+10);
            translate([-15,-15,0]) cube([30,30,6]);            // foot
        }
        translate([0,0,40-7]) cylinder(h=7+eps, d=pulley_brg); // top 608 seat
        translate([0,0,-eps]) cylinder(h=7, d=pulley_brg);     // bottom 608 seat
        translate([0,0,-eps]) cylinder(h=42, d=9);             // shaft clearance
        for (x=[-1,1],y=[-1,1]) translate([x*11,y*11,-eps]) cylinder(h=8,d=3.4);
    }
}

// ---------- idler: 608 in a CLEVIS (shaft in double shear) ----------
// High side load (2·T·sin(θ/2), up to ~370N @ 90°) → no cantilever.
module idler_post() {
    gap   = idler_w + 2;                 // space for the 608
    armt  = 5;
    shZ   = 8 + idler_od/2 + 2;          // shaft-center height
    color("orange") difference() {
        union() {
            translate([-20,-16,0]) cube([40,32,6]);            // slotted base
            for (s=[-1,1])
                translate([-7, s*(gap/2+armt/2)-armt/2, 6])
                    cube([14, armt, shZ]);                     // two arms
        }
        translate([0,-20,shZ]) rotate([-90,0,0])
            cylinder(h=40, d=8.2);                             // shaft, both arms
        // X slots to set position / turn angle on the plate
        for (y=[-9,9]) hull() {
            translate([-12,y,-eps]) cylinder(h=8,d=3.6);
            translate([ 12,y,-eps]) cylinder(h=8,d=3.6);
        }
    }
}

module baseplate() {
    difference() {
        cube(bp);
        // motor pilot + bolt pattern (NEMA17 hangs below)
        translate([DRUM_X, CY, -eps]) {
            cylinder(h=bp[2]+1, d=nema_pilot);
            for (x=[-1,1],y=[-1,1]) translate([x*nema_bolt/2,y*nema_bolt/2,0])
                cylinder(h=bp[2]+1, d=3.4);
        }
        // pulley post bolts
        translate([PUL_X, CY, -eps]) for (x=[-1,1],y=[-1,1])
            translate([x*11,y*11,0]) cylinder(h=bp[2]+1, d=3.4);
        // idler adjustment SLOTS (route/space the two runs)
        for (y=[CY-30, CY+30]) hull() {
            translate([IDL_X-25, y, -eps]) cylinder(h=bp[2]+1, d=3.6);
            translate([IDL_X+25, y, -eps]) cylinder(h=bp[2]+1, d=3.6);
        }
    }
    // standoff feet
    for (x=[12,bp[0]-12],y=[12,bp[1]-12])
        translate([x,y,-foot_h]) cylinder(h=foot_h, d=14);
}

// ---------- assembled layout (visual check) ----------
module layout() {
    color("gainsboro") baseplate();
    color("dimgray")  translate([DRUM_X,CY,-40]) cube([nema,nema,40],center=true); // motor (below)
    color("steelblue") translate([DRUM_X,CY,bp[2]]) capstan_drum();
    color("seagreen")  translate([PUL_X,CY,bp[2]]) { driven_pulley(); }
    color([.6,.6,.6])  translate([PUL_X,CY,bp[2]]) pulley_post();
    for (y=[CY-30,CY+30]) translate([IDL_X,y,bp[2]]) idler_post();
}

// ---- render one ----
layout();
// capstan_drum();
// driven_pulley();
// pulley_post();
// idler_post();
// baseplate();
