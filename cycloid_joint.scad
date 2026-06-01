// ============================================================
//  cycloid_joint.scad — THE canonical joint. One parametric cycloidal
//  cartridge, instantiated 3x for the buildable trunk: J1, J2, J3.
//
//  Consolidates (and supersedes) the earlier split:
//    cycloidal_disc.scad  -> the validated cycloid profile math
//    joint_module.scad    -> double-eccentric cam + output flange
//    coaxial_joint.scad   -> clevis-free stator/rotor cartridge with the
//                            big crossed-roller bearing OUTBOARD of the
//                            gears (carries the cantilever / tipping moment)
//    base.scad            -> J1 is just this cartridge, axis vertical, with
//                            the output bearing sized up = the moment bearing
//
//  POWER PATH (every joint, identical):
//    NEMA17 --2:1 GT2 belt--> input shaft (on 2x 608)
//      --> double eccentric cam (2x journals, 180 deg) --> two cycloid discs
//        --> 6 output pins --> output flange (= bearing inner race)
//          --> big BB crossed-roller bearing --> magnet -> output encoder
//    Net ratio = belt(2) x lobes(N_pins-1).  Default N_pins=19 -> 36:1.
//
//  DRIVE STYLE: floating-roller cycloid (converged decision) — the ring
//  "pins" are nylon rollers free to spin; clearance sets backlash; SLA
//  bearing surfaces for finish. (No steel dowels required.)
//
//  Axis = Z. z=0 = output mounting face (bolts to the downstream link /
//  for J1 the table side). Motor sits behind (-Z). Open center bore = output
//  encoder magnet + cable pass-through.
//
//  This is a build-intent layout: profiles & seats are real; fillet /
//  lighten / add fasteners in slicer-ready CAD. Render one part or the
//  assembly via `part` + `which` below.
// ============================================================

$fn = 96;

// ---------- which joint + what to render ----------
which = "J2";          // "J1" | "J2" | "J3"
part  = "assembly";    // "assembly" | "disc" | "ring" | "cam" | "flange" | "stator"

// ---------- cycloid profile math (parametric) ----------
function _psi(t,N,R,E) = atan2( sin((1-N)*t), (R/(E*N)) - cos((1-N)*t) );
function _px(t,N,R,Rr,E) =  R*cos(t) - Rr*cos(t+_psi(t,N,R,E)) - E*cos(N*t);
function _py(t,N,R,Rr,E) = -R*sin(t) + Rr*sin(t+_psi(t,N,R,E)) + E*sin(N*t);
function disc_pts(N,R,Rr,E,steps=540) =
    [ for(i=[0:steps-1]) let(t=i*360/steps) [_px(t,N,R,Rr,E), _py(t,N,R,Rr,E)] ];

// ---------- joint presets ----------
//   N      pins (lobes=N-1=cyclo ratio)     R   pin-circle radius
//   Rr     roller radius                    E   eccentricity (< R/N !)
//   Tdisc  disc thickness                   raceR / ball_d / brgW  = output+moment bearing
//   nout/outbc/outpin = output-pin set      bore = center through-bore
//   belt   pre-stage ratio (lives in the GT2 belt / geared stepper)
function cfg(j) =
    j=="J1" ? [ "J1 base",     19, 44, 3.5, 1.8, 9, 62, 6, 12,  6, 26, 7,  30, 2 ] :
    j=="J3" ? [ "J3 elbow",    19, 32, 2.7, 1.3, 7, 44, 6, 9,   6, 18, 6,  22, 2 ] :
              [ "J2 shoulder", 19, 36, 3.0, 1.5, 8, 52, 6, 10,  6, 22, 6,  24, 2 ] ;
// accessors
function c_name(c)=c[0]; function c_N(c)=c[1];   function c_R(c)=c[2];
function c_Rr(c)=c[3];   function c_E(c)=c[4];    function c_T(c)=c[5];
function c_raceR(c)=c[6];function c_ball(c)=c[7];  function c_brgW(c)=c[8];
function c_nout(c)=c[9];  function c_outbc(c)=c[10];function c_outpin(c)=c[11];
function c_bore(c)=c[12]; function c_belt(c)=c[13];

WALL = 4; GAP = 0.5; EPS = 0.01;
NEMA = 42.3; NEMA_BC = 31;

// ---------- printable parts ----------
module cyc_disc(c) {
    R=c_R(c); N=c_N(c); Rr=c_Rr(c); E=c_E(c); T=c_T(c);
    bore_r = c_raceR(c)*0 + 12;                  // eccentric-cam bearing bore (6802-class)
    out_hole_r = c_outpin(c)/2 + E;              // oversized so the orbiting disc clears
    assert(E < R/N, "Invalid: E must be < R/N_pins");
    linear_extrude(height=T) difference() {
        polygon(disc_pts(N,R,Rr,E));
        circle(r=bore_r, $fn=96);
        for(a=[0:360/c_nout(c):359])
            translate([c_outbc(c)*cos(a), c_outbc(c)*sin(a)]) circle(r=out_hole_r, $fn=48);
    }
}

// fixed ring of floating nylon rollers (modeled as pin seats)
module pin_ring(c, h, flange=4) {
    R=c_R(c); Rr=c_Rr(c); N=c_N(c); E=c_E(c); Ro=R+Rr+WALL;
    difference() {
        cylinder(h=h+flange, r=Ro, $fn=220);
        translate([0,0,flange]) cylinder(h=h+1, r=R-Rr+E+0.4, $fn=220);   // disc cavity
        for(i=[0:N-1]) { a=i*360/N;
            translate([R*cos(a), R*sin(a), flange-1]) cylinder(h=h+2, r=Rr+0.15, $fn=40); }
    }
}

module double_eccentric_cam(c) {
    E=c_E(c); jr=15/2; jw=c_T(c); shaft=8;
    difference() {
        union() {
            translate([ E,0,0])        cylinder(h=jw, r=jr, $fn=96);
            translate([-E,0,jw+GAP])   cylinder(h=jw, r=jr, $fn=96);
            translate([-E,0,0])        cylinder(h=jw, r=jr-1, $fn=96);   // counterweights
            translate([ E,0,jw+GAP])   cylinder(h=jw, r=jr-1, $fn=96);
        }
        translate([0,0,-1]) cylinder(h=2*jw+GAP+2, d=shaft, $fn=64);     // input shaft bore
        translate([0,-shaft/2-2,jw]) rotate([90,0,0]) cylinder(h=6,d=3,$fn=24); // set screw
    }
}

module output_flange(c) {
    fd=2*c_outbc(c)+16; ft=6; pin_len=2*c_T(c)+GAP+4;
    difference() {
        union() {
            cylinder(h=ft, d=fd, $fn=160);
            for(a=[0:360/c_nout(c):359])
                translate([c_outbc(c)*cos(a), c_outbc(c)*sin(a), ft])
                    cylinder(h=pin_len, d=c_outpin(c), $fn=40);
        }
        translate([0,0,-EPS]) cylinder(h=2.6, d=6.2, $fn=48);            // encoder magnet
        for(a=[45:90:359]) translate([(fd/2-8)*cos(a),(fd/2-8)*sin(a),-1])
            cylinder(h=ft+2, d=3.2, $fn=24);                            // link bolts
    }
}

module ball_groove(c, z) {
    translate([0,0,z]) rotate_extrude($fn=220)
        translate([c_raceR(c),0,0]) circle(d=c_ball(c)+0.4, $fn=32);
}

// ---------- cartridge halves (bearing OUTBOARD of the gearset) ----------
module stator(c) {                 // fixed side: motor mount + pin ring + outer race
    raceR=c_raceR(c); Rh=raceR+c_ball(c)/2+WALL; Hg=c_T(c)*2+GAP+6; brgW=c_brgW(c);
    difference() {
        cylinder(h=WALL+Hg+brgW, r=Rh, $fn=240);
        translate([0,0,WALL]) cylinder(h=Hg+brgW+1, r=raceR-3, $fn=240);     // cavity
        translate([0,0,-EPS]) cylinder(h=WALL+2*EPS, d=10, $fn=48);          // input shaft
        for(a=[0:90:359]) translate([NEMA_BC/2*cos(a),NEMA_BC/2*sin(a),-EPS])
            cylinder(h=WALL+2*EPS, d=3.4, $fn=24);                           // motor bolts
        ball_groove(c, WALL+Hg+brgW/2);                                      // outer race half
    }
    translate([0,0,WALL]) pin_ring(c, c_T(c)*2+GAP+2);                       // fixed pin ring
}

module rotor(c) {                  // output side: bearing inner + bolt face + encoder
    raceR=c_raceR(c); Hg=c_T(c)*2+GAP+6; brgW=c_brgW(c);
    difference() {
        union() {
            cylinder(h=Hg+brgW, r=raceR-3.2, $fn=240);
            translate([0,0,Hg+brgW]) cylinder(h=WALL, r=raceR-3.2, $fn=240);
        }
        translate([0,0,-EPS]) cylinder(h=Hg+brgW+WALL+1, d=c_bore(c), $fn=120); // through-bore
        ball_groove(c, Hg+brgW/2 - WALL);                                    // inner race half
        for(a=[0:60:359]) translate([(raceR-12)*cos(a),(raceR-12)*sin(a),Hg+brgW])
            cylinder(h=WALL+EPS, d=3.4, $fn=24);                             // link bolts
        translate([0,0,Hg+brgW+WALL-2.6]) cylinder(h=2.7, d=6.2, $fn=48);    // magnet pocket
    }
}

// ---------- assembly preview ----------
module joint_assembly(c) {
    Hg=c_T(c)*2+GAP+6;
    color("dimgray")   stator(c);
    color([.3,.3,.32]) translate([0,0,WALL+Hg+c_brgW(c)+WALL]) rotor(c);     // (lifted to show stack)
    color("steelblue") translate([0,0,WALL+2]) double_eccentric_cam(c);
    color("orange")    translate([ c_E(c),0,WALL+2.5]) cyc_disc(c);
    color("seagreen")  translate([-c_E(c),0,WALL+2.5+c_T(c)+GAP]) rotate([0,0,180]) cyc_disc(c);
    color([.18,.18,.2]) translate([0,0,-NEMA/2]) cube([NEMA,NEMA,NEMA*0+38],center=false); // motor (schematic)
    // bearing race ring (visual)
    color("silver") translate([0,0,WALL+Hg]) difference(){
        cylinder(h=c_brgW(c), r=c_raceR(c)+c_ball(c)/2+1, $fn=160);
        translate([0,0,-1]) cylinder(h=c_brgW(c)+2, r=c_raceR(c)-3, $fn=160); }
}

// ---------- render select ----------
C = cfg(which);
if      (part=="disc")   cyc_disc(C);
else if (part=="ring")   pin_ring(C, c_T(C)*2+GAP+2);
else if (part=="cam")    double_eccentric_cam(C);
else if (part=="flange") output_flange(C);
else if (part=="stator") stator(C);
else                     joint_assembly(C);

echo(str(c_name(C), ": cyclo ", c_N(C)-1, ":1 x belt ", c_belt(C),
         " = ", (c_N(C)-1)*c_belt(C), ":1 | bearing ~",
         2*(c_raceR(C)+c_ball(C)/2), " mm | ring OD ~", 2*(c_R(C)+c_Rr(C)+WALL), " mm"));
