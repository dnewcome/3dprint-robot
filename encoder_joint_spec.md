# Integrated joint encoder — spec (output-side, absolute)

Goal: true joint angle, fully built-in, no purchased rotary encoder.
A diametric magnet on the **output** shaft end + a magnetic-encoder IC
on a small PCB fixed to the **non-rotating** housing, ~1–2 mm away.

## Two-tier plan
| Tier | IC | Bits | Bus | Use |
|------|----|------|-----|-----|
| Prototype | **AS5600** | 12 (4096) | I²C @0x36 | dead simple, $3 breakout, great libraries |
| Production | **MT6701** | 14 (16384) | SSI/SPI or I²C | higher res + speed, same magnet |

Start with AS5600 on Proto 2; the magnet & mechanical mount are
identical, so swapping to MT6701 later is drop-in.

## Magnet (the part that matters most)
- **Diametrically magnetized** cylinder, **6 mm Ø × 2.5 mm**, N35+.
- Mounted **on the rotation axis**, on the very end of the output shaft.
- Air gap to IC face: **0.5–2 mm** (aim ~1.5 mm).
- Lateral centering: **±0.25 mm** — runout shows up directly as angle error.
- Holder must be **non-ferrous** (brass/alu/plastic). Keep steel screws,
  the output bearing, and the dowel pins **≥ ~8 mm away** or they skew
  the field. This is the #1 cause of bad readings — design the magnet
  boss to stick out past any steel.

## AS5600 (SOP-8) wiring — prototype
| Pin | Name | Connect |
|-----|------|---------|
| 1 | VDD3V3 | 3.3 V (add 100 nF) |
| 2 | VDD5V  | 5 V if 5 V supply (internal LDO), else tie to VDD3V3 |
| 3 | OUT    | leave NC (using I²C) |
| 4 | GND    | GND |
| 5 | DIR    | GND = one count direction (tie high to flip) |
| 6 | SCL    | I²C clock (4.7 kΩ pull-up) |
| 7 | SDA    | I²C data  (4.7 kΩ pull-up) |
| 8 | PGO    | NC (factory-prog only) |

- I²C address is fixed **0x36** → only ONE AS5600 per bus. For 6 joints
  use an **I²C mux (TCA9548A)** or one MCU per joint on a CAN/serial bus.
- Read `RAW ANGLE` (0x0C/0x0D) for unfiltered absolute position.

## MT6701 — production
- 14-bit absolute, supports **SSI (3-wire: CSN/CLK/DO)**, I²C, ABZ, PWM.
- Prefer **SSI/SPI** for the arm: no address clash, daisy-chain-able,
  fast enough for closed-loop later.
- 3.3 V logic. Same 6×2.5 mm diametric magnet, same ~1.5 mm gap.
- Verify exact SOP-8 pin numbers against the MT6701QT datasheet before
  laying out the PCB (pinout differs from AS5600).

## Dual-encoder forward-compat
Add a second identical magnet boss on the **motor shaft** end of each
module (don't populate the IC yet). Output-side = absolute joint angle
for homing/accuracy; motor-side = commutation/anti-stall when you go
closed-loop. ~$2 of board + magnet now saves a redesign later.

## Homing bonus
Absolute output-side encoders mean **no limit switches**: power on and
every joint angle is already known. Store a one-time per-joint zero
offset in config.
