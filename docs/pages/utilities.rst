
Utilities
=========

Helper functions and classes that are not plot windows or drawable objects.

Number formatting
-----------------

.. autofunction:: kaxe.koundTeX

Global settings
---------------

.. autofunction:: kaxe.setSetting

.. note::
   Currently supported keys: ``removeInfo`` (bool) — suppress progress bars and bake timing logs.

Colors
------

.. autofunction:: kaxe.to_rgba

.. autofunction:: kaxe.setDefaultColors

.. autofunction:: kaxe.resetColor

.. autofunction:: kaxe.getRandomColor

Colormaps
---------

.. autoclass:: kaxe.Colormap
    :members:

.. autoclass:: kaxe.Colormaps
    :members:

.. autoclass:: kaxe.SingleColormap
    :members:

Symbols
-------

.. autoclass:: kaxe.Symbol
    :members:

.. autoclass:: kaxe.symbol
    :members:

Themes
------

.. autoclass:: kaxe.Themes
    :members:

Axis
----

The axis object used by most plots exposes additional attributes and methods:

.. autoclass:: kaxe.Axis

    .. automethod:: kaxe.Axis.add

Ghost legends
-------------

Add legend entries that are not tied to a specific plotted object:

.. autoclass:: kaxe.GhostLegend
    :members:

Excel data loader
-----------------

Load a rectangular range from an ``.xlsx`` workbook. Column indices are 1-based (Excel convention):

.. code-block:: python

   import kaxe

   # Sheet "Results", columns A–B, rows 2 through last row
   table = kaxe.data.loadExcel("results.xlsx", "Results", top=(1, 2), bottom=(2, -1))

   x = [row[0] for row in table]
   y = [row[1] for row in table]
   plt = kaxe.Plot()
   plt.add(kaxe.Points2D(x, y))

Set ``flip=True`` to transpose rows and columns. See :doc:`recipes` for a full example.

.. automethod:: kaxe.data.loadExcel

Point thinning
--------------

Reduce large point series before adding them to a plot — especially useful for
SVG export where millions of markers make files slow to load:

.. code-block:: python

   import kaxe

   # Cap at 5000 points (uniform index sampling)
   x_thin, y_thin = kaxe.thin_points(x, y, max_points=5000)

   # Keep every 10th point
   x_thin, y_thin = kaxe.thin_points(x, y, every=10)

   # Min spacing in data coordinates
   x_thin, y_thin = kaxe.thin_points(x, y, min_distance=0.05)

   # Min spacing in screen pixels (needs plot with fixed bounds)
   plt = kaxe.Plot([0, 10, 0, 10])
   plt.theme(kaxe.Themes.A4Medium)
   x_thin, y_thin = kaxe.thin_points(x, y, min_distance=3, space="pixel", plot=plt)

   plt.add(kaxe.Points2D(x_thin, y_thin))

Provide exactly one of ``every``, ``min_distance``, or ``max_points``. Optional
``z`` is thinned with the same indices: ``x, y, z = kaxe.thin_points(x, y, z, every=5)``.

.. autofunction:: kaxe.thin_points
