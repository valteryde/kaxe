
Legends and Titles
==================

Kaxe supports LaTeX math in titles and legend text. Use ``$...$`` for inline math.

Plot titles
-----------

On Cartesian plots, :py:meth:`kaxe.Plot.title` sets axis titles:

.. code-block:: python

   plt = kaxe.Plot()
   plt.title("$x$ axis label", "$y$ axis label")

On polar plots:

.. code-block:: python

   plt = kaxe.PolarPlot([0, 7])
   plt.title("Radial plot title")

On 3D plots, pass up to three axis labels:

.. code-block:: python

   plt = kaxe.Plot3D([0, 1, 0, 1, 0, 1])
   plt.title("$x$", "$y$", "$z$")

Piecewise and complex titles use LaTeX ``\cases`` or other commands:

.. code-block:: python

   plt.title("$f(x)=\\cases{2}{x<2}{4*x+2}{x>2}$", "Secondary axis")

Object legends
--------------

Most plottable objects expose a ``legend()`` method that returns ``self``, so you can chain it before ``add()``:

.. code-block:: python

   points = kaxe.Points2D([1, 2, 3], [1, 4, 9]).legend("data set A")
   plt.add(points)

   curve = kaxe.Function2D(lambda x: x**2).legend("$x^2$", symbol=kaxe.symbol.LINE)
   plt.add(curve)

Parameters vary by object type:

* ``text`` — legend label (LaTeX supported)
* ``symbol`` — :data:`kaxe.symbol.CIRCLE`, ``LINE``, ``CROSS``, etc.
* ``color`` — override the legend swatch color

.. code-block:: python

   contour = kaxe.Contour(lambda x, y: x**2 + y**2)
   contour.legend("level set")
   plt.add(contour)

Ghost legends
-------------

:class:`kaxe.GhostLegend` adds a legend entry without plotting a corresponding object:

.. code-block:: python

   plt.add(kaxe.GhostLegend("reference line", (255, 0, 0, 255), kaxe.symbol.LINE))

Parameters: ``text``, ``color`` (RGBA tuple), ``symbol``.

Chart titles and legends
------------------------

Charts use their own title and legend APIs.

**Pie** — slice legend via ``add``:

.. code-block:: python

   pie = kaxe.Pie()
   pie.add(30, legend="Group A", label="30%")
   pie.title("$\\sum x_i$")

**Bar / GroupBar** — multiple series legends:

.. code-block:: python

   chart = kaxe.Bar()
   chart.add(2020, [5.0, 2.0])
   chart.add(2021, [5.5, 1.0])
   chart.legends("Series A", "Series B")
   chart.title("Main title", "x-axis", "y-axis")

**BoxPlot** (chart):

.. code-block:: python

   chart = kaxe.BoxPlot()
   chart.add([1, 2, 3, 4])
   chart.add([4, 1, 6, 7])
   chart.legends("control", "treatment")

Grid legends
------------

:class:`kaxe.Grid` accepts manual legend entries when sub-plots share a combined legend:

.. code-block:: python

   grid = kaxe.Grid()
   grid.legends(
       ("Curve A", kaxe.symbol.LINE, (222, 107, 72, 255)),
       ("Points B", kaxe.symbol.CIRCLE, (6, 71, 137, 255)),
   )

Each entry is a tuple of ``(label, symbol, color)``.

Available symbols
-----------------

Built-in legend and point symbols (from :data:`kaxe.symbol`):

.. list-table::
   :header-rows: 1

   * - Constant
     - Description
   * - ``kaxe.symbol.CIRCLE``
     - Filled circle (default for points)
   * - ``kaxe.symbol.LINE``
     - Thin line swatch
   * - ``kaxe.symbol.THICKLINE``
     - Thick line swatch
   * - ``kaxe.symbol.RECTANGLE``
     - Filled square
   * - ``kaxe.symbol.CROSS``
     - Cross mark
   * - ``kaxe.symbol.TRIANGLE``
     - Triangle
   * - ``kaxe.symbol.STAR``
     - Star
   * - ``kaxe.symbol.LOLLIPOP``
     - Lollipop marker
   * - ``kaxe.symbol.DONUT``
     - Donut marker

See :doc:`utilities` for the full :class:`kaxe.symbol` API.
