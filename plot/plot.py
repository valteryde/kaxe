
import math
import time
from .helper import *
import logging
from .styles import *
from .axis import *
from .text import Text, getTextDimension
from .legend import LegendBox
from pyglet.gl import *
from .shapes import shapes
from .symbol import makeSymbolShapes
from PIL import Image
import tqdm
from random import randint
import os

"""
structure to parent + child

Axis is diffrent from other objects

To be done:
    pass
"""

class Plot:
    def __init__(self,  window:list=None, trueAxis:bool=None, logarithmic=[None, None]): # |
        """
        trueAxis:bool dictates if line intersection should be (0,0), only works with standard basis

        window:tuple [x0, x1, y0, y1] axis

        left to right is always positive
        bottom to top is always positive
        """
        
        self.firstAxis = None
        self.secondAxis = None
        self.axis = [lambda: self.firstAxis, lambda: self.secondAxis]
        self.untrueAxis = not trueAxis
        self.logarithmic = logarithmic

        # options
        self.windowAxis = window
        if self.windowAxis is None: self.windowAxis = [None, None, None, None]

        self.shapes = []
        self.objects = []
        self.legendObjects = []
        self.legendBatch = shapes.Batch()
        self.legendBoxShape = shapes.Batch()
        
        self.scale = (0,0)
        self.offset = [0,0]
        self.padding = [0,0,0,0] #computed padding
        self.firstTitle = None
        self.secondTitle = None

        # styles
        self.width = None
        self.height = None
        self.backgroundColor = None
        self.markerColor = None
        self.markerWidth = None
        self.markerLength = None
        self.font = None
        self.gridLines = None
        self.gridLineColor = None
        self.fontSize = None
        self.markerStepSizeBand = None
        self.outerPadding = None

        
    def style(
            self, 
            __overwrite__:tuple=True,
            windowWidth:int=None,
            windowHeight:int=None,
            padding:list=None,
            backgroundColor:tuple=None, 
            markerColor:tuple=None,
            markerWidth:int=None,
            markerLength:int=None,
            fontSize:int=None,
            font:str=None,
            gridLines:bool=None,
            gridLineColor:tuple=None,
            markerStepSizeBand:tuple=None
        ):
        """
        change style on plotting window
        padding: left, bottom, top, right
        """

        if not __overwrite__:
            if not windowWidth is None and self.width is None: self.width = windowWidth
            if not windowHeight is None and self.height is None: self.height = windowHeight
            if not padding is None and self.outerPadding is None: self.outerPadding = list(padding)
            if not backgroundColor is None and self.backgroundColor is None: self.backgroundColor = backgroundColor
            if not markerColor is None and self.markerColor is None: self.markerColor = markerColor
            if not markerWidth is None and self.markerWidth is None: self.markerWidth = markerWidth
            if not markerLength is None and self.markerLength is None: self.markerLength = markerLength
            if not font is None and self.font is None: self.font = font
            if not gridLines is None and self.gridLines is None: self.gridLines = gridLines
            if not gridLineColor is None and self.gridLineColor is None: self.gridLineColor = gridLineColor
            if not fontSize is None and self.fontSize is None: self.fontSize = fontSize
            if not markerStepSizeBand is None and self.markerStepSizeBand is None: self.markerStepSizeBand = markerStepSizeBand

        else:
            if not windowWidth is None: self.width = windowWidth
            if not windowHeight is None: self.height = windowHeight
            if not padding is None: self.outerPadding = list(padding)
            if not backgroundColor is None: self.backgroundColor = backgroundColor
            if not markerColor is None: self.markerColor = markerColor
            if not markerWidth is None: self.markerWidth = markerWidth
            if not markerLength is None: self.markerLength = markerLength
            if not font is None: self.font = font
            if not gridLines is None: self.gridLines = gridLines
            if not gridLineColor is None: self.gridLineColor = gridLineColor
            if not fontSize is None: self.fontSize = fontSize
            if not markerStepSizeBand is None: self.markerStepSizeBand = markerStepSizeBand

        if self.width and self.fontSize is None: self.fontSize = int(self.width/70)
        if self.fontSize and self.markerStepSizeBand is None: self.markerStepSizeBand = [int(self.fontSize*7), int(self.fontSize*4)]


        # package options
        self.markerOptions = {
            "color":self.markerColor,
            "fontSize":self.fontSize, 
            "markerWidth":self.markerWidth,
            "markerLength":self.markerLength,
            "gridlineColor":self.gridLineColor,
            "showLine":self.gridLines
        }

        return self


    def theme(self, theme):
        """
        use a defined theme
        
        calls self.style
        """
        self.style(**theme)


    def include(self, cx, cy, width, height):
        """includes cx, cy in frame by adding padding"""
        dx = min(cx - width/2, 0)
        dy = min(cy - height/2, 0)
        dxm = min(self.width - (cx + width/2), 0)
        dym = min(self.height - (cy + height/2), 0)

        if dx < 0 or dy < 0 or dxm < 0 or dym < 0:
            self.addPaddingCondition(left=-(dx), bottom=-(dy), right=-(dxm), top=-(dym))


    def addPaddingCondition(self, left:int=0, bottom:int=0, top:int=0, right:int=0):
        # could be a problem depending on where padding is calcualted
        left = int(left)
        right = int(right)
        bottom = int(bottom)
        top = int(top)

        self.padding = (
            self.padding[0] + left,
            self.padding[1] + bottom,
            self.padding[2] + right,
            self.padding[3] + top,
        )

        # opdater ikke disse. Forskellen er indlejret i padding
        # self.offset[0] += left
        # self.offset[1] += bottom

        self.windowBox = (self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1])

        for i in self.shapes:
            if type(i) is tuple: # list is still unsorted
                i[0].push(left, bottom)
                continue
            i.push(left, bottom)
        
        # for i in self.objects:
        #     i.push(left, bottom)


    def __setWindowDimensionBasedOnAxis__(self, firstAxis:Axis, secondAxis:Axis):
        
        p1, p2 = firstAxis.getEndPoints()
        p3, p4 = secondAxis.getEndPoints()
        
        minX = min(p1[0], p2[0], p3[0], p4[0])
        minY = min(p1[1], p2[1], p3[1], p4[1])
        maxX = max(p1[0], p2[0], p3[0], p4[0])
        maxY = max(p1[1], p2[1], p3[1], p4[1])

        if self.standardBasis and self.untrueAxis:
            xLength = max(abs(p2[0]-p1[0]), abs(p3[0]-p4[0]))
            yLength = max(abs(p2[1]-p1[1]), abs(p3[1]-p4[1]))
            self.scale = (self.width / xLength, self.height / yLength)
            
            self.offset = [minX*self.scale[0], minY*self.scale[1]]

            # move axis to untrue visual values
            # if firstaxis is vertical
            # move secondaxis
            if firstAxis.hasNull:
                secondAxis.finalize(self, vectorMultipliciation(firstAxis.get(0), self.scale))

            elif firstAxis.end < 0:
                secondAxis.finalize(self, vectorMultipliciation(firstAxis.get(firstAxis.end), self.scale))

            else:
                secondAxis.finalize(self)

            # move firstaxis
            if secondAxis.hasNull:
                firstAxis.finalize(self, vectorMultipliciation(secondAxis.get(0), self.scale))
            
            elif secondAxis.end < 0:
                firstAxis.finalize(self, vectorMultipliciation(secondAxis.get(secondAxis.end), self.scale))

            else:
                firstAxis.finalize(self)

        else: # use full scale

            xLength = abs(maxX - minX)
            yLength = abs(maxY - minY)
            self.scale = (self.width / xLength, self.height / yLength)
            self.offset = [minX*self.scale[0], minY*self.scale[1]]

            firstAxis.finalize(self)
            secondAxis.finalize(self)

        nullX, nullY = self.pixel(0,0)
        self.nullInPlot = insideBox(self.windowBox, (nullX, nullY))


    def __createStandardAxis__(self):
        if self.firstAxis: return # or self.secondAxis

        self.standardBasis = True
        
        if self.logarithmic[0]:
            self.firstAxis = Axis((1,0), func=math.log10, invfunc=lambda x: math.pow(10, x))
        else:
            self.firstAxis = Axis((1,0))
        
        if self.logarithmic[1]:
            self.secondAxis = Axis((0,1), func=math.log10, invfunc=lambda x: math.pow(10, x))
        else:
            self.secondAxis = Axis((0,1))


    def __calculateWindowBorders__(self):
        """
        where all objects is in
        unless windowAxis is already specefied
        """
        if sorted(self.windowAxis, key=lambda x: x==None)[-1] == None:
            horizontal = []
            vertical = []
            for i in self.objects:
                try:
                    horizontal.append(i.farLeft)
                    horizontal.append(i.farRight)
                    vertical.append(i.farTop)
                    vertical.append(i.farBottom)
                except AttributeError:
                    continue
            
            try:
                if not self.windowAxis[0]: self.windowAxis[0] = min(horizontal)
                if not self.windowAxis[1]: self.windowAxis[1] = max(horizontal)
                if not self.windowAxis[2]: self.windowAxis[2] = min(vertical)
                if not self.windowAxis[3]: self.windowAxis[3] = max(vertical)
            except Exception as e:
                logging.warn(e) # not tested
                self.windowAxis = [-10, 10, -5, 5]
        
        if self.untrueAxis is None:
            
            # is null in x0, x1 and y0, y1?
            self.untrueAxis = False
            if self.standardBasis and (min(self.windowAxis[0], self.windowAxis[1]) < 0 or max(self.windowAxis[2], self.windowAxis[3]) > 0):
                self.untrueAxis = True

        else:
            self.untrueAxis = self.untrueAxis


    def bake(self):
        # finish making plot
        # fit "plot" into window 
        startTime = time.time()

        self.__calculateWindowBorders__()
        
        self.__createStandardAxis__()
        self.firstAxis._addStartAndEnd(self.windowAxis[0], self.windowAxis[1], makeOffsetAvaliable=self.untrueAxis)
        self.secondAxis._addStartAndEnd(self.windowAxis[2], self.windowAxis[3], makeOffsetAvaliable=self.untrueAxis)

        # computed options, padding needs to set before this point
        self.windowBox = (self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1])
        self.nullInPlot = False

        self.__setWindowDimensionBasedOnAxis__(self.firstAxis, self.secondAxis)
        self.firstAxis._addMarkersToAxis(self)
        self.secondAxis._addMarkersToAxis(self)

        # legend & title
        if self.firstTitle: self.firstAxis._addTitle(self.firstTitle, self)
        if self.secondTitle: self.secondAxis._addTitle(self.secondTitle, self)
        
        self.legendbox = LegendBox(*self.objects)
        self.legendbox.finalize(self)

        if self.untrueAxis and not self.standardBasis:
            logging.warn('untrueAxis is on, but Axis+Axis is not a standard basis')

        # objects
        pbar = tqdm.tqdm(total=len(self.objects), desc='Baking')
        for obj in self.objects:
            obj.finalize(self)
            pbar.update()
            self.addDrawingFunction(obj)
        pbar.close()

        self.shapes = [i[0] for i in sorted(self.shapes, key=lambda x: x[1])]

        # add back outerPadding
        self.addPaddingCondition(*self.outerPadding)

        logging.info('Compiled in {}s'.format(str(round(time.time() - startTime, 4))))


    # translations
    def pos(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: abstract value
        """
        
        x -= self.firstAxis.offset
        y -= self.secondAxis.offset

        return (
            self.firstAxis.directionVector[0] * x + self.secondAxis.directionVector[0] * y,
            self.firstAxis.directionVector[1] * x + self.secondAxis.directionVector[1] * y
        )


    def translate(self, x:int, y:int) -> tuple:
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: translated value
        """

        return (
            self.firstAxis._translate(x) * self.scale[0] - self.offset[0] + self.padding[0],
            self.secondAxis._translate(y) * self.scale[1] - self.offset[1] + self.padding[1]
        )


    def scaled(self, x, y):
        return self.scale[0]*x, self.scale[1]*y


    def pixel(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """

        x, y = self.pos(x, y)
        return self.translate(x,y)


    def inversepixel(self, x:int, y:int):
        """
        para: pixel values according to axis
        return abstract value
        """

        x, y = self.inversetranslate(x,y)
        
        x += self.firstAxis.offset
        y += self.secondAxis.offset

        v1 = self.firstAxis.directionVector
        v2 = self.secondAxis.directionVector

        #b = (-r__b*v__1a + r__a)/(v__1a*v__2b + v__1b*v__2a)
        b = (v1[0]*y - v2[0]*x)/(v1[0]*v2[1] - v1[1]*v2[0])

        #a = (-b*v__1b + r__a)/v__1a
        a = (-b*v1[1] + x)/v1[0]

        return a, b


    def line(self, pos, n): # -> name e.g lineOnWindowBorder
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: two translated values on border of plot
        """
        
        return boxIntersectWithLine(self.windowBox, [n[0]*self.scale[0], n[1]*self.scale[1]], self.translate(*pos))

    
    def inside(self, x, y):
        """
        para: translated
        """
        return insideBox(self.windowBox, (x,y))


    def inversetranslate(self, x:int=None, y:int=None):
        """
        para: translated value
        return: x,y position according to basis (1,0), (0,1) in abstract space
        """

        p = [None, None]
        if not x is None: p[0] = (self.firstAxis._invtranslate(x)+self.offset[0]-self.padding[0])/self.scale[0]
        if not y is None: p[1] = (self.secondAxis._invtranslate(y)+self.offset[1]-self.padding[1])/self.scale[1]

        return p


    # shape
    def addDrawingFunction(self, shape, z=0):
        self.shapes.append((shape, z))


    # api
    def add(self, o):
        self.objects.append(o)

    
    def title(self, first=None, second=None):
        self.firstTitle = first
        self.secondTitle = second
        return self


    def setAxis(self, first:Axis, second:Axis):
        self.firstAxis = first
        self.secondAxis = second
        self.standardBasis = (first.v[0] == 0 or first.v[1] == 0) and (second.v[0] == 0 or second.v[1] == 0)


    # bake functions
    def show(self, static:bool=True):

        if static:
            fname = '.__tempImage{}.png'.format(''.join([str(randint(0,9)) for i in range(10)]))
            self.save(fname)
            pilImage = Image.open(fname)
            pilImage.show()
            os.remove(fname)
            return


    def save(self, fname):
        
        totStartTime = time.time()

        self.style(
            windowWidth=2000,
            windowHeight=1500,
            # padding=(100,100,100,100),
            padding=(20,20,20,20),
            backgroundColor=WHITE,
            markerColor=BLACK,
            markerLength=20,
            markerWidth=3,
            # fontSize=10,
            font = "Times New Roman",
            gridLineColor=(200,200,200,255),
            gridLines = True,
            # markerStepSizeBand=[200, 150],
            __overwrite__=False
        )

        self.bake()
        startTime = time.time()
        pbar = tqdm.tqdm(total=len(self.shapes), desc='Decorating')

        winSize = self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3]
        background = shapes.Rectangle(0,0,winSize[0], winSize[1], color=self.backgroundColor)
        surface = Image.new('RGBA', winSize)

        background.draw(surface)

        for shape in self.shapes:
            shape.draw(surface)
            pbar.update()

        surface.save(fname)
        pbar.close()
        logging.info('Painted in {}s'.format(str(round(time.time() - startTime, 4))))
        logging.info('Total time to save {}s'.format(str(round(time.time() - totStartTime, 4))))
    
    