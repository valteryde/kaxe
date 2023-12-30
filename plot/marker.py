
from .helper import *
from .shapes import shapes
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
        self.shown = True

        self.visualOffset = addVector(visualOffset, self.axis.visualOffset) #inherit

        if self.showLine:
            p1, p2 = parent.pointOnWindowBorderFromLine(self.axis.get(self.x), self.axis.v)
            self.line = shapes.Line(*p1, *p2, color=self.gridlineColor)
        
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
            self.shown = False
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

        if self.showLine: parent.addDrawingFunction(self.line)
        parent.addDrawingFunction(self.batch, 2)
        parent.addDrawingFunction(self.textLabel, 2)
        
        parent.include(self.textLabel.x, self.textLabel.y, self.textLabel.width, self.textLabel.height)


    def getBoundingBox(self):
        if hasattr(self, 'textLabel'):
            return self.textLabel.getBoundingBox()
        return [0,0]
    

    def pos(self):
        if hasattr(self, 'textLabel'):
            return self.textLabel.x, self.textLabel.y
