
# Kaxe

![BoxPlot](logo.png)

Kaxe is an lightweight graphing tools for functions, equations, points and more written in pure python. Kaxe supports various plotting windows and charts.

Kaxe documentation can be found [here](https://kaxe.readthedocs.io/en/latest/)

## Goals

Kaxe was made to create pretty, simple and easy graphs to be used along side articels, repports and other Acedima made in LaTeX. The goals for Kaxe then became

* Create pretty plots thats fit into the astectic of LaTeX
* A very simple object oriented interface

## Examples of plots

2D Plots
![BoxPlot](tests/images/box.png)

Polar plots
![Polar plot](tests/images/polar.png)

3D Plots
![3DPlot](tests/images/3d-box.png)
![Style3DPlot](tests/images/3d-box-style.png)
![PrettyPlot3D2](tests/images/3d-function-pretty-2.png)
![Style3DPlot3](tests/images/3d-function-pretty-3.png)


## Preview of Code

To get started create a plot object

```python
import kaxe

plt = kaxe.Plot()
plt.add( ... ) # Object to be added
plt.save("plot.png")
```

This is all you need for a plot and some objects. To get started visit [the getting started section](https://kaxe.readthedocs.io/en/latest/pages/start.html)

![AllLegends](tests/images/alllegeneds.png)
![Functions](tests/images/function.png)
![Points](tests/images/labels.png)
![Equations](tests/images/equation.png)

