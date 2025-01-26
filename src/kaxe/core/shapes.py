
# https://pypi.org/project/drawsvg/

from random import randint
from PIL import Image, ImageDraw
from .styles import *
from .helper import *
from .line import drawLineOnPillowImage
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


def prepColor(color):
    return tuple(int(round(i)) for i in color)



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
        self.color = prepColor(color)
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


    def drawPillowSimple(self, surface:Image):
        # does not support alpha channel

        [y0, y1] = flipHorizontal(surface, self.y0, self.y1)

        draw = ImageDraw.Draw(surface)

        if self.thickness > 0:
            draw.line((self.x0, y0, self.x1, y1), fill=self.color, width=self.thickness)


    def drawPillowNew(self, surface:Image):

        [y0, y1] = flipHorizontal(surface, self.y0, self.y1)

        # Make an overlay image the same size as the specified image, initialized to
        # a fully transparent (0% opaque) version of the line color, then draw a
        # semi-transparent line on it.
        overlay = Image.new('RGBA', surface.size, (0,0,0,0))
        draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
        draw.line((self.x0, y0, self.x1, y1), fill=self.color, width=self.thickness)
        # Alpha composite the overlay image onto the original.
        surface.alpha_composite(overlay)

    def drawFromNumpyArray(self, surface:Image):

        if self.thickness == 0:
            return

        [y0, y1] = flipHorizontal(surface, self.y0, self.y1)        

        drawLineOnPillowImage(
            surface,
            self.x0,
            y0,
            self.x1,
            y1,
            self.color,
            self.thickness
        )



    def drawPillow(self, surface:Image):
        # return self.drawPillowAlpha(surface)
        return self.drawFromNumpyArray(surface)
        return self.drawPillowNew(surface)
        return self.drawPillowSimple(surface)


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

        if type(file) is str:
            pass#self.img = pg.shapes

        elif type(file) is Image.Image:
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
    
    def __init__(self, points, color:tuple=BLACK, width=1, batch:Batch=None, center:bool=False, dotted=False, dottedDist=30, dashed=False, dashedDist=30, *args, **kwargs):
        self.points = points
        self.x = [x for x,y in self.points]
        self.y = [y for x,y in self.points]
        self.dotted = dotted
        self.dottedDist = dottedDist
        self.dashed = dashed
        self.dashedDist = dashedDist
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


    def __drawDottedLines__(self, draw:ImageDraw.ImageDraw, pos):
        
        # find distance
        lastPoint = pos[0], pos[1]
        for i in range(2, len(pos), 2):
            x, y = pos[i], pos[i+1]
            dist = np.linalg.norm((lastPoint[0] - x, lastPoint[1] - y))
            if dist > self.dottedDist:
                lastPoint = (x,y)
                draw.circle((x,y), self.thickness, fill=self.color)

    
    def __drawDashedLines__(self, draw:ImageDraw.ImageDraw, pos):

        # find distance
        lastPoint = pos[0], pos[1]
        drewLastPoint = False
        for i in range(2, len(pos), 2):
            x, y = pos[i], pos[i+1]
            dist = np.linalg.norm((lastPoint[0] - x, lastPoint[1] - y))
            if dist > self.dashedDist:
                
                if not drewLastPoint: # hvis forrige punkt ikke blev tegnet
                    draw.line((*lastPoint, x,y), width=self.thickness, fill=self.color)
                    drewLastPoint = True
                else:
                    drewLastPoint = False
                
                lastPoint = (x,y)


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

        if self.dotted:
            self.__drawDottedLines__(draw, newpos)
        elif self.dashed:
            self.__drawDashedLines__(draw, newpos)
        else:
            draw.line(newpos, fill=self.color, width=self.thickness, joint="curve")



class Arc(Shape):
    
    def __init__(self, phaseshift:int, angle:int, center:tuple, radius:int, color:tuple=BLACK, batch:Batch=None, *args, **kwargs):
        """
        phaseshift and angle is in degrees
        """

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
    Line = Line # to points
    Circle = Circle
    Triangle=Triangle
    Polygon=Polygon
    Image = ImageShape
    ImageArray = ImageArrayShape
    Batch = Batch
    LineSegment = LineSegment # multiple points
    Arc = Arc
