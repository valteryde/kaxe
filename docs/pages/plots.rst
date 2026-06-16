
Plots
=====

All plots inherits from the Window base class. This class should not be used in practise and is only used to be inherited from.

.. autoclass:: kaxe.Window
    :members: 
    :exclude-members: clamp, include, inside, inversetranslate, pointOnWindowBorderFromLine, translate
    :show-inheritance:

    .. automethod:: kaxe.AttrMap.style
        
    .. automethod:: kaxe.AttrMap.help


Export
------

See :doc:`export` for PNG, SVG, and Jupyter display details.


Classical Plot
--------------
.. autoclass:: kaxe.Plot
    :show-inheritance:
    :exclude-members: identity, inversepixel, pixel
    :members:

    .. image:: /_static/plot.png
        :width: 400 px

Polar guide overlay
~~~~~~~~~~~~~~~~~~~

Add a polar-style guide grid (concentric arcs and radial lines) on top of a
Cartesian :class:`kaxe.Plot`. This is useful for s-plane root locus diagrams
and other plots that combine Cartesian axes with polar guide geometry. Use
:class:`kaxe.PolarGuideGrid`, not :class:`kaxe.PolarPlot`, when data lives in
Cartesian coordinates:

.. code-block:: python

   import kaxe

   plt = kaxe.Plot([-10, 2, -5, 5])
   plt.title("Real Axis", "Imag Axis")
   plt.add(kaxe.PolarGuideGrid(
       center=(0, 0),
       radii=[2, 4, 6, 8, 10],
       angles=[120, 135, 150, 160, 170, 175, 178, 179],
       arc_span=(90, 270),
       radius_labels=True,
       angle_labels=[0.2, 0.4, 0.56, 0.7, 0.81, 0.9, 0.955, 0.988],
       dashed=True,
   ))
   plt.add(kaxe.Points2D(reals, imags, connect=True))
   plt.save("splane.png")

See :class:`kaxe.PolarGuideGrid` in :doc:`objects` for all parameters.

Zoom inset
~~~~~~~~~~

Use :py:meth:`kaxe.Plot.zoom` to add a magnified region with optional connector lines. The returned inset accepts its own objects via ``zoom.add()``:

.. code-block:: python

   import math
   import kaxe

   plot = kaxe.Plot([0, 4 * math.pi, -1, 1])
   plot.add(kaxe.Function2D(math.sin))
   zoom = plot.zoom(2.5, 4, -0.4, -0.1, position=(5, -0.5))
   zoom.add(kaxe.Points2D([3.2], [-0.2], color=(255, 0, 0, 255)))

.. autoclass:: kaxe.BoxedPlot
    :show-inheritance:
    :members:

    .. image:: /_static/boxedplot.png
        :width: 400 px

.. autoclass:: kaxe.EmptyPlot
    :show-inheritance:
    :members:

    .. image:: /_static/emptyplot.png
        :width: 400 px

.. autoclass:: kaxe.EmptyWindow
    :show-inheritance:
    :members:

    .. image:: /_static/emptywindow.png
        :width: 400 px

    .. note:: Yes, its blank
    

.. autoclass:: kaxe.DoubleAxisPlot
    :show-inheritance:
    :members:

    .. image:: /_static/doubleaxisplot.png
        :width: 400 px

    .. note:: This plot window is still in early devolplement
    

Polar plot
----------

.. autoclass:: kaxe.PolarPlot
    :show-inheritance:
    :members:
    :exclude-members: clamp, inside, inversetranslate, pixel, pointOnWindowBorderFromLine, translate

    .. image:: /_static/polarplot.png
        :width: 400 px

Logarithmic Plot
----------------

.. autoclass:: kaxe.LogPlot
    :show-inheritance:
    :members:
    :exclude-members: hideUgly, inversepixel, pixel

    .. image:: /_static/logplot.png
        :width: 400 px


.. autoclass:: kaxe.BoxedLogPlot
    :show-inheritance:
    :members:
    :exclude-members: hideUgly, inversepixel, pixel

    .. image:: /_static/boxedlogplot.png
        :width: 400 px



3D Plots
--------

.. caution::
   Kaxe 3D graphs are pretty, but are still in early devolplement.
   Also Kaxe is written enterily in Python and is thereby slow.
   This method should in the future utilize the GPU, but for the time being this methods relies 
   enterily on the CPU to create the graphs.

.. autoclass:: kaxe.Plot3D
    :show-inheritance:
    :members:
    :exclude-members: forceWidthHeight

    .. image:: /_static/plot3d.png
        :width: 400 px

.. autoclass:: kaxe.PlotCenter3D
    :show-inheritance:
    :members:

    .. image:: /_static/plotcenter3d.png
        :width: 400 px
        

.. autoclass:: kaxe.PlotFrame3D
    :show-inheritance:
    :members:

    .. image:: /_static/plotframe3d.png
        :width: 400 px

.. autoclass:: kaxe.PlotEmpty3D
    :show-inheritance:
    :members:

    .. note:: This one is also just empty


Grid
----

Combine multiple plot windows into one image. Sub-plots keep their own styles and objects:

.. code-block:: python

   import kaxe

   top = kaxe.Plot([-3, 3, -3, 3])
   top.add(kaxe.Function2D(lambda x: x))

   bottom = kaxe.Plot([-3, 3, -3, 3])
   bottom.add(kaxe.Function2D(lambda x: x**2))

   grid = kaxe.Grid()
   grid.addColumn(top, bottom)
   grid.save("stacked.png")

Use ``addRow(*plots)`` for horizontal layouts. :class:`kaxe.Grid` saves PNG only — see :doc:`export`.

.. autoclass:: kaxe.Grid
    :show-inheritance:
    :members:
