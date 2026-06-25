
Charts
======

Charts are standalone :class:`kaxe.Window` instances for statistical graphics. They are **not** added to a :class:`kaxe.Plot` with ``add()`` — create the chart directly, populate it, then save or show.

All charts support the shared window API: ``style()``, ``theme()``, ``save()``, and ``show()``.

Pie chart
---------

.. code-block:: python

   import kaxe

   pie = kaxe.Pie()
   pie.add(30, legend="A", label="30%")
   pie.add(70, legend="B", label="70%")
   pie.save("pie.png")

.. autoclass:: kaxe.Pie
    :show-inheritance:
    :members:

    .. image:: /_static/pie.png
        :width: 400 px


Bar chart
---------

.. code-block:: python

   import kaxe

   chart = kaxe.Bar()
   chart.add("a", [1, 2, 3, 4])
   chart.add("b", [2, 4])
   chart.save("bars.png")

.. autoclass:: kaxe.Bar
    :show-inheritance:
    :members:

    .. image:: /_static/bar.png
        :width: 600 px


Grouped bar chart
-----------------

.. code-block:: python

   import kaxe

   chart = kaxe.GroupBar()
   chart.add("series 1", [1, 2, 3])
   chart.add("series 2", [2, 1, 4])
   chart.save("groupbars.png")

.. autoclass:: kaxe.GroupBar
    :show-inheritance:
    :members:

    .. image:: /_static/groupbar.png
        :width: 600 px


Box plot chart
--------------

Statistical box-and-whisker chart. Not the same as :class:`kaxe.BoxedPlot`, which is a 2D plot window with boxed axes.

.. code-block:: python

   import kaxe

   chart = kaxe.BoxPlot()
   chart.add([1, 2, 3, 4])
   chart.add([4, 1, 6, 1, 6.3, 7, 9.1])
   chart.legends("dataset 1", "dataset 2")
   chart.save("boxplot.png")

Overlay points
~~~~~~~~~~~~~~

Use :meth:`kaxe.BoxPlot.overlay` to draw custom point subsets on top of a box row.
Each overlay can have its own color, symbol, and optional legend entry. This is
useful when you want to split one group visually — for example, to show where a
low and high subgroup fall along the same box.

The box is still computed from the full dataset passed to :meth:`kaxe.BoxPlot.add`.
Overlay values are plotted at their x positions on the target row. When several
overlay points share the same x value on one box row, they are separated
vertically (beeswarm) so different colored series do not stack on the same pixel.
Unique x values stay on the box midline. Overlay call order controls slot order
within a cluster. The ``box`` argument is the index of the target box in
:meth:`~kaxe.BoxPlot.add` order (``0`` = first ``add()`` call).

When looping over subgroup names, use a stable order (for example
``sorted(set(groups))``) so legend and draw order do not change between runs.

.. code-block:: python

   import kaxe

   chart = kaxe.BoxPlot()
   chart.add([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
   chart.overlay(
       [2, 3, 4],
       box=0,
       color=(220, 50, 50, 255),
       symbol=kaxe.symbol.CIRCLE,
       legend="low",
   )
   chart.overlay(
       [8, 9, 10],
       box=0,
       color=(50, 80, 220, 255),
       symbol=kaxe.symbol.CROSS,
       legend="high",
   )
   chart.legends("full group")
   chart.save("boxplot_overlay.png")

Control the vertical spread of clustered points with the ``overlayJitter`` style
(default ``0.8``, as a fraction of box height):

.. code-block:: python

   chart.style(overlayJitter=0.6)

Points outside the whisker range are still drawn automatically as outliers on each
:meth:`~kaxe.BoxPlot.add` series unless disabled with ``showOutliers=False``.
Overlays are independent and do not change the box or whisker calculation.

.. code-block:: python

   chart.style(showOutliers=False)

.. autoclass:: kaxe.BoxPlot
    :show-inheritance:
    :members:

    .. image:: /_static/box.png
        :width: 600 px


QQ plot
-------

.. code-block:: python

   import kaxe

   data = [1.2, 0.8, 1.5, 0.3, 2.1, -0.4, 0.9]
   qq = kaxe.QQPlot(data)
   qq.save("qq.png")

.. autoclass:: kaxe.QQPlot
    :show-inheritance:
    :members:

    .. image:: /_static/qqplot.png
        :width: 600 px
