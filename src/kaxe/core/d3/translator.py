
from .render import Render
from ..shapes import Shape, Line, Circle, Triangle, Batch

from .objects import * # Line3D, Point3D, TextureQuad, Triangle

from ...plot.empty import EmptyWindow
from ...plot.d3 import Plot3D

# 
def getEquivalent2DPlot(parent:Plot3D) -> EmptyWindow:
    plt = EmptyWindow(parent.window[:5])
    plt.style(
        width=parent.getAttr('width'), 
        height=parent.getAttr('height'),
        outerPadding=[0,0,0,0]
    )
    plt.__bake__()

    
    # add 
    plt.__3DPlotRef = parent
    return plt


def has3DReference(parent) -> bool:
    return hasattr(parent, '__3DPlotRef')


# recurssive unpacking
def unpackBatch(batch:Batch) -> list[Shape]:
    """
    Get ("unpack") all shapes in 2D batch recurssivly

    Also cleans batch
    """

    result = []

    for shape in batch.objects:

        if type(shape) is Batch:
            result.extend(unpackBatch(shape))
            continue

        result.append(shape)

    # clean
    batch.objects.clear()
    return result

    

def translate2DTo3DObjects(plt2d:EmptyWindow, batch):

    objs:list[Shape] = unpackBatch(batch)
    plt3d:Plot3D = plt2d.__3DPlotRef
    render:Render = plt3d.render

    for shape in objs:
        
        #### Circle
        if type(shape) is Circle:
            x, y = plt2d.inversepixel(shape.x, shape.y)
            render.add3DObject( Point3D(*plt3d.pixel(x, y, 0), 2, color=shape.color) )
    
    # render.add3DObject(
    #     Triangle(
    #         p1,
    #         p2,
    #         p3,
    #         color=color
    #     )
    # )



