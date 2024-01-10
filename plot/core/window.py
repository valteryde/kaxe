
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

class Window(AttrObject):
    
    # defaults = MappingProxyType({
    #     "width": 2000,
    #     "height": 1500,
    #     "backgroundColor": (255,255,255,255),
    #     "outerPadding": [100, 100, 100, 100],
    #     "fontSize": 50,
    #     "color": (0,0,0,255)
    # })

    name = "Window"

    def __init__(self): # |
        """
        left to right is always positive
        bottom to top is always positive
        """
        super().__init__()
        self.identity = None
        
        self.attrmap = AttrMap()
        self.attrmap.default(attr='width', value=2000)
        self.attrmap.default(attr='height', value=1500)
        self.attrmap.default(attr='backgroundColor', value=(255,255,255,255))
        self.attrmap.default(attr='outerPadding', value=[50,50,50,50])
        self.attrmap.default(attr='fontSize', value=50)
        self.attrmap.default(attr='color', value=(0,0,0,255))
        self.setAttrMap(self.attrmap)

        self.attrmap.submit(LegendBox)

        # options
        self.shapes = []
        self.objects = []
        self.legendObjects = []
        self.legendBatch = shapes.Batch()
        self.legendBoxShape = shapes.Batch()
        
        self.offset = [0,0]
        self.padding = [0,0,0,0] #computed padding

        self.style = self.attrmap.styles


    def __eq__(self, s):
        if not self.identity: return False
        return self.identity == s


    def __ne__(self, s):
        if not self.identity: return True
        return self.identity != s


    # styles
    # """
    # padding: left, bottom, top, right
    # """


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

        self.setAttrMap(self.attrmap)


    # baking
    def __bake__(self):
        # finish making plot
        # fit "plot" into window 
        startTime = time.time()        

        self.windowBox = (self.padding[0], self.padding[1], self.getAttr('width')+self.padding[0], self.getAttr('height')+self.padding[1])
        self.__prepare__()
        self.__addInnerContent__()
        self.__addOuterContent__()
        
        self.shapes = [i[0] for i in sorted(self.shapes, key=lambda x: x[1])]

        # add style padding
        self.addPaddingCondition(*self.getAttr('outerPadding'))

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
        background = shapes.Rectangle(0,0,winSize[0], winSize[1], color=self.getAttr('backgroundColor'))
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
        if self.identity in o.supports:
            self.objects.append(o)
        else:
            logging.error(f'{o}, is not supported in {self}')