
Getting Started
===============

Kaxe is object oriented: create a plot or chart window, add content, style it, then save or show the result.

Installation
------------

.. code-block:: bash

   pip install kaxe

Complete example
----------------

This example shows the full workflow: bounds, objects, theme, title, and export.

.. code-block:: python

   import kaxe

   plt = kaxe.Plot([-5, 5, -5, 5])
   plt.add(kaxe.Function2D(lambda x: x**2 - 4))
   plt.add(kaxe.Points2D([1, 2, 3], [1, 4, 9]))
   plt.theme(kaxe.Themes.A4Medium)
   plt.title("$x^2 - 4$")
   plt.save("figure.png")
   plt.save("figure.svg")

Minimal plot
------------

.. code-block:: python

   import kaxe

   plt = kaxe.Plot()
   plt.show()

Plot windows
------------

Plot windows hold drawable objects (functions, points, contours, and more).

* :class:`kaxe.Plot` — standard Cartesian plot
* :class:`kaxe.BoxedPlot` — axes pinned to the bottom-left corner
* :class:`kaxe.PolarPlot` — polar coordinates
* :class:`kaxe.LogPlot`, :class:`kaxe.BoxedLogPlot` — logarithmic axes
* :class:`kaxe.DoubleAxisPlot` — two y-axes
* :class:`kaxe.EmptyPlot`, :class:`kaxe.EmptyWindow` — blank canvases
* :class:`kaxe.Grid` — multi-panel layouts
* :class:`kaxe.Plot3D`, :class:`kaxe.PlotCenter3D`, :class:`kaxe.PlotFrame3D`, :class:`kaxe.PlotEmpty3D` — 3D plots

See :doc:`plots` for the full API reference.

Adding objects
--------------

Add objects with :py:meth:`kaxe.Window.add`. Smart objects pick 2D or 3D based on the plot:

.. code-block:: python

   plt.add(kaxe.Function(lambda x: 2 * x - 1))
   plt.add(kaxe.Points([0, 1, 2, 3], [0, 1, 2, 3]))

For explicit 2D types:

.. code-block:: python

   plt.add(kaxe.Function2D(lambda x: x**2))
   plt.add(kaxe.Points2D([1, 2], [3, 4]))

See :doc:`objects` for all object types.

Styling
-------

Set individual style keys with :py:meth:`kaxe.AttrMap.style`:

.. code-block:: python

   plt.style(fontSize=80, lineWidth=4)

List available keys with :py:meth:`kaxe.AttrMap.help`:

.. code-block:: python

   plt.help()

Apply a page-sized preset with :py:meth:`kaxe.Window.theme`:

.. code-block:: python

   plt.theme(kaxe.Themes.A4Large)

Scale the figure to a fraction of an A4 page width with :py:meth:`kaxe.Window.adjust`:

.. code-block:: python

   plt.adjust(0.5)

See :doc:`api_workflow` for how plots, charts, objects, and styling fit together.

More guides
-----------

* :doc:`recipes` — copy-paste examples for common tasks
* :doc:`styling` — style keys, colors, themes, and ``adjust``
* :doc:`legends_and_titles` — titles, object legends, chart legends, symbols
* :doc:`export` — PNG, SVG, Jupyter, and LaTeX inclusion

Charts
------

Charts are standalone windows — they are not added to a :class:`kaxe.Plot`.

* :class:`kaxe.Pie`
* :class:`kaxe.Bar`
* :class:`kaxe.GroupBar`
* :class:`kaxe.BoxPlot` — box-and-whisker chart (not the same as :class:`kaxe.BoxedPlot`)
* :class:`kaxe.QQPlot`

See :doc:`charts` for per-chart usage and the full API.

Export
------

Save as PNG (default) or SVG (2D plots and charts):

.. code-block:: python

   plt.save("myplot.png")
   plt.save("myplot.svg")

See :doc:`export` for format details, Jupyter usage, and LaTeX tips.

API quick reference
-------------------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Category
     - Main symbols
   * - Plot windows
     - :class:`kaxe.Plot`, :class:`kaxe.BoxedPlot`, :class:`kaxe.PolarPlot`, :class:`kaxe.LogPlot`, :class:`kaxe.Grid`, :class:`kaxe.Plot3D`
   * - Charts
     - :class:`kaxe.Pie`, :class:`kaxe.Bar`, :class:`kaxe.GroupBar`, :class:`kaxe.BoxPlot`, :class:`kaxe.QQPlot`
   * - Smart objects
     - :class:`kaxe.Function`, :class:`kaxe.Points`, :class:`kaxe.Arrow`, :class:`kaxe.ParametricEquation`
   * - Window methods
     - ``add``, ``style``, ``theme``, ``adjust``, ``title``, ``save``, ``show``, ``help``, ``zoom``
   * - Utilities
     - :class:`kaxe.Themes`, :func:`kaxe.koundTeX`, :func:`kaxe.resetColor`, :func:`kaxe.setSetting`, :func:`kaxe.data.loadExcel`
