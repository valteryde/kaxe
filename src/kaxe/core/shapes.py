
from random import randint
from PIL import Image, ImageDraw
from .styles import *
from .helper import *
import os
import numpy as np
import logging
from typing import Union

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
def blitImageToSurface(surface:Image, image:Image, pos:Union[tuple, list]):
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
        self.__hidden__ = False


    def draw(self, *args, **kwargs):
        if self.__hidden__:return

        try:
            if self.engine == engine.PILLOW:
                self.drawPillow(*args, **kwargs)
        except AttributeError:
            logging.critical('No man')

    
    def hide(self):
        self.__hidden__ = True

    def show(self):
        self.__hidden__ = False


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


    def drawPillowOld(self, surface:Image):
        [y0, y1] = flipHorizontal(surface, self.y0, self.y1)
        p1, p2 = (self.x0, y0), (self.x1, y1)
        (mnx, _), (mny, _) = findMinMax((p1[0], p2[0]), (p1[1], p2[1]))

        width = max(self.x0, self.x1) - min(self.x0, self.x1)
        height = max(self.y0, self.y1) - min(self.y0, self.y1)

        if width > 10000 or height > 10000:
            return

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


    def drawPillow(self, surface:Image):
        [y0, y1] = flipHorizontal(surface, self.y0, self.y1)

        draw = ImageDraw.Draw(surface)

        if self.thickness > 0:
            draw.line((self.x0, y0, self.x1, y1), fill=self.color, width=self.thickness)


class Circle(Shape):

    def __init__(self, x:int, y:int, radius:int=5, color:tuple=BLACK, batch:Batch=None, cornerAlign:bool=False, fill:bool=True, width:int=5):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.cornerAlign = cornerAlign
        self.fill = fill
        self.width = width
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
        if self.fill:
            draw.ellipse((0, 0, doubleRadius, doubleRadius), fill=self.color)
        else:
            draw.ellipse((0, 0, doubleRadius, doubleRadius), outline=self.color, width=self.width)
        img = img.crop(img.getbbox())
        blitImageToSurface(surface, img, (self.x - self.radius, y))


    def getBoundingBox(self): # returns 
        return [self.radius*2, self.radius*2]


class ImageShape(Shape):
    def __init__(self, file:Union[str, Image.Image], x:int, y:int, batch:Batch=None):
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


class ImageArrayShape(Shape):
    def __init__(self, imarr:np.ndarray, x:int, y:int, batch:Batch=None):
        self.file = imarr
        self.x = x
        self.y = y
        if batch: batch.add(self)
        super().__init__()
        self.img = Image.fromarray(imarr)


    def centerAlign(self): #rimlig sikker på det her kun virker for pillow
        self.y -= self.img.height/2
        self.x -= self.img.width/2

    
    def getBoundingBox(self):
        return [self.img.width, self.img.height]


    def drawPillow(self, surface):
        return blitImageToSurface(surface, self.img, (self.x, flipHorizontal(surface, self.y)[0] - self.img.height))


class Triangle(Shape):

    def __init__(self, p1, p2, p3, color:tuple=BLACK, batch:Batch=None, *args, **kwargs):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.color = color
        self.batch = batch
        super().__init__()
        if batch: batch.add(self)

        p1, p2, p3 = map(lambda p: (int(p[0]), int(p[1])), [self.p1, self.p2, self.p3])
        
        maxcorner = (max(p1[0], p2[0], p3[0]), max(p1[1], p2[1], p3[1]))
        mincorner = (min(p1[0], p2[0], p3[0]), min(p1[1], p2[1], p3[1]))
        
        self.x = mincorner[0]
        self.y = mincorner[1]
        self.width = maxcorner[0] - mincorner[0]
        self.height = maxcorner[1] - mincorner[1]

        self.img = Image.new('RGBA', size=(maxcorner[0]-mincorner[0], maxcorner[1]-mincorner[1]), color=(0,0,0,0))
        imgdraw = ImageDraw.ImageDraw(self.img)
        
        p1, p2, p3 = map(lambda p: (p[0]-mincorner[0], p[1]-mincorner[1]), [self.p1, self.p2, self.p3])

        imgdraw.polygon([p1, p2, p3], fill = self.color)

    
    def drawPillow(self, surface:Image):
        [y] = flipHorizontal(surface, self.y)
        img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        blitImageToSurface(surface, img, (self.x, y - self.height))

    
    def getBoundingBox(self):
        return [self.width, self.height]


    def push(self, x, y):
        self.x += x
        self.y += y
        self.p1 = (self.p1[0]+x, self.p1[1]+y)
        self.p2 = (self.p2[0]+x, self.p2[1]+y)
        self.p3 = (self.p3[0]+x, self.p3[1]+y)



class Polygon(Shape):

    def __init__(self, *points, color:tuple=BLACK, batch:Batch=None):
        self.color = color
        self.batch = batch
        super().__init__()
        if batch: batch.add(self)

        points = list(map(lambda p: tuple(map(int, p)), points))

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        maxcorner = (max(*xs), max(*ys))
        mincorner = (min(*xs), min(*ys))
        
        self.x = mincorner[0]
        self.y = mincorner[1]
        self.width = maxcorner[0] - mincorner[0]
        self.height = maxcorner[1] - mincorner[1]

        self.img = Image.new('RGBA', size=(maxcorner[0]-mincorner[0], maxcorner[1]-mincorner[1]), color=(0,0,0,0))
        imgdraw = ImageDraw.ImageDraw(self.img)
        
        self.points = list(map(lambda p: (p[0]-mincorner[0], p[1]-mincorner[1]), points))

        imgdraw.polygon(self.points, fill = self.color)

    
    def drawPillow(self, surface:Image):
        [y] = flipHorizontal(surface, self.y)
        img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        blitImageToSurface(surface, img, (self.x, y - self.height))

    
    def getBoundingBox(self):
        return [self.width, self.height]



class LineSegment(Shape):
    
    def __init__(self, points, color:tuple=BLACK, width=1, batch:Batch=None, center:bool=False, *args, **kwargs):
        self.points = points
        self.x = [x for x,y in self.points]
        self.y = [y for x,y in self.points]
        self.thickness = width
        self.color = color
        self.batch = batch
        self.centerAlign = center
        self.offset = [0,0]
        super().__init__()
        if batch: batch.add(self)


    # overwrites push
    def push(self, x, y):
        self.offset[0] += x
        self.offset[1] += y


    def drawPillow(self, surface:Image):
        #[y0, y1] = flipHorizontal(surface, self.y0, self.y1)

        if len(self.points) <= 2:
            #print('For få punkter')
            return

        draw = ImageDraw.Draw(surface)
        
        newpos = []
        for x,y in self.points:
            newpos.append(x+self.offset[0])
            newpos.append(flipHorizontal(surface, y+self.offset[1])[0])

        draw.line(newpos, fill=self.color, width=self.thickness, joint="curve")



class Arc(Shape):
    
    def __init__(self, phaseshift:int, angle:int, center:tuple, radius:int, color:tuple=BLACK, batch:Batch=None, *args, **kwargs):
        self.phaseshift = phaseshift
        self.angle = angle
        self.radius = int(radius)
        self.center = [center[0], center[1]]
        
        self.color = color
        self.batch = batch
        
        super().__init__()
        if batch: batch.add(self)


    # overwrites push
    def push(self, x, y):
        self.center[0] += x
        self.center[1] += y


    def drawPillow(self, surface:Image):
        [self.center[1]] = flipHorizontal(surface, self.center[1])

        doubleRadius = self.radius*2
        img = newImage(doubleRadius, doubleRadius, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        draw.pieslice((0,0, doubleRadius, doubleRadius), -self.angle-self.phaseshift, -self.phaseshift, fill=self.color)

        blitImageToSurface(surface, img, (self.center[0]-self.radius, self.center[1]-self.radius))


# NAMESPACE
class shapes:
    Rectangle = Rectangle
    Line = Line
    Circle = Circle
    Triangle=Triangle
    Polygon=Polygon
    Image = ImageShape
    ImageArray = ImageArrayShape
    Batch = Batch
    LineSegment = LineSegment
    Arc = Arc
