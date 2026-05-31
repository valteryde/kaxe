
Project files (.kaxe)
=====================

A ``.kaxe`` file is a JSON project that stores everything needed to **reopen and edit** a figure: titles, styles, point data, heatmap grids, and curves sampled from functions. You can fix a typo or tweak ``fontSize`` and export again without the original script or data pipeline.

PNG, SVG, and PDF are **outputs**. A ``.kaxe`` file is the **editable source**.

Saving a project
----------------

Use :func:`kaxe.save_project` or pass ``project=`` when saving an image:

.. code-block:: python

   import kaxe

   plt = kaxe.Plot([-5, 5, -5, 5])
   plt.add(kaxe.Function2D(lambda x: x**2 - 4))
   plt.title("$x^2 - 4$")
   plt.theme(kaxe.Themes.A4Medium)

   plt.save("figure.pdf", project="figure.kaxe")

Loading and editing
-------------------

.. code-block:: python

   plt = kaxe.load_project("figure.kaxe")
   plt.title("$x^2 - 4$ corrected")
   plt.style(fontSize=55)
   plt.save("figure_v2.pdf", project="figure_v2.kaxe")

:func:`kaxe.load_project` returns a fresh, unbaked plot window.

What is stored
--------------

* Plot type (``Plot``, ``LogPlot``, ``BoxedPlot``, ``PolarPlot``, …)
* Axis limits, titles, padding, style overrides
* Numeric series (``Points2D``, ``HeatMap``, …)
* Functions as **sampled** ``x``/``y`` arrays (the curve shape is preserved; the original lambda is not)

Limitations (v1)
----------------

* **No pickle** — plain JSON only
* **Grid**, **charts**, **DoubleAxisPlot**, and **3D** plots cannot be saved as projects yet
* Callable-only objects (``Equation``, ``Contour``, ``Inequality``, ``Fill``) are not exported in v1
* Large heatmaps produce large JSON files; a ZIP-based format may be added in a future ``kaxe_version``

API reference
-------------

.. autofunction:: kaxe.save_project

.. autofunction:: kaxe.load_project
