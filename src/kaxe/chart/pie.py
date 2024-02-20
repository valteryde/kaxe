

# a simple xy plot
# faster than the true plot

from ..core.helper import *
import logging
from ..core.axis import *
from ..core.window import Window
from ..core.styles import getRandomColor, isLightOrDark
from ..core.symbol import symbol

XYPLOT = 'xy'


class PieSlice:

    def __init__(self, number, legend, label, color:tuple=(255,255,255,255), width:int=None) -> None:
        
        self.number = number
        self.label = label
        self.width = width

        self.batch = shapes.Batch()
        
        self.color = color
        self.legendText = legend
        self.legendSymbol = symbol.CIRCLE
        self.legendColor = self.color


    def setSlice(self, angle, shift):
        self.angle = angle
        self.phaseshift = shift

    
    def finalize(self, parent):
        center = parent.center

        r = parent.r
        shapes.Arc(
            self.phaseshift,
            self.angle,
            center, 
            r, 
            color=self.color,
            batch=self.batch
        )

        angle = (self.angle/2 + self.phaseshift) % 360
        textAngle = angle
        if 90 < angle < 270:
            textAngle = textAngle - 180

        if self.label:
            textStr = self.label
        else:
            textStr = f'${self.number}$'

        width, _ = getTextDimension(textStr, parent.getAttr('fontSize'))
        color = (255,255,255,255)
        if isLightOrDark(self.color): color = (0,0,0,255)
        a = r*0.05
        text = Text(
            textStr, 
            center[0]+(r-width/2-a)*math.cos(math.radians(angle)), 
            center[1]+(r-width/2-a)*math.sin(math.radians(angle)), 
            rotate=textAngle,
            fontSize=parent.getAttr('fontSize'),
            color=color
        )

        parent.addDrawingFunction(text, 3)
    
    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


    def push(self, x, y):
        self.batch.push(x, y)


    def legend(self, text:str):
        self.legendText = text
        return self



class Pie(Window):
    
    def __init__(self): # |
        super().__init__()
        self.identity = 'piechart'

        self.titleText = None
        self.attrmap.default('titleFontSize', 100)
        self.attrmap.default('width', 1250)
        self.attrmap.default('height', 1000)
        self.attrmap.default('gap', 10)
        self.attrmap.default('phaseshift', 0)
        self.attrmap.default('circleSizeProcent', 0.75)

        self.linebatch = shapes.Batch()
        self.sum = 0
        self.pieslices = 0

   
    def __prepare__(self):

        r = min(self.windowBox[2], self.windowBox[3])/2 + 5
        center = (self.windowBox[0] + self.windowBox[2]/2, self.windowBox[1] + self.windowBox[3]/2 - r*(1-self.getAttr('circleSizeProcent')))
        r *= self.getAttr('circleSizeProcent')

        self.center = center
        self.r = r

        self.height -= int(self.height - self.center[1] - r)

        colors = self.getAttr('pieColor')
        if colors == None:
            colors = [getRandomColor() for _ in range(self.pieslices)]
        elif type(colors[0]) is int:
            colors = [colors]

        phaseshift = math.radians(self.getAttr('phaseshift'))
        firstLeg = (center[0]+math.cos(phaseshift)*r, center[1]+math.sin(phaseshift)*r)
        anglesum = self.getAttr('phaseshift')
        for i, obj in enumerate(self.objects):
            proc = obj.number / self.sum
            angle = proc * 360
            obj.setSlice(angle, anglesum)
            obj.color = colors[i]
            obj.legendColor = obj.color
            anglesum += angle

            dir = math.cos(math.radians(anglesum)), math.sin(math.radians(anglesum))
            width = self.getAttr('gap')
            shapes.LineSegment(
                [
                    firstLeg,
                    center,
                    (center[0]+dir[0]*r, center[1]+dir[1]*r),
                ], 
                color=self.getAttr('backgroundColor'),
                center=True,
                width=width,
                batch=self.linebatch,
            )

        self.addDrawingFunction(self.linebatch, 2)

        if self.titleText:
            title = Text(self.titleText, center[0], center[1]+r, fontSize=self.getAttr('titleFontSize'))
            title.y += title.height

            self.addDrawingFunction(title)

            x = self.include(title.x, title.y, title.width, title.height)[0]
            self.center = center[0]+x, center[1]


    def add(self, number, legend=None, label=None):
        self.objects.append(PieSlice(number, legend, label))
        self.pieslices += 1
        self.sum += number


    # special api
    def title(self, title=None):
        self.titleText = title
        return self
