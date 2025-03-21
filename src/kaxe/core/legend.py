
from .symbol import makeSymbolShapes, symbol
from .text import Text
from .shapes import shapes
from .styles import AttrObject, ComputedAttribute
import math
from types import MappingProxyType
from PIL import Image

debug = False

class LegendObject:
    def __init__(self, text, symbol, color):
        self.legendText = text
        self.legendSymbol = symbol
        self.legendColor = color


def getMaxwidth(map):
    return map.getAttr('width')*0.85

class LegendBox(AttrObject):

    name = "LegendBox"

    defaults = MappingProxyType({
        "topMargin": 50,
        "maxWidth": ComputedAttribute(getMaxwidth),
        "gaps": ComputedAttribute(lambda map: (map.getAttr('fontSize')/2, map.getAttr('fontSize')/2)),
        "symbolTextSpacing": ComputedAttribute(lambda map: int(map.getAttr('fontSize')/4))
    })

    def __init__(self, *obj):
        super().__init__()
        self.objects = obj
        self.batch = shapes.Batch()
        self.boxshape = shapes.Batch()
        self.others = []

    
    def add(self, text="", symbol=symbol.CIRCLE, color=(0,0,0,255)):
        self.others.append(LegendObject(text, symbol, color))


    def setObjects(self, objects:list) -> None:
        self.objects = objects


    def finalize(self, parent, sneaky=False): # maybe add as a seperate object
        """
        stadigvæk lidt skrøbelig

        if sneaky is True the method will not do anything to parent
        The function will also just return an image of the legendbox

        """
        self.setAttrMap(parent.attrmap)
        fontSize = self.getAttr('fontSize')

        self.legendShapes = []
        objects = []

        __shapes = []

        
        for obj in [*self.objects, *self.others]:
            if hasattr(obj, "legendText"): # has legend ready
                
                symbol = makeSymbolShapes(obj.legendSymbol, fontSize, obj.legendColor, self.batch)

                objects.append((
                    symbol, 
                    Text(obj.legendText,
                        x=0,
                        y=0,
                        color=self.getAttr('color'), 
                        batch=self.batch,
                        anchor_x="left",
                        anchor_y="top",
                        # font_name=self.font,
                        fontSize=fontSize
                        )
                    )
                )


        if len(objects) > 0:

            legendMaxWidth = self.getAttr('maxWidth')
            legendGridSpacing = self.getAttr('gaps')
            legendSymbolTextSpacing = self.getAttr('symbolTextSpacing')
            legendGap = self.getAttr('topMargin')

            # legendSizeThickness = 2 #NOTE: STYLE
            # legendPadding = (5, 5, 5, 5) # NOTE: STYLE, left bottom right top

            # Da symbol og tekst skal centeres omkring linjens center midterlinje skal den 
            # maksimale linje højde og bredde findes
            currentLineWidth = 0
            grid = [{"elements":[], "height":0}]
            
            for symbol, text in objects:
                
                # start med at få bredden
                symbolSize = symbol.getBoundingBox()
                width = symbolSize[0] + text.width + legendGridSpacing[0] + legendSymbolTextSpacing
                height = max(symbolSize[0], text.height)

                currentLineWidth += width
                # hvis bredden er for meget så gå en linje ned
                if currentLineWidth > legendMaxWidth:
                    grid.append({"elements":[], "height":0})
                    currentLineWidth = 0
                
                grid[-1]["elements"].append((symbol, text, width, height))
                grid[-1]["height"] = max(grid[-1]["height"], height)

            grid.reverse()

            # create legends
            currentLinePos = [0, 0]
            maxPos = [0, 0]
            minPos = [math.inf, math.inf]
            for row in grid:
                currentLinePos[0] = 0
                
                for symbol, text, width, height in row["elements"]:
                    symbolSize = symbol.getBoundingBox()

                    x = currentLinePos[0]
                    y = currentLinePos[1]

                    currentLinePos[0] += width
                    symbol.x = x
                    symbol.y = y + row["height"]/2 - symbolSize[1]/2
                    text.setLeftTopPos(
                        x + symbolSize[0] + legendSymbolTextSpacing, 
                        y + text.height/2 + row["height"]/2 #+ text.height + height/2 - text.height/2 #+ height/2 + text.height/2
                    )

                    if debug:
                        shapes.Rectangle(x, y, text.width + symbolSize[0] + legendSymbolTextSpacing, row["height"], batch=self.batch, color=(200,200,200,100))
                    
                    # find left top most
                    tx, ty = text.getLeftTopPos()
                    maxPos[0] = max(maxPos[0], tx + text.width, symbol.x + symbolSize[0])
                    maxPos[1] = max(maxPos[1], ty, symbol.y + symbolSize[1])

                    minPos[0] = min(minPos[0], tx, symbol.x)
                    minPos[1] = min(minPos[1], ty - text.height, symbol.y)

                currentLinePos[1] += row["height"] + legendGridSpacing[1]

            if debug: shapes.Circle(0,0, 10, batch=self.batch)

            height = (maxPos[1] - minPos[1])
            width = (maxPos[0] - minPos[0])
            
            ### skub den ned til window 0,0 (her burde title være med)
            # self.batch.push(-minPos[0], -minPos[1])
            ### skub dens egen højde ned
            # self.batch.push(0, -height)
            ### giv den noget mellemrum 
            # self.batch.push(0, -legendGap)
            ### centrer den horisontalt
            # self.batch.push(parent.getSize()[0]/2 - width/2, 0)

            # combine
            if not sneaky:
                self.batch.push(
                    -minPos[0] + parent.getSize()[0]/2 - width/2, 
                    -minPos[1] - height - legendGap
                )

            if not sneaky:
                parent.addDrawingFunction(self.boxshape)
                parent.addDrawingFunction(self.batch)
                
                # tilføj plads til legenden
                parent.addPaddingCondition(bottom=height+legendGap)

            else: # Only works with PILLOW
                surface = Image.new('RGBA', (int(width), int(height)), (0,0,0,0))

                self.boxshape.draw(surface)
                self.batch.draw(surface)
                return surface