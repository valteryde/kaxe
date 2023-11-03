
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
                                  batch=self.batch, 
                                  align="center", 
                                  anchor_x="center",
                                  anchor_y="center",
                                #   font_name=self.font,
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
            nudge = - (distPointLine(n, p2, box[2:4]) + 2)
        
        if r == 1 and insideBox(box, p1):
            nudge = distPointLine(n, p1, box[2:4]) + 2

        self.textLabel.x += n[0] * nudge
        self.textLabel.y += n[1] * nudge

        parent.addDrawingFunction(self)
        
        dx = min(self.textLabel.x - self.textLabel.width/2, 0)
        dy = min(self.textLabel.y - self.textLabel.height/2, 0)
        if dx < 0 or dy < 0:
            parent.addPaddingCondition(-(dx), -(dy))

        #print(self.textLabel.x - self.textLabel.width/2, self.textLabel.y - self.textLabel.height/2)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, x, y):
        self.batch.push(x,y)


    def getBoundingBox(self):
        if hasattr(self, 'textLabel'):
            return self.textLabel.getBoundingBox()
        return [0,0]


class Axis:
    def __init__(self, 
                 directionVector:tuple, 
                 start, 
                 end, 
                 color=(0,0,0,255), 
                 offset:bool=True):
        """
        offset:bool If graph should be offset with equvalient of start value
        """
        
        self.start = start
        self.end = end
        self.offset = 0
        if offset:
            self.offset = self.start
        self.title = None

        self.directionVector = directionVector
        self.vLen = math.sqrt(directionVector[0]**2+directionVector[1]**2)
        self.v = (directionVector[0]/self.vLen, directionVector[1]/self.vLen)
        self.n = (-self.v[1],self.v[0])
        self.pos = self.getEndPoints()[0]

        # styles
        self.color = color
        self.width = 2

        # computed 
        self.hasNull = (self.start <= 0 and self.end >= 0)


    def get(self, x:int) -> tuple:
        """
        x distance from 0
        """

        x -= self.offset

        return (self.v[0]*x, self.v[1]*x)


    def getEndPoints(self) -> tuple:
        return self.get(self.start), self.get(self.end)


    def _addMarkersToAxis_(self, parent):
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
        if (parent.padding[0] <= nullX <= parent.width+self.padding[0]) and (parent.padding[1] <= nullY <= parent.height+parent.padding[1]):

            distBeforeNull = vlen(vdiff((nullX, nullY), self.lineStartPoint))
            distafterNull = vlen(vdiff((nullX, nullY), self.lineEndPoint))

            procentBeforeNull = distBeforeNull/pixelLength
            procentAfterNull = distafterNull/pixelLength

            ticksBeforeNull = math.ceil(lengthOverStep*procentBeforeNull)
            ticksAfterNull = math.ceil(lengthOverStep*procentAfterNull)

            # NOTE: øhh der er et problem ved fx hjørnerne ikke bliver dækket hvis der er skrå akser
            if not self.standardBasis: 
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


    def finalize(self, parent, visualOffset:tuple=(0,0)):
        self.visualOffset = visualOffset
        
        p1, p2 = self.getEndPoints()
        self.p1 = (p1[0]*parent.scale[0]-parent.offset[0], p1[1]*parent.scale[1]-parent.offset[1])
        self.p2 = (p2[0]*parent.scale[0]-parent.offset[0], p2[1]*parent.scale[1]-parent.offset[1])
        # self.p1 = (p1[0]*parent.scale[0]-parent.offset[0], p1[1]*parent.scale[1]-parent.offset[1])
        # self.p2 = (p2[0]*parent.scale[0]-parent.offset[0], p2[1]*parent.scale[1]-parent.offset[1])

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
        # self.shapePoint1 = pg.shapes.Circle(*self.p1, 5, color=self.color)
        # self.shapePoint2 = pg.shapes.Circle(*self.p2, 5, color=self.color)
        parent.addDrawingFunction(self)


    def getPixelPos(self):
        return (self.shapeLine.x0, self.shapeLine.y0), (self.shapeLine.x1, self.shapeLine.y1)    


    def addTitle(self, title:str, parent) -> None:
        angle = angleBetweenVectors(self.v, (1,0))

        p1, p2 = self.getPixelPos()
        v = vectorScalar(vdiff(p1, p2), 1/2)
        axisPos = addVector(p1, v)
            
        maxMarkerWidth = max([marker.getBoundingBox()[0] for marker in self.markers])

        textDimension = getTextDimension(title, parent.fontSize)
        v = vectorScalar(self.n, (maxMarkerWidth+textDimension[1]) * self.markers[-1].directionFromAxis)

        pos = (axisPos[0]+v[0], axisPos[1]+v[1])
        self.title = Text(title, *pos, parent.fontSize, parent.markerColor, angle)

        parent.addPaddingCondition(bottom=-min(pos[1], 0) + parent.fontSize/2, left=-min(pos[0], 0) + parent.fontSize/2)


    def draw(self, *args, **kwargs):
        self.shapeLine.draw(*args, **kwargs)
        if self.title: self.title.draw(*args, **kwargs)


    def push(self, x,y):
        self.shapeLine.push(x,y)
        if self.title: self.title.push(x,y)

