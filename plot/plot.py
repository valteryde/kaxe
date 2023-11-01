
import math
from .helper import *
import logging
from .styles import *
from .axis import *
from .text import Text, getTextDimension
from pyglet.gl import *
from .shapes import shapes
from .symbol import makeSymbolShapes
from PIL import Image
import tqdm
from random import randint
import os

"""
structure to parent + child

Axis is diffrent from other objects

To be done:
    pass
"""

class Plot:
    def __init__(self, 
                 labels:list=["", ""],
                 window:tuple=[None, None, None, None], 
                 untrueAxis:bool=None,
                 firstAxis:tuple = (1,0),
                 secondAxis:tuple = (0,1)
                ): # |
        """
        untrueAxis:bool dictates if line intersection should be (0,0), only works with standard basis

        window:tuple [x0, x1, y0, y1] axis

        left to right is always positive
        bottom to top is always positive
        """
        
        self.axis = [lambda: self.firstAxis, lambda: self.secondAxis]

        # options
        self.windowAxis = window
        self.firstAxisVector = firstAxis
        self.secondAxisVector = secondAxis
        self.standardBasis = (self.firstAxisVector[0] == 0 or self.firstAxisVector[1] == 0) and (self.secondAxisVector[0] == 0 or self.secondAxisVector[1] == 0)

        self.untrueAxis = untrueAxis

        self.shapes = []
        self.objects = []
        self.legendObjects = []
        self.legendBatch = shapes.Batch()
        self.legendBoxShape = shapes.Batch()
        
        self.scale = (0,0)
        self.offset = [0,0]

        # styles
        self.width = None
        self.height = None
        self.padding = None
        self.backgroundColor = None
        self.markerColor = None
        self.markerWidth = None
        self.markerLength = None
        self.font = None
        self.gridLines = None
        self.gridLineColor = None
        self.fontSize = None
        self.markerStepSizeBand = None

        
    def style(
            self, 
            __overwrite__:tuple=True,
            windowWidth:int=None,
            windowHeight:int=None,
            padding:list=None,
            backgroundColor:tuple=None, 
            markerColor:tuple=None,
            markerWidth:int=None,
            markerLength:int=None,
            fontSize:int=None,
            font:str=None,
            gridLines:bool=None,
            gridLineColor:tuple=None,
            markerStepSizeBand:tuple=None
        ):
        """
        change style on plotting window
        padding: left, bottom, top, right
        """

        if not __overwrite__:
            if not windowWidth is None and self.width is None: self.width = windowWidth
            if not windowHeight is None and self.height is None: self.height = windowHeight
            if not padding is None and self.padding is None: self.padding = list(padding)
            if not backgroundColor is None and self.backgroundColor is None: self.backgroundColor = backgroundColor
            if not markerColor is None and self.markerColor is None: self.markerColor = markerColor
            if not markerWidth is None and self.markerWidth is None: self.markerWidth = markerWidth
            if not markerLength is None and self.markerLength is None: self.markerLength = markerLength
            if not font is None and self.font is None: self.font = font
            if not gridLines is None and self.gridLines is None: self.gridLines = gridLines
            if not gridLineColor is None and self.gridLineColor is None: self.gridLineColor = gridLineColor
            if not fontSize is None and self.fontSize is None: self.fontSize = fontSize
            if not markerStepSizeBand is None and self.markerStepSizeBand is None: self.markerStepSizeBand = markerStepSizeBand

        else:
            if not windowWidth is None: self.width = windowWidth
            if not windowHeight is None: self.height = windowHeight
            if not padding is None: self.padding = list(padding)
            if not backgroundColor is None: self.backgroundColor = backgroundColor
            if not markerColor is None: self.markerColor = markerColor
            if not markerWidth is None: self.markerWidth = markerWidth
            if not markerLength is None: self.markerLength = markerLength
            if not font is None: self.font = font
            if not gridLines is None: self.gridLines = gridLines
            if not gridLineColor is None: self.gridLineColor = gridLineColor
            if not fontSize is None: self.fontSize = fontSize
            if not markerStepSizeBand is None: self.markerStepSizeBand = markerStepSizeBand

        if self.width and self.fontSize is None: self.fontSize = int(self.width/70)
        if self.fontSize and self.markerStepSizeBand is None: self.markerStepSizeBand = [int(self.fontSize*7), int(self.fontSize*4)]


        # package options
        self.markerOptions = {
            "color":self.markerColor,
            "fontSize":self.fontSize, 
            "markerWidth":self.markerWidth,
            "markerLength":self.markerLength,
            "gridlineColor":self.gridLineColor,
            "showLine":self.gridLines
        }

        return self


    def addPaddingCondition(self, left:int=0, bottom:int=0, top:int=0, right:int=0):
        # could be a problem depending on where padding is calcualted
        left = int(left)
        right = int(right)
        bottom = int(bottom)
        top = int(top)


        self.padding = (
            self.padding[0] + left,
            self.padding[1] + bottom,
            self.padding[2] + right,
            self.padding[3] + top,
        )

        # opdater ikke disse. Forskellen er indlejret i padding
        # self.offset[0] += left
        # self.offset[1] += bottom

        for i in self.shapes:
            if type(i) is tuple: # list is still unsorted
                i[0].push(left, bottom)
                continue
            i.push(left, bottom)
        
        # for i in self.objects:
        #     i.push(left, bottom)


    def __createLegendBox__(self): # maybe add as a seperate object
        """
        stadigvæk lidt skrøbelig
        """

        self.legendShapes = []
        
        for obj in self.objects:
            if hasattr(obj, "legendText"): # has legend ready

                symbol = makeSymbolShapes(obj.legendSymbol, self.fontSize, obj.legendColor, self.legendBatch)

                self.legendObjects.append((
                    symbol, 
                    Text(obj.legendText,
                        x=0,
                        y=0,
                        color=self.markerColor, 
                        batch=self.legendBatch,
                        anchor_x="left",
                        anchor_y="top",
                        # font_name=self.font,
                        fontSize=self.fontSize
                        )
                    )
                )


        if len(self.legendObjects) > 0:
            
            # calculate grid sizes
            legendMaxWidth = self.width * .7 # NOTE: STYLE
            legendSizeThickness = 2 #NOTE: STYLE
            legendGridSpacing = (int(self.fontSize/2), int(self.fontSize/2)+2) # NOTE: STYLE
            legendPadding = (5, 5, 5, 5) # NOTE: STYLE, left bottom right top
            legendSymbolTextSpacing = int(self.fontSize/4) # NOTE: STYLE
            legendDrawBox = False

            # legendGridSpacing = (0, 0) # NOTE: STYLE
            # legendPadding = (0, 0, 0, 0) # NOTE: STYLE, left bottom right top

            grid = [[]]
            rowWidth = 0
            maxGridWidth = 0
            sumTextHeight = 0
            rowTextHeight = 0
            for symbol, text in self.legendObjects:
                
                width = text.width + symbol.getBoundingBox()[0] + legendGridSpacing[0] + legendSymbolTextSpacing
                rowWidth += width
                rowTextHeight = max(rowTextHeight, text.height)

                if rowWidth > legendMaxWidth:
                    grid.append([])
                    maxGridWidth = max(maxGridWidth, rowWidth-width)
                    rowWidth = width
                    sumTextHeight += rowTextHeight

                grid[-1].append((symbol, text))
            sumTextHeight += rowTextHeight
            maxGridWidth = max(maxGridWidth, rowWidth)
            
            maxGridWidth -= legendGridSpacing[0]
            
            legendBoxSize = [
                maxGridWidth + legendPadding[0] + legendPadding[2],  
                sumTextHeight + legendGridSpacing[1] * (len(grid)-1) + legendPadding[1] + legendPadding[3]
            ]
            
            legendPos = [self.width/2 + self.padding[0] - legendBoxSize[0]/2, 0]

            # draw grid
            rowPos = 0
            for row in grid:
                colPos = 0

                for symbol, text in row:
                    self.legendShapes.append(symbol)
                    self.legendShapes.append(text)

                    symbolSize = symbol.getBoundingBox()

                    basePos = [
                        legendPos[0] + legendPadding[0],
                        legendPos[1] + legendBoxSize[1] - legendPadding[1]
                    ]

                    # set base pos
                    text.x = basePos[0] + colPos + symbolSize[0] + legendSymbolTextSpacing
                    text.y = basePos[1] - rowPos
                    symbol.x = basePos[0] + colPos
                    symbol.y = basePos[1] - text.height / 2 - symbolSize[1]/2 - rowPos

                    colPos += symbolSize[0] + text.width + legendSymbolTextSpacing + legendGridSpacing[0]
                
                rowPos += text.height + legendGridSpacing[1]

            # legend box
            # legendBoxSize = [10,30]
            if legendDrawBox:
                self.legendShapes.append(shapes.Rectangle(
                    legendPos[0]-legendSizeThickness,
                    legendPos[1]-legendSizeThickness,
                    legendBoxSize[0]+2*legendSizeThickness,
                    legendBoxSize[1]+2*legendSizeThickness, # JEG VED IKKE HVORFOR 30
                    batch=self.legendBoxShape,
                    color=self.markerColor # NOTE: STYLE
                ))

                self.legendShapes.append(shapes.Rectangle(
                    legendPos[0], 
                    legendPos[1], 
                    legendBoxSize[0],
                    legendBoxSize[1], # JEG VED IKKE HVORFOR 30
                    color=self.backgroundColor,
                    batch=self.legendBoxShape
                ))

            self.addPaddingCondition(bottom=legendBoxSize[1]+self.fontSize)


    def __setWindowDimensionBasedOnAxis__(self, firstAxis, secondAxis):
        
        p1, p2 = firstAxis.getEndPoints()
        p3, p4 = secondAxis.getEndPoints()
        
        minX = min(p1[0], p2[0], p3[0], p4[0])
        minY = min(p1[1], p2[1], p3[1], p4[1])
        maxX = max(p1[0], p2[0], p3[0], p4[0])
        maxY = max(p1[1], p2[1], p3[1], p4[1])

        if self.standardBasis and self.untrueAxis:
            xLength = max(abs(p2[0]-p1[0]), abs(p3[0]-p4[0]))
            yLength = max(abs(p2[1]-p1[1]), abs(p3[1]-p4[1]))
            self.scale = (self.width / xLength, self.height / yLength)
            
            self.offset = [minX*self.scale[0], minY*self.scale[1]]

            # move axis to untrue visual values
            # if firstaxis is vertical
            # move secondaxis
            if firstAxis.hasNull:
                secondAxis.finalize(self, vectorMultipliciation(firstAxis.get(0), self.scale))

            elif firstAxis.end < 0:
                secondAxis.finalize(self, vectorMultipliciation(firstAxis.get(firstAxis.end), self.scale))

            else:
                secondAxis.finalize(self)

            # move firstaxis
            if secondAxis.hasNull:
                firstAxis.finalize(self, vectorMultipliciation(secondAxis.get(0), self.scale))
            
            elif secondAxis.end < 0:
                firstAxis.finalize(self, vectorMultipliciation(secondAxis.get(secondAxis.end), self.scale))

            else:
                firstAxis.finalize(self)


        else: # use full scale

            xLength = abs(maxX - minX)
            yLength = abs(maxY - minY)
            self.scale = (self.width / xLength, self.height / yLength)
            self.offset = [minX*self.scale[0], minY*self.scale[1]]

            firstAxis.finalize(self)
            secondAxis.finalize(self)

        nullX, nullY = self.pixel(0,0)
        self.nullInPlot = insideBox(self.windowBox, (nullX, nullY))
        

    def __addMarkersToAxis__(self, axis): # move into axis method?
        
        maxMarkerLengthStr = min(max(len(str(axis.start)), len(str(axis.end))), 10)

        self.markers = []

        p1 = self.inversetranslate(*axis.lineStartPoint)
        p2 = self.inversetranslate(*axis.lineEndPoint)
        pixelLength = vlen(vdiff(axis.lineStartPoint, axis.lineEndPoint))
        length = vlen(vdiff(p1, p2))

        MARKERSTEPSIZE = self.markerStepSizeBand
        MARKERSTEP = [2, 5, 10]
        acceptence = [math.floor(pixelLength/MARKERSTEPSIZE[0]),math.floor(pixelLength/MARKERSTEPSIZE[1])]

        c = 0
        cameFromDirection = 0
        while True:

            step = MARKERSTEP[c%len(MARKERSTEP)] * 10**(c//len(MARKERSTEP))

            lengthOverStep = length / step

            direction = 0

            if lengthOverStep > acceptence[1]:
                direction = 1
            
            if lengthOverStep < acceptence[0]:
                direction = -1
            
            c += direction

            if cameFromDirection == direction*-1:
                break
            
            cameFromDirection = direction

            if direction != 0:
                continue

            break
        
        lengthOverStep = round(lengthOverStep)
        

        # is null in frame?
        # NOTE: FEJL her ved start på noget underligt, fx startPos = 0.7832
        nullX, nullY = self.pixel(0,0)
        if (self.padding[0] <= nullX <= self.width+self.padding[0]) and (self.padding[1] <= nullY <= self.height+self.padding[1]):

            distBeforeNull = vlen(vdiff((nullX, nullY), axis.lineStartPoint))
            distafterNull = vlen(vdiff((nullX, nullY), axis.lineEndPoint))

            procentBeforeNull = distBeforeNull/pixelLength
            procentAfterNull = distafterNull/pixelLength

            ticksBeforeNull = math.ceil(lengthOverStep*procentBeforeNull)
            ticksAfterNull = math.ceil(lengthOverStep*procentAfterNull)

            # NOTE: øhh der er et problem ved fx hjørnerne ikke bliver dækket hvis der er skrå akser
            if not self.standardBasis: 
                marker = Marker("0", 0, shell(axis), **self.markerOptions)
                marker.finalize(self)

            for i in range(1, ticksBeforeNull+1):
                marker = Marker(str(round(-step*i, maxMarkerLengthStr)), -step*i, shell(axis), **self.markerOptions)
                marker.finalize(self)
            
            for i in range(1, ticksAfterNull+1):
                marker = Marker(str(round(step*i, maxMarkerLengthStr)), step*i, shell(axis), **self.markerOptions)
                marker.finalize(self)

        else: # check for true axis support
            
            direction = (-1)**(0 < nullX)
            if direction == -1:
                startPos = axis.end
            else:
                startPos = axis.start

            startPos = startPos - startPos%step

            for i in range(math.floor(lengthOverStep)+2):
                p = direction*step*i + startPos
                marker = Marker(str(round(p,maxMarkerLengthStr)), p, shell(axis), **self.markerOptions)
                marker.finalize(self)

    
    def bake(self):
        # finish making plot
        # fit "plot" into window

        # options to be determined before Axis
        if sorted(self.windowAxis, key=lambda x: x==None)[-1] == None:
            horizontal = []
            vertical = []
            for i in self.objects:
                try:
                    horizontal.append(i.farLeft)
                    horizontal.append(i.farRight)
                    vertical.append(i.farTop)
                    vertical.append(i.farBottom)
                except AttributeError:
                    continue
            
            try:
                if not self.windowAxis[0]: self.windowAxis[0] = min(horizontal)
                if not self.windowAxis[1]: self.windowAxis[1] = max(horizontal)
                if not self.windowAxis[2]: self.windowAxis[2] = min(vertical)
                if not self.windowAxis[3]: self.windowAxis[3] = max(vertical)
            except:
                self.windowAxis = [-10, 10, -5, 5]
        
        if self.untrueAxis is None:
            
            # is null in x0, x1 and y0, y1?
            self.untrueAxis = False
            if self.standardBasis and (min(self.windowAxis[0], self.windowAxis[1]) < 0 or max(self.windowAxis[2], self.windowAxis[3]) > 0):
                self.untrueAxis = True

        else:
            self.untrueAxis = self.untrueAxis
        
        # legend
        self.__createLegendBox__()

        self.firstAxis = Axis(self.firstAxisVector, self.windowAxis[0], self.windowAxis[1], offset=self.untrueAxis)
        self.secondAxis = Axis(self.secondAxisVector, self.windowAxis[2], self.windowAxis[3], offset=self.untrueAxis)


        # computed options, padding needs to set before this point
        self.windowBox = (self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1])
        self.nullInPlot = False

        self.__setWindowDimensionBasedOnAxis__(self.firstAxis, self.secondAxis)
        self.__addMarkersToAxis__(self.firstAxis)
        self.__addMarkersToAxis__(self.secondAxis)

        if self.untrueAxis and not self.standardBasis:
            logging.warn('untrueAxis is on, but Axis+Axis is not a standard basis')

        # objects
        for obj in self.objects:
            obj.finalize(self)
            self.addDrawingFunction(obj)

        self.shapes = [i[0] for i in sorted(self.shapes, key=lambda x: x[1])]


    # translations
    def pos(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: abstract value
        """
        
        x -= self.firstAxis.offset
        y -= self.secondAxis.offset

        return (
            self.firstAxis.directionVector[0] * x + self.secondAxis.directionVector[0] * y,
            self.firstAxis.directionVector[1] * x + self.secondAxis.directionVector[1] * y
        )


    def translate(self, x:int, y:int) -> tuple:
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: translated value
        """

        return x*self.scale[0]-self.offset[0]+self.padding[0], y*self.scale[1]-self.offset[1]+self.padding[1]


    def pixel(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """

        x, y = self.pos(x, y)
        return self.translate(x,y)


    def inversepixel(self, x:int, y:int):
        """
        para: pixel values according to axis
        return abstract value
        """

        x, y = self.inversetranslate(x,y)
        
        x += self.firstAxis.offset
        y += self.secondAxis.offset

        v1 = self.firstAxis.directionVector
        v2 = self.secondAxis.directionVector

        #b = (-r__b*v__1a + r__a)/(v__1a*v__2b + v__1b*v__2a)
        b = (v1[0]*y - v2[0]*x)/(v1[0]*v2[1] - v1[1]*v2[0])

        #a = (-b*v__1b + r__a)/v__1a
        a = (-b*v1[1] + x)/v1[0]

        return a, b


    def line(self, pos, n):
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: two translated values on border of plot
        """
        
        return boxIntersectWithLine(self.windowBox, [n[0]*self.scale[0], n[1]*self.scale[1]], self.translate(*pos))

    
    def inside(self, x, y):
        """
        para: translated
        """
        return insideBox(self.windowBox, (x,y))


    def inversetranslate(self, x:int=None, y:int=None):
        """
        para: translated value
        return: x,y position according to basis (1,0), (0,1) in abstract space
        """

        p = [None, None]
        if not x is None: p[0] = (x+self.offset[0]-self.padding[0])/self.scale[0]
        if not y is None: p[1] = (y+self.offset[1]-self.padding[1])/self.scale[1]

        return p


    # shape
    def addDrawingFunction(self, shape, z=0):
        self.shapes.append((shape, z))


    # api
    def add(self, o):
        self.objects.append(o)

    
    def show(self, static:bool=True):

        if static:
            fname = '.__tempImage{}.png'.format(''.join([str(randint(0,9)) for i in range(10)]))
            self.save(fname)
            pilImage = Image.open(fname)
            pilImage.show()
            os.remove(fname)
            return

        self.style(
            windowWidth=800,
            windowHeight=600,
            padding=(30,0,30,30),
            backgroundColor=WHITE,
            markerColor=BLACK,
            markerLength=20,
            markerWidth=3,
            fontSize=10,
            font = "Times New Roman",
            gridLineColor=(200,200,200,255),
            gridLines = True,
            markerStepSizeBand=[200, 150],
            __overwrite__=False
        )


        self.bake()

        window = pg.window.Window(self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3])
        background = pg.shapes.Rectangle(0,0,self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3], color=self.backgroundColor)

        @window.event
        def on_draw():
            window.clear()
            background.draw()

            # glEnable(GL_BLEND)
            # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            for shape in self.shapes:
                shape.draw()

            self.legendBoxShape.draw()
            self.legendBatch.draw()

            # self.paddingBatch.draw()

        pg.app.run()


    def save(self, fname):
        
        self.style(
            windowWidth=2000,
            windowHeight=1500,
            padding=(100,100,100,100),
            backgroundColor=WHITE,
            markerColor=BLACK,
            markerLength=20,
            markerWidth=3,
            # fontSize=10,
            font = "Times New Roman",
            gridLineColor=(200,200,200,255),
            gridLines = True,
            # markerStepSizeBand=[200, 150],
            __overwrite__=False
        )

        self.bake()
        bar = tqdm.tqdm(total=len(self.shapes))

        winSize = self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3]
        background = shapes.Rectangle(0,0,winSize[0], winSize[1], color=self.backgroundColor)
        surface = Image.new('RGBA', winSize)

        background.draw(surface)

        for shape in self.shapes:
            shape.draw(surface)
            bar.update()

        self.legendBoxShape.draw(surface)
        self.legendBatch.draw(surface)

        surface.save(fname)
        bar.close()
        