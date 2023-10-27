
from PIL import Image, ImageDraw
from .styles import *
from .helper import *

def blitImageToSurface(surface:Image, image:Image, pos:tuple | list):
    return surface.paste(image, (int(pos[0]), int(pos[1])), image)


def newImage(width, height, color):
    img = Image.new('RGBA', (int(width), int(height)), color=color)
    return img


def flipHorizontal(surface, *flips):
    flips = list(flips)
    for i in range(len(flips)):
        flips[i] = surface.height - flips[i]
    return flips


def findMinMax(*pairs):
    #also makes int 
    l = []
    for pair in pairs:
        l.append((int(min(*pair)), int(max(*pair))))
    return l
    

# BATCH MAP
batchMap = {}


def addToBatch(batch, obj):
    if not batch:
        return

    if batch in batchMap:
        batchMap[batch].append(obj)
    else:
        batchMap[batch] = [obj]


def drawStaticBatch(batch, surface):
    objects = batchMap.get(batch)
    if not objects:
        return

    for o in objects:
        o.drawStatic(surface)


# SHAPES
# Man kan også bare tegne direkte på istedet for at paste?
class Rectangle:
    
    def __init__(self, x, y, width, height, color:tuple=BLACK, batch=None, *args, **kwargs):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.color = color
        self.batch = batch
        addToBatch(batch, self)


    def draw(self):
        pass


    def drawStatic(self, surface:Image):
        [y] = flipHorizontal(surface, self.y)
        img = newImage(self.width, self.height, self.color)
        blitImageToSurface(surface, img, (self.x, y - self.height))


class Line:
    
    def __init__(self, x0, y0, x1, y1, color:tuple=BLACK, width=1, batch=None, center:bool=False, *args, **kwargs):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.thickness = width
        self.color = color
        self.batch = batch
        self.width = int(self.x1)
        self.height = int(max(self.y0, self.y1) - min(self.y0, self.y1))
        self.centerAlign = center
        addToBatch(batch, self)


    def draw(self):
        pg.shapes.Line(self.x0, self.y0, self.x1, self.y1, color=self.color, width=self.thickness)


    def drawStatic(self, surface:Image):
        [y0, y1] = flipHorizontal(surface, self.y0, self.y1)
        p1, p2 = (self.x0, y0), (self.x1, y1)
        (mnx, _), (mny, _) = findMinMax((p1[0], p2[0]), (p1[1], p2[1]))

        width = max(self.x0, self.x1) - min(self.x0, self.x1)
        height = max(self.y0, self.y1) - min(self.y0, self.y1)

        img = newImage(width+self.thickness*2, height+self.thickness*2, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        pos = (mnx, mny)
        p1Local = vdiff(pos, p1)
        p2Local = vdiff(pos, p2)

        p1Local = (p1Local[0]+self.thickness, p1Local[1]+self.thickness)
        p2Local = (p2Local[0]+self.thickness, p2Local[1]+self.thickness)

        draw.line((*p1Local, *p2Local), fill=self.color, width=self.thickness)

        vConnect = vdiff(p1Local, p2Local)

        img = img.crop(img.getbbox())

        vConnectLength = vlen(vConnect)
        vConnect = (vConnect[1]/vConnectLength, vConnect[0]/vConnectLength)
        if not self.centerAlign:
            vConnect = (0,0)

        if p1[1] > p2[1]:
            vConnect = (-1*vConnect[0], vConnect[1])


        blitImageToSurface(surface, img, (pos[0]-vConnect[0]*self.thickness//2, pos[1]-vConnect[1]*self.thickness//2))



class Circle:

    def __init__(self, x:int, y:int, radius:int=5, color:tuple=BLACK, batch:pg.shapes.Batch=None):
        addToBatch(batch, self)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    
    def draw(self):
        pass

    
    def drawStatic(self, surface):
        [y] = flipHorizontal(surface, self.y)

        doubleRadius = self.radius*2 # FIX
        img = newImage(doubleRadius*2, doubleRadius*2, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, doubleRadius, doubleRadius), fill=self.color)
        img = img.crop(img.getbbox())
        blitImageToSurface(surface, img, (self.x-self.radius, y-self.radius))



# NAMESPACE
class shapes:
    Rectangle = Rectangle
    Line = Line
    Circle = Circle

    batchMap = batchMap



# SYMBOLS
def shapeBoundingBox(shape):
    
    if type(shape) is shapes.Rectangle:
        return [shape.width, shape.height]


def makeSymbolShapes(symbol:str, height:int, color:tuple, batch):
    return shapes.Rectangle(0, 0, height*2, height/3, color=color, batch=batch)

