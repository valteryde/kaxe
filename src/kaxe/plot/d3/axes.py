"""Axis, wireframe, and grid logic for Plot3D."""

import math
import time
import numpy as np
from PIL import Image

from ...core.axis import Axis
from ...core.shapes import ImageShape
from ...core.marker import Marker
from ...core.d3.objects.line import Line3D, FlatLine3D
from ...core.d3.objects.point import Point3D
from ...core.d3.objects.triangle import Triangle
from ...core.d3.helper import formatColor

from .geometry import isPointInTriangle, distance_point_to_line


class Plot3DAxesMixin:
    def __createAxisBoxLine__(self, p1, p2, axisType, color=(0,0,0,255)):
        lineWidth = self.getAttr('wireframeLinewidth')
        
        line = Line3D(p1, p2, width=lineWidth, color=color)
        line.axisType = axisType # x, y or z

        return line


    def __createWireframe__(self):
        """
        Generate the 3D wireframe box geometry with 8 vertices and 12 edges.
        
        Creates a cube structure that serves as the foundation for axis positioning
        and background rendering. The cube is scaled according to self.size and
        organized into edge groups by axis direction for efficient axis selection.
        
        Vertex Layout (right-hand coordinate system):
        - Bottom face: p1(-,-,-), p2(+,-,-), p3(-,+,-), p5(+,+,-)  
        - Top face:    p4(-,-,+), p6(+,-,+), p8(-,+,+), p7(+,+,+)
        
        Edge Organization:
        - X-direction: 4 edges parallel to X-axis  
        - Y-direction: 4 edges parallel to Y-axis
        - Z-direction: 4 edges parallel to Z-axis
        """
        
        h = self.h  # Half-size of the normalized cube
        
        # ===== VERTEX GENERATION =====
        # Generate 8 vertices of the cube, scaled by axis proportions
        self.p1 = np.array((-h, -h, -h)) * self.size  # Bottom-left-back
        self.p2 = np.array((h, -h, -h)) * self.size   # Bottom-right-back  
        self.p3 = np.array((-h, h, -h)) * self.size   # Bottom-left-front
        self.p4 = np.array((-h, -h, h)) * self.size   # Top-left-back
        self.p5 = np.array((h, h, -h)) * self.size    # Bottom-right-front
        self.p6 = np.array((h, -h, h)) * self.size    # Top-right-back
        self.p7 = np.array((h, h, h)) * self.size     # Top-right-front  
        self.p8 = np.array((-h, h, h)) * self.size    # Top-left-front

        # Edge indices by axis direction for axis positioning:
        # X-axis edges: l1, l9, l10, l12 (4 edges parallel to X)
        # Y-axis edges: l2, l5, l6, l11  (4 edges parallel to Y) 
        # Z-axis edges: l3, l4, l7, l8   (4 edges parallel to Z)
    
        # Color coding for debug visualization (currently all black)
        BLUE = (0, 0, 0, 255)   # Could be used for X-axis edges
        GREEN = (0, 0, 0, 255)  # Could be used for Y-axis edges  
        RED = (0, 0, 0, 255)    # Could be used for Z-axis edges

        # ===== EDGE CREATION =====
        # Create 12 wireframe edges connecting the 8 vertices
        # Each edge is tagged with its axis direction for selection algorithm
        
        # X-direction edges (4 edges parallel to X-axis)
        self.l1 = self.__createAxisBoxLine__(self.p1, self.p2, 'x', color=BLUE)   # Bottom-back edge
        self.l9 = self.__createAxisBoxLine__(self.p4, self.p6, 'x', color=GREEN)  # Top-back edge
        self.l10 = self.__createAxisBoxLine__(self.p7, self.p8, 'x', color=RED)   # Top-front edge
        self.l12 = self.__createAxisBoxLine__(self.p3, self.p5, 'x')              # Bottom-front edge
        
        # Y-direction edges (4 edges parallel to Y-axis)  
        self.l2 = self.__createAxisBoxLine__(self.p2, self.p5, 'y', color=BLUE)   # Bottom-right edge
        self.l5 = self.__createAxisBoxLine__(self.p6, self.p7, 'y', color=GREEN)  # Top-right edge
        self.l6 = self.__createAxisBoxLine__(self.p1, self.p3, 'y', color=RED)    # Bottom-left edge
        self.l11 = self.__createAxisBoxLine__(self.p4, self.p8, 'y')              # Top-left edge
        
        # Z-direction edges (4 edges parallel to Z-axis)
        self.l3 = self.__createAxisBoxLine__(self.p2, self.p6, 'z', color=BLUE)   # Right-back edge
        self.l4 = self.__createAxisBoxLine__(self.p5, self.p7, 'z', color=GREEN)  # Right-front edge  
        self.l7 = self.__createAxisBoxLine__(self.p3, self.p8, 'z', color=RED)    # Left-front edge
        self.l8 = self.__createAxisBoxLine__(self.p1, self.p4, 'z')               # Left-back edge

        # ===== EDGE ORGANIZATION =====
        # Group edges by axis direction for efficient axis positioning
        self.lines = [
            [self.l1, self.l9, self.l10, self.l12],    # X-axis candidates
            [self.l2, self.l6, self.l11, self.l5],     # Y-axis candidates  
            [self.l3, self.l4, self.l7, self.l8]       # Z-axis candidates
        ]

        # Storage for the final selected axis lines
        self.axisLines = [None, None, None]  # Will hold chosen [X, Y, Z] axis lines

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

        center = self._scaledPixel(0,0,0) + offset
        a, b = self._scaledPixel(*line.p1) + offset, self._scaledPixel(*line.p2) + offset
        if np.linalg.norm(b - a) < 1e-6:
            b = a + np.array([1.0, 0.0])
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

    def _scaledPixel(self, x, y, z):
        scale = getattr(self, '_gui_overlay_scale', 1.0)
        return self.render.pixel(x, y, z) * scale

    def __drawBackground__(self, i, xyz):
        # add background

        backgroundColor = self.getAttr('backgroundColorBackdrop')

        p1, p2, p3, p4, v1, v2 = self.faceNormals[i]
        
        n = np.cross(v1, v2)
        
        # r/|n| = a 
        a = 1e-4 / np.linalg.norm(n)
        smallzOffset = n * a
        
        if len(self.backgroundTriangles) < 6:
            self.backgroundTriangles.append(
                self.render.add3DObject(Triangle(p1+smallzOffset, p2+smallzOffset, p3+smallzOffset, color=backgroundColor, ableToUseLight=False))
            )
            self.backgroundTriangles.append(
                self.render.add3DObject(Triangle(p4+smallzOffset, p2+smallzOffset, p3+smallzOffset, color=backgroundColor, ableToUseLight=False))
            )
        
        # find den koordinat som de alle sammen har altså holdes konstant igennem fladen
        for i in range(3): # 3 koordinater
            if p1[i] == p2[i] == p3[i] == p4[i]:
                        
                if p1[i] < 0:
                    xyz[i] = self.windowAxis[i*2]
                else:
                    xyz[i] = self.windowAxis[i*2+1]


    def __drawGridLines__(self, axisx:Axis, axisy:Axis, axisz:Axis, xyz):
        axisLineColor = self.getAttr('axisLineColorBackdrop')
        
        xyz = xyz.copy()

        midpointx = (self.windowAxis[0] + self.windowAxis[1]) / 2
        midpointy = (self.windowAxis[2] + self.windowAxis[3]) / 2
        midpointz = (self.windowAxis[4] + self.windowAxis[5]) / 2

        alpha = 0 # if some smallZOffset is needed
        if xyz[0] > midpointx:
            xyz[0] = xyz[0] + alpha
        else:
            xyz[0] = xyz[0] - alpha

        if xyz[1] > midpointy:
            xyz[1] = xyz[1] + alpha
        else:
            xyz[1] = xyz[1] - alpha
            
        if xyz[2] > midpointz:
            xyz[2] = xyz[2] + alpha
        else:
            xyz[2] = xyz[2] - alpha

        width = int(round(self.getAttr('wireframeLinewidth') * 1.25))

        for i in axisx.markers:
            epsilon = (self.windowAxis[1] - self.windowAxis[0]) / 1000
            x = i.x
            if i.x == self.windowAxis[0]:
                x += epsilon
            if i.x == self.windowAxis[1]:
                x -= epsilon                

            self.__lines__.add(self.render.add3DObject(FlatLine3D(self.pixel(x, self.windowAxis[2], xyz[2]), self.pixel(x, self.windowAxis[3], xyz[2]), (0,0,1), color=axisLineColor, ableToUseLight=False, width=width)))
            self.__lines__.add(self.render.add3DObject(FlatLine3D(self.pixel(x, xyz[1], self.windowAxis[4]), self.pixel(x, xyz[1], self.windowAxis[5]), (0,1,0), color=axisLineColor, ableToUseLight=False, width=width)))
            
        for i in axisy.markers:
            epsilon = (self.windowAxis[3] - self.windowAxis[2]) / 1000
            x = i.x
            if i.x == self.windowAxis[2]:
                x += epsilon
            if i.x == self.windowAxis[3]:
                x -= epsilon

            self.__lines__.add(self.render.add3DObject(FlatLine3D(self.pixel(self.windowAxis[0], x, xyz[2]), self.pixel(self.windowAxis[1], x, xyz[2]), (0,0,1), color=axisLineColor, ableToUseLight=False, width=width)))
            self.__lines__.add(self.render.add3DObject(FlatLine3D(self.pixel(xyz[0], x, self.windowAxis[4]), self.pixel(xyz[0], x, self.windowAxis[5]), (1,0,0), color=axisLineColor, ableToUseLight=False, width=width)))
            
        for i in axisz.markers:
            epsilon = (self.windowAxis[5] - self.windowAxis[4]) / 1000
            x = i.x
            if i.x == self.windowAxis[4]:
                x += epsilon
            if i.x == self.windowAxis[5]:
                x -= epsilon

            self.__lines__.add(self.render.add3DObject(FlatLine3D(self.pixel(self.windowAxis[0], xyz[1], x), self.pixel(self.windowAxis[1], xyz[1], x), (0,1,0), color=axisLineColor, ableToUseLight=False, width=width)))
            self.__lines__.add(self.render.add3DObject(FlatLine3D(self.pixel(xyz[0], self.windowAxis[2], x), self.pixel(xyz[0], self.windowAxis[3], x), (1,0,0), color=axisLineColor, ableToUseLight=False, width=width)))
    
    

    def is3DPointInsideAnyBoxFace(self, p1, p2):
        """
        Mål: Tjekke om punktet er inde i de tegnede firkanter.
        Det er lidt et hack, men ideen er at tjekke midterpunkterne på hver linje og så 
        tjekke n-pixel normal for linjen i begge retninger (markeret a og b). 
        Problemmet er nemlig at vi tjekker trekanterne i normal fladerene og de flader 
        trekanter adskilles af de mulige akselinje. 
           +--------------+
          /|             /|
         / |            / |
        *--+-----------*  |
        |  |           |  |
        |  |          a|b |
        |  |           |  |
        |  +-----------+--+
        | /            | /
        |/             |/
        *--------------*
        Det gør så også at den langsomme funktion is3DPointInsideAnyBoxFace skal
        køres dobbelt så mange gange
        """

        p1, p2 = self.render.pixel(*p1), self.render.pixel(*p2)
        point = (p1 + p2) / 2

        v = p2 - p1
        n = np.array([-v[1], v[0]])
        n = n / np.linalg.norm(n)

        topPoint = point + n
        bottomPoint = point - n

        for p1, p2, p3, p4 in self.projectedFaceNormals:

            a = isPointInTriangle(topPoint, p1, p2, p3)
            b = isPointInTriangle(topPoint, p4, p2, p3)

            c = isPointInTriangle(bottomPoint, p1, p2, p3)
            d = isPointInTriangle(bottomPoint, p4, p2, p3)
            
            if (a or b) and (c or d): return True

        return False

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
        if (distance_point_to_line(*l1_p1, *l2_p1, *l2_p2) <= thickness or
            distance_point_to_line(*l1_p2, *l2_p1, *l2_p2) <= thickness or
            distance_point_to_line(*l2_p1, *l1_p1, *l1_p2) <= thickness or
            distance_point_to_line(*l2_p2, *l1_p1, *l1_p2) <= thickness):
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
        """
        Execute the main rendering pipeline after all 3D objects have been added.
        
        This is the core of the 3D rendering system and handles:
        1. Performance optimization through frame rate control
        2. Dynamic axis positioning based on camera view
        3. Background face and grid line generation  
        4. Collision detection and axis overlap resolution
        5. Final image composition and 2D overlay positioning
        
        The method is called every frame and must be highly optimized since it
        runs in real-time during interactive manipulation.
        """
        
        skip3d = self.render.skipObjectUpdate and self.__cachedAxis__ is not None

        # ===== CLEANUP PREVIOUS FRAME =====
        if not skip3d:
            for tri in self.backgroundTriangles:
                self.render.remove3DObject(tri)
            self.backgroundTriangles.clear()

            for line in self.__lines__:
                self.render.remove3DObject(line)
            self.__lines__.clear()

        # ===== 2D IMAGE SETUP =====
        # Create the canvas for final 2D composition
        self.image = ImageShape(Image.new('RGBA', (self.width, self.height)), 0, 0)
        self.addDrawingFunction(self.image)

        needs_axis_update = not self.render.skipObjectUpdate or not self.__cachedAxis__

        # ===== FACE PROJECTION CALCULATION =====
        if self.__boxed__ and needs_axis_update:
            self.projectedFaceNormals = [
                (
                    self.render.pixel(*p1),
                    self.render.pixel(*p2),
                    self.render.pixel(*p3),
                    self.render.pixel(*p4)
                )
                for (p1, p2, p3, p4, *_) in self.faceNormals
            ]

        # ===== BOXED PLOT RENDERING =====
        if self.__boxed__:
            
            # Use cached axis positions if available and not updating objects
            if needs_axis_update:

                # ===== VISIBLE FACE DETECTION =====
                # Determine which cube faces are visible to camera for background rendering
                xyz = {}  # Will store coordinates for background positioning
                
                # Check each of the 6 cube faces for visibility (optimized: ~0.3ms)
                for i, (p1, p2, p3, p4, v1, v2) in enumerate(self.faceNormals):

                    # Calculate face normal vector using cross product
                    n = np.cross(v1, v2)
                    
                    # Transform normal to camera coordinate system
                    x, y, z = self.render.camera.R @ n
                    
                    # Apply coordinate system correction for Y-axis
                    n = np.array([n[0], n[1], -n[2]])
                    x, y, z = self.render.camera.R @ n
                    
                    # ===== FACE CULLING LOGIC =====
                    # Only render faces that are facing toward the camera
                    # This complex logic handles different rotation quadrants
                    specialcase = (180 < self.rotation[1] < 270)  # Special angle range
                    over90 = self.rotation[1] > 90                # Past vertical
                    
                    # Skip faces that are facing away from camera
                    if (y < 0 and (over90 and not specialcase)): continue
                    if (y > 0 and (not over90 or specialcase)): continue

                    # Draw background face if enabled
                    if self.__isBackgroundDrawn__:
                        self.__drawBackground__(i, xyz)
                
                # ===== OPTIMAL AXIS POSITIONING ALGORITHM =====
                # Find the best 3 edges to place X, Y, Z axes on based on:
                # 1. Axis must not overlap with any visible cube face (visibility constraint)
                # 2. Axis should be as close to camera as possible (readability constraint)  
                # 3. Axes must not overlap with each other (clarity constraint)
                
                # Track closest valid axis for each dimension [X, Y, Z]
                closestAxis = [
                    (math.inf, None),   # (distance, Line3D object)
                    (math.inf, None), 
                    (math.inf, None)
                ]

                # Store backup options in case closest axes overlap
                alternativeAxis = {}
                
                # Test all possible axis positions (optimized: 3.5ms → 0.3ms)
                for i, lines in enumerate(self.lines):  # i = axis dimension (0=X, 1=Y, 2=Z)
                    
                    for possibleAxis in lines:  # Test each of 4 edges for this axis

                        p1 = possibleAxis.p1
                        p2 = possibleAxis.p2
                        
                        # ===== VISIBILITY CONSTRAINT =====
                        # Skip if axis would overlap with visible background faces
                        if self.is3DPointInsideAnyBoxFace(p1, p2):
                            continue
                        
                        # ===== DISTANCE CALCULATION =====
                        # Transform to camera coordinates and find closest distance
                        camera = np.array([0, -4*self.h, 0])  # Camera position offset
                        p1_cam = self.render.camera.R @ p1 - camera
                        p2_cam = self.render.camera.R @ p2 - camera
                        
                        # Find minimum distance from camera to axis line
                        dist = min(np.linalg.norm(p1_cam), np.linalg.norm(p2_cam))
                        
                        # Update closest axis if this one is nearer
                        if dist < closestAxis[i][0]:
                            closestAxis[i] = (dist, possibleAxis)
                        
                        # Store as alternative option for overlap resolution
                        if closestAxis[i][1] != possibleAxis:
                            alternativeAxis[i] = possibleAxis
            
                # ===== EXTRACT OPTIMAL AXIS CANDIDATES =====
                # Get the closest valid axis for each dimension
                axis: list[Line3D] = [
                    closestAxis[0][1],  # X-axis line
                    closestAxis[1][1],  # Y-axis line  
                    closestAxis[2][1],  # Z-axis line
                ]
                for i in range(3):
                    if axis[i] is None:
                        axis[i] = self.lines[i][0]

                # ===== OVERLAP RESOLUTION =====
                # Check if any axes would visually overlap and use alternatives (0.2ms)
                for i, l1 in enumerate(axis):
                    # Skip if no alternative available for this axis
                    if i not in alternativeAxis.keys():
                        continue

                    # Check overlap with all other axes
                    for j, l2 in enumerate(axis):
                        if i == j: continue  # Don't compare axis with itself

                        # Test for thick line overlap in 2D projection
                        overlapping = self.__thickAxisLinesOverlap__(l1, l2)

                        if overlapping:
                            # Use alternative axis position to avoid overlap
                            axis[i] = alternativeAxis[i]
                            break  # Found solution, move to next axis
            
            else:
                axis = self.__cachedAxis__
                xyz = self.__cachedXYZ__

            if not skip3d:
                if self.__frame__:
                    for line in axis:
                        if line is not None:
                            self.render.add3DObject(line)
                            self.__lines__.add(line)
                elif self.__boxed__:
                    for axis_lines in self.lines:
                        for line in axis_lines:
                            self.render.add3DObject(line)
                            self.__lines__.add(line)

            ## create axis
            # createAxis * 3 = 5.5 ms (old)
            # createAxis * 3 = 1 ms (new)
            self.__cachedAxis__ = axis
            self.__cachedXYZ__ = xyz
            axisx = self.__createAxis__(axis[0], 0)
            axisy = self.__createAxis__(axis[1], 1)
            axisz = self.__createAxis__(axis[2], 2)

            self.__checkAxisCrossover__() # 0.2 ms
            
            #### Add grid lines
            if self.__isBackgroundDrawn__ and not skip3d:
                self.__drawGridLines__(axisx, axisy, axisz, xyz)
        
        # AXIS IN THE MIDDLE
        if self.__normal__:
            # normal has no markers

            x = min(max(self.windowAxis[0], 0), self.windowAxis[1])
            y = min(max(self.windowAxis[2], 0), self.windowAxis[3])
            z = min(max(self.windowAxis[4], 0), self.windowAxis[5])

            line = Line3D(self.pixel(self.windowAxis[0], y, z), self.pixel(self.windowAxis[1], y, z))
            axisx = self.__createAxis__(line, 0, self.__centerAddMarkers__, [0,1,0])
            self.__lines__.add(self.render.add3DObject(line))

            line = Line3D(self.pixel(x, self.windowAxis[2], z), self.pixel(x, self.windowAxis[3], z))
            axisy = self.__createAxis__(line, 1, self.__centerAddMarkers__, [1,0,0])
            if not self.__centerAddMarkers__:
                axisy.markers = []
            self.__lines__.add(self.render.add3DObject(line))

            line = Line3D(self.pixel(x, y, self.windowAxis[4]), self.pixel(x, y, self.windowAxis[5]))
            axisz = self.__createAxis__(line, 2, self.__centerAddMarkers__, [1,0,0])
            if not self.__centerAddMarkers__:
                axisz.markers = []
            self.__lines__.add(self.render.add3DObject(line))

            self.__checkAxisCrossover__()

        if self.firstAxisTitle:
            axisx.addTitle(self.firstAxisTitle, self)
        
        if self.secondAxisTitle:
            axisy.addTitle(self.secondAxisTitle, self)

        if self.thirdAxisTitle:
            axisz.addTitle(self.thirdAxisTitle, self)
