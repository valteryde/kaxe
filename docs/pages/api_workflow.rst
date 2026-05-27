
API Workflow
============

Every plot and chart in Kaxe follows the same four-step pattern.

The four steps
--------------

1. **Create a window** — ``Plot``, ``Bar``, ``Plot3D``, or another window class.
2. **Add content** — :py:meth:`kaxe.Window.add` for plot objects, or chart-specific methods like ``Bar.add(label, values)``.
3. **Style** — :py:meth:`kaxe.Window.theme`, :py:meth:`kaxe.AttrMap.style`, :py:meth:`kaxe.Window.title`, :py:meth:`kaxe.Window.legend`.
4. **Output** — :py:meth:`kaxe.Window.save` or :py:meth:`kaxe.Window.show`.

.. code-block:: python

   import kaxe

   plt = kaxe.Plot([-3, 3, -1, 9])
   plt.add(kaxe.Function2D(lambda x: x**2))
   plt.theme(kaxe.Themes.A4Medium)
   plt.style(fontSize=60)
   plt.save("parabola.png")

Plots vs charts
---------------

**Plots** display mathematical and geometric objects: functions, points, equations, contours, 3D surfaces, and similar.

**Charts** display statistical summaries: pie slices, bar groups, box plots, QQ plots.

Both inherit from :class:`kaxe.Window`, so they share ``style``, ``theme``, ``save``, and ``show``. The difference is how you populate them:

.. list-table::
   :header-rows: 1

   * - Window type
     - Typical constructor
     - Add content via
   * - Plot
     - ``kaxe.Plot([x0, x1, y0, y1])``
     - ``plt.add(kaxe.Function2D(...))``
   * - Chart
     - ``kaxe.Bar()``
     - ``chart.add("label", [1, 2, 3])``

Charts are **not** passed to ``Plot.add()``. Create a chart window directly:

.. code-block:: python

   chart = kaxe.Bar()
   chart.add("A", [1, 2, 3])
   chart.save("bars.png")

Smart objects vs typed objects
------------------------------

**Smart objects** adapt to the plot type you add them to:

* :class:`kaxe.Function` — callable for 2D or 3D plots
* :class:`kaxe.Points` — x/y or x/y/z data
* :class:`kaxe.ParametricEquation`, :class:`kaxe.Arrow`

Use smart objects when the same code should work on both 2D and 3D plots.

**Typed objects** target a specific dimension:

* 2D: :class:`kaxe.Function2D`, :class:`kaxe.Points2D`, :class:`kaxe.Equation`, :class:`kaxe.Contour`, ...
* 3D: :class:`kaxe.Function3D`, :class:`kaxe.Points3D`, :class:`kaxe.Mesh`, ...

Use typed objects when you need explicit control or extra parameters only available on the 2D/3D class.

Window methods reference
------------------------

.. list-table::
   :header-rows: 1

   * - Method
     - Purpose
   * - :py:meth:`kaxe.Window.add`
     - Add a drawable object to a plot
   * - :py:meth:`kaxe.AttrMap.style`
     - Set style attributes (``fontSize``, ``lineWidth``, colors, ...)
   * - :py:meth:`kaxe.AttrMap.help`
     - Print available style keys
   * - :py:meth:`kaxe.Window.theme`
     - Apply an A4 page preset from :class:`kaxe.Themes`
   * - :py:meth:`kaxe.Window.adjust`
     - Scale figure size relative to a LaTeX page
   * - :py:meth:`kaxe.Window.title`
     - Set the plot title (LaTeX math supported)
   * - :py:meth:`kaxe.Window.legend`
     - Configure the legend
   * - :py:meth:`kaxe.Window.save`
     - Write PNG or SVG to disk or a buffer
   * - :py:meth:`kaxe.Window.show`
     - Display in a viewer or Jupyter notebook
   * - :py:meth:`kaxe.Plot.zoom`
     - Create a magnified inset on a 2D plot

See also :doc:`styling`, :doc:`legends_and_titles`, and :doc:`recipes`.

Themes and LaTeX page sizing
----------------------------

:class:`kaxe.Themes` provides presets sized for A4 documents:

* ``A4Large``, ``A4Medium``, ``A4Small``, ``A4Slim``, ``A4Mini``

.. code-block:: python

   plt.theme(kaxe.Themes.A4Medium)

:py:meth:`kaxe.Window.adjust` estimates font and figure size for a given fraction of page width:

.. code-block:: python

   plt.adjust(0.5)  # roughly half an A4 text width

Both methods only change style attributes — they do not resize an already-rendered image.

Plot bounds
-----------

Pass ``[x0, x1, y0, y1]`` to set the visible data range. Use ``None`` for an axis bound to auto-scale from the data:

.. code-block:: python

   plt = kaxe.Plot([-5, 5, -1, 10])       # fixed x and y
   plt = kaxe.Plot([-40, 30, None, None]) # auto y from data
   plt = kaxe.Plot()                       # auto both axes

Polar plots take ``[r_min, r_max]``. 3D plots take ``[x0, x1, y0, y1, z0, z1]``.

Log plots use positive bounds on logarithmic axes. For log-log, pass both flags:

.. code-block:: python

   plt = kaxe.LogPlot([0.1, 100, 0.1, 1000], firstAxisLog=True, secondAxisLog=True)

Zoom inset
----------

On 2D plots, :py:meth:`kaxe.Plot.zoom` returns a linked sub-window. Objects added via ``zoom.add()`` appear only in the inset:

.. code-block:: python

   import math

   plot = kaxe.Plot([0, 4 * math.pi, -1, 1])
   plot.add(kaxe.Function2D(math.sin))

   zoom = plot.zoom(2.5, 4, -0.4, -0.1, position=(5, -0.5))
   zoom.add(kaxe.Points2D([3.2], [-0.2], color=(255, 0, 0, 255)))

See :doc:`plots` for all ``zoom()`` parameters.
