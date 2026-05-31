"""
Tests for .kaxe project save/load round-trip.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import smoke, unit

OUTPUT = Path(__file__).resolve().parent.parent / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)


@unit()
def test_project_roundtrip_metadata():
    plot = kaxe.Plot([-5, 5, -5, 5])
    plot.title(first="$x$", second="$y$")
    plot.style(fontSize=77)

    path = OUTPUT / "roundtrip_meta.kaxe"
    kaxe.save_project(plot, path)

    loaded = kaxe.load_project(path)
    assert loaded.firstTitle == "$x$"
    assert loaded.secondTitle == "$y$"
    assert loaded.getAttr("fontSize") == 77
    assert loaded.windowAxis == [-5, 5, -5, 5]


@unit()
def test_project_roundtrip_points():
    plot = kaxe.Plot([-1, 4, 0, 10])
    plot.add(kaxe.Points2D([1, 2, 3], [1, 4, 9]))

    path = OUTPUT / "roundtrip_points.kaxe"
    kaxe.save_project(plot, path)
    loaded = kaxe.load_project(path)

    assert len(loaded.objects) == 1
    pts = loaded.objects[0]
    assert list(pts.x) == [1, 2, 3]
    assert list(pts.y) == [1, 4, 9]


@smoke()
def test_project_roundtrip_function_sampled():
    plot = kaxe.Plot([-3, 3, -2, 10])
    plot.add(kaxe.Function2D(lambda x: x**2))

    path = OUTPUT / "roundtrip_fn.kaxe"
    kaxe.save_project(plot, path)

    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    assert doc["objects"][0]["representation"] == "sampled"
    assert len(doc["objects"][0]["x"]) > 10

    loaded = kaxe.load_project(path)
    assert len(loaded.objects) == 1
    return loaded


@unit()
def test_project_edit_workflow():
    plot = kaxe.Plot([-2, 2, -2, 2])
    plot.title(first="Old title")
    path = OUTPUT / "edit_workflow.kaxe"
    kaxe.save_project(plot, path)

    loaded = kaxe.load_project(path)
    loaded.title(first="New title")
    kaxe.save_project(loaded, path)

    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    assert doc["window"]["titles"]["first"] == "New title"


@unit()
def test_save_with_project_kwarg():
    plot = kaxe.Plot([0, 1, 0, 1])
    out = OUTPUT / "save_kwarg.png"
    proj = OUTPUT / "save_kwarg.kaxe"
    plot.save(out, project=str(proj))
    assert proj.exists()


@unit()
def test_plot3d_project_raises():
    plt3 = kaxe.Plot3D()
    try:
        kaxe.save_project(plt3, OUTPUT / "bad3d.kaxe")
        assert False, "expected NotImplementedError"
    except NotImplementedError as exc:
        assert "3D" in str(exc)


@unit()
def test_grid_project_raises():
    grid = kaxe.Grid()
    try:
        grid.save(OUTPUT / "grid.png", project=str(OUTPUT / "grid.kaxe"))
        assert False, "expected NotImplementedError"
    except NotImplementedError as exc:
        assert "Grid" in str(exc)
