
from PIL import Image
from .shapes import ImageShape, shapes, Batch
from .styles import *
import numpy as np
from .fileloader import loadFile

triangle = Image.open(loadFile('symboltriangle.png'))
lollipop = Image.open(loadFile('symbollollipop.png'))
cross = Image.open(loadFile('symbolcross.png'))

class CustomSymbol(ImageShape):
    def __init__(self, symbimg:Image, width:int, height:int, color:tuple=BLACK, batch:Batch=None):
        self.img = symbimg.copy()
        self.img = self.img.resize((width, height))
        
        data = np.array(self.img)
        r2, g2, b2, a2 = *color[:3], 255

        red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        mask = (alpha > 0)
        data[:,:,:4][mask] = [r2, g2, b2, a2]

        self.img = Image.fromarray(data)

        super().__init__(self.img, 0, 0, batch=batch)


# SYMBOLS
class symbol:
    CIRCLE = 'o'
    LINE = 'LINE'
    TRIANGLE = 'TRI'
    STAR = 'STAR'
    RECTANGLE = "RECT"
    LOLLIPOP = 'LOLLIPOP'
    THICKLINE = 'THICKLINE'
    CROSS = "CROSS"


def makeSymbolShapes(symb:str, height:int, color:tuple, batch):
    if symb == symbol.LINE:
        return shapes.Rectangle(0, 0, height, height/6, color=color, batch=batch)
    if symb == symbol.THICKLINE:
        return shapes.Rectangle(0, 0, height, height/2, color=color, batch=batch)
    if symb == symbol.RECTANGLE:
        return shapes.Rectangle(0, 0, height, height, color=color, batch=batch)
    if symb == symbol.CIRCLE:
        return shapes.Circle(0,0, int(height/2), cornerAlign=True, color=color, batch=batch)
    if symb == symbol.TRIANGLE:
        return CustomSymbol(triangle, height, height, color=color, batch=batch)
    if symb == symbol.LOLLIPOP:
        return CustomSymbol(lollipop, height, height, color=color, batch=batch)
    if symb == symbol.CROSS:
        return CustomSymbol(cross, height, height, color=color, batch=batch)
