
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
        self.attrmap.default('barGap', 100)
        self.attrmap.default('barSmallGapProc', 0.2)
        self.attrmap.default('barGapProc', 0.8)

        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)

        if rotate:
            self.axis = Axis((1,0))
        else:
            self.axis = Axis((0,1))

        self.maxNumber = 0
        self.maxNumberAmount = 0
        self.bars = []
        self.numberAmount = 0

        self.legendsLabels = []

        self.titleText = None
        self.secondAxisTitle = None
        self.firstAxisTitle = None

   
    def __getMaxNumber__(self):
        return self.maxNumber


    def __prepare__(self):

        
        self.axis.addStartAndEnd(0, self.__getMaxNumber__())
        
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

        self.colors = self.getAttr('barColor')
        if self.colors == None:
            self.colors = [getRandomColor() for _ in range(self.maxNumberAmount)]
        elif type(self.colors[0]) is int:
            self.colors = [self.colors]

        for i, label in enumerate(self.legendsLabels):
            if label: self.legendbox.add(label, color=self.colors[i])

        self.barbatch = shapes.Batch()
        self.addDrawingFunction(self.barbatch)

        # add bars
        self.__renderBars__()

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


    # bars
    def __renderBars__(self):
          
        if self.rotate:
            barGap = self.getAttr('barGap')
            barWidth = self.height / len(self.bars) - (len(self.bars)+1)/len(self.bars) * barGap
            x = self.windowBox[1] + barGap

        else:
            barGap = self.getAttr('barGap')
            barWidth = self.width / len(self.bars) - (len(self.bars)+1)/len(self.bars) * barGap
            x = self.windowBox[0] + barGap
        
        for label, numbers in self.bars:
            
            if self.rotate:
                y = self.windowBox[0]
            else:
                y = self.windowBox[1]


            for i, number in enumerate(numbers):

                # så længde den er lineær så dur det her
                if self.rotate:
                    height = self.axis.get(number)[0] - self.windowBox[0]
                    shapes.Rectangle(y, x, height, barWidth, color=self.colors[i], batch=self.barbatch)
                else:
                    height = self.axis.get(number)[1] - self.windowBox[1]
                    shapes.Rectangle(x, y, barWidth, height, color=self.colors[i], batch=self.barbatch)

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
                text.x -= text.width/2 + self.getAttr('fontSize')*0.25
            else:
                text.y -= text.height/2 + self.getAttr('fontSize')*0.25
            
            self.include(text.x, text.y, text.width, text.height)

            x += barWidth + barGap


    def add(self, label, numbers):
        if type(numbers) is not list: numbers = [numbers]
        filterednums = [i for i in numbers if i is not None]
        self.maxNumber = max(sum(filterednums), self.maxNumber)
        self.maxNumberAmount = max(len(filterednums), self.maxNumberAmount)
        self.numberAmount += len(filterednums)
        self.bars.append([label, numbers])

    
    def legends(self, *legends):
        self.legendsLabels = legends


    def title(self, firstAxis:str=None, secondAxis:str=None, title=None):
        self.titleText = title
        self.firstAxisTitle=firstAxis
        self.secondAxisTitle=secondAxis
        return self


class GroupBar(Bar):

    
    # en måde at gøre den nemmer at ændre på er at dele tingene op i flere
    # delfunktioner. fx __setAxisPos__ ændres af BoxPlot til altid at have 
    # akserne i nederste hjørne

    def __init__(self, rotate=False):
        super().__init__(rotate)
        self.identity = 'groupbarchart'


    def __getMaxNumber__(self):
        return max([max([j for j in i if j is not None]) for _, i in self.bars])

    def __renderBars__(self):
        
        numberSmallGaps = sum([len(i)-1 for _, i in self.bars if len(i) > 1])
        
        # definition: self.bars = self.groups
        # height = numberSmallGaps * smallBarGap + barWidth * self.numberAmount + barGap * (len(self.bars)-1)
        # smallBarGap = barWidth * proc_s
        # barGap = barWidth * proc_l

        smallGapProc = self.getAttr('barSmallGapProc')
        barGapProc = self.getAttr('barGapProc')
        
        # height = numberSmallGaps * barWidth * barGapProc + barWidth * self.numberAmount + barWidth * smallGapProc * (len(self.bars)-1)
        # 1 / ((numberSmallGaps * barGapProc + self.numberAmount + smallGapProc * (len(self.bars)-1)) / height) =  * barWidth
        # height / (numberSmallGaps * barGapProc + self.numberAmount + smallGapProc * (len(self.bars)-1)) = barWidth

        if self.rotate:
            barWidth = self.height / ((numberSmallGaps-1) * smallGapProc + self.numberAmount + barGapProc * (len(self.bars)+1))
        else:
            barWidth = self.width / ((numberSmallGaps-1) * smallGapProc + self.numberAmount + barGapProc * (len(self.bars)+1))

        barGap = barGapProc * barWidth
        smallBarGap = smallGapProc * barWidth

        if self.rotate:
            x = self.windowBox[1] + barGap
        else:
            x = self.windowBox[0] + barGap

        for label, numbers in self.bars:
            
            if self.rotate:
                y = self.windowBox[0]
            else:
                y = self.windowBox[1]

            for i, number in enumerate(numbers):
                if number is None: continue

                # så længde den er lineær så dur det her
                if self.rotate:
                    height = self.axis.get(number)[0] - self.windowBox[0]
                    shapes.Rectangle(y, x, height, barWidth, color=self.colors[i], batch=self.barbatch)
                else:
                    height = self.axis.get(number)[1] - self.windowBox[1]
                    shapes.Rectangle(x, y, barWidth, height, color=self.colors[i], batch=self.barbatch)

                x += smallBarGap + barWidth
            x -= barWidth + smallBarGap

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
                text.y -= (len([i for i in numbers if i is not None])-1) * barWidth/2
                text.x -= text.width/2 + self.getAttr('fontSize')*0.25
            else:
                text.x -= (len([i for i in numbers if i is not None])-1) * barWidth/2
                text.y -= text.height/2 + self.getAttr('fontSize')*0.25
            
            self.include(text.x, text.y, text.width, text.height)

            x += barWidth + barGap
