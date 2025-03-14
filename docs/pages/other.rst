
Other
=====

This section covers various functionalities of Kaxe that do not fit into other specific categories. 
Below are some of the additional features and utilities provided by Kaxe.


Small excel data loader
-----------------------


Firstly Kaxe has a simple excel data loader:

.. automethod:: kaxe.data.loadExcel


Color gradients
---------------
For gradients kaxe has an colormap. i.g. in 3D graphs kaxe uses theese as colors

.. autoclass:: kaxe.Colormap
    :members: 

.. autoclass:: kaxe.Colormaps
    :members: 

.. autoclass:: kaxe.SingleColormap
    :members: 


Default colors
--------------

To change the behavior of the default colors, you can use the following functions:

.. autofunction:: kaxe.setDefaultColors

.. autofunction:: kaxe.resetColors


Symbols and themes
------------------

Kaxe has multiple symbols and themes such as

.. autoclass:: kaxe.Symbol
    :members:

.. autoclass:: kaxe.symbol
    :members:

.. autoclass:: kaxe.Themes
    :members:


Axis
----

The axis used in most of the plots also contains some attributes and methods that could be useful:

.. autoclass:: kaxe.Axis
    
    .. automethod:: kaxe.Axis.add


Legends not attatched to objects
--------------------------------

.. autoclass:: kaxe.GhostLegend
    :members:
