
# window
from random import randint
import sys
from ..core.helper import insideBox, getbbox
from ..core.window import Window, settings
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
from typing import Union

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
    drawBackground: bool, optional
        Draw background with gridlines
    size : list | bool | None, optional
        if True the axis will be scaled accordingly to window. If a list is passed theese sizes will be used.
    light : list
        light direction. If null vector is given light will not be added.
    """


    def __init__(self,  
                 window:list=None, 
                 rotation:Union[list, tuple]=[60, -70], 
                 size:Union[bool, list, tuple]=None, 
                 drawBackground:bool=False,
                 light:list=[0,0,0],
                 addMarkers:bool=True
        ):
        
        super().__init__()

        rotation = rotation.copy()
        rotation[0] -= 90
        
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

        self.identity = XYZPLOT
        self.light = light
        self.axis = [None, None, None]
        self.__boxed__ = True
        self.__frame__ = False
        self.__normal__ = False
        self.__centerAddMarkers__ = addMarkers
        self.__isBackgroundDrawn__ = drawBackground
        self.forceWidthHeight = False # secret toggle only used by Kaxe.Grid and internal use

        self.firstAxisTitle = None
        self.secondAxisTitle = None
        self.thirdAxisTitle = None

        self.size = size

        # styles
        self.attrmap.default('width', 2000)
        self.attrmap.default('height', 2000)
        self.attrmap.default('wireframeLinewidth', 3)
        self.attrmap.default('backgroundColor', (255,255,255,255))
        self.attrmap.default('backgroundColorBackdrop', (240, 240, 240, 255))
        self.attrmap.default('axisLineColorBackdrop', (200,200,200,255))
        self.attrmap.default('fontSize', 100)
        self.attrmap.setAttr('axis.drawAxis', False)
        self.attrmap.setAttr('axis.stepSizeBand', [125, 75])
        self.attrmap.setAttr('axis.drawMarkersAtEnd', False)
        self.attrmap.setAttr('marker.showLine', False)
        self.attrmap.setAttr('marker.tickWidth', 2)
        self.attrmap.setAttr('marker.offsetTick', True)
        self.attrmap.setAttr('arrowWidth', 0.02)
        self.attrmap.setAttr('arrowHeight', 0.075)
        self.attrmap.setAttr('axis.showArrow', True)

        self.attrmap.default(attr='xNumbers', value=None)
        self.attrmap.default(attr='yNumbers', value=None)
        self.attrmap.default(attr='zNumbers', value=None)

        """
        window:tuple [x0, x1, y0, y1, z0, z1] axis
        """
        
        self.attrmap.submit(Axis)
        self.attrmap.submit(Marker)

        self.h = 1/2
        
        if rotation[0] < 0:
            rotation[0] = 360 + rotation[0]%360
        if rotation[1] < 0:
            rotation[1] = 360 + rotation[1]%360

        self.rotation = [rotation[0]%360, rotation[1]%360]

        self.windowAxis = window
        if window is None:
            self.windowAxis = []



    def __createAxisBoxLine__(self, p1, p2, axisType, color=(0,0,0,255)):
        lineWidth = self.getAttr('wireframeLinewidth')
        
        line = Line3D(p1, p2, width=lineWidth, color=color)
        line.__axisType = axisType # x, y or z
        return self.render.add3DObject(line)


    def __createWireframe__(self):
        # bottom frame
        h = self.h
        self.p1 = np.array((-h, -h, -h)) * self.size
        self.p2 = np.array((h, -h, -h)) * self.size
        self.p3 = np.array((-h, h, -h)) * self.size
        self.p4 = np.array((-h, -h, h)) * self.size
        self.p5 = np.array((h, h, -h)) * self.size
        self.p6 = np.array((h, -h, h)) * self.size
        self.p7 = np.array((h, h, h)) * self.size
        self.p8 = np.array((-h, h, h)) * self.size

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

    def __createAxis__(self, line:Line3D, i, addMarkers=True, arrowRotationVector=None):
        """
        if no arrowRotationVector(=None) is given an arrow will not be added.
        """
        
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
        
        if arrowRotationVector is not None and self.getAttr('axis.showArrow'):
            
            self.arrowWidth = self.getAttr('arrowWidth')
            self.arrowHeight = self.getAttr('arrowHeight')

            connect = line.p2 - line.p1
            connect = connect / np.linalg.norm(connect)
            
            normal = arrowRotationVector
            normal = normal/np.linalg.norm(normal)
            
            dw = normal * self.arrowWidth
            dh = connect * self.arrowHeight

            dhoff = dh/6

            axis.startArrows = [
                self.render.add3DObject(Triangle(line.p1 - dhoff, line.p1 + dw + dh, line.p1 + dh * 2/3)),
                self.render.add3DObject(Triangle(line.p1 - dhoff, line.p1 - dw + dh, line.p1 + dh * 2/3))
            ]

            axis.endArrows = [
                self.render.add3DObject(Triangle(line.p2 + dhoff, line.p2 + dw - dh, line.p2 - dh * 2/3)),
                self.render.add3DObject(Triangle(line.p2 + dhoff, line.p2 - dw - dh, line.p2 - dh * 2/3))
            ]

            # line.p1 += 1/3*dh
            # line.p2 -= 1/3*dh
            
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
        self.window = self.windowAxis

        # create sizes
        if self.size is None:
            self.size = np.array([1, 1, 1])
        elif type(self.size) in [list, tuple]:
            self.size = np.array(self.size) / max(self.size)
        else: # accurate sizes
            self.size = np.array([
                self.window[1] - self.window[0],
                self.window[3] - self.window[2],
                self.window[5] - self.window[4],
            ])
            self.size = self.size / max(self.size)

        self.offset = np.array((-self.h,-self.h,-self.h)) * self.size

        width = height = min(self.getAttr('width'), self.getAttr('height'))
        self.setAttr('width', width)
        self.setAttr('height', height)

        self.backgroundColor = self.getAttr("backgroundColor")
        self.render = Render(
            width=self.getAttr('width'), 
            height=self.getAttr('height'),
            cameraAngle=[math.radians(self.rotation[0]), 
                         math.radians(self.rotation[1])],
            light=self.light,
            backgroundColor=self.backgroundColor
        )
        
        self.__createWireframe__()
        self.__scaleRender__()
        
        # add color to wireframe
        lineBoxColor = self.getAttr('Axis.axisColor')
        if self.__boxed__ or self.__frame__:
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

        # self.__drawDebug__()


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
            
            x,y,z = self.render.camera.R @ n
            if z < 0:
                color = (0,255,0,255)
            
            self.render.add3DObject(Point3D(
                *pos,
                10,
                color=color
            ))


    def __drawBackground__(self, i, xyz):
        # add background

        backgroundColor = self.getAttr('backgroundColorBackdrop')

        p1, p2, p3, p4, v1, v2 = self.faceNormals[i]
        
        n = np.cross(v1, v2)
        smallzOffset = (n/np.linalg.norm(n))/5000
        smallzOffset *= 1

        self.render.add3DObject(Triangle(p1+smallzOffset, p2+smallzOffset, p3+smallzOffset, color=backgroundColor, ableToUseLight=False))
        self.render.add3DObject(Triangle(p4+smallzOffset, p2+smallzOffset, p3+smallzOffset, color=backgroundColor, ableToUseLight=False))
                
        # find den koordinat som de alle sammen har altså holdes konstant igennem fladen
        for i in range(3): # 3 koordinater
            if p1[i] == p2[i] == p3[i] == p4[i]:
                        
                if p1[i] < 0:
                    xyz[i] = self.windowAxis[i*2]
                else:
                    xyz[i] = self.windowAxis[i*2+1]


    def __drawGridLines__(self, axisx:Axis, axisy:Axis, axisz:Axis, xyz):
        axisLineColor = self.getAttr('axisLineColorBackdrop')

        for i in axisx.markers:
            epsilon = (self.windowAxis[1] - self.windowAxis[0]) / 1000
            x = i.x
            if i.x == self.windowAxis[0]:
                x += epsilon
            if i.x == self.windowAxis[1]:
                x -= epsilon                

            self.render.add3DObject(Line3D(self.pixel(x, self.windowAxis[2], xyz[2]), self.pixel(x, self.windowAxis[3], xyz[2]), color=axisLineColor))
            self.render.add3DObject(Line3D(self.pixel(x, xyz[1], self.windowAxis[4]), self.pixel(x, xyz[1], self.windowAxis[5]), color=axisLineColor))
            
        for i in axisy.markers:
            epsilon = (self.windowAxis[3] - self.windowAxis[2]) / 1000
            x = i.x
            if i.x == self.windowAxis[2]:
                x += epsilon
            if i.x == self.windowAxis[3]:
                x -= epsilon

            self.render.add3DObject(Line3D(self.pixel(self.windowAxis[0], x, xyz[2]), self.pixel(self.windowAxis[1], x, xyz[2]), color=axisLineColor))
            self.render.add3DObject(Line3D(self.pixel(xyz[0], x, self.windowAxis[4]), self.pixel(xyz[0], x, self.windowAxis[5]), color=axisLineColor))
            
        for i in axisz.markers:
            epsilon = (self.windowAxis[5] - self.windowAxis[4]) / 1000
            x = i.x
            if i.x == self.windowAxis[4]:
                x += epsilon
            if i.x == self.windowAxis[5]:
                x -= epsilon

            self.render.add3DObject(Line3D(self.pixel(self.windowAxis[0], xyz[1], x), self.pixel(self.windowAxis[1], xyz[1], x), color=axisLineColor))
            self.render.add3DObject(Line3D(self.pixel(xyz[0], self.windowAxis[2], x), self.pixel(xyz[0], self.windowAxis[3], x), color=axisLineColor))
    
    
    def isPointInTriangle(self, p, p1, p2, p3, tol=-1):
        def sign(p, p1, p2):
            return (p[0] - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (p[1] - p2[1])
    
        d1 = sign(p, p1, p2)
        d2 = sign(p, p2, p3)
        d3 = sign(p, p3, p1)
            
        has_neg = (d1 < -tol) or (d2 < -tol) or (d3 < -tol)
        has_pos = (d1 > tol) or (d2 > tol) or (d3 > tol)
            
        return not (has_neg and has_pos)


    def is3DPointInsideAnyBoxFace(self, p1, p2):
        """
        stupidly slow function, but it really only has to be run 30 times
        """

        p1, p2 = self.render.pixel(*p1), self.render.pixel(*p2)
        point = (p1 + p2) / 2

        v = p2 - p1
        n = np.array([-v[1], v[0]])
        n = n/np.linalg.norm(n)

        topPoint = point + n
        bottomPoint = point - n

        for i, (p1, p2, p3, p4, v1, v2) in enumerate(self.faceNormals):

            a = self.isPointInTriangle(topPoint, self.render.pixel(*p1), self.render.pixel(*p2), self.render.pixel(*p3))
            b = self.isPointInTriangle(topPoint, self.render.pixel(*p4), self.render.pixel(*p2), self.render.pixel(*p3))

            c = self.isPointInTriangle(bottomPoint, self.render.pixel(*p1), self.render.pixel(*p2), self.render.pixel(*p3))
            d = self.isPointInTriangle(bottomPoint, self.render.pixel(*p4), self.render.pixel(*p2), self.render.pixel(*p3))

            if (a or b) and (c or d): return True

        return False


    def __distancePointToLine__(self, px, py, x1, y1, x2, y2):
        """Calculate the perpendicular distance from a point (px, py) to a line segment (x1, y1) - (x2, y2)"""
        line_mag = np.hypot(x2 - x1, y2 - y1)
        if line_mag == 0:
            return np.hypot(px - x1, py - y1)
        
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
        u = np.clip(u, 0, 1)
        
        closest_x = x1 + u * (x2 - x1)
        closest_y = y1 + u * (y2 - y1)
        
        return np.hypot(px - closest_x, py - closest_y)

    def __thickAxisLinesOverlap__(self, l1, l2):
        """
        Check if two thick lines (treated as rectangles) overlap
        Minus the end point overlap
        """
        
        thickness = 5
        
        l1_p1 = self.render.pixel(*l1.p1)
        l1_p2 = self.render.pixel(*l1.p2)
        l2_p1 = self.render.pixel(*l2.p1)
        l2_p2 = self.render.pixel(*l2.p2)
        
        v1 = l1_p2 - l1_p1
        v1 = v1 / np.linalg.norm(v1)
        l1_p1 += v1 * thickness * 2
        l1_p2 -= v1 * thickness * 2

        v2 = l2_p2 - l2_p1
        v2 = v2 / np.linalg.norm(v2)
        l2_p1 += v2 * thickness * 2
        l2_p2 -= v2 * thickness * 2

        # Check if any endpoint of one line is within thickness distance of the other line
        if (self.__distancePointToLine__(*l1_p1, *l2_p1, *l2_p2) <= thickness or
            self.__distancePointToLine__(*l1_p2, *l2_p1, *l2_p2) <= thickness or
            self.__distancePointToLine__(*l2_p1, *l1_p1, *l1_p2) <= thickness or
            self.__distancePointToLine__(*l2_p2, *l1_p1, *l1_p2) <= thickness):
            return True
        
        return False


    def __checkAxisCrossover__(self):
        self.axis[0].checkCrossOvers(self, self.axis[1])
        self.axis[0].checkCrossOvers(self, self.axis[2])
        self.axis[1].checkCrossOvers(self, self.axis[0])
        self.axis[1].checkCrossOvers(self, self.axis[2])
        self.axis[2].checkCrossOvers(self, self.axis[0])
        self.axis[2].checkCrossOvers(self, self.axis[1])

    def __after__(self):
        # add to window
        
        self.image = ImageShape(Image.new('RGBA', (self.width, self.height)), 0, 0)
        self.addDrawingFunction(self.image)

        # BOXED AND FRAMED
        if self.__boxed__:
            
            #### Add axis to correct line 
            # Calculate faces facing camera
            xyz = {}
            
            for i, (p1, p2, p3, p4, v1, v2) in enumerate(self.faceNormals):

                n = np.cross(v1, v2)
                x,y,z = self.render.camera.R @ n
                
                n = np.array([n[0], n[1], -n[2]])
                x,y,z = self.render.camera.R @ n
                
                # TODO: 
                #   Understand why this works
                # [180; 270]
                specialcase = (180 < self.rotation[1] < 270)
                over90 = self.rotation[1] > 90
                if (y < 0 and (over90 and not specialcase)): continue
                if (y > 0 and (not over90 or specialcase)): continue

                if self.__isBackgroundDrawn__:
                    self.__drawBackground__(i, xyz)

            
            #### Get positions for axis
            # Regler:
            #   Akse må ikke ligge inden i firkanten altså overlappe noget
            #   Aksen skal være tættest på kameraet som muligt.
            #   Akser må ikke overlappe hindanden
            closestAxis = [
                (math.inf, None), 
                (math.inf, None), 
                (math.inf, None)
            ]

            drawnAxis = []
            alternativeAxis = {}
            for i, lines in enumerate(self.lines):
                
                for possibleAxis in lines:
                    
                    p1 = possibleAxis.p1
                    p2 = possibleAxis.p2
                    
                    # Mål: Tjekke om punktet er inde i de tegnede firkanter.
                    # Det er lidt et hack, men ideen er at tjekke midterpunkterne på hver linje og så 
                    # tjekke n-pixel normal for linjen i begge retninger (markeret a og b). 
                    # Problemmet er nemlig at vi tjekker trekanterne i normal fladerene og de flader 
                    # trekanter adskilles af de mulige akselinje. 
                    #    +--------------+
                    #   /|             /|
                    #  / |            / |
                    # *--+-----------*  |
                    # |  |           |  |
                    # |  |          a|b |
                    # |  |           |  |
                    # |  +-----------+--+
                    # | /            | /
                    # |/             |/
                    # *--------------*
                    # Det gør så også at den langsomme funktion is3DPointInsideAnyBoxFace skal
                    # køres dobbelt så mange gange
                    
                    if self.is3DPointInsideAnyBoxFace(p1, p2):
                        drawnAxis.append(possibleAxis)
                        continue    
                    
                    camera = np.array([0, -4*self.h, 0])
                    p1 = self.render.camera.R @ p1 - camera
                    p2 = self.render.camera.R @ p2 - camera
                    p3 = self.render.camera.R @ p3 - camera

                    dist = min(np.linalg.norm(p1), np.linalg.norm(p2), np.linalg.norm(p3))
                    
                    if dist < closestAxis[i][0]:

                        closestAxis[i] = (dist, possibleAxis)
                    
                    if closestAxis[i][1] != possibleAxis:
                        alternativeAxis[i] = possibleAxis
            
            # front runners
            axis:list[Line3D] = [
                closestAxis[0][1],
                closestAxis[1][1],
                closestAxis[2][1],
            ]

            # tjek om linjerne overlapper
            for i, l1 in enumerate(axis):
                if i not in alternativeAxis.keys():
                    continue

                for j, l2 in enumerate(axis):

                    if i == j: continue

                    overlapping = self.__thickAxisLinesOverlap__(l1, l2)

                    if overlapping:
                        
                        axis[i] = alternativeAxis[i]

                        break
                    

            if self.__frame__:
                for line in drawnAxis:
                    line.hide()

            ## create axis
            axisx = self.__createAxis__(axis[0], 0)
            axisy = self.__createAxis__(axis[1], 1)
            axisz = self.__createAxis__(axis[2], 2)

            self.__checkAxisCrossover__()
            
            #### Add grid lines
            if self.__isBackgroundDrawn__:
                self.__drawGridLines__(axisx, axisy, axisz, xyz)

        
        # AXIS IN THE MIDDLE
        if self.__normal__:
            # normal has no markers

            x = min(max(self.windowAxis[0], 0), self.windowAxis[1])
            y = min(max(self.windowAxis[2], 0), self.windowAxis[3])
            z = min(max(self.windowAxis[4], 0), self.windowAxis[5])

            line = Line3D(self.pixel(self.windowAxis[0], y, z), self.pixel(self.windowAxis[1], y, z))
            R = self.render.camera.R
            axisx = self.__createAxis__(line, 0, self.__centerAddMarkers__, [0,1,0])
            self.render.add3DObject(line)

            line = Line3D(self.pixel(x, self.windowAxis[2], z), self.pixel(x, self.windowAxis[3], z))
            axisy = self.__createAxis__(line, 1, self.__centerAddMarkers__, [1,0,0])
            if not self.__centerAddMarkers__:
                axisy.markers = []
            self.render.add3DObject(line)

            line = Line3D(self.pixel(x, y, self.windowAxis[4]), self.pixel(x, y, self.windowAxis[5]))
            axisz = self.__createAxis__(line, 2, self.__centerAddMarkers__, [1,0,0])
            if not self.__centerAddMarkers__:
                axisz.markers = []
            self.render.add3DObject(line)

            self.__checkAxisCrossover__()


        if self.firstAxisTitle:
            axisx.addTitle(self.firstAxisTitle, self)
        
        if self.secondAxisTitle:
            axisy.addTitle(self.secondAxisTitle, self)

        if self.thirdAxisTitle:
            axisz.addTitle(self.thirdAxisTitle, self)

        self.image.img = self.render.render()
        
        if self.forceWidthHeight:
            """
            with this toggle the image will be placed in the middle
            """
            w, h = self.getSize()

            self.image.img.width, self.image.img.height

            self.pushAll((w - self.image.img.width)/2, (h - self.image.img.height)/2)

        else:
            """
            crop image and resize the whole image
            """

            bbox = getbbox(self.image.img, self.backgroundColor)
            oldpadding = [i for i in self.padding]
            self.__setSize__(bbox[2] - bbox[0], bbox[3] - bbox[1])
            x, y = -bbox[0]-oldpadding[0], -(self.image.img.height-bbox[3])-oldpadding[1]
            self.pushAll(x,y)
            self.__includeAllAgain__()

        # self.addPaddingCondition(bottom=-y+10)


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


    def scaled3D(self, x:int, y:int, z:int) -> tuple:
        return np.array((
            self.size[0] * (x - self.window[0]) / self.windowAxisLength[0],
            self.size[1] * (y - self.window[2]) / self.windowAxisLength[1],
            self.size[2] * (z - self.window[4]) / self.windowAxisLength[2]
        ))

    def pixel(self, x:int, y:int, z:int) -> tuple:
        return self.scaled3D(x,y,z) + self.offset

    
    def inside3D(self, x, y, z):
        return all([
            self.windowAxis[0] <= x <= self.windowAxis[1],
            self.windowAxis[2] <= y <= self.windowAxis[3],
            self.windowAxis[4] <= z <= self.windowAxis[5],
        ])

    def insidePixel(self, x, y, z):
        return all([
            -self.h <= x <= self.h,
            -self.h <= y <= self.h,
            -self.h <= z <= self.h,
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
        The rotation angles for the plot in degrees [alpha, beta] (default is [60, -70]).
    drawBackground: bool, optional
        Draw background with gridlines
    size:  list | bool | None, optional
        if True the axis will be scaled accordingly to window. If a list is passed theese sizes will be used.
    light : list, optional
        light direction. If null vector is given light will not be added.
    """

    def __init__(self, 
                 window:list=None, 
                 rotation=[60, -70], 
                 size:Union[bool, list, tuple]=None, 
                 light:list=[0,0,0],
                 addMarkers:bool=True,
        ):
        super().__init__(window, rotation, size=size, light=light, addMarkers=addMarkers)
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
    size:  list | bool | None, optional
        if True the axis will be scaled accordingly to window. If a list is passed theese sizes will be used.
    light : list, optional
        light direction. If null vector is given light will not be added.
    """

    def __init__(self,  
                 window:list=None, 
                 rotation=[60, -70], 
                 drawBackground=True, 
                 size:Union[bool, list, tuple]=None, 
                 light:list=[0,0,0],
        ):
        super().__init__(window, rotation, size=size, drawBackground=drawBackground, light=light)
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
    size:  list | bool | None, optional
        if True the axis will be scaled accordingly to window. If a list is passed theese sizes will be used.
    light : list, optional
        light direction. If null vector is given light will not be added.
    """

    def __init__(self,  
                window:list=None, 
                rotation=[60, -70], 
                size:Union[bool, list, tuple]=None, 
                light:list=[0,0,0],
        ):
        super().__init__(window, rotation, size=size, light=light)
        self.__boxed__ = False
        self.__frame__ = False
        self.__normal__ = False
