
from .helper import *
from .shapes import shapes
from .styles import AttrObject, ComputedAttribute
from .text import Text, getTextDimension
from .round import koundTeX
from .marker import Marker
import sys
from types import MappingProxyType, FunctionType

# AXIS COMPUTABLE STYLES
stepSizeBandAttribute = ComputedAttribute(lambda a: [a.getAttr('fontSize')*7, a.getAttr('fontSize')*4])


class Axis(AttrObject):
    
    defaults = MappingProxyType({
        "stepSizeBand": stepSizeBandAttribute,
        "showLine": True, # bliver ikke brugt pt
        "width": 3,
    })

    name = "Axis"

    def __init__(self, directionVector:tuple):
        super().__init__()

        self.directionVector = directionVector
        self.vLen = vlen(directionVector)
        self.v = (directionVector[0]/self.vLen, directionVector[1]/self.vLen)
        self.n = (-self.v[1],self.v[0])
    

    def get(self, x):

        v = vdiff(self.startPos, self.endPos)
        v = vectorScalar(v, (x-self.startNumber)/self.realLength)
        v = addVector(self.startPos, v)
        return v
    

    def computeMarkersAutomatic(self, parent):
        markers = []

        p1, p2 = parent.inversetranslate(*self.startPos), parent.inversetranslate(*self.endPos)

        pixelLength = vlen(vdiff(self.startPos, self.endPos))
        length = vlen(vdiff(p1, p2))

        MARKERSTEPSIZE = self.getAttr('stepSizeBand')
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
        if parent.inside(nullX, nullY):

            distBeforeNull = vlen(vdiff((nullX, nullY), self.startPos))
            distafterNull = vlen(vdiff((nullX, nullY), self.endPos))

            procentBeforeNull = distBeforeNull/pixelLength
            procentAfterNull = distafterNull/pixelLength

            ticksBeforeNull = math.ceil(lengthOverStep*procentBeforeNull)
            ticksAfterNull = math.ceil(lengthOverStep*procentAfterNull)
            
            for i in range(0, ticksBeforeNull+1):
                p = -step*i
                markers.append({
                    "text": str(koundTeX(p)),
                    "pos" : p
                })
            
            for i in range(1, ticksAfterNull+1):
                p = step*i
                markers.append({
                    "text": str(koundTeX(p)),
                    "pos" : p
                })

        else:
            
            direction = (-1)**(0 < nullX)
            if direction == -1:
                startPos = self.endNumber
            else:
                startPos = self.startNumber

            startPos = startPos - startPos%step

            for i in range(math.floor(lengthOverStep)+2):
                p = direction*step*i + startPos
                markers.append({
                    "text": str(str(koundTeX(p))),
                    "pos" : p
                })
        
        return markers


    def addMarkersToAxis(self, markers, parent):
        self.setAttrMap(parent.attrmap)
        
        self.markers = []
        for marker in markers:
            marker = Marker(
                marker["text"],
                marker["pos"],
                shell(self)
            )
            marker.finalize(parent)
            self.markers.append(marker)



    def autoAddMarkers(self, parent):
        self.setAttrMap(parent.attrmap)

        markers = self.computeMarkersAutomatic(parent)
        self.addMarkersToAxis(markers, parent)


    def addStartAndEnd(self, start:float|int, end:float|int):
        self.startNumber = start
        self.endNumber = end
        self.hasNull = self.startNumber < 0 < self.endNumber
        self.realLength = end - start
        

    def setPos(self, startPos:tuple|list, endPos:tuple|list):
        self.startPos = startPos
        self.endPos = endPos

        self.pixelLength = vlen(vdiff(self.startPos, self.endPos))


    def finalize(self, parent):
        self.setAttrMap(parent.attrmap)
        
        self.shapeLine = shapes.Line(
            self.startPos[0], 
            self.startPos[1], 
            self.endPos[0], 
            self.endPos[1], 
            color=self.getAttr('color'), 
            width=self.getAttr('width')
        )
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

        p1, p2 = self.startPos, self.endPos
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
    def draw(self, *args, **kwargs):
        self.shapeLine.draw(*args, **kwargs)


    def push(self, x,y):
        self.shapeLine.push(x,y)
        self.startPos = (self.startPos[0]+x, self.startPos[1]+y)
        self.endPos = (self.endPos[0]+x, self.endPos[1]+y)
