// ============================================================
//  integrated_actuator.scad — frameless BLDC built INTO a cycloidal
//  reducer = one drive unit (cross-section / concept stack).
//
//  Maps the motor onto the cycloid's members:
//    rotor magnet ring  -> ECCENTRIC CARRIER (input, motor speed)
//    stator ring        -> FIXED to housing  (with the pin ring)
//    output plate       -> rides the big MOMENT BEARING (slow output)
//
//  The rotor spins CONCENTRIC on a main bearing (so the air gap stays
//  uniform); a separate ECCENTRIC crank on the rotor drives the disc(s),
//  which react against the fixed pin ring. Output rollers carry the slow
//  rotation out to the moment-bearing plate.
//
//  This is a CONCEPT cross-section to show the axial stack & radii — not a
//  printable part (magnetics, windings, bearings are stylized blocks).
//  Render the half-section with `section=true` (default) to read the stack.
//
//  Axis = Z. z=0 = output mounting face (bolts to downstream link).
//  Colors: housing=gray, stator=teal, rotor/magnets=indigo,
//          eccentric=red, disc=seagreen, pins=gold, output=orange,
//          bearings=steel, encoders=black.
// ============================================================

$fn = 120;

// ---- top-level dims (mm) — sized to the ~90 mm cycloid ring ----
OD        = 92;     // overall housing OD
ecc       = 1.6;    // cycloid eccentricity (disc orbit radius)
air_gap   = 0.6;    // stator<->magnet gap

// radii (from axis)
r_housing = OD/2;             // 46
r_pins    = 36;              // fixed pin-ring pitch radius
r_disc    = 34;              // cycloid disc OD-ish
r_magnet  = 30;              // rotor magnet ring radius (outrunner, big = torque)
r_stator  = r_magnet - air_gap - 4;  // stator OD just inside the magnets
r_outroll = 18;              // output-roller pitch radius
r_mainbrg = 12;              // rotor main bearing
r_bore    = 7;              // center through-bore (wiring / on-axis routing)

// axial heights (stacked from z=0 up)
h_outbrg  = 9;     // moment bearing + output plate zone
h_disc    = 8;     // cycloid disc plane
h_magnet  = 14;    // motor (magnet/stator) zone
h_back    = 6;     // back plate + encoder

eps = 0.02;
section = true;    // true = cut a half-section to expose the stack

// running z cursor
z_out  = 0;
z_disc = z_out  + h_outbrg;
z_mot  = z_disc + h_disc;
z_back = z_mot  + h_magnet;
H      = z_back + h_back;

module ring(r_out, r_in, h){ difference(){ cylinder(h=h, r=r_out);
    translate([0,0,-eps]) cylinder(h=h+2*eps, r=r_in); } }

// ------- STATIC side: housing cup + pin ring + stator + bearings -------
module housing(){
    color([.34,.34,.37]){
        ring(r_housing, r_housing-3, H);                 // outer wall
        translate([0,0,z_back]) ring(r_housing, r_bore, h_back); // back plate
        translate([0,0,z_mot]) ring(r_mainbrg+4, r_bore, h_magnet+h_back-eps); // center boss
    }
    // fixed PIN RING (gold pins around the disc plane)
    color("gold") translate([0,0,z_disc])
        for(i=[0:23]) rotate([0,0,i*360/24])
            translate([r_pins,0,0]) cylinder(h=h_disc, d=2.4, center=false);
    // STATOR ring (windings) bonded to a metal insert for heat path
    color([.55,.55,.6]) translate([0,0,z_mot]) ring(r_stator+1.5, r_stator-3, h_magnet); // metal insert
    color("teal")       translate([0,0,z_mot+1]) ring(r_stator, r_stator-2.5, h_magnet-2);
    // motor-side main bearing (rotor rides this — concentric)
    color("steelblue") translate([0,0,z_mot]) ring(r_mainbrg, r_mainbrg-3, h_magnet);
    // motor encoder (rotor position, FOC) on back plate, on-axis
    color([.1,.1,.1]) translate([0,0,z_back+h_back]) cylinder(h=2, d=10);
}

// ------- ROTOR: magnet ring (concentric) + eccentric crank -------
module rotor(){
    // magnet ring — CONCENTRIC about axis (uniform air gap)
    color([.30,.25,.55]) translate([0,0,z_mot+1]) ring(r_magnet, r_magnet-3, h_magnet-2);
    // rotor hub on the main bearing
    color([.45,.4,.6]) translate([0,0,z_mot]) ring(r_mainbrg+3.5, r_mainbrg, h_magnet);
    // rotor back disc tying magnet ring to hub
    color([.45,.4,.6]) translate([0,0,z_mot+h_magnet-2]) ring(r_magnet, r_mainbrg, 2);
    // ECCENTRIC crank — offset by `ecc`, reaches down into the disc plane
    color("red") translate([ecc,0,z_disc]) ring(10, 6.5, h_disc+ (z_mot - z_disc));
}

// ------- CYCLOID disc(s) — orbit on the eccentric, engage pin ring ----
module disc(){
    color("seagreen") translate([ecc,0,z_disc])
        difference(){
            cylinder(h=h_disc-1, r=r_disc);
            translate([0,0,-eps]) cylinder(h=h_disc, r=6.6);   // eccentric bearing bore
            // output-roller holes
            for(i=[0:5]) rotate([0,0,i*60]) translate([r_outroll,0,-eps])
                cylinder(h=h_disc+1, d=7);
            // lobe scallops (schematic) around the rim
            for(i=[0:23]) rotate([0,0,i*360/24+ (180/24)])
                translate([r_disc,0,-eps]) cylinder(h=h_disc+1, d=4.2);
        }
}

// ------- OUTPUT: rollers through disc -> output plate on moment bearing -
module output(){
    // output rollers (carry slow rotation out; absorb the orbit)
    color([.8,.5,.2]) translate([0,0,z_out+2])
        for(i=[0:5]) rotate([0,0,i*60]) translate([r_outroll,0,0])
            cylinder(h=z_disc-z_out+h_disc-2, d=6);
    // output plate (bolts to downstream link)
    color("orange") ring(r_pins+3, r_bore, h_outbrg-3);
    // big MOMENT bearing (crossed-roller / BB race) between output & housing
    color("steelblue") translate([0,0,z_out]) ring(r_housing-3.5, r_pins+4, h_outbrg);
    // output encoder magnet on the plate (sensor would be on housing)
    color([.1,.1,.1]) translate([r_bore+4,0,h_outbrg-3]) cylinder(h=1.5, d=8);
}

module actuator(){ housing(); rotor(); disc(); output(); }

module the_unit(){
    if(section)
        difference(){ actuator();
            translate([0,-OD,-1]) cube([OD,2*OD,H+2]); }  // cut +Y half away
    else actuator();
}

the_unit();

echo(str("integrated actuator: OD ", OD, " | height ", H,
         " mm | magnet r=", r_magnet, " | pins r=", r_pins,
         " | ecc=", ecc, " | bore Ø", 2*r_bore));
