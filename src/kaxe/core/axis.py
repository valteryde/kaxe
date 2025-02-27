
from .helper import *
from .shapes import shapes
from .styles import AttrObject, ComputedAttribute
from .text import Text, getTextDimension
from .round import koundTeX
from .marker import Marker
from types import MappingProxyType, FunctionType
from typing import Union
import numpy as np
from PIL import Image
from random import randint


class Axis(AttrObject):
    """
    Axis is a class for creating and managing axes in a plot.
    """

    defaults = MappingProxyType({
        "showArrow": False,
        "width": 4,
        "titleGap": ComputedAttribute(lambda map: map.getAttr('fontSize')*0.5),
        "arrowSize": ComputedAttribute(lambda map: map.getAttr('fontSize')*0.75),
        "drawAxis": True,
        "drawMarkersAtEnd": True,
        "axisColor": ComputedAttribute(lambda map: map.getAttr('color')),
        "ghostMarkers": False,
    })

    name = "Axis"

    def __init__(self, directionVector:tuple, titleNormal:tuple, numberOnAxisGoalReference:str):
        """
        
        Example (horisontal) axis:
        __________ --> DirectionVector
            |
            |  titleNormal
            v
          title
            
        """

        super().__init__()

        self.directionVector = directionVector
        self.titleNormal = np.array(titleNormal) / vlen(titleNormal)
        self.vLen = vlen(directionVector)
        self.v = (directionVector[0]/self.vLen, directionVector[1]/self.vLen)
        self.n = (-self.v[1],self.v[0])
        self.finalized = False    
        self.markers = []
        
        # only a refernce for the name of attribute on parent object
        self.numberOnAxisGoalReference = numberOnAxisGoalReference
        self.userAddedMarkers = []

    def add(self, text:str, pos:Union[int, float], showLine:bool=True):
        """
        Add markers to the axis.

        Parameters
        ----------
        text : str
            The text label for the marker.
        pos : int | float
            The position of the marker on the axis.
        showLine : bool, optional
            Whether to show a line for the marker (default is True).

        """

        self.userAddedMarkers.append({
            "text": text,
            "pos" : pos,
            "style": [('showNumber', True), ('showLine', showLine)]
        })


    def get(self, x):
        """
        returns pixel value between start point and end point
        """

        v = vdiff(self.startPos, self.endPos)
        v = vectorScalar(v, (x-self.startNumber)/self.realLength)
        v = addVector((self.shapeLine.x0, self.shapeLine.y0), v)
        
        return v
    

    def computeMarkersAutomatic(self, parent):
        markers = []
        assert self.finalized

        # hvis der ikke er en scale defineret, som fx ved Bar chart så bare brug det akserene kører på
        if not hasattr(parent, 'scale'): 
            scale = vlen(vdiff(self.startPos, self.endPos)) / abs(self.endNumber - self.startNumber)
            parent.scale = [scale, scale]

        pixelLength = vlen(vdiff(self.startPos, self.endPos))
        length = self.endNumber - self.startNumber

        numberOnAxisGoal = self.getAttr(self.numberOnAxisGoalReference)
        if not numberOnAxisGoal: # default
            numberOnAxisGoal = pixelLength // (3*self.getAttr('fontSize'))

        if numberOnAxisGoal - 1 == 0:
            numberOnAxisGoal = 2

        acceptence = [numberOnAxisGoal-1, numberOnAxisGoal+1]

        MARKERSTEP = [2, 5, 10]
        
        c = 0
        cameFromDirection = 0
        tries = 0
        while True:
            tries += 1

            if tries > 1000:
                #logging('Trying new stepsize')
                acceptence = [min(acceptence[0]-1, 1), acceptence[1]+1]

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
                    "pos" : p,
                    "style": []
                })
            
            for i in range(1, ticksAfterNull+1):
                p = step*i
                markers.append({
                    "text": str(koundTeX(p)),
                    "pos" : p,
                    "style": []
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
                    "pos" : p,
                    "style": []
                })
        
        drawMarkersAtEnd = self.getAttr('drawMarkersAtEnd')
        v = self.endPos - self.startPos
        lenAB = np.linalg.norm(v)
        accMarkers = []
        for marker in markers:
            
            v0 = np.array(self.get(marker["pos"])) - self.startPos
            d = np.dot(v, v0)

            lenv0 = np.linalg.norm(v0)
            
            proc = lenv0/lenAB
            
            if d >= 0 and proc <= 1:
                accMarkers.append(marker)

            if (not drawMarkersAtEnd) and (closeToZero(proc, 0.01) or closeToZero(proc-1, 0.01)):
                marker["style"].append(("tickWidth", 0))
                marker["style"].append(("tickLength", self.getAttr('marker.tickLength')//2))

        accMarkers.sort(key=lambda x: x["pos"])
        return accMarkers


    def addMarkerAtPos(self, pos, text, parent):
        marker = Marker(
            text,
            pos,
            shell(self)
        )
        marker.finalize(parent)
        self.markers.append(marker)


    def addMarkersToAxis(self, markers:list, parent):
        """
        Adds markers to axis

        Also does overlap between markers on same axis

        """

        self.setAttrMap(parent.attrmap)

        # Ghost markers
        ghostMarkersNumber = self.getAttr('ghostMarkers')
        if ghostMarkersNumber:
            sortedMarkers = list(sorted(markers, key=lambda m: m["pos"]))
            newcolor = list(self.getAttr('marker.gridlineColor'))
            newcolor[3] = newcolor[3]//4
            
            diff = 0
            for i in [*range(len(sortedMarkers)), None]:
                
                if i != len(sortedMarkers) - 1 and i != None:
                    diff = sortedMarkers[i+1]["pos"] - sortedMarkers[i]["pos"]

                for j in range(ghostMarkersNumber):
                    if i == None:
                        pos = sortedMarkers[0]["pos"] - diff * (j + 1) / (ghostMarkersNumber + 1)
                    
                    else:
                        pos = sortedMarkers[i]["pos"] + diff * (j + 1) / (ghostMarkersNumber + 1)

                    if not parent.inside(*self.get(pos)):
                        continue

                    markers.append({
                        "text": "",
                        "pos": pos,
                        "style": [
                            ('tickWidth', self.getAttr('marker.tickWidth') // 2),
                            ('gridlineColor', newcolor)
                        ],
                    })

        markers += self.userAddedMarkers

        for marker in markers:
            marker_ = Marker(
                marker["text"],
                marker["pos"],
                shell(self)
            )
            
            marker_.setAttrMap(parent.attrmap)

            for style, val in marker["style"]:
                marker_.setAttr(style, val)

            marker_.finalize(parent)
            self.markers.append(marker_)
        
        # get largets overlap
        maxOverlays = 1
        for a in self.markers:
            overlays = 0
            for b in self.markers:
                if not hasattr(a, 'textLabel') or not hasattr(b, 'textLabel'):
                    continue

                overlays += self.__boxOverlays__(
                    a.textLabel.getCenterPos(), 
                    (a.textLabel.width, a.textLabel.height),
                    b.textLabel.getCenterPos(), 
                    (b.textLabel.width, b.textLabel.height)
                )

            maxOverlays = max(maxOverlays, overlays)
        
        # Burde ikke tælle sig selv med
        # Dog når der tages modulo skal der plus en
        # maxOverlays -= 1

        # created markers
        # Når der er et nul på aksen startes der ved 0 og så går op og springer over
        # hver n element. Dette gøres så nul altid kommer med.
        # Samme ide bruges andre steder
        sortedMarkers = []

        markerOffset = 1
        if self.hasNull:
            afterNull = [i for i in self.markers if i.x > 0]
            afterNull.sort(key=lambda m: m.x)
            beforeNull = [i for i in self.markers if i.x < 0]
            beforeNull.sort(key=lambda m: -m.x)

            sortedMarkers.append(afterNull)
            sortedMarkers.append(beforeNull)

        else:
            sortedMarkers.append(self.markers)

        for markers in sortedMarkers:

            for i, marker in enumerate(markers):

                if (i + markerOffset) % maxOverlays != 0:

                    marker.textLabel.img = Image.new('RGBA', (0,0))
                    if hasattr(marker, 'line'):
                        marker.line.color = (
                            marker.line.color[0],
                            marker.line.color[1],
                            marker.line.color[2],
                            marker.line.color[3]//4,
                        )
                    if hasattr(marker, 'tickLine'):
                        marker.tickLine.color = (
                            marker.tickLine.color[0],
                            marker.tickLine.color[1],
                            marker.tickLine.color[2],
                            marker.tickLine.color[3]//4,
                        )


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
        self.startPos = np.array(startPos)
        self.endPos = np.array(endPos)

        self.pixelLength = vlen(vdiff(self.startPos, self.endPos))


    def finalize(self, parent):
        self.setAttrMap(parent.attrmap)

        parent.addDrawingFunction(self, 2)

        self.shapeLine = shapes.Line(
            self.startPos[0], 
            self.startPos[1], 
            self.endPos[0], 
            self.endPos[1], 
            color=self.getAttr('axisColor'), 
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


    def __topLeftBoxOverlays__(self, label:Text, title:Text):
        lx, ly, lwidth, lheight = label.getBoundingBox()
        tx, ty, twidth, theight = title.getBoundingBox()

        return self.__boxOverlays__((lx+lwidth/2, ly+lheight/2), (lwidth, lheight), (tx+twidth/2, ty+theight/2), (twidth, theight))

        
    def __pixelCollision__(self, label:Text, title:Text):

        lx, ly, lwidth, lheight = label.getBoundingBox()
        tx, ty, twidth, theight = title.getBoundingBox()

        # if the two hitboxes dosent cross -> no collision
        # check is fast
        if not self.__boxOverlays__((lx+lwidth/2, ly+lheight/2), (lwidth, lheight), (tx+twidth/2, ty+theight/2), (twidth, theight)):
            return False
        #print('tjekker', label.text)

        # else check for pixel collision
        ax, ay, aw, ah = tx, ty, twidth, theight
        bx, by, bw, bh = lx, ly, lwidth, lheight

        # givet to firkanter
        #        _______________
        #        |             |
        # _______|_______      |
        # |      |      |      |
        # |      |      |      |
        # |      |      |      |
        # |      |______|______|
        # |             |
        # |_____________|
        # 
        # Firkanterne er givet ved en P1 og P2 hver især
        # Overlapnings området i x starter ved
        # det maksimale af venstres venstre koordinat og højre firkants venstre koordinat

        x_left = max(ax, bx)
        x_right = min(ax + aw, bx + bw)
        
        y_left = max(ay, by)
        y_right = min(ay + ah, by + bh)

        A = np.array(title.img)
        B = np.array(label.img)
        
        # print(ax, ax + aw, bx, bx + bw)

        #A = np.flip(A, 0)
        #B = np.flip(B, 0)

        alphacutoff = 0
        for x in range(x_left+1, x_right):

            for y in range(y_left+1, y_right):

                if A[len(A) - y + ay][x - ax][3] > alphacutoff and B[len(B) - y + by][x - bx][3] > alphacutoff:
                    return True
                
                # A[len(A) - y + ay][x - ax] = (255,0,0,255)
                # B[len(B) - y + by][x - bx] = (0,0,255,255)

        # title.img = Image.fromarray(A)
        # label.img = Image.fromarray(B)

        return False


    def addTitle(self, title:str, parent) -> None:
        v = (self.v[0]*parent.scale[0], self.v[1]*parent.scale[1])
        angle = angleBetweenVectors(v, (1,0))
        
        # adjust angle to readable text
        if angle > 90:
            angle -= 180
        
        if self.v[1] < 0:
            angle = -angle

        if closeToZero(angle + 90):
            angle = -angle

        p1, p2 = self.startPos, self.endPos
        diff = vdiff(p1, p2)
        v = vectorScalar(diff, 1/2)
        axisPos = addVector(p1, v)

        nscaled = (-diff[1], diff[0])
        nscaledlength = vlen(nscaled)
        nscaled = (nscaled[0] / nscaledlength, nscaled[1] / nscaledlength)

        maxDist = [distPointLine(nscaled, p1, marker.pos()) for marker in self.markers if hasattr(marker, 'textLabel')]
        if len(maxDist) > 0:
            maxDist = max(maxDist)
        else:
            maxDist = 0

        textDimension = getTextDimension(title, self.getAttr('fontSize'))
        v = vectorScalar(self.titleNormal, (textDimension[1]/2 + maxDist))

        # nudge out of marker spots
        # givet to kasser
        # vi tjekker om den to kasser er oveni hindanden (om de overlapper)
        # hvis ja så rykker vi kassen langs normal linjen
        # er måske lige no shit det her men ja
        # ---------------
        # |             |
        # |             |
        # |  --------   |
        # |  |      |   |
        # ---|------|----
        #    |      |
        #    --------
        pos = (axisPos[0]+v[0], axisPos[1]+v[1])
        v = self.titleNormal # hmmm
        
        self.title = Text(title, *pos, self.getAttr('fontSize'), self.getAttr('color'), angle)
        
        for _ in range(1000): # max nudge 1000

            overlap = False
            for _, marker in enumerate(self.markers):
                
                if not hasattr(marker, 'textLabel'):
                    continue

                if self.__pixelCollision__(marker.textLabel, self.title):
                    self.title.push(v[0]*2, v[1]*2) #kører skævt når den skal runde op
                    overlap = True
                    break

            if not overlap:
               break
        
        # add title gap to title label
        self.title.push(
            *vectorScalar(self.titleNormal, self.getAttr('titleGap'))
        )

        parent.addDrawingFunction(self.title, 2)
        parent.includeElement(self.title)


    def __checkMarkersOverlapping__(self, parent, axis):
        if not(len(self.markers) == 0 or len(axis.markers) == 0):
            
            def min_(l):
                if len(l) == 1:
                    return l[0]
                return min(*l, key=lambda x: x.x)
            def max_(l):
                if len(l) == 1:
                    return l[0]
                return max(*l, key=lambda x: x.x)

            afirst = min_(self.markers)
            bfirst = min_(axis.markers)
            
            alast = max_(self.markers)
            blast = max_(axis.markers)

            l = [
                (alast, blast),
                (alast, bfirst),
                (afirst, blast),
                (afirst, bfirst)
            ]

            # textbuble
            # axis fejl

            posSelfCenter = np.array((self.startPos/2 + self.endPos/2))
            posAxisCenter = np.array((axis.startPos/2 + axis.endPos/2))
            for a, b in l:
                if not hasattr(a, 'textLabel') or not hasattr(b, 'textLabel'):
                    continue
                
                if not self.__topLeftBoxOverlays__(a.textLabel, b.textLabel):
                    continue
                
                if not hasattr(a, 'tickLine') or not hasattr(b, 'tickLine'):
                    continue

                posMarkerA = np.array((a.tickLine.x0/2 + a.tickLine.x1/2, a.tickLine.y0/2 + a.tickLine.y1/2))
                posMarkerB = np.array((b.tickLine.x0/2 + b.tickLine.x1/2, b.tickLine.y0/2 + b.tickLine.y1/2))

                va = posSelfCenter - posMarkerA
                va /= np.sqrt(np.dot(va, va))

                vb = posAxisCenter - posMarkerB
                vb /= np.sqrt(np.dot(vb, vb))

                for i in range(parent.width): # maxpixel

                    b.textLabel.push(*vb*10)
                    a.textLabel.push(*va*10)

                    if not self.__topLeftBoxOverlays__(a.textLabel, b.textLabel):
                        b.textLabel.push(*vb*10)
                        a.textLabel.push(*va*10)
                        
                        parent.includeElement(a.textLabel)
                        parent.includeElement(b.textLabel)
                        
                        break
                    
                else:
                    continue
                
                break


    def checkCrossOvers(self, parent, axis):

        self.__checkMarkersOverlapping__(parent, axis)

        # check arrow
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
        if self.getAttr('drawAxis'):
            self.shapeLine.draw(*args, **kwargs)
            self.arrowBatch.draw(*args, **kwargs)


    def push(self, x,y):
        self.shapeLine.push(x,y)
        self.arrowBatch.push(x, y)
        self.startPos = np.array((self.startPos[0]+x, self.startPos[1]+y))
        self.endPos = np.array((self.endPos[0]+x, self.endPos[1]+y))
