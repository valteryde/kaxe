
Export and Display
==================

Saving figures
--------------

All windows support :py:meth:`kaxe.Window.save`. The output format is inferred from the file extension, or set explicitly with ``format=``.

PNG (default)
~~~~~~~~~~~~~

PNG is the default raster format. Plots render at high resolution (default 2500×2000 pixels unless overridden via ``style(width=..., height=...)``).

.. code-block:: python

   plt.save("figure.png")

SVG (2D plots and charts)
~~~~~~~~~~~~~~~~~~~~~~~~~

SVG export produces a self-contained vector file. Curves, axes, and labels are vector graphics. Math labels use `fondi <https://github.com/valteryde/fondi>`_ with embedded New Computer Modern fonts.

.. code-block:: python

   plt.save("figure.svg")

.. note::
   SVG is supported for 2D plots, charts, and :class:`kaxe.Grid` layouts. Individual :class:`kaxe.Plot3D` windows save PNG only; in a grid, 3D cells are embedded as raster images inside the SVG. :meth:`kaxe.Grid.show` always previews PNG.

.. code-block:: python

   grid = kaxe.Grid()
   grid.addRow(plt1, plt2)
   grid.save("figure_grid.svg")

When writing to a buffer without a filename extension, pass ``format`` explicitly:

.. code-block:: python

   from io import BytesIO

   buf = BytesIO()
   plt.save(buf, format="svg")

PNG and SVG can be saved from the same plot; saving SVG does not invalidate a cached PNG.

PDF (2D plots and charts)
~~~~~~~~~~~~~~~~~~~~~~~~~

PDF export produces a vector file with the same content as SVG. Math labels use Computer Modern fonts from `fondi`. Install the optional dependencies first:

.. code-block:: bash

   pip install kaxe[pdf]

.. code-block:: python

   plt.save("figure.pdf")

.. note::
   PDF follows the same rules as SVG: supported for 2D plots, charts, and :class:`kaxe.Grid` layouts. Individual :class:`kaxe.Plot3D` windows save a raster image inside a PDF page; in a grid, 3D cells are embedded as raster images inside the vector PDF.

.. code-block:: python

   grid = kaxe.Grid()
   grid.addRow(plt1, plt2)
   grid.save("figure_grid.pdf")

When writing to a buffer without a filename extension, pass ``format`` explicitly:

.. code-block:: python

   from io import BytesIO

   buf = BytesIO()
   plt.save(buf, format="pdf")

Display with show()
-------------------

:py:meth:`kaxe.Window.show` renders and displays the figure.

**Terminal:** opens the image with the system viewer (via Pillow).

**Jupyter / IPython:** detects the active shell and displays the image inline instead of opening an external viewer.

.. code-block:: python

   plt.show()

In notebooks, prefer ``show()`` for quick previews and ``save()`` when you need a file for LaTeX inclusion.

Including figures in LaTeX
--------------------------

**PNG** — simple and widely compatible:

.. code-block:: latex

   \\usepackage{graphicx}
   ...
   \\includegraphics[width=0.8\\textwidth]{figures/parabola.png}

**SVG** — vector output with embedded Computer Modern math (requires ``\\usepackage{svg}`` or convert to PDF):

.. code-block:: latex

   \\includesvg[width=0.8\\textwidth]{figures/parabola.svg}

**PDF** — vector output, widely compatible with ``\\includegraphics`` (requires ``pip install kaxe[pdf]``):

.. code-block:: latex

   \\includegraphics[width=0.8\\textwidth]{figures/parabola.pdf}

Tips for publication figures:

* Use ``plt.theme(kaxe.Themes.A4Medium)`` or ``plt.adjust(0.5)`` to match document font size — see :doc:`styling`
* Prefer ``.svg`` or ``.pdf`` for 2D plots in LaTeX documents
* Use ``kaxe.resetColor()`` before each figure if you need consistent colors across multiple saves in one script

Suppressing progress output
---------------------------

Kaxe logs bake progress to the terminal by default. In Jupyter, logging is automatically reduced. To suppress progress bars and info messages globally:

.. code-block:: python

   kaxe.setSetting(removeInfo=True)
