# build123d / OCP CAD Notes

Hard-won, reusable lessons from building the integrated-actuator parts in
build123d (OCC kernel). Read this before fighting the geometry — most of the
pain here came from a handful of OCC quirks that have clean workarounds.

The interpreter that has `build123d` + `ocp_vscode` is **pyenv 3.12.9**, not the
system `python3`. Run everything with it:

```bash
/home/dan/.pyenv/versions/3.12.9/bin/python <script>.py
# or just `make ...` — the Makefile's python3 resolves to the pyenv shim
```

---

## 1. Live preview — OCP CAD Viewer in VSCode

The OCP CAD Viewer renders build123d **BREP solids directly** (its own
tessellation), over a local port (default **3939**) in a VSCode webview — so it
works without a special display, unlike the MuJoCo `launch_passive` viewer.

- Install: `pip install ocp_vscode` **into pyenv 3.12.9**, plus the "OCP CAD
  Viewer" VSCode extension (bernhard-42).
- Set the VSCode interpreter to 3.12.9 (Ctrl-Shift-P → *Python: Select
  Interpreter*) so the extension and your scripts agree. `.vscode/` is
  gitignored (its interpreter path is user-specific).

**`preview.py`** wraps `show()` so it's a no-op when `ocp_vscode` isn't installed
(keeps `make`/CI headless-safe):

```python
from preview import show
if __name__ == "__main__":
    show(part())                       # one part
    # show(a, b, names=["body","plate"])  # multiple, toggle-able
```

`arm_assembly.py --show` renders the whole arm. The "viewer is just showing the
logo" state simply means no `show()` has connected yet; it clears on the first
push to 3939.

**Camera "stuck" after a reload** is `reset_camera=KEEP` — the geometry *did*
update; hit the viewer's resize/fit button once.

---

## 2. Live reload — `make watch`

`watch.py` re-runs a part on every save so its `show()` refreshes the viewer:

```bash
make watch                          # default: angle_mount.py
make watch PART=arm_section.py
make watch PART="arm_assembly.py --show"
```

Two watchdog gotchas, both fixed in `watch.py` — note them if you write another
watcher:

1. **Editors save atomically** (write temp + rename), which arrives as
   `created`/`moved`, *not* `modified`. Listening only for `on_modified` misses
   real saves. → handle `on_any_event`.
2. But `on_any_event` also fires `opened` / `closed_no_write` — and **running
   the part opens its own `.py` to read it**, so reacting to those re-runs
   forever (an infinite loop with no input). → react only to write events
   (`created`/`modified`/`moved`), and set the debounce timestamp **after** the
   build finishes (the build is slow enough that events queued during it would
   otherwise re-fire).

---

## 3. Reading imported geometry instead of hardcoding

The vendor parts come in as exact BREP. Query them rather than guessing numbers:

```python
from build123d import GeomType, Axis
cyl = [f for f in solid.faces() if f.geom_type == GeomType.CYLINDER]
f.radius                       # cylinder radius
f.axis_of_rotation             # true axis: .position (origin) + .direction
f.area                         # spot degenerate/sliver faces
solid.bounding_box().max.Z     # real extents (don't trust a constant that drifted)
solid.is_valid                 # PROPERTY, not a method
solid.center(CenterOf.MASS)    # not `.center_of_mass`
```

This is how we found the micro housing's real **inner bore = r18.5 (d37)**, not
the `BORE=17` a constant claimed — and the **OD = r21**, **height 18.2**.

---

## 4. OCC boolean traps (these cost the most time)

### Coincident-face cuts hang OCC — forever
Cutting a cylinder whose radius **exactly matches an existing cylindrical face**
produces coincident/tangent surfaces the boolean engine churns on indefinitely.
Cutting the housing bore at exactly `r18.5` (its real wall) never returns.

> **Rule:** keep cutters off existing faces. To open the bore we cut **r18.0**
> — a deliberate 0.5 mm margin inside the r18.5 wall. `r18.4` also works but
> 0.1 mm near-coincidence is fragile; give it real clearance.

Quick way to spot a hang vs. slowness: a coincident cut doesn't *slow down*, it
**never finishes** — kill it and look for a cutter dimension equal to a measured
face.

### Diff order matters — cut sub-parts *before* unioning
Cutting the bore out of the **whole** assembly (`body + web + base`) slices
through the vendor housing's **internal cycloidal teeth**. Do the relief/bore
cut on the **web alone**, *then* union the body in, so the imported internals are
preserved:

```python
web -= Pos(0,0, body_top/2) * Cylinder(18.0, body_top+8)   # web only
out = body + web + base                                     # teeth intact
```

### A clean union needs real volume overlap
Two solids that merely touch at a tangent line (zero-area contact) won't fuse
into one solid. Give a connecting web genuine overlap into what it joins
(`len(out.solids()) == 1` is the check).

---

## 5. Hull / extend-a-surface

- **No 3D convex hull of solids exists** in build123d, and faking one with
  booleans is a great way to hang OCC. Don't.
- **`make_hull()` is 2D and must run inside `BuildSketch`.** Calling it on loose
  `Plane.XZ * Circle(...)` edges throws scipy `ConvexHull` "flat simplex"
  errors. The working pattern (a tapered web bridging two profiles):

  ```python
  with BuildSketch(Plane.XZ) as sk:
      with Locations((BR/2, BH/2)): Rectangle(BR, BH)   # grip the body flank
      with Locations((BR+GAP, z1)): Rectangle(BASE_T, 4) # pad under the plate
      make_hull()
  web = extrude(sk.sketch, amount=WEB_T/2, both=True)    # give it Y thickness
  ```
  (`Plane.XZ` maps sketch-local `(u,v)` → global `(X, 0, Z)`.)

- **`extrude(face, amount)`** literally pushes one face outward — the simplest
  "extend the surface out":
  ```python
  f = solid.faces().sort_by(Axis.X)[-1]
  out = solid + extrude(f, amount=15)
  ```
- **`loft([a, b])`** skins between two cross-sections, but wants actual
  `Face`/sketch sections (bare planes error). Heavier; use only when the profile
  must morph (circle → rectangle).

---

## 6. Null-triangulation: vanishing faces (countersinks)

**Symptom:** a face is missing in the OCP viewer *and* the STL, and exports warn
`N faces have been skipped due to null triangulation`.

**Cause:** some valid analytic faces — notably the NEMA17 base's **countersink
CONE faces** — come out of STEP with parametrics OCC's mesher (`BRepMesh`) can't
triangulate. The solid is `is_valid == True`; it's a *mesher* limit, not bad
geometry. Tightening `export_stl(tolerance=...)` and `ShapeFix_Shape` **do not
help** (finer tolerance makes it slightly worse). This matters for printing: a
skipped face is a **hole in the STL → non-watertight**.

**Fix:** convert the offending solid to NURBS (cones → splines the mesher
handles), then cache so it's a one-time cost. Implemented in
`arm_section._load()`:

```python
from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
healed = BRepBuilderAPI_NurbsConvert(solid.wrapped, True).Shape()
solid  = Solid(TopoDS.Solid_s(healed))      # ~1.3 s; all faces now mesh
```

Diagnosing which faces fail (mesh, then look for null triangulation):

```python
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
BRepMesh_IncrementalMesh(shape, 0.1, False, 0.5, True)
exp = TopExp_Explorer(shape, TopAbs_FACE)
while exp.More():
    if BRep_Tool.Triangulation_s(TopoDS.Face_s(exp.Current()), TopLoc_Location()) is None:
        ...   # this face will vanish
    exp.Next()
```

For the inverse problem — repairing an *already-meshed* STL (low-tooth gears
undercut to non-manifold) — `trimesh` `merge_vertices + fix_winding +
fill_holes` recovers watertightness.

---

## 7. BREP disk cache (amortize expensive healing)

NURBS-healing costs ~1.3 s per part; doing it every watch-loop save is painful.
So `_load()` caches the healed solid as **BREP** (`out/.vendor_cache/`, keyed on
the STEP's mtime). BREP write/read is ~0 ms and survives the round-trip clean, so
the first build pays once and rebuilds drop back to ~0.6 s.

```python
from OCP.BRepTools import BRepTools
BRepTools.Write_s(solid.wrapped, cache_path)        # write
sh = TopoDS_Shape(); BRepTools.Read_s(sh, cache_path, BRep_Builder())  # read
```

> **IP note:** the cache holds vendor-derived geometry. `out/` is **gitignored** —
> verify with `git check-ignore out/.vendor_cache/<x>.brep`. Only the two
> permitted vendor STLs may ever be tracked (see `NOTICE`).

---

## 8. Headless inspection without VSCode

When you can't open the OCP viewer (agent/CI), export STL, parse the triangles,
and plot projections with matplotlib — fast enough to eyeball collisions,
clearances, and "is the bore open" questions:

```python
# parse binary STL -> (n,3,3) triangle array, then ax.fill(t[:,0], t[:,1]) etc.
# top view (X-Y) shows whether a web intrudes into a bore;
# side (X-Z) shows cap/lip collisions; Poly3DCollection gives a rough iso.
```

A top-down (down +Z) projection over the bore circle is the quickest check that
a web/relief actually cleared the interior.

---

## 9. Misc build123d / environment

- `np.ptp(arr)`, not `arr.ptp()` (removed in numpy 2.0).
- `MjsLight` has no `directional` attribute — use a positioned point light.
- Interactive MuJoCo (`launch_passive`) must run on the user's display
  (`! python sim/view.py`); it fails from agent context. The OCP viewer does not
  have this limitation.
