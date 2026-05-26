"""
2D-to-3D translator bridge for hybrid plot objects.

When a 2D object is added to a Plot3D, some types rasterize on a throwaway
EmptyWindow, then lift Pillow shapes into OpenGL primitives at z=0.

3D support by object:
- Bridge (this module): Function2D, Equation; Contour via nested Equation
- Native finalize3D: Arrow, Parameter
- objects/d3/: Function3D, Points3D, Mesh, Potato, SolidOfRotation
- Overlay-only / no geometry: Text, HeatMap (declare XYZ in supports but no 3D finalize)
"""

from .backend import RenderBackend
from ..shapes import Shape, Line, Circle, Triangle, Batch, LineSegment

from .objects import * # Line3D, Point3D, TextureQuad, Triangle
from .helper import formatColor

from ...plot.empty import EmptyWindow
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from ...plot.d3 import Plot3D

def getEquivalent2DPlot(parent:"Plot3D") -> EmptyWindow:

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
    render: RenderBackend = plt3d.render

    now = time.time()
    for shape in objs:
        
        #### Circle
        if type(shape) is Circle:
            x, y = plt2d.inversepixel(shape.x, shape.y)
            render.add3DObject( Point3D(*plt3d.pixel(x, y, 0), shape.radius, color=formatColor(shape.color)) )
    
        
        ### Line
        if type(shape) is Line:
            x1, y1 = plt2d.inversepixel(shape.x0, shape.y0)
            x1, y1, z1 = plt3d.pixel(x1, y1, 0)

            x2, y2 = plt2d.inversepixel(shape.x1, shape.y1)
            x2, y2, z2 = plt3d.pixel(x2, y2, 0)

            render.add3DObject( Line3D((x1, y1, z1), (x2, y2, z2), color=shape.color, width=shape.thickness) )


        ### Line segment
        if type(shape) is LineSegment:
            
            for i in range(len(shape.points)-1):
                x1, y1 = plt2d.inversepixel(*shape.points[i])
                x1, y1, z1 = plt3d.pixel(x1, y1, 0)

                x2, y2 = plt2d.inversepixel(*shape.points[i+1])
                x2, y2, z2 = plt3d.pixel(x2, y2, 0)
            
                render.add3DObject( Line3D((x1, y1, z1), (x2, y2, z2), color=shape.color, width=shape.thickness) )

    # print(time.time() - now, 's to translate 2D batch to 3D objects')