
import time
from .helper import *
import logging
from .styles import *
from .legend import LegendBox
from .shapes import shapes
from PIL import Image
import tqdm
from random import randint
import os

"""
Alle translationer fra pixel til inverse pixel skal ske i Plot og ikke i vinduet
Vinduet er bare til at lægge ting til og ved ikke hvor og hvodan den skal lægge ting til
Den hjælper lidt med legender og ensarte api til nye plots
Vinduet er altså det midterste af skærmen og holder også styr på padding og forskellige stil 
Det gør at bruger skal arbejde med de samme funktioner hver gang der arbejdes med et plot 
Ligeledes hvilkte plot der arbejdes på
"""

class Window:
    def __init__(self): # |
        """
        left to right is always positive
        bottom to top is always positive
        """
        self.identity = None
        
        # options
        self.shapes = []
        self.objects = []
        self.legendObjects = []
        self.legendBatch = shapes.Batch()
        self.legendBoxShape = shapes.Batch()
        
        self.offset = [0,0]
        self.padding = [0,0,0,0] #computed padding

        # styles
        self.width = None
        self.height = None
        self.backgroundColor = None
        self.markerColor = None
        self.markerWidth = None
        self.markerLength = None
        self.font = None
        self.gridLines = None
        self.gridLineColor = None
        self.fontSize = None
        self.markerStepSizeBand = None
        self.outerPadding = None

    
    def __eq__(self, s):
        if not self.identity: return False
        return self.identity == s

    def __ne__(self, s):
        if not self.identity: return True
        return self.identity != s


    # styles        
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
            if not padding is None and self.outerPadding is None: self.outerPadding = list(padding)
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
            if not padding is None: self.outerPadding = list(padding)
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


    def theme(self, theme):
        """
        use a defined theme
        
        calls self.style
        """
        self.style(**theme)


    # paddings
    def include(self, cx, cy, width, height):
        """includes cx, cy in frame by adding padding"""
        dx = min(cx - width/2, 0)
        dy = min(cy - height/2, 0)
        dxm = min(self.width - (cx + width/2), 0)
        dym = min(self.height - (cy + height/2), 0)

        if dx < 0 or dy < 0 or dxm < 0 or dym < 0:
            self.addPaddingCondition(left=-(dx), bottom=-(dy), right=-(dxm), top=-(dym))


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

        self.windowBox = (self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1])

        for i in self.shapes:
            if type(i) is tuple: # list is still unsorted
                i[0].push(left, bottom)
                continue
            i.push(left, bottom)
        
        # for i in self.objects:
        #     i.push(left, bottom)


    # if point is inside window
    def inside(self, x, y):
        """
        para: translated
        (pixels)
        """
        return insideBox(self.windowBox, (x,y))

    
    def clamp(self, x:int=0, y:int=0):
        """
        clamps value to window max and min
        para: pixels
        """
        return (
            min(max(self.windowBox[0], x), self.windowBox[2]),
            min(max(self.windowBox[1], y), self.windowBox[3])
        )


    # baking
    def __bake__(self):
        # finish making plot
        # fit "plot" into window 
        startTime = time.time()        

        self.__prepare__()
        self.__addInnerContent__()
        self.__addOuterContent__()
        
        self.shapes = [i[0] for i in sorted(self.shapes, key=lambda x: x[1])]

        # add style padding
        self.addPaddingCondition(*self.outerPadding)

        logging.info('Compiled in {}s'.format(str(round(time.time() - startTime, 4))))


    def __addOuterContent__(self):
        
        # legend
        self.legendbox = LegendBox(*self.objects)
        self.legendbox.finalize(self)


    def __addInnerContent__(self):
        
        # finalizeing objects
        pbar = tqdm.tqdm(total=len(self.objects), desc='Baking')
        for obj in self.objects:
            obj.finalize(self)
            pbar.update()
            self.addDrawingFunction(obj)
        pbar.close()


    def __pillowPaint__(self, fname):
        startTime = time.time()
        pbar = tqdm.tqdm(total=len(self.shapes), desc='Decorating')

        winSize = self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3]
        background = shapes.Rectangle(0,0,winSize[0], winSize[1], color=self.backgroundColor)
        surface = Image.new('RGBA', winSize)

        background.draw(surface)

        for shape in self.shapes:
            shape.draw(surface)
            pbar.update()

        surface.save(fname)
        pbar.close()
        logging.info('Painted in {}s'.format(str(round(time.time() - startTime, 4))))


    def __paint__(self, *args, **kwargs):
        
        if True: # self.engine == 'PILLOW':
            self.__pillowPaint__(*args, **kwargs)


    # save and show    
    def save(self, fname):
        
        totStartTime = time.time()

        self.style(
            windowWidth=2000,
            windowHeight=1500,
            # padding=(100,100,100,100),
            padding=(20,20,20,20),
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

        self.__bake__()
        self.__paint__(fname)
        
        logging.info('Total time to save {}s'.format(str(round(time.time() - totStartTime, 4))))
    
    
    def show(self, static:bool=True):

        if static:
            fname = '.__tempImage{}.png'.format(''.join([str(randint(0,9)) for i in range(10)]))
            self.save(fname)
            pilImage = Image.open(fname)
            pilImage.show()
            os.remove(fname)
            return

    # shape
    def addDrawingFunction(self, shape, z=0):
        self.shapes.append((shape, z))


    # api
    def add(self, o):
        self.objects.append(o)
