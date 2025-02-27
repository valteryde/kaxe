
from .helper import *
from .shapes import shapes
from .text import Text, getTextDimension
from .styles import AttrObject
from types import MappingProxyType
import numpy as np
from .styles import ComputedAttribute

# c = 0
# def count():
#     global c
#     c += 1
#     print(c)

def sign(v):
    return 1 if v > 0 else -1

class Marker(AttrObject):

    name = "Marker"

    defaults = MappingProxyType({
        "showNumber": True,
        "showLine": True,
        "showTick":True,
        "tickWidth" : 4,
        "tickLength": 15,
        "gridlineColor" : (0,0,0,100),
        "gridlineWidth": 2,
        "offsetTick": False,
        "tickGap": ComputedAttribute(lambda m: max(m.getAttr('fontSize')//10, 5)),
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

        n = (self.axis.titleNormal[0]/parent.scale[0], self.axis.titleNormal[1]/parent.scale[1])
        nlen = vlen(n)
        n = (n[0]/nlen, n[1]/nlen)

        self.markerLength = self.getAttr('tickLength')

        halfMarkerLength = self.markerLength/2
        
        p1 = (pos[0]+n[0]*halfMarkerLength, pos[1]+n[1]*halfMarkerLength)
        p2 = (pos[0]-n[0]*halfMarkerLength, pos[1]-n[1]*halfMarkerLength)

        if (not parent.inside(*pos)):
            self.line = None
            self.shown = False
            return

        if self.getAttr('showTick'):
            
            if self.getAttr('offsetTick'):
                p1 = p1[0]+n[0]*halfMarkerLength, p1[1]+n[1]*halfMarkerLength
                p2 = p2[0]+n[0]*halfMarkerLength, p2[1]+n[1]*halfMarkerLength
                self.tickLine = shapes.Line(*p1, *p2, color=color, width=markerWidth, batch=self.batch, center=True)
            else:
                self.tickLine = shapes.Line(*p1, *p2, color=color, width=markerWidth, batch=self.batch, center=True)
        
        if not self.getAttr('showNumber'):
            return

        # how long away for text box not to hit marker
        # force specefic height

        self.textLabel = Text(self.text,
                                  x=pos[0], 
                                  y=pos[1], 
                                  color=color, 
                                #   batch=self.batch, 
                                  anchor_x="center",
                                  anchor_y="center",
                                # font_name=self.font,
                                  fontSize=int(fontSize),
        )

        # da den placeres på aksen til at starte med skal den bare 
        # flyttes tickLength ned med n.

        # hvilken side rammer den mest (husk markers ikke roteres)
        # mest horisontalt
        
        if abs(self.axis.titleNormal[0]) > abs(self.axis.titleNormal[1]):
            self.textLabel.push(sign(self.axis.titleNormal[0])*self.textLabel.width/2, 0) # kan godt være den skal rundes op til 1 eller -1

        # mest vertikalt
        else:
            self.textLabel.push(0, sign(self.axis.titleNormal[1])*self.textLabel.height/2)

        nudge = vectorScalar(self.axis.titleNormal, self.getAttr('showTick') * (self.getAttr('offsetTick')*self.getAttr('tickLength')/2 + self.getAttr('tickLength')/2) + self.getAttr('tickGap')) # 5 kunne være et valg
        
        self.textLabel.push(*nudge)

        if showLine: parent.addDrawingFunction(self.line)
        parent.addDrawingFunction(self.batch, 2)
        parent.addDrawingFunction(self.textLabel, 2)
        
        parent.includeElement(self.textLabel)


    def getBoundingBox(self):
        if hasattr(self, 'textLabel'):
            return self.textLabel.getBoundingBox()
        return [0,0]
    

    def pos(self):
        if hasattr(self, 'textLabel'):
            return self.textLabel.getCenterPos()
