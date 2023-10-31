
import pyglet as pg
from ..plot.styles import *
from ..plot.shapes import drawStaticBatch, shapes
from ..plot.helper import *

class Points:
    def __init__(self, x, y, color:tuple=None, size:int=None, symbol:str=CIRCLE, connect:bool=False):
        self.batch = pg.shapes.Batch()
        self.points = []
        self.lines = []
        
        x, y = list(zip(*sorted(zip(x, y), key=lambda x: x[0])))

        self.x = x
        self.y = y
    
        # color
        if color is None:
            self.color = getRandomColor()
        else:
            self.color = color

        self.size = size
        self.symbol = symbol
        self.legendSymbol = self.symbol
        self.legendColor = self.color
        self.connect = connect
        
        self.farLeft = min(self.x)
        self.farRight = max(self.x)
        self.farTop = max(self.y)
        self.farBottom = min(self.y)

    
    def finalize(self, parent):
        
        # set style 
        if self.size is None: self.size = round(parent.fontSize / 6)


        for i, (x,y) in enumerate(zip(self.x,self.y)):
            x,y = parent.pixel(x, y)
            if not parent.inside(x,y):
                continue

            if self.symbol:
                circle = shapes.Circle(x,y, self.size, color=self.color, batch=self.batch)
                self.points.append(circle)
            
            if not self.connect or i == len(self.x)-1:
                continue
            
            x1, y1 = parent.pixel(self.x[i+1], self.y[i+1])
            if vlen(vdiff((x1, y1), (x,y))) < self.size:
                continue

            line = shapes.Line(x,y, x1, y1, color=self.color, width=self.size, batch=self.batch, center=True)
            self.lines.append(line)
        
    
    def draw(self):
        self.batch.draw()

    
    def drawStatic(self, surface):
        drawStaticBatch(self.batch, surface)


    def legend(self, text:str):
        self.legendText = text