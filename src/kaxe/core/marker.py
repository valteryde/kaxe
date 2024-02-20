
from .helper import *
from .shapes import shapes
from .text import Text, getTextDimension
from .styles import AttrObject
from types import MappingProxyType

# c = 0
# def count():
#     global c
#     c += 1
#     print(c)

class Marker(AttrObject):

    name = "Marker"

    defaults = MappingProxyType({
        "showNumber": True,
        "showLine": True,
        "tickWidth" : 3,
        "tickLength": 15,
        "gridlineColor" : (0,0,0,75),
        "gridlineWidth": 2
    })

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


    def finalize(self, parent):
        self.setAttrMap(parent.attrmap)

        self.axis = self.axis()
        self.shown = True

        # styles
        color = self.getAttr('color')
        markerWidth = self.getAttr('tickWidth')
        fontSize = self.getAttr('fontSize')
        showLine = self.getAttr('showLine')

        if showLine:
            p1, p2 = parent.pointOnWindowBorderFromLine(parent.inversetranslate(*self.axis.get(self.x)), self.axis.v)
            self.line = shapes.Line(*p1, *p2, color=self.getAttr('gridlineColor'), width=self.getAttr('gridlineWidth'))

        pos = self.axis.get(self.x)

        n = (self.axis.n[0]/parent.scale[0], self.axis.n[1]/parent.scale[1])
        nlen = vlen(n)
        n = (n[0]/nlen, n[1]/nlen)

        self.markerLength = self.getAttr('tickLength')

        halfMarkerLength = self.markerLength/2
        
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
        if not self.getAttr('showNumber'):
            return

        # how long away for text box not to hit marker
        # force specefic height
        fontSizeRatio = fontSize/getTextDimension(self.text, fontSize)[1]

        self.textLabel = Text(self.text,
                                  x=textPos[0], 
                                  y=textPos[1], 
                                  color=color, 
                                #   batch=self.batch, 
                                  align="center", 
                                  anchor_x="center",
                                  anchor_y="center",
                                # font_name=self.font,
                                  fontSize=int(fontSize),  #altså ja den her konstant hjælper en del på at udligne forholdet
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
        self.textLabel.y += n[1] * (nudge + fontSize * (1-fontSizeRatio) / 2) # SKAL VIRKELIG GENNEMTÆNKES IGEN

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
