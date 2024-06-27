
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
try:
    from IPython import display
except ImportError:
    pass

"""
Alle translationer fra pixel til inverse pixel skal ske i Plot og ikke i vinduet
Vinduet er bare til at lægge ting til og ved ikke hvor og hvodan den skal lægge ting til
Den hjælper lidt med legender og ensarte api til nye plots
Vinduet er altså det midterste af skærmen og holder også styr på padding og forskellige stil 
Det gør at bruger skal arbejde med de samme funktioner hver gang der arbejdes med et plot 
Ligeledes hvilkte plot der arbejdes på
"""

terminaltype = 'terminal'
try:
    ipy_str = str(type(get_ipython()))
    if 'zmqshell' in ipy_str:
        terminaltype = 'jupyter'
    if 'terminal' in ipy_str:
        terminaltype = 'ipython'
except:
    pass

class Window(AttrObject):
    
    name = "Window"

    def __init__(self): # |
        """
        left to right is always positive
        bottom to top is always positive
        """
        super().__init__()
        self.identity = None
        
        self.attrmap = AttrMap()
        self.attrmap.default(attr='width', value=2500)
        self.attrmap.default(attr='height', value=2000)
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
        
        self.padding = [0,0,0,0] #computed padding

        self.style = self.attrmap.styles
        self.help = self.attrmap.help

        self.legendbox = LegendBox()
        self.offset = [0,0]
        #self.scale = [1,1], if not set axis will help set it


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
    def include(self, cx, cy, width=0, height=0):
        """
        includes cx, cy in frame by adding padding
        """

        dx = min(cx - width/2 , 0)
        dy = min(cy - height/2, 0)
        
        dxm = min(self.width - (cx + width/2) + self.padding[0], 0)
        dym = min(self.height - (cy + height/2) + self.padding[1], 0)

        if dx < 0 or dy < 0 or dxm < -self.padding[2] or dym < -self.padding[3]:
            self.addPaddingCondition(left=-(dx), bottom=-(dy), right=-(dxm), top=-(dym))
            return -dx, -dy, -dxm, -dym
        
        return 0, 0, 0, 0

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

        self.windowBox = (self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1])

        for i in self.shapes:
            if type(i) is tuple: # list is still unsorted
                i[0].push(left, bottom)
                continue
            i.push(left, bottom)
        
        # for i in self.objects:
        #     i.push(left, bottom)

        self.setAttrMap(self.attrmap)


    # calculate windowAxis
    def __calculateWindowBorders__(self):
        """
        where all objects is in
        unless windowAxis is already specefied
        """
        if not hasattr(self, 'windowAxis'):
            return

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
                if self.windowAxis[0] is None: 
                    self.windowAxis[0] = min(horizontal)
            
            except Exception as e:
                self.windowAxis[0] = -10
            
            try:
                if self.windowAxis[1] is None: 
                    self.windowAxis[1] = max(horizontal)
            except Exception as e:
                self.windowAxis[1] = 10
            
            try:
                if self.windowAxis[2] is None: 
                    self.windowAxis[2] = min(vertical)
            except Exception as e:
                self.windowAxis[2] = -5
            
            try:
                if self.windowAxis[3] is None: 
                    self.windowAxis[3] = max(vertical)
            except Exception as e:
                self.windowAxis[3] = 5

    # baking
    def __bake__(self):
        # finish making plot
        # fit "plot" into window 
        startTime = time.time()        

        # get styles
        self.width = self.getAttr('width')
        self.height = self.getAttr('height')

        self.windowBox = (self.padding[0], self.padding[1], self.getAttr('width')+self.padding[0], self.getAttr('height')+self.padding[1])
        self.__calculateWindowBorders__()
        
        # get styles
        self.width = self.getAttr('width')
        self.height = self.getAttr('height')

        self.windowBox = (
            self.padding[0], 
            self.padding[1], 
            self.width+self.padding[0], 
            self.height+self.padding[1]
        )

        self.__prepare__()
        self.__addInnerContent__()
        self.__addOuterContent__()
        
        self.shapes = [i[0] for i in sorted(self.shapes, key=lambda x: x[1])]

        # add style padding
        self.addPaddingCondition(*self.getAttr('outerPadding'))

        logging.info('Compiled in {}s'.format(str(round(time.time() - startTime, 4))))


    def __addOuterContent__(self):
        
        # legend
        self.legendbox.setObjects(self.objects)
        self.legendbox.finalize(self)


    def __addInnerContent__(self):
        
        # finalizeing objects
        if terminaltype == "terminal": pbar = tqdm.tqdm(total=len(self.objects), desc='Baking')
        for obj in self.objects:
            obj.finalize(self)
            if terminaltype == "terminal": pbar.update()
            self.addDrawingFunction(obj)
        if terminaltype == "terminal":pbar.close()


    def __pillowPaint__(self, fname):
        startTime = time.time()
        if terminaltype == "terminal": pbar = tqdm.tqdm(total=len(self.shapes), desc='Decorating')

        winSize = self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3]
        background = shapes.Rectangle(0,0,winSize[0], winSize[1], color=self.getAttr('backgroundColor'))
        surface = Image.new('RGBA', winSize)

        background.draw(surface)

        for shape in self.shapes:
            shape.draw(surface)
            if terminaltype == "terminal": pbar.update()

        surface.save(fname)
        if terminaltype == "terminal": pbar.close()
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
    
    
    def show(self):
        fname = 'plot{}.png'.format(''.join([str(randint(0,9)) for i in range(10)]))

        if terminaltype != "terminal":
            self.save(fname)
            i = display.Image(filename=fname, width=800, unconfined=True)
            display.display(i)
            os.remove(fname)

        else:
            
            self.save(fname)
            pilImage = Image.open(fname)
            pilImage.show()
            os.remove(fname)

        return fname

    # shape
    def addDrawingFunction(self, shape, z=0):
        self.shapes.append((shape, z))


    # api
    def add(self, o):
        if self.identity in o.supports:
            self.objects.append(o)
        else:
            logging.error(f'{o}, is not supported in {self}')
    


    # defaults, may lead to problems
    def pointOnWindowBorderFromLine(self, pos, n): # -> former def line(...)
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: two translated values on border of plot
        """
        return boxIntersectWithLine(self.windowBox, [n[0]*self.scale[0], n[1]*self.scale[1]], self.translate(*pos))


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


    # translations
    def scaled(self, x, y):
        return self.scale[0]*x, self.scale[1]*y


    def translate(self, x:int, y:int) -> tuple:
        """
        para: x,y position according to basis (1,0), (0,1) in abstract space
        return: translated value
        """

        return (
            x * self.scale[0] - self.offset[0] + self.padding[0],
            y * self.scale[1] - self.offset[1] + self.padding[1]
        )

    
    def inversetranslate(self, x:int=None, y:int=None):
        """
        para: translated value
        return: x,y position according to basis (1,0), (0,1) in abstract space
        """

        p = [None, None]
        if not x is None: p[0] = (x+self.offset[0]-self.padding[0])/self.scale[0]
        if not y is None: p[1] = (y+self.offset[1]-self.padding[1])/self.scale[1]

        return p
