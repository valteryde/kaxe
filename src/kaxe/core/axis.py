
from .helper import *
from .shapes import shapes
from .styles import AttrObject, ComputedAttribute
from .text import Text, getTextDimension
from .round import koundTeX
from .marker import Marker
import sys
from types import MappingProxyType, FunctionType
from typing import Union

# AXIS COMPUTABLE STYLES
stepSizeBandAttribute = ComputedAttribute(lambda a: [a.getAttr('fontSize')*7, a.getAttr('fontSize')*4])


class Axis(AttrObject):
    
    defaults = MappingProxyType({
        "stepSizeBand": stepSizeBandAttribute,
        "showArrow": False,
        "width": 4,
        "titleGap": ComputedAttribute(lambda map: map.getAttr('fontSize')*0.5),
        "arrowSize": ComputedAttribute(lambda map: map.getAttr('fontSize')*0.75)
    })

    name = "Axis"

    def __init__(self, directionVector:tuple):
        super().__init__()

        self.directionVector = directionVector
        self.vLen = vlen(directionVector)
        self.v = (directionVector[0]/self.vLen, directionVector[1]/self.vLen)
        self.n = (-self.v[1],self.v[0])
        self.finalized = False    
        self.markers = []

    def get(self, x):
        """
        returns pixel value between start point and end point
        """

        v = vdiff(self.startPos, self.endPos)
        v = vectorScalar(v, (x-self.startNumber)/self.realLength)
        v = addVector(self.startPos, v)
        return v
    

    def computeMarkersAutomatic(self, parent):
        markers = []
        assert self.finalized

        # hvis der ikke er en scale defineret, som fx ved Bar chart så bare brug det akserene kører på
        if not hasattr(parent, 'scale'): 
            scale = vlen(vdiff(self.startPos, self.endPos)) / abs(self.endNumber - self.startNumber)
            parent.scale = [scale, scale]

        #p1, p2 = parent.inversetranslate(*self.startPos), parent.inversetranslate(*self.endPos)

        pixelLength = vlen(vdiff(self.startPos, self.endPos))
        length = self.endNumber - self.startNumber

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
        nullX, nullY = self.get(0)
        if self.startNumber <= 0 <= self.endNumber:

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


    def addMarkerAtPos(self, pos, text, parent):
        marker = Marker(
            text,
            pos,
            shell(self)
        )
        marker.finalize(parent)
        self.markers.append(marker)

    def addMarkersToAxis(self, markers, parent):
        self.setAttrMap(parent.attrmap)
        
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


    def addStartAndEnd(self, start:Union[float, int], end:Union[float, int]):
        self.startNumber = start
        self.endNumber = end
        self.hasNull = self.startNumber < 0 < self.endNumber
        self.realLength = end - start
        

    def setPos(self, startPos:Union[tuple, list], endPos:Union[tuple, list]):
        self.startPos = startPos
        self.endPos = endPos

        self.pixelLength = vlen(vdiff(self.startPos, self.endPos))


    def finalize(self, parent):
        self.setAttrMap(parent.attrmap)

        parent.addDrawingFunction(self, 2)

        self.shapeLine = shapes.Line(
            self.startPos[0], 
            self.startPos[1], 
            self.endPos[0], 
            self.endPos[1], 
            color=self.getAttr('color'), 
            width=self.getAttr('width')
        )

        self.arrowBatch = shapes.Batch()

        if self.getAttr('showArrow'):
            v = vdiff(self.endPos, self.startPos)
            v = vectorScalar(v, 1/vlen(v))

            n = (-v[1], v[0])

            arrowSize = self.getAttr('arrowSize') / 2
            arrowDownHeight = arrowSize

            p1 = (self.startPos[0] + 2 * arrowSize * v[0], self.startPos[1] + 2 * arrowSize * v[1])
            p2 = (self.startPos[0] + arrowSize * n[0] - arrowDownHeight * v[0], self.startPos[1] + arrowSize * n[1] - arrowDownHeight * v[1])
            p3 = (self.startPos[0] - arrowSize * n[0] - arrowDownHeight * v[0], self.startPos[1] - arrowSize * n[1] - arrowDownHeight * v[1])

            self.startArrows = (
                shapes.Triangle(
                    p1, p2, self.startPos,
                    color=self.getAttr('color'), 
                    batch=self.arrowBatch,
                ),
                shapes.Triangle(
                    p1, p3, self.startPos,
                    color=self.getAttr('color'), 
                    batch=self.arrowBatch,
                )
            )

            minx = min(p1[0],p2[0],p3[0])
            miny = min(p1[1],p2[1],p3[1])
            maxx = max(p1[0],p2[0],p3[0])
            maxy = max(p1[1],p2[1],p3[1])

            halfwidth = (maxx - minx) / 2
            halfheight = (maxy - miny) / 2
            center = (minx + halfwidth, miny + halfheight)

            parent.include(*center, halfwidth*2, halfheight*2)

            p4 = (self.endPos[0] - 2 * arrowSize * v[0], self.endPos[1] - 2 * arrowSize * v[1])
            p5 = (self.endPos[0] + arrowSize * n[0] + arrowDownHeight * v[0], self.endPos[1] + arrowSize * n[1] + arrowDownHeight * v[1])
            p6 = (self.endPos[0] - arrowSize * n[0] + arrowDownHeight * v[0], self.endPos[1] - arrowSize * n[1] + arrowDownHeight * v[1])

            self.endArrows = (
                shapes.Triangle(
                    p4, p5, self.endPos,
                    color=self.getAttr('color'), 
                    batch=self.arrowBatch,
                ),
                shapes.Triangle(
                    p4, p6, self.endPos,
                    color=self.getAttr('color'), 
                    batch=self.arrowBatch,
                )
            )


            minx = min(p4[0],p5[0],p6[0])
            miny = min(p4[1],p5[1],p6[1])
            maxx = max(p4[0],p5[0],p6[0])
            maxy = max(p4[1],p5[1],p6[1])

            halfwidth = (maxx - minx) / 2
            halfheight = (maxy - miny) / 2
            center = (minx + halfwidth, miny + halfheight)

            parent.include(*center, halfwidth*2, halfheight*2)

        self.finalized = True

    
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
        
        v = vectorScalar(nscaled, self.markers[-1].directionFromAxis * self.getAttr('titleGap'))
        pos = addVector(pos, v)
        self.title.x, self.title.y = pos

        parent.addDrawingFunction(self.title, 2)
        parent.include(*pos, *self.title.getBoundingBox())


    def checkCrossOvers(self, parent, axis):

        if not self.getAttr('showArrow'):
            return

        # check start and end points
        startdist = min(
            vlen(vdiff(self.startPos, axis.startPos)),
            vlen(vdiff(self.startPos, axis.endPos))
        )

        enddist = min(
            vlen(vdiff(self.endPos, axis.startPos)),
            vlen(vdiff(self.endPos, axis.endPos))
        )
        
        if startdist < 5:
            self.startArrows[0].hide()
            self.startArrows[1].hide()

        if enddist < 5:
            self.endArrows[0].hide()
            self.endArrows[1].hide()


    # *** api ***
    def draw(self, *args, **kwargs):
        self.shapeLine.draw(*args, **kwargs)
        self.arrowBatch.draw(*args, **kwargs)


    def push(self, x,y):
        self.shapeLine.push(x,y)
        self.startPos = (self.startPos[0]+x, self.startPos[1]+y)
        self.endPos = (self.endPos[0]+x, self.endPos[1]+y)
        self.arrowBatch.push(x, y)
