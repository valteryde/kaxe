
from .render import Render
from ..shapes import Shape, Line, Circle, Triangle, Batch, LineSegment

from .objects import * # Line3D, Point3D, TextureQuad, Triangle

from ...plot.empty import EmptyWindow
from ...plot.d3 import Plot3D

def getEquivalent2DPlot(parent:Plot3D) -> EmptyWindow:

    plt = EmptyWindow(parent.window[:5])
    plt.style(
        width=2000, 
        height=2000,
        outerPadding=[0,0,0,0]
    )
    plt.showProgressBar = False
    plt.printDebugInfo = False
    plt.__bake__()
    del plt.__bakedImage__ # dont save large image in memory
    
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
            render.add3DObject( Point3D(*plt3d.pixel(x, y, 0), shape.radius, color=shape.color) )
    
        
        ### Line
        if type(shape) is Line:
            x1, y1 = plt2d.inversepixel(shape.x0, shape.y0)
            x1, y1, z1 = plt3d.pixel(x, y, 0)

            x2, y2 = plt2d.inversepixel(shape.x1, shape.y1)
            x2, y2, z2 = plt3d.pixel(x, y, 0)

            render.add3DObject( Line3D((x1, y1, z1), (x2, y2, z2), color=shape.color, width=shape.thickness) )


        ### Line segment
        if type(shape) is LineSegment:
            
            for i in range(len(shape.points)-1):
                x1, y1 = plt2d.inversepixel(*shape.points[i])
                x1, y1, z1 = plt3d.pixel(x, y, 0)

                x2, y2 = plt2d.inversepixel(*shape.points[i+1])
                x2, y2, z2 = plt3d.pixel(x, y, 0)
            
                render.add3DObject( Line3D((x1, y1, z1), (x2, y2, z2), color=shape.color, width=shape.thickness) )

