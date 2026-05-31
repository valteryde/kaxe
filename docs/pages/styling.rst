
Styling
=======

Kaxe figures are styled through an attribute map on every window. Use :py:meth:`kaxe.AttrMap.style` to change appearance, :py:meth:`kaxe.AttrMap.help` to list all keys for the current window, and :py:meth:`kaxe.Window.theme` or :py:meth:`kaxe.Window.adjust` for LaTeX-friendly sizing.

How styles work
---------------

Each window owns an :class:`kaxe.AttrMap`. Style keys are grouped by scope:

* **Global keys** — ``fontSize``, ``width``, ``height``, ``color``, ``backgroundColor``, ``outerPadding``
* **Object-scoped keys** — use dot notation, e.g. ``marker.tickWidth``, ``marker.tickLength``

Pass styles as keyword arguments or in a dict:

.. code-block:: python

   plt.style(fontSize=80, lineWidth=4)
   plt.style({"marker.tickWidth": 6, "marker.tickLength": 40})

Call :py:meth:`kaxe.AttrMap.help` on any window to print defaults for that plot type:

.. code-block:: python

   plt.help()

Common global styles
--------------------

.. list-table::
   :header-rows: 1
   :widths: 22 18 60

   * - Key
     - Default (typical)
     - Effect
   * - ``width``
     - 2500
     - Output image width in pixels
   * - ``height``
     - 2000
     - Output image height in pixels
   * - ``fontSize``
     - 50
     - Base font size for labels and math
   * - ``color``
     - black
     - Default foreground color (RGBA tuple or hex string, e.g. ``"#000000"``)
   * - ``backgroundColor``
     - white
     - Canvas background (RGBA tuple or hex string)
   * - ``outerPadding``
     - [50, 50, 50, 50]
     - Padding around the plot area: left, bottom, top, right

Plot-specific styles
--------------------

**Cartesian plots** (:class:`kaxe.Plot`, :class:`kaxe.BoxedPlot`):

* ``xNumbers``, ``yNumbers`` — number of tick marks on each axis (``None`` = automatic)

**Polar plots** (:class:`kaxe.PolarPlot`):

* ``rNumbers`` — radial tick count

**3D plots** (:class:`kaxe.Plot3D` and variants):

* ``xNumbers``, ``yNumbers``, ``zNumbers`` — axis tick counts
* ``wireframeLinewidth`` — box frame line width
* ``backgroundColorBackdrop``, ``axisLineColorBackdrop`` — 3D backdrop colors

**Bar charts** (:class:`kaxe.Bar`, :class:`kaxe.GroupBar`):

* ``rotateLabel`` — label rotation in degrees
* ``barGap``, ``barGapProc``, ``barSmallGapProc`` — spacing between bars
* ``barColor`` — override default bar color

**Pie charts** (:class:`kaxe.Pie`):

* ``circleSizeProcent`` — fraction of canvas used by the pie
* ``phaseshift`` — rotation offset in degrees
* ``gap`` — gap between slices

Marker and axis styles
----------------------

Axis ticks and grid lines use the ``marker`` scope:

.. code-block:: python

   plt.style({"marker.tickWidth": 6, "marker.tickLength": 50})
   plt.style({"marker.gridlineColor": (0, 0, 0, 80)})

Useful ``marker`` keys:

* ``marker.tickWidth``, ``marker.tickLength`` — axis tick appearance
* ``marker.gridlineColor``, ``marker.gridlineWidth`` — grid lines
* ``marker.showNumber``, ``marker.showTick``, ``marker.showLine`` — visibility toggles

Colors
------

Colors accept **RGBA tuples** ``(red, green, blue, alpha)`` with values 0–255, or **hex strings** such as ``"#FF5154"``. Named CSS colors (``"red"``, ``"white"``, …) also work wherever colors are accepted.

.. code-block:: python

   plt.style(color="#000000", backgroundColor="#ffffff")
   func = kaxe.Function2D(lambda x: x, color="#DE6B48")
   plt.add(func)

Use :func:`kaxe.to_rgba` to normalize any supported input to an RGBA tuple.

Default plot colors cycle automatically. Control the cycle with:

* :func:`kaxe.getRandomColor` — next color in the palette
* :func:`kaxe.resetColor` — restart the cycle
* :func:`kaxe.setDefaultColors` — replace the global palette

Gradients on surfaces and contours use :class:`kaxe.Colormap` / :class:`kaxe.Colormaps` — see :doc:`utilities`.

Themes and adjust
-----------------

**Themes** apply a preset dict of styles tuned for A4 LaTeX pages:

.. code-block:: python

   plt.theme(kaxe.Themes.A4Medium)

Available presets: ``A4Large``, ``A4Medium``, ``A4Small``, ``A4Slim``, ``A4Mini``. See :class:`kaxe.Themes` for exact values.

**adjust** scales width, height, font size, and axis tick counts (``xNumbers``, ``yNumbers``) from a target fraction of page width:

.. code-block:: python

   plt.adjust(0.5)  # about half a text column

Optional parameters: ``documentFontSize``, ``documentMarginProcent``, ``documentWidth``, ``imageSlimRatio``.

Grids
-----

On :class:`kaxe.Grid`, ``fontSize``, ``color``, and axis tick counts (``xNumbers``, ``yNumbers``, and ``zNumbers`` for 3D cells) apply to the shared legend **and** every subplot cell when the grid is exported. Set them on the grid only; per-plot values on cells are overridden at bake time.

Use :meth:`kaxe.Grid.adjust` with the same API as single plots. Tick targets are computed from each cell's pixel size after the grid layout is divided, so subplots keep multiple grid lines instead of a single marker interval.

.. code-block:: python

   grid = kaxe.Grid()
   grid.adjust(0.5)
   grid.addRow(p1, p2, p3)

   grid = kaxe.Grid()
   grid.style(width=3000, height=1000, fontSize=100)
   grid.theme(kaxe.Themes.A4Medium)  # same presets as single plots
   grid.addRow(p1, p2, p3)

Per-object colors and widths
----------------------------

Many objects accept constructor arguments that override global styles:

.. code-block:: python

   kaxe.Function2D(lambda x: x**2, width=8, color=(6, 71, 137, 255))
   kaxe.Points2D([1, 2, 3], [1, 4, 9], size=30, symbol=kaxe.symbol.CIRCLE)

See :doc:`objects` for parameters on each object class.
