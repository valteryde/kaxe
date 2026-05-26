#!/usr/bin/env python3
"""Run 3D-related tests from tests/test.py (save paths; GUI show is no-op)."""

import os
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)
os.environ.setdefault("MPLCONFIGDIR", os.path.join(ROOT, ".matplotlib-cache"))

import kaxe

kaxe.setSetting(removeInfo=True)

# Avoid blocking SDL GUI loops during automated runs.
_original_plot3d_show = kaxe.Plot3D.show


def _show_no_gui(self, gui=True):
    if gui:
        return None
    return _original_plot3d_show(self, gui=False)


kaxe.Plot3D.show = _show_no_gui

# Import test module after path setup
sys.path.insert(0, ROOT)
from tests.test import Test  # noqa: E402

THREE_D_TESTS = [
    name
    for name in dir(Test)
    if name.startswith("test")
    and (
        "3D" in name
        or name in ("test2DIn3D", "testGridWith3D", "testParametricEquation")
    )
]


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def main():
    os.makedirs("tests/images/3d", exist_ok=True)
    failed = []
    passed = []

    for name in THREE_D_TESTS:
        fn = getattr(Test, name)
        print(f"Running {name}...", flush=True)
        t0 = time.time()
        try:
            with HiddenPrints():
                fn()
            elapsed = time.time() - t0
            print(f"  PASS ({elapsed:.2f}s)")
            passed.append(name)
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  FAIL ({elapsed:.2f}s): {e}")
            traceback.print_exc()
            failed.append((name, e))

    print()
    print(f"3D tests: {len(passed)} passed, {len(failed)} failed, {len(THREE_D_TESTS)} total")
    if failed:
        for name, err in failed:
            print(f"  - {name}: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
