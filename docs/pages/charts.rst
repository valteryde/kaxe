
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
