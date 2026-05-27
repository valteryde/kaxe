
Recipes
=======

Common plotting tasks with copy-paste examples. Each recipe uses the standard workflow: create a window, add content, optionally style, then save.

Linear and polynomial functions
-------------------------------

.. code-block:: python

   import kaxe

   plt = kaxe.Plot([-5, 5, -5, 5])
   plt.add(kaxe.Function2D(lambda x: x))
   plt.add(kaxe.Function2D(lambda x: x**2 - 4))
   plt.save("functions.png")

Multiple functions with fill and tangent
----------------------------------------

.. code-block:: python

   import math
   import kaxe

   plt = kaxe.Plot()
   f = kaxe.Function(lambda x: math.sin(x) * 2)
   f.tangent(2)
   f.fill(-math.pi, math.pi)
   plt.add(f)
   plt.save("sin-fill.png")

Implicit equations (circles, curves)
------------------------------------

.. code-block:: python

   import kaxe

   plt = kaxe.Plot([-10, 10, -10, 10])
   center = (0, 1)
   plt.add(kaxe.Equation(
       lambda x, y: (x - center[0])**2 + (y - center[1])**2,
       lambda x, y: 4,
   ))
   plt.save("circle.png")

Scatter points with legend
--------------------------

.. code-block:: python

   import kaxe

   plt = kaxe.Plot()
   plt.title("$y = 0.25 x^2$")
   pts = kaxe.Points(range(0, 100), [0.25 * i**2 for i in range(100)]).legend("samples")
   plt.add(pts)
   plt.save("scatter.png")

Histogram and pillars
---------------------

.. code-block:: python

   import kaxe
   import numpy as np

   plt = kaxe.Plot([-5, 5, 0, None])
   data = np.random.normal(0, 1, 5000)
   plt.add(kaxe.Histogram(data, bins=20))
   plt.save("histogram.png")

Polar plot
----------

.. code-block:: python

   import math
   import kaxe

   plt = kaxe.PolarPlot([0, 7])
   plt.add(kaxe.Function(lambda x: math.sin(x) * math.cos(x)))
   steps = [(i / 100) * math.pi * 2 for i in range(100)]
   plt.add(kaxe.Points(steps, [math.cos(i) for i in steps], connect=True).legend("trace"))
   plt.title("Polar example")
   plt.save("polar.png")

Logarithmic axes
----------------

.. code-block:: python

   import math
   import kaxe

   plt = kaxe.LogPlot([0.01, 100, 0.01, 1e10])
   plt.add(kaxe.Function(lambda x: 10 ** x))
   plt.add(kaxe.Points([1, 10, 100], [1, 100, 10000]))
   plt.save("log.png")

Log-log plot (both axes logarithmic):

.. code-block:: python

   plt = kaxe.LogPlot([0.1, 1000, 0.1, 1000], firstAxisLog=True, secondAxisLog=True)

Contour plot
------------

.. code-block:: python

   import math
   import kaxe

   plt = kaxe.Plot([-5, 5, -5, 5])
   plt.add(kaxe.Contour(lambda x, y: 4 * math.sin(x) + 4 * math.cos(y) + x**2 - y))
   plt.save("contour.png")

Zoom inset
----------

.. code-block:: python

   import math
   import kaxe

   plot = kaxe.Plot([0, 4 * math.pi, -1, 1])
   plot.add(kaxe.Function2D(math.sin))
   zoom = plot.zoom(2.5, 4, -0.4, -0.1, position=(5, -0.5))
   zoom.add(kaxe.Points2D([3.2], [-0.2], color=(255, 0, 0, 255)))
   plot.save("zoom.png")

Multi-panel grid
----------------

.. code-block:: python

   import kaxe

   p1 = kaxe.Plot([-3, 3, -3, 3])
   p1.add(kaxe.Function2D(lambda x: x))

   p2 = kaxe.Plot([-3, 3, -3, 3])
   p2.add(kaxe.Function2D(lambda x: x**2))

   grid = kaxe.Grid()
   grid.addRow(p1, p2)
   grid.save("grid.png")

3D surface
----------

.. code-block:: python

   import math
   import kaxe

   plt = kaxe.Plot3D([-5, 5, -5, 5, -2, 2])
   plt.add(kaxe.Function3D(lambda x, y: math.sin(x * y / 10)))
   plt.save("surface3d.png")

Bar chart with multiple series
------------------------------

.. code-block:: python

   import kaxe

   chart = kaxe.Bar()
   chart.add(2020, [4.0, 1.0])
   chart.add(2021, [5.5, 2.0])
   chart.legends("Revenue", "Cost")
   chart.title("Annual results")
   chart.style(rotateLabel=45)
   chart.save("bars.png")

Box plot chart
--------------

.. code-block:: python

   import kaxe

   chart = kaxe.BoxPlot()
   chart.add([1, 2, 3, 4, 5])
   chart.add([4, 1, 6, 7, 9])
   chart.legends("group A", "group B")
   chart.save("boxplot.png")

QQ plot
-------

.. code-block:: python

   import kaxe

   data = [1.2, 0.8, 1.5, 0.3, 2.1, -0.4, 0.9]
   qq = kaxe.QQPlot(data)
   qq.save("qq.png")

LaTeX-ready export
------------------

Combine theme sizing with SVG for vector figures in papers:

.. code-block:: python

   import kaxe

   plt = kaxe.Plot([-5, 5, -5, 5])
   plt.add(kaxe.Function2D(lambda x: x**2 - 4))
   plt.theme(kaxe.Themes.A4Medium)
   plt.title("$x^2 - 4$")
   plt.save("figure.svg")  # include in LaTeX with \\includegraphics

See :doc:`export` for PNG vs SVG details and LaTeX inclusion tips.

Load data from Excel
--------------------

.. code-block:: python

   import kaxe

   # Columns A–C, rows 2–100 on sheet "Data"
   rows = kaxe.data.loadExcel("data.xlsx", "Data", top=(1, 2), bottom=(3, 100))
   x = [row[0] for row in rows]
   y = [row[1] for row in rows]

   plt = kaxe.Plot()
   plt.add(kaxe.Points2D(x, y))
   plt.save("from-excel.png")

See :func:`kaxe.data.loadExcel` for the full parameter reference.
