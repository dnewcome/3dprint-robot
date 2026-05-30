// ============================================================
//  harmonic_ring.scad — FLAT (pancake) strain-wave drive whose two
//  rigid rings are built one-per-arm-link.
//
//  Topology (this is what makes "one side per link" work):
//    Stationary Circular Spline  CS = N+2 teeth  -> built into LINK N
//    Dynamic   Circular Spline   DS = N   teeth  -> built into LINK N+1 (OUTPUT)
//    Flexspline (thin toothed ring, N teeth)  + Wave generator (oval)
//        = the slot-in cartridge between the two links.
//
//    Reduction = N / 2.   Here N=36 -> 18:1, x 2:1 belt = 36:1.
//
//  The CS module here REPLACES pin_ring_bores() in arm_link.scad's cup.
//  The DS is the same module with `teeth=N` printed into the next link.
//
//  HONEST CAVEATS (see harmonic_drive_spec.md):
//   * the flexspline is the wear/fatigue part — print in PP or TPU/nylon,
//     thin wall, expect limited life vs the cycloidal version.
//   * CS and DS must stay CONCENTRIC + axially aligned across the
//     slot-together joint -> the inter-link register spigot is critical.
// ============================================================

// ---- gear params ----
N      = 36;     // flexspline teeth (= DS teeth). CS = N+2.
m      = 2.0;    // module (mm/tooth). 2.0 prints well on a 0.4 nozzle.
H      = 8;      // ring axial height (each circular spline)
ring_wall = 6;   // rigid wall outside the root circle

// ---- simplified internal tooth (rounded trapezoid, points inward) ----
// Real strain-wave profiles are special; a trapezoid is fine for a
// printed skeleton because many teeth engage and average the error.
module internal_ring_gear(teeth, mod=m, h=H, wall=ring_wall) {
    PR = mod*teeth/2;            // pitch radius
    Ra = PR - mod;              // tip radius (inward)
    Rd = PR + 1.25*mod;         // root radius
    Ro = Rd + wall;             // outer radius of ring body
    tb = 360/teeth * 0.30;      // tooth base half-angle
    tt = 360/teeth * 0.16;      // tooth tip  half-angle
    difference() {
        cylinder(h=h, r=Ro, $fn=260);
        cylinder(h=h+0.1, r=Rd, $fn=260);        // bore to root circle
    }
    // teeth protruding inward from Rd to Ra
    for (i=[0:teeth-1]) rotate([0,0,i*360/teeth])
        linear_extrude(height=h)
            polygon([[Rd*cos(tb), Rd*sin(tb)],
                     [Ra*cos(tt), Ra*sin(tt)],
                     [Ra*cos(-tt),Ra*sin(-tt)],
                     [Rd*cos(-tb),Rd*sin(-tb)]]);
}

// ---- flexspline: thin ring with EXTERNAL teeth (N), bore = wave gen ----
module flexspline(teeth=N, mod=m, h=H, wall_t=1.5) {
    PR = mod*teeth/2;
    Ra = PR + mod;              // tip radius (outward)
    Rd = PR - 1.25*mod;         // root radius
    bore = Rd - wall_t;         // thin flexible wall
    tb = 360/teeth * 0.30;
    tt = 360/teeth * 0.16;
    difference() {
        union() {
            cylinder(h=h, r=Rd, $fn=240);
            for (i=[0:teeth-1]) rotate([0,0,i*360/teeth])
                linear_extrude(height=h)
                    polygon([[Rd*cos(tb), Rd*sin(tb)],
                             [Ra*cos(tt), Ra*sin(tt)],
                             [Ra*cos(-tt),Ra*sin(-tt)],
                             [Rd*cos(-tb),Rd*sin(-tb)]]);
        }
        cylinder(h=h+0.1, r=bore, $fn=240);
    }
}

// ---- wave generator: oval that ovalizes the flexspline ----
// Roller type: oval carrier + 2 ball bearings ride the flexspline bore.
// (A printed oval on a greased/PTFE-lined bore also works; rollers cut
//  friction.) delta = radial deflection ~ 0.9*m.
module wave_generator(teeth=N, mod=m, h=H, delta=1.8, shaft_d=8) {
    PR = mod*teeth/2;
    rb = PR - 1.25*mod - 1.5;   // nominal flexspline bore radius
    scale([(rb+delta)/rb, (rb-delta)/rb, 1])   // make it oval
        difference() {
            cylinder(h=h, r=rb, $fn=160);
            cylinder(h=h+0.1, r=12, $fn=96);    // hollow
        }
    // input hub
    difference() {
        cylinder(h=h, r=12, $fn=96);
        cylinder(h=h+0.1, d=shaft_d, $fn=48);  // bore to input shaft
    }
}

// ---- assembly preview: CS (fixed) + DS (output) + flexspline + WG ----
module demo() {
    color("steelblue") internal_ring_gear(N+2);                 // CS, link N
    color("seagreen")  translate([0,0,H+0.5]) internal_ring_gear(N); // DS, link N+1
    color("orange")    translate([0,0,0]) flexspline();         // spans both rings
    color("dimgray")   wave_generator();
}

// ---- render one ----
internal_ring_gear(N+2);     // STATIONARY circular spline (built into housing link)
// internal_ring_gear(N);    // DYNAMIC circular spline (built into output link)
// flexspline();
// wave_generator();
// demo();
