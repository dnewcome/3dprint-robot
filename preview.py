#!/usr/bin/env python3
"""
preview.py — optional OCP CAD Viewer hook (VSCode "OCP CAD Viewer" extension).

Lets any part script render live in VSCode without making ocp_vscode a hard
dependency: if it isn't installed (e.g. headless `make`), show() is a no-op.

    pip install ocp_vscode          # into the env that has build123d
    # + install the "OCP CAD Viewer" VSCode extension (bernhard-42)

Usage in a part file:

    from preview import show
    if __name__ == "__main__":
        show(part())                # or show(a, b, names=["body", "plate"])

The viewer talks to a local server (default port 3939), so it works without a
special display — unlike the MuJoCo launch_passive viewer.
"""


def show(*objs, **kwargs):
    """Render build123d objects in the VSCode OCP viewer if available."""
    try:
        from ocp_vscode import show as _show
    except ImportError:
        print("ocp_vscode not installed; skipping viewer "
              "(pip install ocp_vscode + OCP CAD Viewer extension)")
        return
    _show(*objs, **kwargs)
