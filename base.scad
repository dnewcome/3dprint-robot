// ============================================================
//  base.scad — J1 base: moment-bearing carrier + internal-ring drive
//
//  J1 is a VERTICAL axis → gravity makes no torque about it (only a
//  tipping moment, carried by the bearing). So the drive can be a simple
//  single-stage internal ring + onboard pinion (~4:1); the real work is
//  the big moment bearing.
//
//  Stack:
//    [fixed base plate] holds: BB crossed-roller OUTER race + FIXED
//      internal ring gear + bolts to table.
//    [TURNTABLE] rides the bearing (inner race), carries an ONBOARD
//      stepper whose pinion meshes the fixed ring → turntable rotates.
//      Deck on top carries the shoulder (J2) + J3 motor.
//    Open center bore → slip ring / cable pass-through.
//
//  Gear teeth are SCHEMATIC (trapezoidal) — use a gear library for the
//  final involute profiles. Bearing = airsoft-BB race (Proto-1 part).
// ============================================================

$fn = 120;

// ---- bearing (carries the whole arm's tipping moment) ----
Rbb   = 55;       // ball pitch radius → ~122 mm bearing
ball  = 6;        // airsoft BB
brg_w = 12;

// ---- J1 drive: fixed internal ring + onboard pinion ----
gm    = 1.5;      // module
Nring = 72;       // internal ring teeth  (PD = 108)
Npin  = 18;       // pinion teeth         (PD = 27)  → ratio = 4:1
PDr   = gm*Nring; PDp = gm*Npin;
CD    = (PDr-PDp)/2;     // internal-mesh center distance = 40.5

// ---- structure ----
deck_d   = 150;
bore_d   = 26;    // center pass-through (slip ring / cables)
wall     = 5;
nema     = 42.3; nema_bolt = 31;
eps=0.01;

module ball_groove(z) {
    translate([0,0,z]) rotate_extrude($fn=200)
        translate([Rbb,0,0]) circle(d=ball+0.4, $fn=28);
}

// simple internal ring gear (teeth point inward), fixed to base
module internal_ring(teeth=Nring, m=gm, h=10) {
    PR=m*teeth/2; Ra=PR-m; Rd=PR+1.25*m; tb=360/teeth*0.30; tt=360/teeth*0.16;
    difference(){ cylinder(h=h,r=Rd+wall,$fn=240); cylinder(h=h+1,r=Rd,$fn=240); }
    for(i=[0:teeth-1]) rotate([0,0,i*360/teeth]) linear_extrude(h)
        polygon([[Rd*cos(tb),Rd*sin(tb)],[Ra*cos(tt),Ra*sin(tt)],
                 [Ra*cos(-tt),Ra*sin(-tt)],[Rd*cos(-tb),Rd*sin(-tb)]]);
}

// simple external pinion
module pinion(teeth=Npin, m=gm, h=10) {
    PR=m*teeth/2; Ra=PR+m; Rd=PR-1.25*m; tb=360/teeth*0.30; tt=360/teeth*0.20;
    union(){
        cylinder(h=h,r=Rd,$fn=120);
        for(i=[0:teeth-1]) rotate([0,0,i*360/teeth]) linear_extrude(h)
            polygon([[Rd*cos(tb),Rd*sin(tb)],[Ra*cos(tt),Ra*sin(tt)],
                     [Ra*cos(-tt),Ra*sin(-tt)],[Rd*cos(-tb),Rd*sin(-tb)]]);
    }
}

// ---- fixed base: plate + bearing outer race + fixed ring gear ----
module base_fixed() {
    difference() {
        union() {
            cylinder(h=wall, r=Rbb+ball+wall);                 // foot plate
            translate([0,0,wall]) internal_ring();             // fixed ring gear (inner)
            translate([0,0,wall]) cylinder(h=brg_w, r=Rbb+ball+wall); // outer race wall
        }
        ball_groove(wall+brg_w/2);                             // outer half of race
        translate([0,0,-eps]) cylinder(h=wall+brg_w+1, d=bore_d); // center bore
        // table mounting bolts
        for(a=[0:60:359]) translate([(Rbb+ball+wall-6)*cos(a),(Rbb+ball+wall-6)*sin(a),-eps])
            cylinder(h=wall+2, d=5);
    }
}

// ---- turntable: rides bearing, onboard stepper + pinion, deck on top ----
module turntable() {
    difference() {
        union() {
            translate([0,0,wall+brg_w]) cylinder(h=wall, d=deck_d);   // deck
            translate([0,0,wall]) cylinder(h=brg_w, r=Rbb-2);          // inner race body
        }
        ball_groove(wall+brg_w/2);                              // inner half of race
        translate([0,0,-eps]) cylinder(h=brg_w+2*wall+1, d=bore_d);   // center bore
        // onboard NEMA17 mount (pinion drops down to mesh the ring at radius CD)
        translate([CD,0,wall+brg_w]) {
            cylinder(h=wall+1, d=24);                            // pilot
            for(x=[-1,1],y=[-1,1]) translate([x*nema_bolt/2,y*nema_bolt/2,0])
                cylinder(h=wall+1,d=3.4);
        }
        // shoulder (J2) mount bolt circle on the deck
        for(a=[0:90:359]) translate([45*cos(a),45*sin(a),wall+brg_w])
            cylinder(h=wall+1,d=4.2);
    }
}

// ---- assembly ----
module assembly() {
    color("dimgray")   base_fixed();
    color("gainsboro") turntable();
    color("steelblue") translate([CD,0,wall+1]) pinion();       // meshes fixed ring
    color([.3,.3,.3])  translate([CD,0,wall+brg_w+wall]) cube([nema,nema,40],center=true); // stepper
}

assembly();
// base_fixed();
// turntable();
echo(str("J1 reduction = ", Nring/Npin, ":1  | bearing ~", 2*(Rbb+ball/2), " mm | pinion @ r=", CD));
