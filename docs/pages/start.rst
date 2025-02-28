
Getting Started with Kaxe
=========================

Kaxe is simple and object oriented. There is support for a wide variety of plots, objects and charts.

Installation
------------

You can install Kaxe using pip:

.. code-block:: bash

   pip install kaxe

Quick Start for plots
---------------------

To get started with Kaxe, you can create a simple plot:

.. code-block:: python

   import kaxe
   plt = kaxe.Plot()
   plt.show()

Kaxe has theese plots

* :class:`kaxe.Plot`
* :class:`kaxe.BoxPlot`
* :class:`kaxe.EmptyPlot`
* :class:`kaxe.EmptyWindow`
* :class:`kaxe.PolarPlot`
* :class:`kaxe.LogPlot`
* :class:`kaxe.Plot3D`
* :class:`kaxe.PlotCenter3D`
* :class:`kaxe.PlotFrame3D`
* :class:`kaxe.PlotEmpty3D`


Adding Objects to the Plotting Window
-------------------------------------

You can add different objects to the plotting window. For example, to add a function:

.. code-block:: python

   func = kaxe.Function(lambda x: 2*x-1)
   plt.add(func)

Or to add points:

.. code-block:: python

   points = kaxe.Points([0, 1, 2, 3], [0, 1, 2, 3])
   plt.add(points)

Kaxe has theese objects 

Smart Objects

* :class:`kaxe.Points`
* :class:`kaxe.Function`

2D Objects

* :class:`kaxe.Points2D`
* :class:`kaxe.Arrow`
* :class:`kaxe.Equation`
* :class:`kaxe.ColorScale`
* :class:`kaxe.HeatMap`
* :class:`kaxe.ParametricEquation`
* :class:`kaxe.Pillars`

3D Objects

* :class:`kaxe.Points3D`
* :class:`kaxe.Function3D`


Styling the window
------------------

Styling the plotting window is as simple as

.. code-block:: python

   plt.styles( {"styleName": "style"} otherStyleName=style)

See :py:func:`kaxe.AttrMap.styles`

All the styles avaliable can be printed to the terminal by using

.. code-block:: python

   plt.help()

There are some themes build into Kaxe. Theese can be found in the class :py:class:`kaxe.Themes` and used with

.. code-block:: python

   plt.theme( kaxe.Themes.A4Large )


Kaxe can also give an estimate for some styles to match a acedemia page. This is done using the :py:func:`window.adjust` method.

.. code-block:: python

   plt.adjust( 0.5 )


Quick Start for charts
----------------------

Charts use more or less the same structure as plotting windows but is more limited. 
The charts usage differ from chart to chart and the best way to learn about each one is to inspect the wished chart.
Kaxe supports theese charts

* :class:`kaxe.Pie`
* :class:`kaxe.Bar`
* :class:`kaxe.BarGroup`
