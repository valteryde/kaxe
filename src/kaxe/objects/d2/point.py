
from ...core.styles import *
from ...core.color import to_rgba
from ...core.shapes import shapes
from ...core.symbol import makeSymbolShapes
from ...core.symbol import symbol as symbols
from ...core.helper import *
from ...plot import identities

class Points2D:
    """
    Create points on 2D plane
        
    Parameters
    ----------
    x : list or array-like
        The x-coordinates of the points.
    y : list or array-like
        The y-coordinates of the points.
    color : tuple, optional
        The color of the points in RGB format. If None, a random color is assigned.
    size : int, optional
        The size of the points. Default is None.
    symbol : str, optional
        The symbol used to represent the points. Default is None.
    connect : bool, optional
        If True, the points will be connected by lines. Default is False.
    lollipop : bool, optional
        If True, the points will be represented as lollipops. Default is False.
    show_points : bool, optional
        If False, point markers are not drawn. With ``connect=True``, small
        junction circles matching the line width are still drawn at vertices.
        Default is True.
    """

    def __init__(self, x, y, color:tuple=None, size:int=None, symbol:str=None, connect:bool=False, lollipop=False, show_points:bool=True):        
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
            self.color = to_rgba(color)

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
        self.show_points = show_points
        if not show_points and connect and not symbol:
            self.legendSymbol = symbols.LINE
        
        if len(self.x) > 0:
            self.farLeft = min(self.x)
            self.farRight = max(self.x)
            self.farTop = max(self.y)
            self.farBottom = min(self.y)

        self.supports = [identities.XYPLOT, identities.POLAR, identities.LOGPLOT]

    
    def finalize(self, parent):
        
        # set style 
        if self.size is None: self.size = round(parent.getAttr('fontSize') / 3)
        scale = parent.getVisualScale()
        size = max(1, round(self.size * scale))
        line_width = max(1, int(size * 0.5))

        for i, (x,y) in enumerate(zip(self.x,self.y)):
            x,y = parent.pixel(x, y)
            
            if not parent.inside(x,y):
                continue
            
            # symbol
            if self.show_points:
                if self.symbol:
                    symbol = makeSymbolShapes(self.symbol, size, self.color, batch=self.batch)
                    symbol.x = x
                    symbol.y = y
                    if hasattr(symbol, 'centerAlign'): symbol.centerAlign()
                    self.points.append(symbol)
                else:
                    radius = line_width / 2 if self.connect else size / 2
                    shapes.Circle(x, y, radius, self.color, batch=self.batch)
            elif self.connect:
                shapes.Circle(x, y, line_width / 2, self.color, batch=self.batch)

            # lollipop (lagt til lines)
            if self.lollipop:
                _, y0 = parent.pixel(x, min(max(0, parent.windowAxis[2]), parent.windowAxis[3]))
                line = shapes.Line(x, y, x, y0, color=self.color, width=line_width, batch=self.batch, center=True)
                self.lines.append(line)

            # connect
            if not self.connect or i == len(self.x)-1:
                continue
            
            x1, y1 = parent.pixel(self.x[i+1], self.y[i+1])
            if x1 is None or y1 is None or x is None or y is None:
                continue
            
            skip_dist = size if self.symbol else (line_width if not self.show_points else None)
            if skip_dist and vlen(vdiff((x1, y1), (x,y))) < skip_dist:
                continue

            if not parent.inside(x1, y1):
                continue

            line = shapes.Line(x,y, x1, y1, color=self.color, width=line_width, batch=self.batch, center=True)
            self.lines.append(line)
        
    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)

    def push(self, x, y):
        self.batch.push(x, y)


    def legend(self, text:str, symbol=None, color=None):
        """
        Adds a legend
        
        Parameters
        ----------
        text : str
            The text to be displayed in the legend.
        symbol : symbols, optional
            The symbol to be used in the legend. If not provided, the symbol used to display the points will be used.
        color : optional
            The color to be used for the legend text. If not provided, the default color will be used.
        
        Returns
        -------
        self : object
            Returns the instance of the arrow object with the updated legend.        
        """

        self.legendText = text
        if symbol:
            self.legendSymbol = symbol
        if color:
            self.legendColor = to_rgba(color)
        return self