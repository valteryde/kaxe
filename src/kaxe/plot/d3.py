
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
from random import randint
from ..core.helper import insideBox
from ..core.window import Window
from ..core.shapes import ImageShape
from ..core.axis import Axis
from ..core.marker import Marker

# 3d 
from ..core.d3.render import Render
from ..core.d3.objects.line import Line3D
from ..core.d3.objects.point import Point3D
from ..core.d3.objects.triangle import Triangle

# other
import math
import numpy as np
from PIL import Image

XYZPLOT = 'xyz'


class Plot3D(Window):
    """
    A plotting window used to represent a boxed 3D Plot
        
    Attributes
    ----------
    firstAxis : Kaxe.Axis
        The first axis of the plot.
    secondAxis : Kaxe.Axis
        The second axis of the plot.
    thirdAxis : Kaxe.Axis
        The third axis of the plot.

    Parameters
    ----------
    window : list, optional
        The window dimensions for the plot in the format [x0, x1, y0, y1, z0, z1] (default is [-10, 10, -10, 10, -10, 10]).
    rotation : list, optional
        The rotation angles for the plot in degrees [alpha, beta] (default is [0, -20]).
    
    """
    
    

    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__()

        """
        
           +--------------+
          /|             /|
         / |            / |
        *--+-----------*  |
        |  |           |  |
        |  |           |  |
        |  |           |  |
        |  +-----------+--+
        | /            | /
        |/             |/
        *--------------*

        """

        # rotation = [-272, 103]
        rotation = [60, 60] # den vender forkert lige pt
        rotation = [randint(-360, 360), randint(-360, 360)]

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

        self.attrmap.default(attr='xNumbers', value=None)
        self.attrmap.default(attr='yNumbers', value=None)
        self.attrmap.default(attr='zNumbers', value=5)

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

        self.isRotatedPastZValue = self.rotation[1] > 180


    def __createAxisBoxLine__(self, p1, p2, axisType, color=(0,0,0,255)):
        lineWidth = self.getAttr('wireframeLinewidth')
        
        line = Line3D(p1, p2, width=lineWidth, color=color)
        line.__axisType = axisType # x, y or z
        return self.render.add3DObject(line)


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

        # x : 1, 9, 10, 12
        # y : 2, 5, 6, 11
        # z : 3, 4, 7, 8
    
        # debugging tools
        BLUE = (0,0,0,255)
        GREEN = (0,0,0,255)
        RED = (0,0,0,255)

        self.l1 = self.__createAxisBoxLine__(self.p1, self.p2, 'x', color=BLUE) #1 x
        self.l2 = self.__createAxisBoxLine__(self.p2, self.p5, 'y', color=BLUE) #2 y
        self.l3 = self.__createAxisBoxLine__(self.p2, self.p6, 'z', color=BLUE) #3 z    

        self.l9 = self.__createAxisBoxLine__(self.p4, self.p6, 'x', color=GREEN) #9 x
        self.l5 = self.__createAxisBoxLine__(self.p6, self.p7, 'y', color=GREEN) #5 y
        self.l4 = self.__createAxisBoxLine__(self.p5, self.p7, 'z', color=GREEN) #4 z
        
        self.l10 = self.__createAxisBoxLine__(self.p7, self.p8, 'x', color=RED) #10 x
        self.l6 = self.__createAxisBoxLine__(self.p1, self.p3, 'y', color=RED) #6 y
        self.l7 = self.__createAxisBoxLine__(self.p3, self.p8, 'z', color=RED) #7 z
        
        self.l12 = self.__createAxisBoxLine__(self.p3, self.p5, 'x') #12 x
        self.l11 = self.__createAxisBoxLine__(self.p4, self.p8, 'y') #11 y
        self.l8 = self.__createAxisBoxLine__(self.p1, self.p4, 'z') #8 z 

        self.lines = [
            [self.l1, self.l9, self.l10, self.l12],
            [self.l2, self.l6, self.l11, self.l5],
            [self.l3, self.l4, self.l7, self.l8]
        ]

        self.axisLines = [None, None, None]

        # p1=rød
        # p2=grøn
        # p3=blå
        # p4=gul
        # p5=lilla
        # p6=mørkegrøn
        # p7=lyseblå
        # p8=grå

        self.faceNormals = [
            # points and connection vectors
            (self.p1, self.p2, self.p3, self.p5, self.p3 - self.p1, self.p2 - self.p1), # p1, p2, p3
            (self.p1, self.p2, self.p4, self.p6, self.p2 - self.p1, self.p4 - self.p1), # p1, p2, p4
            (self.p1, self.p3, self.p4, self.p8, self.p4 - self.p1, self.p3 - self.p1), # p1, p3, p4
            (self.p4, self.p8, self.p6, self.p7, self.p6 - self.p4, self.p8 - self.p4), # p4, p8, p6
            (self.p2, self.p5, self.p6, self.p7, self.p5 - self.p2, self.p6 - self.p2), # p2, p5, p6
            (self.p5, self.p3, self.p7, self.p8, self.p5 - self.p3, self.p5 - self.p7), # p5, p3, p7
        ]

        self.faceNormalLines = [
            (self.l1, self.l2, self.l12, self.l6), #rød, grøn, blå
            (self.l8, self.l9, self.l3, self.l1), #rød, grøn, gul
            (self.l6, self.l7, self.l11, self.l8), # rød, blå, gul
            (self.l11, self.l10, self.l5, self.l9), # gul, grå, mørkegrøn
            (self.l3, self.l5, self.l4, self.l2), # grøn, lilla, mørkegrøn
            (self.l12, self.l7, self.l10, self.l4), # lilla, blå, lyseblå
        ]

    def __createAxis__(self, line:Line3D, i, addMarkers=True):
        
        # justere for at marker skubbes fra den forrige axis (ved include)
        offset = np.array((self.image.x, self.image.y))

        center = self.render.pixel(0,0,0) + offset
        a, b = self.render.pixel(*line.p1) + offset, self.render.pixel(*line.p2) + offset
        v = b - a
        
        vc = center - (a + b) / 2
        vc = [-vc[1], vc[0]]

        isNormal = np.dot(v, vc)
        normal = -1
        if isNormal > 0:
            normal = 1
        
        axis = Axis(v, (-v[1]*normal, v[0]*normal), ["xNumbers", "yNumbers", "zNumbers"][i])
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

        self.__drawDebug__()


    def __drawDebug__(self):
        """
        DEBUG:
        Add face normals
        Draw points
        """

        radius = 20
        self.render.add3DObject(Point3D(*self.p1, radius, color=(255,0,0,255))) # p1=rød
        self.render.add3DObject(Point3D(*self.p2, radius, color=(0,255,0,255))) # p2=grøn
        self.render.add3DObject(Point3D(*self.p3, radius, color=(0,0,255,255))) # p3=blå
        self.render.add3DObject(Point3D(*self.p4, radius, color=(255,255,0,255))) # p4=gul
        self.render.add3DObject(Point3D(*self.p5, radius, color=(255,0,255,255))) # p5=lilla
        self.render.add3DObject(Point3D(*self.p6, radius, color=(41,112,10,255))) # p6=mørkegrøn
        self.render.add3DObject(Point3D(*self.p7, radius, color=(0,255,255,255))) # p7=lyseblå
        self.render.add3DObject(Point3D(*self.p8, radius, color=(100,100,100,255))) # p8=grå


        # add center triangle
        a = 4
        p1 = (0, self.h/a, 0)
        p2 = (-self.h/a, -self.h/a, 0)
        p3 = (self.h/a, -self.h/a, 0)
        p4 = (0, 0, self.h/a)
        self.render.add3DObject(Triangle(p1, p2, p4, color=(255,0,0,255)))
        self.render.add3DObject(Triangle(p1, p3, p4, color=(0,255,0,255)))
        self.render.add3DObject(Triangle(p1, p2, p3, color=(0,0,255,255)))
        self.render.add3DObject(Triangle(p2, p4, p3, color=(0,0,0,255)))


        # world view camera (y er op?)
        getFaceCenter = lambda p1, p2, p3: p1 + (p2 - p1)/2 + (p3 - p1)/2

        colors = [
            (255,0,0,255),
            (0,255,0,255),
            (0,0,255,255),
            (0,255,255,255),
            (255,0,255,255),
            (255,255,0,255),
        ]


        for i, (p1, p2, p3, p4, v1, v2) in enumerate(self.faceNormals):

            self.render.add3DObject(Triangle(p1, p2, p3, color=colors[i]))
            self.render.add3DObject(Triangle(p4, p2, p3, color=colors[i]))

            n = np.cross(v1, v2)

            pos = getFaceCenter(p1, p2, p3)

            self.render.add3DObject(Line3D(
                p1=pos,
                p2=pos + n/4,
                color=(255,0,0,255)
            ))
            color = (255,0,0,255)
            
            n = np.array([n[0], n[1], -n[2]])

            x,y,z = self.render.camera.R @ n
            if y < 0:
                color = (0,255,0,255)
            
            self.render.add3DObject(Point3D(
                *pos,
                10,
                color=color
            ))


    def __drawBackground__(self, i, xyz):
        # add background

        backgroundColor = (250, 250, 250, 255)
        # backgroundColor = (200, 250, 250, 255)

        p1, p2, p3, p4, v1, v2 = self.faceNormals[i]
        
        n = np.cross(v1, v2)
        smallzOffset = (n/np.linalg.norm(n))/500
        smallzOffset *= 1

        # self.render.add3DObject(Triangle(p1+smallzOffset, p2+smallzOffset, p3+smallzOffset, color=backgroundColor))
        # self.render.add3DObject(Triangle(p4+smallzOffset, p2+smallzOffset, p3+smallzOffset, color=backgroundColor))
                
        # find den koordinat som de alle sammen har altså holdes konstant igennem fladen
        for i in range(3): # 3 koordinater
            if p1[i] == p2[i] == p3[i] == p4[i]:
                        
                if p1[i] < 0:
                    xyz[i] = self.windowAxis[i*2]
                else:
                    xyz[i] = self.windowAxis[i*2+1]


    def __drawGridLines__(self, axisx:Axis, axisy:Axis, axisz:Axis, xyz):
        axisLineColor = (200,200,200,255)

        for i in axisx.markers:
            self.render.add3DObject(Line3D(self.pixel(i.x, self.windowAxis[2], xyz[2]), self.pixel(i.x, self.windowAxis[3], xyz[2]), color=axisLineColor))
            self.render.add3DObject(Line3D(self.pixel(i.x, xyz[1], self.windowAxis[4]), self.pixel(i.x, xyz[1], self.windowAxis[5]), color=axisLineColor))
            
        for i in axisy.markers:
            self.render.add3DObject(Line3D(self.pixel(self.windowAxis[0], i.x, xyz[2]), self.pixel(self.windowAxis[1], i.x, xyz[2]), color=axisLineColor))
            self.render.add3DObject(Line3D(self.pixel(xyz[0], i.x, self.windowAxis[4]), self.pixel(xyz[0], i.x, self.windowAxis[5]), color=axisLineColor))
            
        for i in axisz.markers:
            self.render.add3DObject(Line3D(self.pixel(self.windowAxis[0], xyz[1], i.x), self.pixel(self.windowAxis[1], xyz[1], i.x), color=axisLineColor))
            self.render.add3DObject(Line3D(self.pixel(xyz[0], self.windowAxis[2], i.x), self.pixel(xyz[0], self.windowAxis[3], i.x), color=axisLineColor))


    def __after__(self):
        # add to window
        
        self.image = ImageShape(Image.new('RGBA', (self.width, self.height)), 0, 0)
        self.addDrawingFunction(self.image)

        # BOXED AND FRAMED
        if self.__boxed__:
            
            #### Add axis to correct line 
            # Calculate faces facing camera and bottom <-h, h, -h>
            faces = []

            xyz = {}
            
            closestAxis = [
                (math.inf, None), 
                (math.inf, None), 
                (math.inf, None)
            ]

            for i, lines in enumerate(self.lines):
                
                for possibleAxis in lines:
                    p1 = possibleAxis.p1
                    p2 = possibleAxis.p2
                    p3 = (possibleAxis.p1 + possibleAxis.p2) / 2

                    camera = np.array([0, 0, 100])
                    p1 = self.render.camera.R @ p1 - camera
                    p2 = self.render.camera.R @ p2 - camera
                    p3 = self.render.camera.R @ p3 - camera

                    dist = min(np.linalg.norm(p1), np.linalg.norm(p2), np.linalg.norm(p3))

                    if dist < closestAxis[i][0]:
                        closestAxis[i] = (dist, possibleAxis)

            print(closestAxis)

            for i, (p1, p2, p3, p4, v1, v2) in enumerate(self.faceNormals):

                ### nyt 


                ####


                n = np.cross(v1, v2)
                x,y,z = self.render.camera.R @ n

                if y > 0:
                    faces.append(i)
                
                n = np.array([n[0], n[1], -n[2]])
                x,y,z = self.render.camera.R @ n

                if y < 0: continue


                self.__drawBackground__(i, xyz)


            # find shared lines between two faces
            sharedLines = set()

            # faceNormalLines = [ (line1, line2, line3), (line2, line3, line7), ... ]
            # faces = [1, 2, 5]

            # det her ser helt klart mere dyrt ud end det er. Husk at len(faces)=3
            for i in faces:
                
                for line1 in self.faceNormalLines[i]:

                    for j in faces:

                        if j == i:
                            continue

                        for line2 in self.faceNormalLines[j]:

                            if line1 == line2:
                                sharedLines.add(line1)

            sharedLines = list(sharedLines)

            # for line in sharedLines:
            #     if line.__axisType == "x":
            #         axisx = self.__createAxis__(line, 0)
            #     elif line.__axisType == "y":
            #         axisy = self.__createAxis__(line, 1)
            #     elif line.__axisType == "z": 
            #         axisz = self.__createAxis__(line, 2)

            for line in sharedLines:
                if line.__axisType == "x":
                    axisx = self.__createAxis__(closestAxis[0][1], 0)
                elif line.__axisType == "y":
                    axisy = self.__createAxis__(closestAxis[1][1], 1)
                elif line.__axisType == "z": 
                    axisz = self.__createAxis__(closestAxis[2][1], 2)

            axisx.checkCrossOvers(self, axisy)
            axisx.checkCrossOvers(self, axisz)
            axisy.checkCrossOvers(self, axisz)
            
            #### Add grid lines
            # self.__drawGridLines__(axisx, axisy, axisz, xyz)

        
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
        """
        Adds title to the plot.
        
        Parameters
        ----------
        firstAxis : str, optional
            Title for the first axis.
        secondAxis : str, optional
            Title for the second axis.
        thirdAxis : str, optional
            Title for the third axis.

        Returns
        -------
        Kaxe.Plot
            The active plotting window
        """
        
        if firstAxis:
            self.firstAxisTitle = firstAxis
        
        if secondAxis:
            self.secondAxisTitle = secondAxis

        if thirdAxis:
            self.thirdAxisTitle = thirdAxis

        return self

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

    
    def inside(self, x, y, z=None):
        if z is None:
            return insideBox(self.windowBox, (x,y))

        return self.inside3D(x,y,z)

    
    # For adding 2D objects into 3D windows 
    # theese functions should acts as an 2D inverse
    def inversepixel(self, x:int, y:int):
        w, h = self.getAttr('width'), self.getAttr('height')
        
        p = [None, None]
        if not x is None: p[0] = (x+self.offset[0]-self.padding[0])/w
        if not y is None: p[1] = (y+self.offset[1]-self.padding[1])/h

        return p




    def inversetranslate(self, x:int, y:int):
        return self.inversepixel(x, y)


class PlotCenter3D(Plot3D):
    """
    A plotting window used to represent a 3D Plot with axis placed correctly 
    
    Parameters
    ----------
    window : list, optional
        The window dimensions for the plot in the format [x0, x1, y0, y1, z0, z1] (default is [-10, 10, -10, 10, -10, 10]).
    rotation : list, optional
        The rotation angles for the plot in degrees [alpha, beta] (default is [0, -20]).
    """

    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__(window, rotation)
        self.__boxed__ = False
        self.__frame__ = False
        self.__normal__ = True


class PlotFrame3D(Plot3D):
    """
    A plotting window used to represent a 3D Plot with only x-, y- and z-axis drawn
    
    Parameters
    ----------
    window : list, optional
        The window dimensions for the plot in the format [x0, x1, y0, y1, z0, z1] (default is [-10, 10, -10, 10, -10, 10]).
    rotation : list, optional
        The rotation angles for the plot in degrees [alpha, beta] (default is [0, -20]).
    """

    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__(window, rotation)
        self.__boxed__ = True
        self.__frame__ = True
        self.__normal__ = False


class PlotEmpty3D(Plot3D):
    """
    A plotting window used to represent a 3D Plot without axis drawn
    
    Parameters
    ----------
    window : list, optional
        The window dimensions for the plot in the format [x0, x1, y0, y1, z0, z1] (default is [-10, 10, -10, 10, -10, 10]).
    rotation : list, optional
        The rotation angles for the plot in degrees [alpha, beta] (default is [0, -20]).
    """

    def __init__(self,  window:list=None, rotation=[0, -20]):
        super().__init__(window, rotation)
        self.__boxed__ = False
        self.__frame__ = False
        self.__normal__ = False
