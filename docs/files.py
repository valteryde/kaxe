
import os
from pathlib import Path
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
import shutil
import math
import sys

sys.path.insert(0, str(Path('src').resolve()))
import kaxe

fpath = Path(__file__).absolute()
fpath = os.path.sep+os.path.join(*str(fpath).split(os.path.sep)[:-2])
docfpath = os.path.join(fpath, 'docs')

def _getImageFromChildren(tokens, images=[]):

    for token in tokens:

        if token.children:
            _getImageFromChildren(token.children, images)

        if token.type == "image":
            images.append(token.attrs["src"])
            token.attrs["src"] = "_static/" + os.path.split(token.attrs["src"])[1]

    return images


# load images from tests
def copyImagesFromTest():
    md = (
    MarkdownIt('commonmark', {'breaks':True,'html':True})
        .use(front_matter_plugin)
        .use(footnote_plugin)
        .enable('table')
    )
    
    READMEFILEPATH = os.path.join(fpath, 'README.md')
    
    with open(READMEFILEPATH) as file:
        tokens = md.parse(file.read())
        
        images = _getImageFromChildren(tokens)

        for img in images:
            
            shutil.copy(os.path.join(fpath, img), os.path.join(docfpath, img))


# paths
j = lambda p: os.path.join(docfpath, '_static', p+'.png')
def create2DWithObject(obj, fname, window=None):
    
    plt = kaxe.Plot(window)
    plt.add(obj)
    plt.save(j(fname))


def create3DWithObject(obj, fname, window=None):
    
    plt = kaxe.Plot3D(window)
    plt.add(obj)
    plt.save(j(fname))


# load all static images
def createAllDocImages():
    
    # standard plot
    plt = kaxe.Plot()
    plt.save(j('plot'))

    plt = kaxe.BoxPlot()
    plt.save(j('boxplot'))

    plt = kaxe.EmptyPlot()
    plt.save(j('emptyplot'))

    plt = kaxe.EmptyWindow()
    plt.save(j('emptywindow'))

    plt = kaxe.LogPlot()
    plt.save(j('logplot'))

    plt = kaxe.PolarPlot()
    plt.save(j('polarplot'))

    plt = kaxe.Plot3D()
    plt.save(j('plot3d'))

    plt = kaxe.PlotCenter3D()
    plt.save(j('plotcenter3d'))

    plt = kaxe.PlotFrame3D()
    plt.save(j('plotframe3d'))

    plt = kaxe.DoubleAxisPlot([0, 10, 0, 10, 0, 5])
    plt.save(j('doubleaxisplot'))

    # ???
    # plt = kaxe.PlotEmpty3D()
    # plt.save(j('plotempty3d.png'))

    chart = kaxe.Pie()
    chart.add( 5.0 , legend="a", label="5")
    chart.add( 3.0 , legend="b", label="3+1-1" )
    chart.add( 2.5 , legend="c", label="2 < x < 3" )
    chart.save(j('pie'))

    chart = kaxe.Bar()
    chart.add("a", [1,2,3,4])
    chart.add("b", [2,4])
    chart.add("c", [4])
    chart.save(j('bar'))

    chart = kaxe.GroupBar()
    chart.add("a", [1,2,3,4])
    chart.add("b", [2,4])
    chart.add("c", [4])
    chart.save(j('groupbar'))

    create2DWithObject(kaxe.Points2D([0,1,2,3,4], [0,1,2,3,4], size=20), 'points2d')
    create2DWithObject(kaxe.Function2D(lambda x: x/2-0.5), 'function2d')
    create2DWithObject(kaxe.Arrow((0,1), (3,-5)), 'arrow')
    create2DWithObject(kaxe.Equation(lambda x,y: x**2 + y**2, lambda x,y: 4**2), 'equation')
    create2DWithObject(kaxe.ColorScale(0, 5), 'colorscale')
    create2DWithObject(kaxe.HeatMap([[j*math.sin(i/20) for j in range(10)] for i in range(10)]), 'heatmap')
    create2DWithObject(kaxe.ParametricEquation(lambda t: (t**2-9, math.sin(t)), [0, 10]), 'parametricequation')
    create2DWithObject(kaxe.Pillars([0, 1, 2], [1, 2, 1]), 'pillars')
    create2DWithObject(kaxe.RootLocus([1, 0, 0, 0, 0, -1], [0, 0, 0, 1, 0, 1]), 'rootlocus', [-1, 1, -2, 2])

    nums = 50
    points = [
        (10*i/nums,10*j/nums,math.sin(i*j/(nums*5))) for j in range(-nums, nums)
        for i in range(-nums, nums)
    ]
    create3DWithObject(kaxe.Points3D(
        [x for x,y,z in points], [y for x,y,z in points], [z for x,y,z in points]
    ), 'points3d')
    create3DWithObject(kaxe.Function3D(lambda x,y: math.sin(x*y/10)), 'function3d')

try:
    copyImagesFromTest()
    createAllDocImages()
except Exception as e:
    print(e)