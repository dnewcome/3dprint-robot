#!/usr/bin/env python3
"""
watch.py — re-run a part script on every save, pushing it to the OCP CAD Viewer.

Each save re-runs the target with this same interpreter; the script's show()
call (see preview.py) refreshes the VSCode viewer. Watches every .py in the
repo root so editing a dependency (arm_section, shoulder_bracket, ...) reloads
the part that uses it too.

    python watch.py                 # default: angle_drive.py
    python watch.py arm_section.py
    python watch.py arm_assembly.py --show

Ctrl-C to stop.  Needs: pip install watchdog
"""
import os, sys, time, subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HERE = os.path.dirname(os.path.abspath(__file__))
DEBOUNCE = 0.3            # collapse editor's rapid save bursts


def run(target, extra):
    print(f"\n\033[36m── running {target} {' '.join(extra)} ──\033[0m", flush=True)
    subprocess.run([sys.executable, target, *extra], cwd=HERE)


class Rerun(FileSystemEventHandler):
    def __init__(self, target, extra):
        self.target, self.extra, self.last = target, extra, 0.0

    # React only to real CONTENT changes. Editors save atomically (write temp +
    # rename), so a save can arrive as created/moved, not just modified -- catch
    # all three. But do NOT react to 'opened'/'closed_no_write': merely RUNNING
    # the part opens its .py to read it, and reacting to that re-runs forever.
    WRITE_EVENTS = ("modified", "created", "moved")

    def on_any_event(self, event):
        if event.is_directory or event.event_type not in self.WRITE_EVENTS:
            return
        paths = [getattr(event, "src_path", ""), getattr(event, "dest_path", "")]
        names = [os.path.basename(p) for p in paths if p.endswith(".py")]
        if not names or all(n in ("watch.py", "preview.py") for n in names):
            return
        if time.time() - self.last < DEBOUNCE:
            return
        run(self.target, self.extra)
        self.last = time.time()        # measure debounce from run END (build is slow)


def main():
    args = sys.argv[1:]
    target = args[0] if args and args[0].endswith(".py") else "angle_drive.py"
    extra = [a for a in args if a != target]
    run(target, extra)                          # initial render

    handler = Rerun(target, extra)
    obs = Observer()
    obs.schedule(handler, HERE, recursive=False)
    obs.start()
    print(f"\033[33mwatching *.py in {HERE} — save to reload, Ctrl-C to stop\033[0m")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


if __name__ == "__main__":
    main()
