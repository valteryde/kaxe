
from .helper import *
from .shapes import shapes
from .text import Text, getTextDimension

class Marker:

    def __init__(self, 
                 text:str, 
                 x:int, 
                 axis, 
                 color:tuple=(0,0,0,255),
                 fontSize:int=10,
                 showNumber:bool=True,
                 showLine:bool=True,
                 markerWidth:int = 1,
                 markerLength:int = 15,
                 gridlineColor:tuple=(0,0,0,75),
                 font:str="Times New Roman",
                ):
        """
        marker with line
        """

        self.text = text
        self.x = x
        self.axis = axis
        self.batch = shapes.Batch()
        
        self.markerLength = markerLength
        self.markerWidth = markerWidth
        self.showNumber = showNumber
        self.showLine = showLine
        self.fontSize = fontSize
        self.font = font
        self.color = color
        self.gridlineColor = gridlineColor


    def finalize(self, parent, visualOffset:tuple=(0,0)):
        self.axis = self.axis()

        self.visualOffset = addVector(visualOffset, self.axis.visualOffset) #inherit

        if self.showLine:
            p1, p2 = parent.line(self.axis.get(self.x), self.axis.v)
            self.line = shapes.Line(*p1, *p2, color=self.gridlineColor, batch=self.batch)
        
        pos = parent.translate(*self.axis.get(self.x))

        n = (self.axis.n[0]/parent.scale[0], self.axis.n[1]/parent.scale[1])
        nlen = vlen(n)
        n = (n[0]/nlen, n[1]/nlen)

        halfMarkerLength = self.markerLength/2
        
        pos = addVector(pos, self.visualOffset)

        p1 = (pos[0]+n[0]*halfMarkerLength, pos[1]+n[1]*halfMarkerLength)
        p2 = (pos[0]-n[0]*halfMarkerLength, pos[1]-n[1]*halfMarkerLength)

        distanceFromMarker = self.markerLength
        r = 1

        # special case, marker is vertical or horizontal
        if n[0] == 0:
            r = -1
        if n[1] == 0:
            r = 1
        
        self.directionFromAxis = r
        textPos = (pos[0]+r*n[0]*distanceFromMarker, pos[1]+r*n[1]*distanceFromMarker)
        
        if (not parent.inside(*pos)):
            self.line = None
            return

        self.tickLine = shapes.Line(*p1, *p2, color=self.color, width=self.markerWidth, batch=self.batch, center=True)
        if not self.showNumber:
            return

        # how long away for text box not to hit marker
        self.textLabel = Text(self.text,
                                  x=textPos[0], 
                                  y=textPos[1], 
                                  color=self.color, 
                                #   batch=self.batch, 
                                  align="center", 
                                  anchor_x="center",
                                  anchor_y="center",
                                # font_name=self.font,
                                  fontSize=self.fontSize,
        )

        box = [
            textPos[0]-self.textLabel.width/2,
            textPos[1]-self.textLabel.height/2,
            textPos[0]+self.textLabel.width/2,
            textPos[1]+self.textLabel.height/2
        ]

        nudge = 0
        if r == -1 and insideBox(box, p2):
            nudge = - (distPointLine(n, p2, box[2:4]))
        
        if r == 1 and insideBox(box, p1):
            nudge = distPointLine(n, p1, box[2:4])

        if r == 1:
            nudge += 5
        elif r == -1:
            nudge -= 5

        self.textLabel.x += n[0] * nudge
        self.textLabel.y += n[1] * nudge

        parent.addDrawingFunction(self, 2)
        parent.addDrawingFunction(self.textLabel, 2)
        
        # dx = min(self.textLabel.x - self.textLabel.width/2, 0)
        # dy = min(self.textLabel.y - self.textLabel.height/2, 0)
        # dxm = min(parent.width - (self.textLabel.x + self.textLabel.width/2), 0)
        # dym = min(parent.height - (self.textLabel.y + self.textLabel.height/2), 0)

        parent.include(self.textLabel.x, self.textLabel.y, self.textLabel.width, self.textLabel.height)

        # if dx < 0 or dy < 0 or dxm < 0 or dym < 0:
        #     parent.addPaddingCondition(left=-(dx), bottom=-(dy), right=-(dxm), top=-(dym))


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, x, y):
        self.batch.push(x,y)


    def getBoundingBox(self):
        if hasattr(self, 'textLabel'):
            return self.textLabel.getBoundingBox()
        return [0,0]
    

    def pos(self):
        if hasattr(self, 'textLabel'):
            return self.textLabel.x, self.textLabel.y


class Axis:
    def __init__(self, 
                 directionVector:tuple, 
                 color=(0,0,0,255)):
        """
        offset:bool If graph should be offset with equvalient of start value
        """
        
        self.directionVector = directionVector
        self.vLen = math.sqrt(directionVector[0]**2+directionVector[1]**2)
        self.v = (directionVector[0]/self.vLen, directionVector[1]/self.vLen)
        self.n = (-self.v[1],self.v[0])

        # styles
        self.color = color
        self.width = 2


    def get(self, x:int) -> tuple:
        """
        x distance from 0
        """

        x -= self.offset

        return (self.v[0]*x, self.v[1]*x)


    def getEndPoints(self) -> tuple:
        return self.get(self.start), self.get(self.end)


    def _addMarkersToAxis(self, parent):
        maxMarkerLengthStr = min(max(len(str(self.start)), len(str(self.end))), 10)

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
        # NOTE: FEJL her ved start på noget underligt, fx startPos = 0.7832
        nullX, nullY = parent.pixel(0,0)
        if (parent.padding[0] <= nullX <= parent.width+parent.padding[0]) and (parent.padding[1] <= nullY <= parent.height+parent.padding[1]):

            distBeforeNull = vlen(vdiff((nullX, nullY), self.lineStartPoint))
            distafterNull = vlen(vdiff((nullX, nullY), self.lineEndPoint))

            procentBeforeNull = distBeforeNull/pixelLength
            procentAfterNull = distafterNull/pixelLength

            ticksBeforeNull = math.ceil(lengthOverStep*procentBeforeNull)
            ticksAfterNull = math.ceil(lengthOverStep*procentAfterNull)

            # NOTE: øhh der er et problem ved fx hjørnerne ikke bliver dækket hvis der er skrå akser
            if not parent.standardBasis: 
                marker = Marker("0", 0, shell(self), **parent.markerOptions)
                marker.finalize(parent)
                markers.append(marker)

            for i in range(1, ticksBeforeNull+1):
                marker = Marker(str(round(-step*i, maxMarkerLengthStr)), -step*i, shell(self), **parent.markerOptions)
                marker.finalize(parent)
                markers.append(marker)
            
            for i in range(1, ticksAfterNull+1):
                marker = Marker(str(round(step*i, maxMarkerLengthStr)), step*i, shell(self), **parent.markerOptions)
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
                marker = Marker(str(round(p,maxMarkerLengthStr)), p, shell(self), **parent.markerOptions)
                marker.finalize(parent)
                markers.append(marker)
        
        self.markers = markers


    def _addStartAndEnd(self, start:float | int, end:float | int, makeOffsetAvaliable:bool=True):
        # computed 
        self.start = start
        self.end = end
        self.offset = 0
        if makeOffsetAvaliable:
            self.offset = self.start
        self.title = None
        self.hasNull = (self.start <= 0 and self.end >= 0)
        self.pos = self.getEndPoints()[0]


    def finalize(self, parent, visualOffset:tuple=(0,0)):
        self.visualOffset = visualOffset
        
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


    def _addTitle(self, title:str, parent) -> None:
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

