
Plots
=====

All plots inherits from the Window base class. This class should not be used in practise and is only used to be inherited from.

.. autoclass:: kaxe.Window
    :members: 
    :exclude-members: clamp, include, inside, inversetranslate, pointOnWindowBorderFromLine, translate
    :show-inheritance:

    .. automethod:: kaxe.AttrMap.style
        
    .. automethod:: kaxe.AttrMap.help


Classical Plot
--------------
.. autoclass:: kaxe.Plot
    :show-inheritance:
    :exclude-members: identity, inversepixel, pixel
    :members:

    .. image:: /_static/plot.png
        :width: 400 px

.. autoclass:: kaxe.BoxPlot
    :show-inheritance:
    :members:

    .. image:: /_static/boxplot.png
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


.. autoclass:: kaxe.BoxLogPlot
    :show-inheritance:
    :members:
    :exclude-members: hideUgly, inversepixel, pixel

    .. image:: /_static/boxlogplot.png
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

.. autoclass:: kaxe.Grid
    :show-inheritance:
    :members:
