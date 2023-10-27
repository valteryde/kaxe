
import pyglet as pg
from .helper import *
from .shapes import shapes, drawStaticBatch
from .text import Text

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
        self.batch = pg.shapes.Batch()
        
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

        if (not parent.inside(*pos)):
            self.line = None
            return

        self.tickLine = shapes.Line(*p1, *p2, color=self.color, width=self.markerWidth, batch=self.batch, center=True)
        if not self.showNumber:
            return


        distanceFromMarker = self.markerLength
        r = 1

        # special case, marker is vertical or horizontal
        if n[0] == 0:
            r = -1
        if n[1] == 0:
            r = 1
        
        textPos = (pos[0]+r*n[0]*distanceFromMarker, pos[1]+r*n[1]*distanceFromMarker)
        
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
            textPos[0]-self.textLabel.content_width/2,
            textPos[1]-self.textLabel.content_height/2,
            textPos[0]+self.textLabel.content_width/2,
            textPos[1]+self.textLabel.content_height/2
        ]

        nudge = 0
        if r == -1 and insideBox(box, p2):
            nudge = - (distPointLine(n, p2, box[2:4]) + 2)
        
        if r == 1 and insideBox(box, p1):
            nudge = distPointLine(n, p1, box[2:4]) + 2

        self.textLabel.x += n[0] * nudge
        self.textLabel.y += n[1] * nudge

        parent.addDrawingFunction(self)


    def draw(self):
        self.batch.draw()


    def drawStatic(self, surface):
        drawStaticBatch(self.batch, surface)


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


    def draw(self):
        self.shapeLine.draw()


    def drawStatic(self, surface):
        self.shapeLine.drawStatic(surface)
