
from ..core.helper import *
import logging
from ..core.axis import *
from ..core.styles import getRandomColor, isLightOrDark
from ..core.symbol import symbol
from ..core.window import Window

class Bar(Window):
    
    # en måde at gøre den nemmer at ændre på er at dele tingene op i flere
    # delfunktioner. fx __setAxisPos__ ændres af BoxPlot til altid at have 
    # akserne i nederste hjørne

    def __init__(self, rotate=False): # |
        super().__init__()
        self.identity = 'barchart'
        self.rotate = rotate

        self.attrmap.default('titleFontSize', 100)
        self.attrmap.default('width', 3000)
        self.attrmap.default('height', 1500)
        self.attrmap.default('barColor', None)
        self.attrmap.default('rotateLabel', 0)

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)

        if rotate:
            self.axis = Axis((1,0))
        else:
            self.axis = Axis((0,1))

        self.maxNumber = 0
        self.maxNumberAmount = 0
        self.bars = []

        self.legendsLabels = []

        self.titleText = None
        self.secondAxisTitle = None
        self.firstAxisTitle = None

   
    def __prepare__(self):

        self.axis.addStartAndEnd(0, self.maxNumber)
        
        topPoint = (self.windowBox[0], self.windowBox[3]-self.windowBox[1])
        if self.rotate:
            self.axis.setPos(
                (self.windowBox[0], self.windowBox[1]),
                (self.windowBox[2]-self.windowBox[0], self.windowBox[1])
            )
        else:
            self.axis.setPos(
                (self.windowBox[0], self.windowBox[1]),
                topPoint
            )

        self.axis.finalize(self)        
        self.axis.autoAddMarkers(self)

        colors = self.getAttr('barColor')
        if colors == None:
            colors = [getRandomColor() for _ in range(self.maxNumberAmount)]
        elif type(colors[0]) is int:
            colors = [colors]


        for i, label in enumerate(self.legendsLabels):
            if label: self.legendbox.add(label, color=colors[i])

        minYLabel = math.inf  # til akse label
        self.barbatch = shapes.Batch()
        
        if self.rotate:
            barGap = self.height/30
            barWidth = self.height / len(self.bars) - (len(self.bars)+1)/len(self.bars) * barGap
            x = self.windowBox[1] + barGap
        else:
            barGap = self.width/30
            barWidth = self.width / len(self.bars) - (len(self.bars)+1)/len(self.bars) * barGap
            x = self.windowBox[0] + barGap
        
        # bars
        self.addDrawingFunction(self.barbatch)
        for label, numbers in self.bars:
            
            if self.rotate:
                y = self.windowBox[0]
            else:
                y = self.windowBox[1]


            for i, number in enumerate(numbers):

                # så længde den er lineær så dur det her
                if self.rotate:
                    height = self.axis.get(number)[0] - self.windowBox[0]
                    shapes.Rectangle(y, x, height, barWidth, color=colors[i], batch=self.barbatch)
                else:
                    height = self.axis.get(number)[1] - self.windowBox[1]
                    shapes.Rectangle(x, y, barWidth, height, color=colors[i], batch=self.barbatch)

                y += height

            if self.rotate:
                x0, y0 = self.windowBox[0], x+barWidth/2
            else:
                x0, y0 = x+barWidth/2, self.windowBox[1]

            text = Text(str(label),
                        x0, 
                        y0, 
                        fontSize=self.getAttr('fontSize'), 
                        color=self.getAttr('color'), 
                        batch=self.barbatch,
                        rotate=self.getAttr('rotateLabel')
            )
            
            if self.rotate:
                pass
                text.x -= text.width/2 + self.getAttr('fontSize')*0.25
            else:
                text.y -= text.height/2 + self.getAttr('fontSize')*0.25
            
            minYLabel = min(text.y, minYLabel)
            self.include(text.x, text.y, text.width, text.height)

            x += barWidth + barGap

        # title
        if self.titleText:
            
            title = Text(self.titleText, self.windowBox[0] + self.windowBox[2]/2, topPoint[1], fontSize=self.getAttr('titleFontSize'))
            title.y += title.height*1.5
            self.addDrawingFunction(title)
            self.include(title.x, title.y, title.width, title.height)

        if self.secondAxisTitle: self.axis.addTitle(self.secondAxisTitle, self)

        if self.firstAxisTitle and not self.rotate:
            self.firstTitle = Text(self.firstAxisTitle, self.windowBox[0]+self.windowBox[2]/2, 0, fontSize=self.getAttr('fontSize'))
        
        if self.firstAxisTitle and self.rotate:
            self.firstTitle = Text(self.firstAxisTitle, 0, self.windowBox[1]+self.windowBox[3]/2, fontSize=self.getAttr('fontSize'), rotate=90)
        
        if self.firstAxisTitle:
            self.include(self.firstTitle.x, self.firstTitle.y, self.firstTitle.width, self.firstTitle.height)
            self.addDrawingFunction(self.firstTitle)




    def add(self, label, numbers):
        if type(numbers) is not list: numbers = [numbers]
        self.maxNumber = max(sum(numbers), self.maxNumber)
        self.maxNumberAmount = max(len(numbers), self.maxNumberAmount)
        self.bars.append([label, numbers])

    
    def legends(self, *legends):
        self.legendsLabels = legends


    def title(self, firstAxis:str=None, secondAxis:str=None, title=None):
        self.titleText = title
        self.firstAxisTitle=firstAxis
        self.secondAxisTitle=secondAxis
        return self
