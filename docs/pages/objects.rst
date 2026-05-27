
Objects
=======

Drawable objects are added to plot windows with :py:meth:`kaxe.Window.add`. Charts use their own data APIs instead.

See :doc:`recipes` for worked examples and :doc:`legends_and_titles` for ``legend()`` usage.

Object methods
--------------

Several objects expose chainable methods before ``add()``:

.. list-table::
   :header-rows: 1

   * - Object
     - Methods
     - Purpose
   * - :class:`kaxe.Function`, :class:`kaxe.Function2D`
     - ``fill(x0, x1)``, ``tangent(x)``
     - Shade under a curve; draw a tangent line
   * - :class:`kaxe.Points`, :class:`kaxe.Points2D`
     - ``legend(text, ...)``
     - Set legend label and symbol
   * - :class:`kaxe.Equation`, :class:`kaxe.Contour`, :class:`kaxe.Arrow`
     - ``legend(text, symbol=..., color=...)``
     - Custom legend entry per object

Example:

.. code-block:: python

   import math
   f = kaxe.Function(lambda x: math.sin(x))
   f.fill(-math.pi, math.pi)
   f.tangent(1)
   plt.add(f)

Smart objects
-------------

Smart objects adapt to the plot type (2D or 3D) based on the window you add them to — similar to method overloading.

.. autoclass:: kaxe.Points
    :members: 
    
.. autoclass:: kaxe.Function
    :members: 

.. autoclass:: kaxe.ParametricEquation
    :members:

    .. image:: /_static/parametricequation.png
        :width: 400 px

    .. image:: /_static/parametricequation3d.png
        :width: 400 px

.. autoclass:: kaxe.Arrow
    :members:

    .. image:: /_static/arrow.png
        :width: 400 px
    
    .. image:: /_static/arrow3d.png
        :width: 400 px

2D objects
----------

Use typed 2D objects when you need explicit control or parameters only available on the 2D class.

.. autoclass:: kaxe.Points2D
    :members: 
    
    .. image:: /_static/points2d.png
        :width: 400 px


.. autoclass:: kaxe.Function2D
    :members: 

    .. image:: /_static/function2d.png
        :width: 400 px
    

.. autoclass:: kaxe.Equation
    :members:

    .. image:: /_static/equation.png
        :width: 400 px

.. autoclass:: kaxe.ColorScale
    :members:

    .. image:: /_static/colorscale.png
        :width: 400 px

.. autoclass:: kaxe.HeatMap
    :members:

    .. image:: /_static/heatmap.png
        :width: 400 px


.. autoclass:: kaxe.Pillars
    :members:

    .. image:: /_static/pillars.png
        :width: 400 px
    
    .. image:: /_static/pillarspolar.png
        :width: 400 px

.. autoclass:: kaxe.Histogram
    :members:

    .. image:: /_static/histogram.png
        :width: 400 px
    

.. autoclass:: kaxe.Contour
    :members:

    .. image:: /_static/contour.png
        :width: 400 px

.. autoclass:: kaxe.Fill
    :members:

    .. image:: /_static/fill.png
        :width: 400 px


.. autoclass:: kaxe.Bubble
    :members:

    .. image:: /_static/bubble.png
        :width: 400 px

.. autoclass:: kaxe.objects.text.Text
    :members:


3D objects
----------

3D objects are lazy-loaded and require a 3D plot window (:class:`kaxe.Plot3D`, :class:`kaxe.PlotCenter3D`, or :class:`kaxe.PlotFrame3D`).


.. autoclass:: kaxe.Points3D
    :members: 

    .. image:: /_static/points3d.png
        :width: 400 px
    

.. autoclass:: kaxe.Function3D
    :members: 

    .. image:: /_static/function3d.png
        :width: 400 px


.. autoclass:: kaxe.Mesh
    :members: 

    .. image:: /_static/mesh.png
        :width: 300 px

.. autoclass:: kaxe.Potato
    :members: 

    .. image:: /_static/potato.png
        :width: 300 px

.. autoclass:: kaxe.SolidOfRotation
    :members: 

    .. image:: /_static/solidofrotation.png
        :width: 300 px
