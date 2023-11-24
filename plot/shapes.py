
from PIL import Image, ImageDraw
from .styles import *
from .helper import *
import os
import numpy as np
import logging

# ENGINE
class engine:
    PILLOW = 'PILLOW'
    
# SET ENGINE
currentEngine = engine.PILLOW #spaghetti
def setEngine(engine):
    global currentEngine
    currentEngine = engine

def getEngine():
    return currentEngine


# HELPER
def blitImageToSurface(surface:Image, image:Image, pos:tuple | list):
    return surface.paste(image, (int(pos[0]), int(pos[1])), image)


def newImage(width, height, color):
    img = Image.new('RGBA', (int(width), int(height)), color=color)
    return img


def flipHorizontal(surface, *flips):
    # flips y's according to surface height
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


# BATCH
class Batch:
    def __init__(self):
        self.objects = []
        self.engine = getEngine()

    def add(self, o):
        self.objects.append(o)

    def push(self, x,y):
        for i in self.objects: i.push(x,y)

    def draw(self, *args, **kwargs):
        for i in self.objects: i.draw(*args, **kwargs)


# BASESHAPE
class Shape:
    def __init__(self):
        self.engine = getEngine()


    def draw(self, *args, **kwargs):
        try:
            if self.engine == engine.PILLOW:
                self.drawPillow(*args, **kwargs)
        except AttributeError:
            logging.critical('No man')

    def push(self, x, y):
        self.x += x
        self.y += y


# SHAPES
# Man kan også bare tegne direkte på istedet for at paste?
class Rectangle(Shape):
    
    def __init__(self, x, y, width, height, color:tuple=BLACK, batch:Batch=None, *args, **kwargs):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.color = color
        self.batch = batch
        super().__init__()
        if batch: batch.add(self)

    
    def centerAlign(self):
        self.x -= self.width/2
        self.y -= self.height/2


    def drawPillow(self, surface:Image):
        [y] = flipHorizontal(surface, self.y)
        img = newImage(self.width, self.height, self.color)
        blitImageToSurface(surface, img, (self.x, y - self.height))

    
    def getBoundingBox(self):
        return [self.width, self.height]


class Line(Shape):
    
    def __init__(self, x0, y0, x1, y1, color:tuple=BLACK, width=1, batch:Batch=None, center:bool=False, *args, **kwargs):
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
        super().__init__()
        if batch: batch.add(self)

    # overwrites push
    def push(self, x, y):
        self.x0 += x
        self.x1 += x
        self.y0 += y
        self.y1 += y


    def drawPyglet(self):
        pg.shapes.Line(self.x0, self.y0, self.x1, self.y1, color=self.color, width=self.thickness)


    def drawPillow(self, surface:Image):
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

        if vConnectLength == 0:
            return

        vConnect = (vConnect[1]/vConnectLength, vConnect[0]/vConnectLength)
        if not self.centerAlign:
            vConnect = (0,0)

        if p1[1] > p2[1]:
            vConnect = (-1*vConnect[0], vConnect[1])

        blitImageToSurface(surface, img, (pos[0]-vConnect[0]*self.thickness//2, pos[1]-vConnect[1]*self.thickness//2))


class Circle(Shape):

    def __init__(self, x:int, y:int, radius:int=5, color:tuple=BLACK, batch:Batch=None, cornerAlign:bool=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.cornerAlign = cornerAlign
        super().__init__()
        if batch: batch.add(self)


    def centerAlign(self):
        self.cornerAlign = False


    def drawPillow(self, surface):
        [y] = flipHorizontal(surface, self.y)

        if not self.cornerAlign:
            y -= self.radius
        else:
            self.x += self.radius   
            y -= 2 * self.radius

        doubleRadius = self.radius*2 # FIX
        img = newImage(doubleRadius*2, doubleRadius*2, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, doubleRadius, doubleRadius), fill=self.color)
        img = img.crop(img.getbbox())
        blitImageToSurface(surface, img, (self.x - self.radius, y))


    def getBoundingBox(self): # returns 
        return [self.radius*2, self.radius*2]


class ImageShape(Shape):
    def __init__(self, file:str|Image.Image, x:int, y:int, batch:Batch=None):
        self.file = file
        self.x = x
        self.y = y
        if batch: batch.add(self)
        super().__init__()

        if type(self.file) is str:
            pass#self.img = pg.shapes

        elif type(self.img) is Image.Image:
            self.img = self.file

        else: #file is something else?
            pass
    

    def centerAlign(self): #rimlig sikker på det her kun virker for pillow
        self.y -= self.img.height/2
        self.x -= self.img.width/2

    
    def getBoundingBox(self):
        return [self.img.width, self.img.height]


    def drawPillow(self, surface):
        return blitImageToSurface(surface, self.img, (self.x, flipHorizontal(surface, self.y)[0] - self.img.height))



# NAMESPACE
class shapes:
    Rectangle = Rectangle
    Line = Line
    Circle = Circle
    Image = ImageShape

    Batch = Batch