
from .helper import *
from .shapes import shapes
from .styles import AttrObject, ComputedAttribute
from .text import Text, getTextDimension
from .round import koundTeX
from .marker import Marker
import sys
from types import MappingProxyType


# AXIS COMPUTABLE STYLES
stepSizeBandAttribute = ComputedAttribute(lambda a: [a.getAttr('fontSize')*5, a.getAttr('fontSize')*6])


class Axis(AttrObject):
    
    defaults = MappingProxyType({
        "stepSizeBand": stepSizeBandAttribute,
        "showLine": True, # bliver ikke brugt pt
        "width": 3
    })

    name = "Axis"

    def __init__(self,
                 directionVector:tuple, 
                 pos:tuple|None=None, 
                 func=None,
                 invfunc=None):
        """
        offset:bool If graph should be offset with equvalient of start value
        """
        super().__init__()

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
        self.setAttrMap(parent.attrmap)

        p1 = parent.inversetranslate(*self.lineStartPoint)
        p2 = parent.inversetranslate(*self.lineEndPoint)

        pixelLength = vlen(vdiff(self.lineStartPoint, self.lineEndPoint))
        length = vlen(vdiff(p1, p2))

        MARKERSTEPSIZE = self.getAttr('stepSizeBand')
        print(MARKERSTEPSIZE)
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
                marker = Marker("0", 0, shell(self))
                marker.finalize(parent)
                markers.append(marker)

            for i in range(1, ticksBeforeNull+1):
                marker = Marker(
                    str(koundTeX(self.translate(-step*i))), 
                    -step*i, 
                    shell(self), 
                )
                marker.finalize(parent)
                markers.append(marker)
            
            for i in range(1, ticksAfterNull+1):
                marker = Marker(
                    str(koundTeX(self.translate(step*i))), 
                    step*i, 
                    shell(self), 
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
        self.setAttrMap(parent.attrmap)

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

        self.shapeLine = shapes.Line(p1[0], p1[1], p2[0], p2[1], color=self.getAttr('color'), width=self.getAttr('width'))
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

        textDimension = getTextDimension(title, self.getAttr('fontSize'))
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
        self.title = Text(title, 0,0, self.getAttr('fontSize'), self.getAttr('color'), angle)
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
