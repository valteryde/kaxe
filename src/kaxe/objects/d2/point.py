
from ...core.styles import *
from ...core.shapes import shapes
from ...core.symbol import makeSymbolShapes
from ...core.symbol import symbol as symbols
from ...core.helper import *
from ...plot import identities

class Points2D:
    def __init__(self, x, y, color:tuple=None, size:int=None, symbol:str=None, connect:bool=False, lollipop=False):
        self.batch = shapes.Batch()
        self.points = []
        self.lines = []
        
        # clean lists
        cx, cy = [], []
        for i in range(len(x)):

            if isRealNumber(x[i]) and isRealNumber(y[i]):
                cx.append(x[i])
                cy.append(y[i])

        x, y = list(zip(*sorted(zip(cx, cy), key=lambda x: x[0])))

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
        if not symbol:
            self.legendSymbol = symbols.CIRCLE
        self.lollipop = lollipop
        if not symbol and self.lollipop:
            self.legendSymbol = symbols.LOLLIPOP

        self.legendColor = self.color
        self.connect = connect
        
        if len(self.x) > 1:
            self.farLeft = min(self.x)
            self.farRight = max(self.x)
            self.farTop = max(self.y)
            self.farBottom = min(self.y)

        self.supports = [identities.XYPLOT, identities.POLAR]

    
    def finalize(self, parent):
        
        # set style 
        if self.size is None: self.size = round(parent.getAttr('fontSize') / 3)

        for i, (x,y) in enumerate(zip(self.x,self.y)):
            x,y = parent.pixel(x, y)
            
            if not parent.inside(x,y):
                continue
            
            # symbol
            if self.symbol:
                
                #shapes.Circle(x,y, self.size, color=self.color, batch=self.batch)
                symbol = makeSymbolShapes(self.symbol, self.size, self.color, batch=self.batch)
                symbol.x = x
                symbol.y = y
                if hasattr(symbol, 'centerAlign'): symbol.centerAlign()
                self.points.append(symbol)
            
            else:
                shapes.Circle(x, y, self.size/2, self.color, batch=self.batch)

            # lollipop (lagt til lines)
            if self.lollipop:
                _, y0 = parent.pixel(x, 0)
                line = shapes.Line(x, y, x, y0, color=self.color, width=int(self.size*.5), batch=self.batch, center=True)
                self.lines.append(line)

            # connect
            if not self.connect or i == len(self.x)-1:
                continue
            
            x1, y1 = parent.pixel(self.x[i+1], self.y[i+1])
            if x1 is None or y1 is None or x is None or y is None:
                continue
            
            if (vlen(vdiff((x1, y1), (x,y))) < self.size) and self.symbol:
                continue

            if not parent.inside(x1, y1):
                continue

            line = shapes.Line(x,y, x1, y1, color=self.color, width=int(self.size*.5), batch=self.batch, center=True)
            self.lines.append(line)
        
    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)

    def push(self, x, y):
        self.batch.push(x, y)


    def legend(self, text:str, symbol=None, color=None):
        self.legendText = text
        if symbol:
            self.legendSymbol = symbol
        if color:
            self.legendColor = color
        return self