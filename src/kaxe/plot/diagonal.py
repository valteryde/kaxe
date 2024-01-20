
"""
Denne kodebase skal virkelig skrives om og burde anses som fortabt
Dette er derfor legacy per 12 jan 2024 og virker ikke
                 ______
           _____/      \\_____
          |  _     ___   _   ||
          | | \     |   | \  ||
          | |  |    |   |  | ||
          | |_/     |   |_/  ||
          | | \     |   |    ||
          | |  \    |   |    ||
          | |   \. _|_. | .  ||
          |                  ||
          |                  ||
          |                  ||
  *       | *   **    * **   |**      **
   \))ejm97/.,(//,,..,,\||(,,.,\\,.((//
"""

"""
copied from axis
"""

from .core.helper import *
import logging
from .core.window import Window
from .standard import XYPLOT
from .core.axis import Axis
from .core.marker import Marker

class AxisPlot(Window):
    
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

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)


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

        # get styles
        self.width = self.getAttr('width')
        self.height = self.getAttr('height')

        self.windowBox = (
            self.padding[0], 
            self.padding[1], 
            self.width+self.padding[0], 
            self.height+self.padding[1]
        )
        self.nullInPlot = False

        # NOTE: burde nok være omvendt
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



from .helper import *
from .shapes import shapes
from .text import Text, getTextDimension
from .round import koundTeX
from .marker import Marker
import sys

class Axis:
    def __init__(self, 
                 directionVector:tuple, 
                 color=(0,0,0,255),
                 pos:tuple|None=None, 
                 func=None,
                 invfunc=None):
        """
        offset:bool If graph should be offset with equvalient of start value
        """

        self.directionVector = directionVector
        self.vLen = math.sqrt(directionVector[0]**2+directionVector[1]**2)
        self.v = (directionVector[0]/self.vLen, directionVector[1]/self.vLen)
        self.n = (-self.v[1],self.v[0])
        
        # tjek 
        if ((int(self.v[0]) == 0 and int(self.v[1]) == 1) or (int(self.v[0]) == 1 and int(self.v[1]) == 0)) == func:
            print('Custom Axis and non standard basis is not supported')
            sys.exit()

        if func is None:
            func = lambda x: x
            invfunc = lambda x: x
        
        self.func = func
        self.invfunc = invfunc
        self._translate = lambda x: x
        self._invtranslate = lambda x: x

        # styles
        self.color = color
        self.width = 2


    def translate(self, x):
        """
        translate value
        """
        try:
            return self.invfunc(x)
        except (ValueError, OverflowError):
            return 0


    def invtranslate(self, x):
        """
        inverse translate value
        """
        try:
            return self.func(x)
        except (ValueError, OverflowError):
            return 0


    def get(self, x:int) -> tuple:
        """
        x distance from 0
        """

        x -= self.offset

        return (self.v[0]*x, self.v[1]*x)


    def getEndPoints(self) -> tuple:
        return self.get(self.start), self.get(self.end)


    def addMarkersToAxis(self, parent):
        markers = []

        p1 = parent.inversetranslate(*self.lineStartPoint)
        p2 = parent.inversetranslate(*self.lineEndPoint)

        pixelLength = vlen(vdiff(self.lineStartPoint, self.lineEndPoint))
        length = vlen(vdiff(p1, p2))

        MARKERSTEPSIZE = parent.markerStepSizeBand
        MARKERSTEP = [2, 5, 10]
        acceptence = [math.floor(pixelLength/MARKERSTEPSIZE[0]),math.floor(pixelLength/MARKERSTEPSIZE[1])]

        c = 0
        cameFromDirection = 0
        while True:

            step = MARKERSTEP[c%len(MARKERSTEP)] * 10**(c//len(MARKERSTEP))

            lengthOverStep = length / step

            direction = 0

            if lengthOverStep > acceptence[1]:
                direction = 1
            
            if lengthOverStep < acceptence[0]:
                direction = -1
            
            c += direction

            if cameFromDirection == direction*-1:
                break
            
            cameFromDirection = direction

            if direction != 0:
                continue

            break
        
        lengthOverStep = round(lengthOverStep)
        
        # is null in frame?
        nullX, nullY = parent.pixel(0,0)
        if (parent.padding[0] <= nullX <= parent.width+parent.padding[0]) and (parent.padding[1] <= nullY <= parent.height+parent.padding[1]):

            distBeforeNull = vlen(vdiff((nullX, nullY), self.lineStartPoint))
            distafterNull = vlen(vdiff((nullX, nullY), self.lineEndPoint))

            procentBeforeNull = distBeforeNull/pixelLength
            procentAfterNull = distafterNull/pixelLength

            ticksBeforeNull = math.ceil(lengthOverStep*procentBeforeNull)
            ticksAfterNull = math.ceil(lengthOverStep*procentAfterNull)

            # NOTE: øhh der er et problem ved fx hjørnerne ikke bliver dækket hvis der er skrå akser
            if hasattr(parent, 'standardBasis') and not parent.standardBasis:
                marker = Marker("0", 0, shell(self), **parent.markerOptions)
                marker.finalize(parent)
                markers.append(marker)

            for i in range(1, ticksBeforeNull+1):
                marker = Marker(
                    str(koundTeX(self.translate(-step*i))), 
                    -step*i, 
                    shell(self), 
                    **parent.markerOptions
                )
                marker.finalize(parent)
                markers.append(marker)
            
            for i in range(1, ticksAfterNull+1):
                marker = Marker(
                    str(koundTeX(self.translate(step*i))), 
                    step*i, 
                    shell(self), 
                    **parent.markerOptions
                )
                marker.finalize(parent)
                markers.append(marker)

        else: # check for true axis support
            
            direction = (-1)**(0 < nullX)
            if direction == -1:
                startPos = self.end
            else:
                startPos = self.start

            startPos = startPos - startPos%step

            for i in range(math.floor(lengthOverStep)+2):
                p = direction*step*i + startPos
                marker = Marker(
                    str(koundTeX(self.translate(p))), 
                    p, 
                    shell(self), 
                    **parent.markerOptions
                )
                marker.finalize(parent)
                markers.append(marker)
        
        self.markers = markers

        # only use new translate after plot basis is made
        self._translate = self.invtranslate
        self._invtranslate = self.translate


    def addStartAndEnd(self, start:float | int, end:float | int, makeOffsetAvaliable:bool=True):
        
        # computed
        # self.start = fsolve(lambda x: self.func(x) - start, start)[0]
        # self.end = fsolve(lambda x: self.func(x) - end, end)[0]

        self.start = self.invtranslate(start)
        self.end = self.invtranslate(end)
        
        self.offset = 0
        if makeOffsetAvaliable:
            self.offset = self.start

        self.title = None
        self.hasNull = (self.start <= 0 and self.end >= 0)
        self.pos = self.getEndPoints()[0]


    def finalize(self, parent, visualOffset:tuple=(0,0), poss:tuple|None=None):
        self.visualOffset = visualOffset
        
        if not poss:

            p1, p2 = self.getEndPoints()
            
            self.p1 = (p1[0]*parent.scale[0]-parent.offset[0], p1[1]*parent.scale[1]-parent.offset[1])
            self.p2 = (p2[0]*parent.scale[0]-parent.offset[0], p2[1]*parent.scale[1]-parent.offset[1])

            v = (self.p1[0] - self.p2[0], self.p1[1] - self.p2[1])
            n = (-v[1], v[0])

            p1, p2 = boxIntersectWithLine((0, 0, parent.width, parent.height), n, self.p1)

            self.p1 = (self.p1[0]+parent.padding[0], self.p1[1]+parent.padding[1])
            self.p2 = (self.p2[0]+parent.padding[0], self.p2[1]+parent.padding[1])

            p1 = (p1[0]+parent.padding[0]+visualOffset[0], p1[1]+parent.padding[1]+visualOffset[1])
            p2 = (p2[0]+parent.padding[0]+visualOffset[0], p2[1]+parent.padding[1]+visualOffset[1])
                    
        else:
            poss = (poss[0], poss[1]), (poss[2], poss[3])
            self.p1, self.p2 = p1, p2 = poss
        
        self.lineStartPoint = p1
        self.lineEndPoint = p2

        self.shapeLine = shapes.Line(p1[0], p1[1], p2[0], p2[1], color=self.color, width=self.width)
        parent.addDrawingFunction(self, 2)

    
    def __boxOverlays__(self, aCenterPos, aSize, bCenterPos, bSize):
        #https://code.tutsplus.com/collision-detection-using-the-separating-axis-theorem--gamedev-169t
        #https://stackoverflow.com/questions/40795709/checking-whether-two-rectangles-overlap-in-python-using-two-bottom-left-corners
        
        atop_right = (aCenterPos[0] + aSize[0]/2, aCenterPos[1] + aSize[1]/2)
        abottom_left = (aCenterPos[0] - aSize[0]/2, aCenterPos[1] - aSize[1]/2)

        btop_right = (bCenterPos[0] + bSize[0]/2, bCenterPos[1] + bSize[1]/2)
        bbottom_left = (bCenterPos[0] - bSize[0]/2, bCenterPos[1] - bSize[1]/2)
        
        return not (atop_right[0] < bbottom_left[0]
                or abottom_left[0] > btop_right[0]
                or atop_right[1] < bbottom_left[1]
                or abottom_left[1] > btop_right[1])


    def addTitle(self, title:str, parent) -> None:
        v = (self.v[0]*parent.scale[0], self.v[1]*parent.scale[1])
        angle = angleBetweenVectors(v, (1,0))

        p1, p2 = self.getPixelPos()
        diff = vdiff(p1, p2)
        v = vectorScalar(diff, 1/2)
        axisPos = addVector(p1, v)
            
        nscaled = (-diff[1], diff[0])
        nscaledlength = vlen(nscaled)
        nscaled = (nscaled[0] / nscaledlength, nscaled[1] / nscaledlength)

        maxDist = [distPointLine(nscaled, p1, marker.pos()) for marker in self.markers if hasattr(marker, 'textLabel')]
        maxDist = max(maxDist)

        textDimension = getTextDimension(title, parent.fontSize)
        v = vectorScalar(nscaled, (textDimension[1]/2 + maxDist) * self.markers[-1].directionFromAxis)

        # nudge out of marker spots
        # forstil dig to kasser
        # vi tjekker om den to kasser er oveni hindanden (om de overlapper)
        # hvis ja så rykker vi kassen langs normal linjen
        # ---------------
        # |             |
        # |             |
        # |  --------   |
        # |  |      |   |
        # ---|------|----
        #    |      |
        #    --------
        pos = (axisPos[0]+v[0], axisPos[1]+v[1])
        self.title = Text(title, 0,0, parent.fontSize, parent.markerColor, angle)
        size = self.title.getBoundingBox()
        v = vectorScalar(nscaled, self.markers[-1].directionFromAxis * 1)
        for _ in range(1000): # max nudge

            checkMarkers = [i for i in self.markers] # shallow copy (hopefully)

            overlap = False
            for i, marker in enumerate(checkMarkers):
                if not hasattr(marker, 'textLabel'):
                    # checkMarkers.pop(i)
                    #break
                    continue

                # #print(marker.pos(), marker.getBoundingBox(), pos, size)
                # if self.__boxOverlays__(marker.pos(), marker.getBoundingBox(), pos, size): print('hjejsa')

                if self.__boxOverlays__(marker.pos(), marker.getBoundingBox(), pos, size):
                    pos = addVector(pos, v)
                    overlap = True
                    break
                # else:
                #     checkMarkers.pop(i)
                #     break

            if not overlap:
                break
        
        v = vectorScalar(nscaled, self.markers[-1].directionFromAxis * 5)
        pos = addVector(pos, v)
        self.title.x, self.title.y = pos

        parent.addDrawingFunction(self.title, 2)
        parent.include(*pos, *self.title.getBoundingBox())


    # *** api ***
    def getPixelPos(self):
        return (self.shapeLine.x0, self.shapeLine.y0), (self.shapeLine.x1, self.shapeLine.y1)    


    def draw(self, *args, **kwargs):
        self.shapeLine.draw(*args, **kwargs)


    def push(self, x,y):
        self.shapeLine.push(x,y)