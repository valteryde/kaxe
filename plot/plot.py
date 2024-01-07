
from .helper import *
import logging
from .axis import *
from .window import Window

XYPLOT = 'xy'

class Plot(Window):
    
    def __init__(self,  window:list=None, trueAxis:bool=None): # |
        super().__init__()
        self.identity = XYPLOT

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

        # options
        self.windowAxis = window
        if self.windowAxis is None: self.windowAxis = [None, None, None, None]

        self.scale = (0,0)
        self.firstTitle = None
        self.secondTitle = None


    # creating plotting window
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
        self.firstAxis = Axis((1,0))
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


    def __prepare__(self):
        # finish making plot
        # fit "plot" into window 

        self.__calculateWindowBorders__()
        self.__createStandardAxis__()

        self.firstAxis.addStartAndEnd(self.windowAxis[0], self.windowAxis[1], makeOffsetAvaliable=self.untrueAxis)
        self.secondAxis.addStartAndEnd(self.windowAxis[2], self.windowAxis[3], makeOffsetAvaliable=self.untrueAxis)

        self.windowBox = (self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1])
        self.nullInPlot = False

        self.__setWindowDimensionBasedOnAxis__(self.firstAxis, self.secondAxis)
        self.firstAxis.addMarkersToAxis(self)
        self.secondAxis.addMarkersToAxis(self)

        # title
        if self.firstTitle: self.firstAxis.addTitle(self.firstTitle, self)
        if self.secondTitle: self.secondAxis.addTitle(self.secondTitle, self)
        
        if self.untrueAxis and not self.standardBasis:
            logging.warn('untrueAxis is on, but Axis+Axis is not a standard basis')

        # klar til at færdiggøre

    # special api
    def title(self, first=None, second=None):
        self.firstTitle = first
        self.secondTitle = second
        return self


    def setAxis(self, first:Axis, second:Axis):
        self.firstAxis = first
        self.secondAxis = second
        self.standardBasis = (first.v[0] == 0 or first.v[1] == 0) and (second.v[0] == 0 or second.v[1] == 0)


    # translations    
    def scaled(self, x, y):
        return self.scale[0]*x, self.scale[1]*y


    def translate(self, x:int, y:int) -> tuple:
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: translated value
        """

        return (
            self.firstAxis._translate(x) * self.scale[0] - self.offset[0] + self.padding[0],
            self.secondAxis._translate(y) * self.scale[1] - self.offset[1] + self.padding[1]
        )

    
    def inversetranslate(self, x:int=None, y:int=None):
        """
        para: translated value
        return: x,y position according to basis (1,0), (0,1) in abstract space
        """

        p = [None, None]
        if not x is None: p[0] = (self.firstAxis._invtranslate(x)+self.offset[0]-self.padding[0])/self.scale[0]
        if not y is None: p[1] = (self.secondAxis._invtranslate(y)+self.offset[1]-self.padding[1])/self.scale[1]

        return p

    def pixel(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """

        x -= self.firstAxis.offset
        y -= self.secondAxis.offset

        x = self.firstAxis.directionVector[0] * x + self.secondAxis.directionVector[0] * y
        y = self.firstAxis.directionVector[1] * x + self.secondAxis.directionVector[1] * y

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


    def pointOnWindowBorderFromLine(self, pos, n): # -> former def line(...)
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: two translated values on border of plot
        """
        
        return boxIntersectWithLine(self.windowBox, [n[0]*self.scale[0], n[1]*self.scale[1]], self.translate(*pos))


    def inside(self, x, y):
        """
        para: translated
        (pixels)
        """
        return insideBox(self.windowBox, (x,y))

    
    def clamp(self, x:int=0, y:int=0):
        """
        clamps value to window max and min
        para: pixels
        """
        return (
            min(max(self.windowBox[0], x), self.windowBox[2]),
            min(max(self.windowBox[1], y), self.windowBox[3])
        )