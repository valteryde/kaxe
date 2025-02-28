
from io import BytesIO
import time
from typing import Union
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
    from IPython import display # pyright: ignore[reportMissingModuleSource]
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
    ipy_str = str(type(get_ipython())) # pyright: ignore[reportUndefinedVariable]
    if 'zmqshell' in ipy_str:
        terminaltype = 'jupyter'
    if 'terminal' in ipy_str:
        terminaltype = 'ipython'
except:
    pass

class Window(AttrObject):
    """
    The main window class that handles the rendering and layout of graphical elements.
    
    It manages padding, styles, and the inclusion of various elements such as shapes and legends.
    The window can be rendered and saved as an image, and it supports 
    different terminal types including Jupyter and IPython.
    """

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

        self.style = self.attrmap.style # for backwards compatibility
        self.help = self.attrmap.help
        
        self.__included__ = []
        self.__bakedImage__ = False

        self.legendbox = LegendBox()
        self.offset = [0,0]
        self.showProgressBar = terminaltype == "terminal" 
        self.printDebugInfo = True
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
        Applies a theme to the window by updating its style attributes.

        Parameters
        ----------
        theme : dict
            A dictionary containing style attributes and their values.
        

        Examples
        --------
        >>> plt.theme(kaxe.Themes.A4Full)

        See also
        --------
        Kaxe.Plot.styles

        """
        
        self.style(**theme)

    
    def adjust(self, procentWidth, documentFontSize=0.25, documentMarginProcent=1.5, documentWidth=11.8, imageSlimRatio=1):
        """
        Adjust the following styles based on document size and document font size. i. e. match document font size with plot font size

        Directly changed styles; fontSize, width, height, outerPadding

        A lot of styles indirecitly relies on fontSize, width and height.
        
        Resources
        ---------
        https://paper-size.com/c/a-paper-sizes.html
        https://www.overleaf.com/learn/latex/Page_size_and_margins#Paper_size,_orientation_and_margins
        https://tex.stackexchange.com/questions/272607/what-is-the-name-of-latexs-default-style-and-why-was-it-chosen-for-latex
        https://tex.stackexchange.com/questions/155896/what-is-the-default-font-size-of-a-latex-document
        https://tex.stackexchange.com/questions/8260/what-are-the-various-units-ex-em-in-pt-bp-dd-pc-expressed-in-mm

        """

        # Same ratio
        # documentFontSize/documentWidth = fontSize/width
        # fontSize = documentFontSize/documentWidth*width

        width = 4000 * procentWidth
        height = width / (1 + procentWidth) * imageSlimRatio

        fontSize = documentFontSize/(procentWidth*(documentWidth-2*documentMarginProcent))*width
        
        self.style(width=int(width), height=int(height), fontSize=int(fontSize), outerPadding=(5,5,5,5))


    # paddings
    def includeElement(self, element):
        self.include(*element.getIncludeArguments())
        self.__included__.append(element)


    def include(self, cx, cy, width=0, height=0):
        """
        includes cx, cy in frame by adding padding
        """

        dx = min(cx - width/2 , 0)
        dy = min(cy - height/2, 0)
        
        dxm = min(self.width - (cx + width/2) + self.padding[0] + self.padding[2], 0)
        dym = min(self.height - (cy + height/2) + self.padding[1] + self.padding[3], 0)

        if dx < 0 or dy < 0 or dxm < 0 or dym < 0:
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

        self.windowBox = [self.padding[0], self.padding[1], self.width+self.padding[0], self.height+self.padding[1]]

        self.pushAll(left, bottom)
        
        # for i in self.objects:
        #     i.push(left, bottom)
        self.setAttrMap(self.attrmap)


    def pushAll(self, x, y):
        for i in self.shapes:
            if type(i) is tuple: # list is still unsorted
                i[0].push(x, y)
                continue
            i.push(x, y)


    # calculate windowAxis
    def __calculateWindowBorders__(self):
        """
        where all objects is in
        unless windowAxis is already specefied
        """
        
        if not hasattr(self, 'windowAxis'):
            return

        if len(self.windowAxis) != 4:
            [self.windowAxis.append(None) for _ in range(4 - len(self.windowAxis))]

        # har ingen effekt på 3D
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
                self.windowAxis[2] = -10
            
            try:
                if self.windowAxis[3] is None: 
                    self.windowAxis[3] = max(vertical)
            except Exception as e:
                self.windowAxis[3] = 10
        
        # if optimal is one dimensionel
        if self.windowAxis[0] == self.windowAxis[1]:
            self.windowAxis[0] -= 1
            self.windowAxis[1] += 1
        
        if self.windowAxis[2] == self.windowAxis[3]:
            self.windowAxis[2] -= 1
            self.windowAxis[3] += 1
        

    # before objects added to window
    def __before__(self):
        return self.__prepare__()

    
    # after objects added to window
    def __after__(self):
        pass

    
    def __setSize__(self, width, height):
        self.width = width
        self.height = height
        
        self.padding = (0,0,0,0)

        self.windowBox = [
            self.padding[0], 
            self.padding[1], 
            self.width+self.padding[0], 
            self.height+self.padding[1]
        ]

    
    def __pre__(self):
        pass


    def __includeAllAgain__(self):
        for element in self.__included__:
            self.include(*element.getIncludeArguments())

    # baking
    def __bake__(self):
        # finish making plot
        # fit "plot" into window 
        startTime = time.time()        

        self.__pre__()

        # get styles
        self.width = self.getAttr('width')
        self.height = self.getAttr('height')

        self.windowBox = [
            self.padding[0], 
            self.padding[1], 
            self.width+self.padding[0], 
            self.height+self.padding[1]
        ]
        self.__calculateWindowBorders__()

        self.__before__()
        self.__addInnerContent__()
        self.__after__()
        self.__addOuterContent__()

        # include all elements
        self.__includeAllAgain__()
        

        self.shapes = [i[0] for i in sorted(self.shapes, key=lambda x: x[1])]

        # add style padding
        self.addPaddingCondition(*self.getAttr('outerPadding'))

        if self.printDebugInfo:
            logging.info('Compiled in {}s'.format(str(round(time.time() - startTime, 4))))
        self.__baked__ = True


    def __addOuterContent__(self):
        
        # legend
        self.legendbox.setObjects(self.objects)
        self.legendbox.finalize(self)


    # enables this code to be manipulated with in other subclasses
    def __callFinalizeObject__(self, obj):
        obj.finalize(self)

    def __addInnerContent__(self):
        
        # finalizeing objects
        if self.showProgressBar: pbar = tqdm.tqdm(total=len(self.objects), desc='Baking')
        for obj in self.objects:
            self.__callFinalizeObject__(obj)
            if self.showProgressBar: pbar.update()
            self.addDrawingFunction(obj)
        if self.showProgressBar:pbar.close()


    def __pillowPaint__(self, fname):
        startTime = time.time()
        if self.showProgressBar: pbar = tqdm.tqdm(total=len(self.shapes), desc='Decorating')

        winSize = self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3]
        background = shapes.Rectangle(0, 0, winSize[0], winSize[1], color=self.getAttr('backgroundColor'))
        surface = Image.new('RGBA', winSize)

        background.draw(surface)

        for shape in self.shapes:
            
            shape.draw(surface)
            
            if self.showProgressBar: pbar.update()

        if fname is str:
            surface.save(fname)
        else:
            surface.save(fname, format="png")

        if self.showProgressBar: pbar.close()
        if self.printDebugInfo: logging.info('Painted in {}s'.format(str(round(time.time() - startTime, 4))))
        
        return surface


    def __paint__(self, *args, **kwargs):
        
        if True: # self.engine == 'PILLOW':
            return self.__pillowPaint__(*args, **kwargs)


    # save and show    
    def save(self, fname:Union[str, BytesIO]):
        """
        Save the current window image to a file.
        
        If a cached image is available, it will be used to save the file.
        Otherwise, the image will be generated and then saved.
        
        Parameters
        ----------
        fname : str | BytesIO
            The filename where the image will be saved or a BytesIO object to save the image in memory.
        
        Examples
        --------
        >>> plt.save( path/where/image/saved.png )

        """
        

        if self.__bakedImage__:
            logging.log(0, 'Using cached plot window')
            self.__bakedImage__.save(fname)
            return

        totStartTime = time.time()

        self.__bake__()
        self.__bakedImage__ = self.__paint__(fname)
        
        if self.printDebugInfo:
            logging.info('Total time to save {}s'.format(str(round(time.time() - totStartTime, 4))))
    
    
    def show(self):
        """
        Show the current image using `Pillow.Image.Show`
        
        If a cached image is available, it will be used to save the file.
        Otherwise, the image will be generated and then saved.

        Examples
        --------
        >>> plt.show( )
        """

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
    # for at kunne overskrive den nederste funktion indføres denne
    def addDrawingFunction(self, shape, z=0):
        self.shapes.append((shape, z))

    # api
    def add(self, obj):
        """
        Adds object to plotting window

        Paramaters
        ----------
        obj
            Object to be added to the plot

        Examples
        --------
        >>> plt.add(kaxe.Function( ... ))
        >>> plt.add(kaxe.Points( ... ))
        """

        if self.identity in obj.supports:
            self.objects.append(obj)
        else:
            logging.error(f'{obj}, is not supported in {self}')
        
        return obj


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


    def getSize(self):
        return self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3]