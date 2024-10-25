
# DONE:
# Crop firkanten så der ikke er så meget "dødt" plads rundt om
#       altså det ikke altid 3d området bruger hele området 
#       så meget af det kan bare fjernes
# Progressbar skal have titler
# .help() skal ikke printe forskellige farver (blå ved ændret)
# Objects (mappen) skal deles op i 3d og 2d
# forskellige farvemaps til forskellige funktioner
#       kunne være ret cool hvis man kunne vælge en grøn farveskala eller en rød farveskala
#       kan laves som en colormap class
#       måske tage en farve og så skrue op for den eller ned på en eller
#       anden måde fx ganget alle indgange med en skalar
# 
# Function skal laves som en samlet funktion
#       det samme med points
#       -> Her bare brug en "fordeler" funktion
# z-aksen titel skal altid være op ad
# Farver skal kunne vælges (som axis)
# axis.drawMarkersAtEnd burde kun være på dem der på enden og ikke 0.4 i intervallet [-0.5, 0.5]

# DONE: Men ikke testet
# Punkter skal sortes fra hvis de ligger udenfor

# Påbegyndt:
# shapes objekter skal have en include metode med vindue som argument så den kan tilføje sig selv
# Funktion skal "samles" hvis bunden kommer udenfor så trekanterne ikke er underligere

# TODO:
# Ryd op i koden og slet alt overflødigt
# Tal på aksen der går igennem (center) og pile
# Frame ligesom matplotlib med baggrund baggerst i firkanten
# kunne være fedt med en funktion der bare hedder plot() og så laver den selv enten
# et 2d eller 3d vindue med fx funktion eller punkter
# 
# Måske lidt mere gap imellem marker og akser


# window
from ..core.window import Window
from ..core.shapes import ImageShape
from ..core.axis import Axis
from ..core.marker import Marker

# 3d 
from ..core.d3.render import Render
from ..core.d3.objects.line import Line3D

# other
import math
import numpy as np
from PIL import Image

XYZPLOT = 'xyz'


class Plot3D(Window):
    
    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__()

        if window is None:
            window = [-10, 10, -10, 10, -10, 10]

        self.identity = XYZPLOT
        self.window = self.windowAxis = window
        self.axis = [None, None, None]
        self.__boxed__ = True
        self.__frame__ = False
        self.__normal__ = False

        self.firstAxisTitle = None
        self.secondAxisTitle = None
        self.thirdAxisTitle = None

        # styles
        self.attrmap.default('width', 1500)
        self.attrmap.default('height', 1500)
        self.attrmap.default('wireframeLinewidth', 2)
        self.attrmap.default('fontSize', 32)
        self.attrmap.setAttr('axis.drawAxis', False)
        self.attrmap.setAttr('axis.stepSizeBand', [125, 75])
        self.attrmap.setAttr('axis.drawMarkersAtEnd', False)
        self.attrmap.setAttr('marker.showLine', False)
        self.attrmap.setAttr('marker.tickWidth', 2)


        """
        window:tuple [x0, x1, y0, y1, z0, z1] axis
        """
        
        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)

        self.h = 1/2
        self.offset = np.array((-self.h,-self.h,-self.h))
        
        if rotation[0] < 0:
            rotation[0] = 360 + rotation[0]%360
        if rotation[1] < 0:
            rotation[1] = 360 + rotation[1]%360

        self.rotation = [rotation[0]%360, rotation[1]%360]


    def __createWireframe__(self):
        # bottom frame
        h = self.h
        self.p1 = np.array((-h, -h, -h))
        self.p2 = np.array((h, -h, -h))
        self.p3 = np.array((-h, h, -h))
        self.p4 = np.array((-h, -h, h))
        self.p5 = np.array((h, h, -h))
        self.p6 = np.array((h, -h, h))
        self.p7 = np.array((h, h, h))
        self.p8 = np.array((-h, h, h))

        lineWidth = self.getAttr('wireframeLinewidth')

        # x : 1, 9, 10, 12
        # y : 2, 5, 6, 11
        # z : 3, 4, 7, 8

        BLUE = (0,0,0,255)
        GREEN = (0,0,0,255)
        RED = (0,0,0,255)

        self.l1 = self.render.add3DObject(Line3D(self.p1, self.p2, width=lineWidth, color=BLUE)) #1 x
        self.l2 = self.render.add3DObject(Line3D(self.p2, self.p5, width=lineWidth, color=BLUE)) #2 y
        self.l3 = self.render.add3DObject(Line3D(self.p2, self.p6, width=lineWidth, color=BLUE)) #3 z    
        
        self.l9 = self.render.add3DObject(Line3D(self.p4, self.p6, width=lineWidth, color=GREEN)) #9 x
        self.l5 = self.render.add3DObject(Line3D(self.p6, self.p7, width=lineWidth, color=GREEN)) #5 y
        self.l4 = self.render.add3DObject(Line3D(self.p5, self.p7, width=lineWidth, color=GREEN)) #4 z
        
        self.l10 = self.render.add3DObject(Line3D(self.p7, self.p8, width=lineWidth, color=RED)) #10 x
        self.l6 = self.render.add3DObject(Line3D(self.p1, self.p3, width=lineWidth, color=RED)) #6 y
        self.l7 = self.render.add3DObject(Line3D(self.p3, self.p8, width=lineWidth, color=RED)) #7 z
        
        self.l12 = self.render.add3DObject(Line3D(self.p3, self.p5, width=lineWidth)) #12 x
        self.l11 = self.render.add3DObject(Line3D(self.p4, self.p8, width=lineWidth)) #11 y
        self.l8 = self.render.add3DObject(Line3D(self.p1, self.p4, width=lineWidth)) #8 z 

        self.lines = [
            [self.l1, self.l9, self.l10, self.l12],
            [self.l2, self.l6, self.l11, self.l5],
            [self.l3, self.l4, self.l7, self.l8]
        ]

        self.axisLines = [None, None, None]

        # beta is offset by -45
        self.titleOrientation = {
            (-45, 45): {
                (0, 45): [(self.l12, 1), (self.l2, -1), (self.l3, 1)],
                (45, 90): [(self.l1, -1), (self.l2, -1), (self.l4, -1)],
                (90, 135): [(self.l1, -1), (self.l2, -1), (self.l8, 1)],
                (135, 180): [(self.l1, -1), (self.l6, 1), (self.l3, -1)],
                (180, 225): [(self.l1, -1), (self.l6, 1), (self.l7, 1)],
                (225, 270): [(self.l12, 1), (self.l6, 1), (self.l4, 1)],
                (270, 315): [(self.l12, 1), (self.l6, 1), (self.l4, 1)],
                (315, 360): [(self.l12, 1), (self.l2, -1), (self.l7, -1)],
            },
            (45, 135): {
                (0, 45): [(self.l10, -1), (self.l5, -1), (self.l3, -1)],
                (45, 90): [(self.l9, -1), (self.l5, -1), (self.l4, 1)],
                (90, 135): [(self.l9, -1), (self.l5, -1), (self.l4, 1)],
                (135, 180): [(self.l9, -1), (self.l11, 1), (self.l3, 1)],
                (180, 225): [(self.l9, -1), (self.l11, 1), (self.l3, 1)],
                (225, 270): [(self.l10, -1), (self.l11, 1), (self.l8, 1)],
                (270, 315): [(self.l10, -1), (self.l11, 1), (self.l8, 1)],
                (315, 360): [(self.l10, -1), (self.l5, -1), (self.l7, 1)],
            },
            (135, 225): {
                (0, 45): [(self.l9, 1), (self.l11, -1), (self.l3, -1)],
                (45, 90): [(self.l10, 1), (self.l11, -1), (self.l8, -1)],
                (90, 135): [(self.l10, 1), (self.l11, -1), (self.l8, -1)],
                (135, 180): [(self.l10, 1), (self.l5, 1), (self.l7, -1)],
                (180, 225): [(self.l10, 1), (self.l5, 1), (self.l7, -1)],
                (225, 270): [(self.l9, 1), (self.l5, 1), (self.l4, -1)],
                (270, 315): [(self.l9, 1), (self.l5, 1), (self.l4, -1)],
                (315, 360): [(self.l9, 1), (self.l11, -1), (self.l3, -1)],
            },
            (225, 315): {
                (0, 45): [(self.l1, 1), (self.l6, -1), (self.l3, 1)],
                (45, 90): [(self.l12, -1), (self.l6, -1), (self.l8, 1)],
                (90, 135): [(self.l12, -1), (self.l6, -1), (self.l8, 1)],
                (135, 180): [(self.l12, -1), (self.l2, 1), (self.l7, 1)],
                (180, 225): [(self.l12, -1), (self.l2, 1), (self.l3, -1)],
                (225, 270): [(self.l1, 1), (self.l2, 1), (self.l4, 1)],
                (270, 315): [(self.l1, 1), (self.l2, 1), (self.l8, -1)],
                (315, 360): [(self.l1, 1), (self.l6, -1), (self.l3, 1)],
            }
        }



    def __createAxis__(self, line:Line3D, normal, i, addMarkers=True):
        
        # justere for at marker skubbes fra den forrige axis (ved include)
        offset = np.array((self.image.x, self.image.y))

        a, b = self.render.pixel(*line.p1) + offset, self.render.pixel(*line.p2) + offset
        v = b - a
        axis = Axis(v, (-v[1]*normal, v[0]*normal))
        axis.setPos(a, b)
        axis.addStartAndEnd(self.window[0+i*2], self.window[1+i*2])
        axis.finalize(self)
        if addMarkers:
            markers = axis.computeMarkersAutomatic(self)
            axis.addMarkersToAxis(markers, self)

        self.axisLines[i] = line
        self.axis[i] = axis
        
        # FRAME
        if self.__frame__ and self.__boxed__:
            for otherline in self.lines[i]:
                if otherline != line:
                    otherline.hide()

        # e = np.array([0,0,0])
        # e[i] = 1
        
        # adjust to perspective distance
        # ved stor nok w er det ikke nødvendigt        
        # markers centeres omkring 0! Ikke starten (altså mindste tal)!
        
        return axis


    def __scaleRender__(self):
        
        # start guess
        self.render.SCL = self.getAttr('width') * 10
        stepSize = 100

        lines = [
            self.l1, 
            self.l2, 
            self.l3,
            self.l4,
            self.l5,
            self.l6,
            self.l7,
            self.l8,
            self.l9,
            self.l10,
            self.l11,
            self.l12
        ]


        for _ in range(1000):
            self.render.SCL -= stepSize

            for line in lines:
                
                if not self.inside(*self.render.pixel(*line.p1)):
                    break
                
                if not self.inside(*self.render.pixel(*line.p2)):
                    break

            else:
                break
            

    def __before__(self):
        # assert self.__normal__ != self.__boxed__

        # finish making plot
        # fit "plot" into window

        # create render
        # add frame

        # print('alpha={}, beta={}'.format(*self.rotation))

        self.render = Render(
            width=self.getAttr('width'), 
            height=self.getAttr('height'),
            cameraAngle=[math.radians(self.rotation[0]), 
                         math.radians(self.rotation[1])]
        )
        
        self.__createWireframe__()
        self.__scaleRender__()
        
        # add color to wireframe
        lineBoxColor = self.getAttr('Axis.axisColor')
        if self.__boxed__:
            for i in self.lines:
                for line in i:
                    line.color = lineBoxColor
        else:
            for i in self.lines:
                for line in i:
                    line.hide()

        # set scale beforehand so axis dosent compute automatically

        # compute windowAxisLength
        self.windowAxisLength = [
            self.window[1] - self.window[0],
            self.window[3] - self.window[2],
            self.window[5] - self.window[4],
        ]


    def __after__(self):
        # add to window
        
        self.image = ImageShape(Image.new('RGBA', (self.width, self.height)), 0, 0)
        self.addDrawingFunction(self.image)

        # BOXED AND FRAMED
        if self.__boxed__:
            for beta0, beta1 in self.titleOrientation:

                # correcting offset
                beta = self.rotation[1]
                if beta > 315:
                    beta = beta - 360

                if beta0 <= beta < beta1:
                    
                    for alpha0, alpha1 in self.titleOrientation[(beta0, beta1)]:
                        
                        config = self.titleOrientation[(beta0, beta1)][(alpha0, alpha1)]
                        if alpha0 <= self.rotation[0] < alpha1:
                            axisx = self.__createAxis__(*config[0], 0)
                            axisy = self.__createAxis__(*config[1], 1)
                            axisz = self.__createAxis__(*config[2], 2)

                            axisx.checkCrossOvers(self, axisy)
                            axisx.checkCrossOvers(self, axisz)
                            axisy.checkCrossOvers(self, axisz)

                            break
            
                    break
        
        # AXIS IN THE MIDDLE
        if self.__normal__:
            # normal has no markers
            # kan måske få nogle arrows på et tidspunkt

            x = min(max(self.windowAxis[0], 0), self.windowAxis[1])
            y = min(max(self.windowAxis[2], 0), self.windowAxis[3])
            z = min(max(self.windowAxis[4], 0), self.windowAxis[5])

            line = Line3D(self.pixel(self.windowAxis[0], y, z), self.pixel(self.windowAxis[1], y, z))
            axisx = self.__createAxis__(line, 1, 0, False)
            self.render.add3DObject(line)

            line = Line3D(self.pixel(x, self.windowAxis[2], z), self.pixel(x, self.windowAxis[3], z))
            axisy = self.__createAxis__(line, 1, 1, False)
            axisy.markers = []
            self.render.add3DObject(line)

            line = Line3D(self.pixel(x, y, self.windowAxis[4]), self.pixel(x, y, self.windowAxis[5]))
            axisz = self.__createAxis__(line, 1, 2, False)
            axisz.markers = []
            self.render.add3DObject(line)

            axisx.checkCrossOvers(self, axisy)
            axisx.checkCrossOvers(self, axisz)
            axisy.checkCrossOvers(self, axisz)


        if self.firstAxisTitle:
            axisx.addTitle(self.firstAxisTitle, self)
        
        if self.secondAxisTitle:
            axisy.addTitle(self.secondAxisTitle, self)

        if self.thirdAxisTitle:
            axisz.addTitle(self.thirdAxisTitle, self)

        # er det bare at tage fx x aksens og så tage den højeste x værdi og så den mindste z værdi?
        # for line in [self.l1, self.l9, self.l10, self.l12]:
        #     print(self.l1.p1)

        self.image.img = self.render.render()
        bbox = self.image.img.getbbox()
        oldpadding = [i for i in self.padding]
        self.__setSize__(bbox[2] - bbox[0], bbox[3] - bbox[1])
        x, y = -bbox[0]-oldpadding[0], -(self.image.img.height-bbox[3])-oldpadding[1]
        self.pushAll(x,y)


    def title(self, firstAxis=None, secondAxis=None, thirdAxis=None):
        
        if firstAxis:
            self.firstAxisTitle = firstAxis
        
        if secondAxis:
            self.secondAxisTitle = secondAxis

        if thirdAxis:
            self.thirdAxisTitle = thirdAxis


    # legacy name
    # def translate(self, x:int, y:int, z:int) -> tuple:
    #     return pixel(x,y,z)
    
    def scaled3D(self, x:int, y:int, z:int) -> tuple:
        return np.array((
            (x - self.window[0]) / self.windowAxisLength[0],
            (y - self.window[2]) / self.windowAxisLength[1],
            (z - self.window[4]) / self.windowAxisLength[2]
        ))

    def pixel(self, x:int, y:int, z:int) -> tuple:
        return self.scaled3D(x,y,z) + self.offset

    
    def inside3D(self, x, y, z):
        return all([
            self.windowAxis[0] <= x <= self.windowAxis[1],
            self.windowAxis[2] <= y <= self.windowAxis[3],
            self.windowAxis[4] <= z <= self.windowAxis[5],
        ])

    # for safety (check if any leaks from old code)
    # method will NOT work in 3 dimensions
    # and should thereby NEVER be used
    def inversepixel(self, x:int, y:int):
        raise NotImplementedError


class PlotCenter3D(Plot3D):
    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__(window, rotation)
        self.__boxed__ = False
        self.__frame__ = False
        self.__normal__ = True


class PlotFrame3D(Plot3D):
    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__(window, rotation)
        self.__boxed__ = True
        self.__frame__ = True
        self.__normal__ = False


class PlotEmpty3D(Plot3D):
    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__(window, rotation)
        self.__boxed__ = False
        self.__frame__ = False
        self.__normal__ = False
