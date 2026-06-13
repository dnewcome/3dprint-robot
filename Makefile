# 3D-printed cycloidal robot arm — common tasks.  `make` or `make help` lists them.
PY ?= python3

# Generated, vendor-derived (gitignored). The model is regenerated from the CAD
# (arm_assembly.py) only when a source changes.
VENDOR  := vendor/micro/housing.step vendor/micro/base_nema17.step
MODEL   := sim/meshes/arm_long.stl          # representative output of arm_assembly.py

.PHONY: help install vendor assembly sim watch gravity backlash plan sizing sweep parts clean

# Which part the live viewer reloads (override: make watch PART=arm_section.py).
PART ?= angle_drive.py
.DEFAULT_GOAL := help

help: ## list targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  make %-10s %s\n", $$1, $$2}'

install: ## pip-install the python deps
	$(PY) -m pip install mujoco build123d numpy pillow

$(VENDOR): extract_vendor_steps.py
	$(PY) extract_vendor_steps.py

vendor: $(VENDOR) ## extract the 2 vendor parts from your purchased Sweep STEP

# arm_assembly.py emits the URDF + meshes + CAD preview from the CAD sources.
$(MODEL): arm_assembly.py arm_section.py shoulder_bracket.py $(VENDOR)
	$(PY) arm_assembly.py

assembly: $(MODEL) ## regenerate the robot model (URDF + meshes + CAD preview)

sim: $(MODEL) ## interactive MuJoCo viewer — pose the joints with the keys
	$(PY) sim/view.py

watch: ## live OCP CAD Viewer: re-run PART on save (PART=angle_drive.py)
	$(PY) watch.py $(PART)

gravity: $(MODEL) ## dynamics: watch it hold / sag under gravity
	$(PY) sim/gravity.py

backlash: $(MODEL) ## backlash -> tool-tip error budget
	$(PY) sim/backlash.py

plan: $(MODEL) ## collision-free pick demo (RRT)
	$(PY) sim/plan.py

sizing: ## torque / reach / motor-catalog analysis
	$(PY) sim/sizing.py

sweep: ## segment-length x NEMA17 motor-size design sweep
	$(PY) sim/sweep_design.py

parts: $(VENDOR) ## export the printable STLs (arm section + shoulder bracket)
	$(PY) arm_section.py upper
	$(PY) shoulder_bracket.py

clean: ## remove generated artifacts (keeps the vendor STEPs)
	rm -rf out sim/meshes __pycache__ sim/__pycache__ MUJOCO_LOG.TXT
