
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
