
from .symbol import makeSymbolShapes
from .text import Text
from .shapes import shapes

class LegendBox:

    def __init__(self, *obj):
        self.objects = obj
        self.batch = shapes.Batch()
        self.boxshape = shapes.Batch()

    
    def finalize(self, parent): # maybe add as a seperate object
        """
        stadigvæk lidt skrøbelig
        """

        self.legendShapes = []
        objects = []
        
        for obj in self.objects:
            if hasattr(obj, "legendText"): # has legend ready

                symbol = makeSymbolShapes(obj.legendSymbol, parent.fontSize, obj.legendColor, self.batch)

                objects.append((
                    symbol, 
                    Text(obj.legendText,
                        x=0,
                        y=0,
                        color=parent.markerColor, 
                        batch=self.batch,
                        anchor_x="left",
                        anchor_y="top",
                        # font_name=self.font,
                        fontSize=parent.fontSize
                        )
                    )
                )


        if len(objects) > 0:
            
            # calculate grid sizes
            legendMaxWidth = parent.width * .7 # NOTE: STYLE
            legendSizeThickness = 2 #NOTE: STYLE
            legendGridSpacing = (int(parent.fontSize/2), int(parent.fontSize/2)+2) # NOTE: STYLE
            legendPadding = (5, 5, 5, 5) # NOTE: STYLE, left bottom right top
            legendSymbolTextSpacing = int(parent.fontSize/4) # NOTE: STYLE
            legendDrawBox = False

            # legendGridSpacing = (0, 0) # NOTE: STYLE
            # legendPadding = (0, 0, 0, 0) # NOTE: STYLE, left bottom right top

            grid = [[]]
            rowWidth = 0
            maxGridWidth = 0
            sumTextHeight = 0
            rowTextHeight = 0
            for symbol, text in objects:
                
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
            
            legendPos = [parent.width/2 + parent.padding[0] - legendBoxSize[0]/2, 0]

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
                    batch=self.boxshape,
                    color=parent.markerColor # NOTE: STYLE
                ))

                self.legendShapes.append(shapes.Rectangle(
                    legendPos[0], 
                    legendPos[1], 
                    legendBoxSize[0],
                    legendBoxSize[1], # JEG VED IKKE HVORFOR 30
                    color=parent.backgroundColor,
                    batch=self.boxshape
                ))

            parent.addPaddingCondition(bottom=legendBoxSize[1]+parent.fontSize)
            parent.addDrawingFunction(self.boxshape)
            parent.addDrawingFunction(self.batch)
