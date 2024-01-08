
from .helper import *
from .shapes import shapes
from .text import Text
from .styles import StyleShape

class Marker(StyleShape):

    defaults = {
        "showNumber":True,
        "showLine":True,
        "tickWidth": 1,
        "tickLength": 15,
        "gridlineColor":(0,0,0,75),
    }

    inheritable = {
        "color",
        "fontSize",
    }

    name = "Marker"

    def __init__(self, 
                 text:str, 
                 x:int, 
                 axis, 
                ):
        """
        marker with line
        """
        super().__init__()

        self.text = text
        self.x = x
        self.axis = axis
        self.batch = shapes.Batch()


    def finalize(self, parent, visualOffset:tuple=(0,0)):
        self.__inherit__(parent)

        self.axis = self.axis()
        self.shown = True

        # styles
        color = self.getStyleAttr('color')
        markerWidth = self.getStyleAttr('tickWidth')
        fontSize = self.getStyleAttr('fontSize')
        showLine = self.getStyleAttr('showLine')

        self.visualOffset = addVector(visualOffset, self.axis.visualOffset) #inherit

        if showLine:
            p1, p2 = parent.pointOnWindowBorderFromLine(self.axis.get(self.x), self.axis.v)
            self.line = shapes.Line(*p1, *p2, color=self.getStyleAttr('gridlineColor'))
        
        pos = parent.translate(*self.axis.get(self.x))

        n = (self.axis.n[0]/parent.scale[0], self.axis.n[1]/parent.scale[1])
        nlen = vlen(n)
        n = (n[0]/nlen, n[1]/nlen)

        self.markerLength = self.getStyleAttr('tickLength')

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

        self.tickLine = shapes.Line(*p1, *p2, color=color, width=markerWidth, batch=self.batch, center=True)
        if not self.getStyleAttr('showNumber'):
            return

        # how long away for text box not to hit marker
        self.textLabel = Text(self.text,
                                  x=textPos[0], 
                                  y=textPos[1], 
                                  color=color, 
                                #   batch=self.batch, 
                                  align="center", 
                                  anchor_x="center",
                                  anchor_y="center",
                                # font_name=self.font,
                                  fontSize=fontSize,
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

        if showLine: parent.addDrawingFunction(self.line)
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
