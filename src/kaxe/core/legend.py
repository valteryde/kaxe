
from .symbol import makeSymbolShapes, symbol
from .text import Text
from .shapes import shapes
from .styles import AttrObject, ComputedAttribute
from .svg import SvgDocument
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


    def finalize(self, parent, sneaky=False, vector=False): # maybe add as a seperate object
        """
        stadigvæk lidt skrøbelig

        if sneaky is True the method will not do anything to parent
        The function will also just return an image of the legendbox (or SvgDocument when vector=True)

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
                height = max(symbolSize[1], text.height)

                if currentLineWidth > 0 and currentLineWidth + width > legendMaxWidth:
                    grid.append({"elements":[], "height":0})
                    currentLineWidth = 0

                currentLineWidth += width
                grid[-1]["elements"].append((symbol, text, width, height))
                grid[-1]["height"] = max(grid[-1]["height"], height)

            grid = [row for row in grid if row["elements"]]
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
                    row_mid = y + row["height"] / 2
                    if isinstance(symbol, shapes.Circle):
                        symbol.x = x + symbolSize[0] / 2
                        symbol.centerAlign()
                        symbol.y = row_mid
                        sym_min_x = x
                        sym_max_x = x + symbolSize[0]
                        sym_min_y = symbol.y - symbolSize[1] / 2
                        sym_max_y = symbol.y + symbolSize[1] / 2
                    else:
                        symbol.x = x
                        symbol.y = row_mid - symbolSize[1] / 2
                        sym_min_x = symbol.x
                        sym_max_x = symbol.x + symbolSize[0]
                        sym_min_y = symbol.y
                        sym_max_y = symbol.y + symbolSize[1]
                    text.setLeftTopPos(
                        x + symbolSize[0] + legendSymbolTextSpacing,
                        y + row["height"] / 2 + text.height / 2,
                    )

                    if debug:
                        shapes.Rectangle(x, y, text.width + symbolSize[0] + legendSymbolTextSpacing, row["height"], batch=self.batch, color=(200,200,200,100))
                    
                    # find left top most
                    tx, ty = text.getLeftTopPos()
                    maxPos[0] = max(maxPos[0], tx + text.width, sym_max_x)
                    maxPos[1] = max(maxPos[1], ty, sym_max_y)

                    minPos[0] = min(minPos[0], tx, sym_min_x)
                    minPos[1] = min(minPos[1], ty - text.height, sym_min_y)

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

            else:
                self.batch.push(-minPos[0], -minPos[1])
                self.boxshape.push(-minPos[0], -minPos[1])
                if vector:
                    doc = SvgDocument((int(width), int(height)))
                    self.boxshape.draw(doc)
                    self.batch.draw(doc)
                    return doc
                surface = Image.new('RGBA', (int(width), int(height)), (0,0,0,0))
                self.boxshape.draw(surface)
                self.batch.draw(surface)
                return surface

    def finalize_svg_sneaky(self, parent):
        """Return an SvgDocument sized to the legend for grid SVG export."""
        return self.finalize(parent, sneaky=True, vector=True)