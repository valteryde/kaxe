
"""
Kaxe 3D Plotting Module

This module provides 3D plotting functionality with OpenGL-accelerated rendering.
It includes classes for creating 3D plots with various visual styles (boxed, frame, center, empty)
and supports rotation, lighting, axis rendering, and interactive GUI display.

Key Features:
- OpenGL-accelerated 3D rendering pipeline
- Multiple plot styles (Plot3D, PlotCenter3D, PlotFrame3D, PlotEmpty3D)
- Camera rotation and perspective projection
- Automatic axis positioning and wireframe generation
- Interactive GUI with real-time manipulation
- Export to image formats

Architecture:
The rendering pipeline follows: Setup → Wireframe → Axis Calculation → Object Addition → Rendering
"""

# Standard library imports
import math
import sys
import time
from io import BytesIO
from typing import Union

# Third-party imports
import numpy as np
from PIL import Image

# Core Kaxe imports - Window and UI components
from ..core.helper import insideBox, getbbox
from ..core.window import Window, settings
from ..core.shapes import ImageShape
from ..core.axis import Axis
from ..core.marker import Marker
from ..core.styles import ComputedAttribute

# 3D rendering engine imports
from ..core.d3.render import Render
from ..core.d3.openglrender import OpenGLRender
from ..core.d3.objects.line import Line3D, FlatLine3D
from ..core.d3.objects.point import Point3D
from ..core.d3.objects.triangle import Triangle
from ..core.d3.helper import formatColor

# Constants
XYZPLOT = 'xyz'  # Plot type identifier for 3D XYZ coordinate system

# ============================================================================
# Geometric Utility Functions
# ============================================================================

def sign(p, p1, p2):
    """
    Calculate the signed area of a triangle formed by three points.
    
    This function computes twice the signed area of the triangle (p1, p2, p).
    Used in point-in-triangle tests to determine which side of a line a point lies on.
    
    Parameters
    ----------
    p : array-like
        Test point [x, y]
    p1, p2 : array-like
        Line segment endpoints [x, y]
        
    Returns
    -------
    float
        Positive if p is on left side of line p1->p2, negative if on right side
    """
    return (p[0] - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (p[1] - p2[1])


def isPointInTriangle(p, p1, p2, p3, tol=-1):
    """
    Test if a point lies inside a triangle using the sign method.
    
    Uses three signed area calculations to determine if a point is inside
    a triangle. A point is inside if all three signs are the same (all positive
    or all negative), indicating the point is on the same side of all three edges.
    
    Parameters
    ----------
    p : array-like
        Test point coordinates [x, y]
    p1, p2, p3 : array-like
        Triangle vertex coordinates [x, y]
    tol : float, optional
        Tolerance for boundary cases (default: -1, meaning strict inside test)
        
    Returns
    -------
    bool
        True if point is inside triangle, False otherwise
        
    Notes
    -----
    This is a fast, numerically stable algorithm for point-in-triangle testing.
    The tolerance parameter allows for fuzzy boundary detection.
    """
    d1 = sign(p, p1, p2)
    d2 = sign(p, p2, p3)
    d3 = sign(p, p3, p1)
        
    has_neg = (d1 < -tol) or (d2 < -tol) or (d3 < -tol)
    has_pos = (d1 > tol) or (d2 > tol) or (d3 > tol)
    
    return not (has_neg and has_pos)


class Plot3D(Window):
    """
    A 3D plotting window with full wireframe box and automatic axis positioning.
    
    This class provides a complete 3D plotting environment with:
    - Automatic wireframe box generation around the plot volume
    - Dynamic axis positioning based on camera angle for optimal visibility
    - OpenGL-accelerated rendering with lighting support
    - Interactive rotation and real-time manipulation
    - Background grid lines and face highlighting
    
    The coordinate system follows right-hand rule with:
    - X-axis: left-right (red lines in debug mode)
    - Y-axis: front-back (green lines in debug mode)  
    - Z-axis: up-down (blue lines in debug mode)
    
    Rendering Pipeline:
    1. Setup camera and 3D transformations (__before__)
    2. Generate wireframe box geometry (__createWireframe__)
    3. Calculate visible faces and axis positions (__after__)
    4. Position axes on closest visible edges to camera
    5. Add grid lines and background faces
    6. Render all 3D objects to 2D image
        
    Attributes
    ----------
    axis : list[Axis]
        The three axes of the plot [x_axis, y_axis, z_axis]
    render : OpenGLRender
        The 3D rendering engine instance
    rotation : list[float]
        Current camera rotation angles [alpha, beta] in degrees
    light : list[float] 
        Light direction vector [x, y, z]. Zero vector disables lighting
    windowAxis : list[float]
        Plot bounds [x_min, x_max, y_min, y_max, z_min, z_max]

    Parameters
    ----------
    window : list, optional
        The plot bounds [x0, x1, y0, y1, z0, z1] (default: [-10, 10, -10, 10, -10, 10])
    rotation : list, optional
        Camera angles [alpha, beta] in degrees (default: [60, -70])
    size : list | bool | None, optional
        Axis scaling: True for automatic, list for custom ratios, None for unit cube
    drawBackground : bool, optional
        Whether to draw background faces and grid lines (default: False)
    light : list, optional
        Light direction vector [x, y, z] (default: [0, 0, 0] = no lighting)
    addMarkers : bool, optional
        Whether to add tick marks and labels to axes (default: True)
        
    Notes
    -----
    The plot automatically selects the best axis positioning based on camera angle
    to avoid overlapping lines and ensure maximum visibility. The wireframe box
    consists of 12 edges forming a cube, with axes positioned on the 3 most
    visible edges closest to the camera.
    """


    def __init__(self,  
                 window: list = None, 
                 rotation: Union[list, tuple] = [60, -70], 
                 size: Union[bool, list, tuple] = None, 
                 drawBackground: bool = False,
                 light: list = [0, 0, 0],
                 addMarkers: bool = True
        ):

        super().__init__()

        # Performance tracking for render optimization
        self.lastRender = time.time()

        # Adjust rotation for internal coordinate system
        # The internal system has a different orientation than user input
        rotation = rotation.copy()
        rotation[0] -= 90
        
        # ASCII art showing the 3D box structure:
        # The plot creates a wireframe box with 8 vertices and 12 edges
        # Axes are positioned on the 3 most visible edges closest to camera
        """
        3D Wireframe Box Geometry:
        
           p8--------------p7
          /|             /|
         / |            / |
        p3-+----------p5  |
        |  |           |  |
        |  |           |  |
        |  p4----------|--p6
        | /            | /
        |/             |/
        p1--------------p2
        
        Edge grouping by axis:
        X-axis edges: p1-p2, p4-p6, p7-p8, p3-p5
        Y-axis edges: p2-p5, p6-p7, p4-p8, p1-p3  
        Z-axis edges: p2-p6, p5-p7, p3-p8, p1-p4
        """

        # Rendering engine selection (currently using OpenGL)
        # self.engine = "opengl"  # Future: could support multiple backends
        
        # Plot identification and configuration
        self.identity = XYZPLOT
        self.light = light
        self.axis = [None, None, None]  # Will hold [x_axis, y_axis, z_axis]
        
        # Plot style flags - control which visual elements are shown
        self.__boxed__ = True        # Show full wireframe box
        self.__frame__ = False       # Show only axis lines (no box)  
        self.__normal__ = False      # Show axes through center (no box)
        self.__centerAddMarkers__ = addMarkers
        self.__isBackgroundDrawn__ = drawBackground
        
        # Layout control - forces image to fit exact width/height
        self.forceWidthHeight = True  # Used by Grid class for precise sizing

        # Axis titles (set via title() method)
        self.firstAxisTitle = None    # X-axis title
        self.secondAxisTitle = None   # Y-axis title  
        self.thirdAxisTitle = None    # Z-axis title

        # Size configuration for axis scaling
        self.size = size

        # ===== STYLE AND APPEARANCE CONFIGURATION =====
        # Set up default visual attributes for the 3D plot
        
        # Image resolution and GUI window size
        self.attrmap.default('width', 2000)           # Render resolution width
        self.attrmap.default('height', 2000)          # Render resolution height  
        self.attrmap.default('guiWidth', 1000)        # GUI window width
        self.attrmap.default('guiHeight', 750)        # GUI window height
        
        # Line and wireframe styling
        # Wireframe thickness scales with image resolution for consistent appearance
        self.attrmap.default('wireframeLinewidth', 
            ComputedAttribute(lambda m: max(round(m.getAttr('width')//300), 3)))
        
        # Color scheme
        self.attrmap.default('backgroundColor', (255, 255, 255, 255))        # White background
        self.attrmap.default('backgroundColorBackdrop', (240, 240, 240, 255)) # Light gray faces
        self.attrmap.default('axisLineColorBackdrop', (200, 200, 200, 255))   # Grid line color
        self.attrmap.default('fontSize', 100)         # Axis label font size
        
        # Axis configuration
        self.attrmap.setAttr('axis.drawAxis', False)           # Don't draw 2D-style axis lines
        self.attrmap.setAttr('axis.stepSizeBand', [125, 75])   # Tick spacing range
        self.attrmap.setAttr('axis.drawMarkersAtEnd', False)   # No end markers on axes
        
        # Tick mark styling  
        self.attrmap.setAttr('marker.showLine', False)         # No connecting lines to ticks
        self.attrmap.setAttr('marker.tickWidth', 
            ComputedAttribute(lambda m: max(round(m.getAttr('width')//300), 1)))
        self.attrmap.setAttr('marker.tickLength', 
            ComputedAttribute(lambda m: max(round(m.getAttr('width')//100), 10)))
        self.attrmap.setAttr('marker.offsetTick', True)        # Offset ticks from axis line
        
        # Arrow styling for axis endpoints
        self.attrmap.setAttr('arrowWidth', 0.02)       # Arrow head width in 3D units
        self.attrmap.setAttr('arrowHeight', 0.075)     # Arrow head length in 3D units  
        self.attrmap.setAttr('axis.showArrow', True)   # Show directional arrows

        # Custom tick mark positions (None = automatic)
        self.attrmap.default(attr='xNumbers', value=None)
        self.attrmap.default(attr='yNumbers', value=None)
        self.attrmap.default(attr='zNumbers', value=None)

        # ===== INTERNAL STATE VARIABLES =====
        # Runtime containers for geometry and caching
        self.backgroundTriangles = []    # Background face triangles (rebuilt each frame)
        self.__cachedAxis__ = None       # Cached axis positions for performance
        self.__cachedXYZ__ = None        # Cached coordinate mapping

        # ===== COORDINATE SYSTEM SETUP =====
        # Configure the 3D coordinate system and plot bounds
        # window format: [x_min, x_max, y_min, y_max, z_min, z_max]
        
        # Register style classes for inheritance
        self.attrmap.submit(Axis)   # Inherit axis styling
        self.attrmap.submit(Marker) # Inherit marker styling

        # 3D cube half-size (creates cube from -0.5 to +0.5 in each dimension)
        self.h = 1/2
        
        # Set camera rotation angles (handles angle normalization)
        self.__setRotation__(rotation)

        # Set plot bounds (default to empty, will be set during rendering)
        self.windowAxis = window if window is not None else []

        # ===== RENDERING COLLECTIONS =====
        # Containers for managing 3D objects during rendering
        self.__triangleFaces__ = dict()  # Face triangle mapping for collision detection
        self.__lines__ = set()           # Set of all line objects for efficient management

    def __setRotation__(self, rotation):
        if rotation[0] < 0:
            rotation[0] = 360 + rotation[0]%360
        if rotation[1] < 0:
            rotation[1] = 360 + rotation[1]%360

        self.rotation = [rotation[0]%360, rotation[1]%360]

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

    def __updateSkipObjectUpdate__(self):
        rot = (self.rotation[0], self.rotation[1])
        prev = getattr(self, '_last_axis_rotation', None)
        now = time.time()

        if prev is not None and rot == prev:
            self.render.skipObjectUpdate = True
            return

        if prev is not None and now - self.lastRender < 0.1:
            self.render.skipObjectUpdate = True
            return

        self._last_axis_rotation = rot
        self.lastRender = now
        self.render.skipObjectUpdate = False

    def __setupGuiOverlayFrame__(self, rotation):
        self._gui_overlay_scale = self.render.guiWidth / self.render.width
        self.width = self.render.guiWidth
        self.height = self.render.guiHeight
        self.attrmap.setAttr('width', self.width)
        self.attrmap.setAttr('height', self.height)
        self.attrmap.setAttr(
            'fontSize',
            max(round(self._overlay_font_size * self._gui_overlay_scale), 12),
        )
        self.windowBox = [0, 0, self.width, self.height]
        self.rotation = rotation
        self.__setRotation__(rotation)
        self.render.camera.satelite(math.radians(self.rotation[0]), math.radians(self.rotation[1]))
        self.__updateSkipObjectUpdate__()

    def __prepareGuiOverlayRebuild__(self):
        self.padding = [0, 0, 0, 0]
        self.__included__.clear()
        self.shapes = list(self.originalShapes)

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
        """
        Initialize the 3D rendering environment and setup the plot geometry.
        
        This method is called during plot setup and handles:
        1. Coordinate system normalization and scaling
        2. 3D render engine initialization 
        3. Wireframe box generation
        4. Camera positioning and scaling
        5. Visual style application
        
        The method transforms the user's plot bounds into a normalized 3D space
        and sets up the OpenGL rendering pipeline with proper camera angles.
        """
        
        # Set the working coordinate bounds from user input
        self.window = self.windowAxis

        # ===== COORDINATE SYSTEM NORMALIZATION =====
        # Transform plot bounds to normalized cube [-0.5, 0.5] in each dimension
        if self.size is None:
            # Default: unit cube (all axes equal length)
            self.size = np.array([1, 1, 1])
        elif type(self.size) in [list, tuple]:
            # Custom proportions: normalize to largest dimension
            self.size = np.array(self.size) / max(self.size)
        else:
            # Proportional to actual data ranges
            self.size = np.array([
                self.window[1] - self.window[0],  # X range
                self.window[3] - self.window[2],  # Y range  
                self.window[5] - self.window[4],  # Z range
            ])
            self.size = self.size / max(self.size)

        # Calculate offset to center the cube at origin
        self.offset = np.array((-self.h, -self.h, -self.h)) * self.size

        # ===== 3D RENDERING ENGINE SETUP =====
        self.backgroundColor = self.getAttr("backgroundColor")
        
        # Initialize OpenGL-accelerated renderer
        # Note: camera angle adjustment (+90 degrees) for coordinate system alignment
        self.render = OpenGLRender(
            width=self.getAttr('width'), 
            height=self.getAttr('height'),
            cameraAngle=[
                math.radians(self.rotation[0] + 90),  # Azimuth angle (horizontal rotation)
                math.radians(self.rotation[1])        # Elevation angle (vertical tilt)
            ],
            light=self.light,
            backgroundColor=self.backgroundColor
        )
    
        # ===== GEOMETRY GENERATION =====
        self.__createWireframe__()  # Generate the 12-edge box structure
        self.__scaleRender__()      # Fit the box within the viewport
        
        # ===== VISUAL STYLING =====
        # Apply wireframe colors based on plot style
        lineBoxColor = self.getAttr('Axis.axisColor')
        if self.__boxed__ or self.__frame__:
            # Show wireframe lines with axis color
            for axis_lines in self.lines:
                for line in axis_lines:
                    line.color = formatColor(lineBoxColor)
        else:
            # Hide wireframe for center/empty plot styles
            for axis_lines in self.lines:
                for line in axis_lines:
                    line.hide()

        # ===== PRECOMPUTE AXIS METRICS =====
        # Calculate axis lengths in user coordinates for marker spacing
        self.windowAxisLength = [
            self.window[1] - self.window[0],  # X-axis length
            self.window[3] - self.window[2],  # Y-axis length  
            self.window[5] - self.window[4],  # Z-axis length
        ]

        # Optional: Enable debug visualization
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

            # self.render.add3DObject(Triangle(p1, p2, p3, color=colors[i]))
            # self.render.add3DObject(Triangle(p4, p2, p3, color=colors[i]))

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

        # self.image.img = self.render.render()
        
        # if self.forceWidthHeight:
        #     """
        #     with this toggle the image will be placed in the middle
        #     """
        #     w, h = self.getSize()

        #     self.pushAll((w - self.image.img.width)/2, (h - self.image.img.height)/2)

        # else:
        #     """
        #     crop image and resize the whole image
        #     """

        #     bbox = getbbox(self.image.img, self.backgroundColor)
        #     oldpadding = [i for i in self.padding]
        #     self.__setSize__(bbox[2] - bbox[0], bbox[3] - bbox[1])
        #     x, y = -bbox[0]-oldpadding[0], -(self.image.img.height-bbox[3])-oldpadding[1]
        #     self.pushAll(x,y)
        #     self.__includeAllAgain__()

        # self.addPaddingCondition(bottom=-y+10)


    def __addInnerContent__(self):
        loading = getattr(self, 'render', None) is not None and self.render.loading_screen_active
        prof = self.render.profiler
        with prof.measure('finalize_objects'):
            for obj in self.objects:
                if loading:
                    self.render.tick_loading()
                with prof.measure('finalize_object'):
                    self.__callFinalizeObject__(obj)
                self.addDrawingFunction(obj)
                if loading:
                    self.render.tick_loading()

    def __finish_start_setup__(self):
        self.originalShapes = self.shapes.copy()
        self._overlay_font_size = self.getAttr('fontSize')
        self.lastRender = 0

    def __make_overlay__(self):
        def overlay(rotation=self.rotation):
            loading = self.render.loading_screen_active

            with self.render.profiler.measure('overlay_init'):
                self.__setupGuiOverlayFrame__(rotation)
            if loading:
                self.render.tick_loading()

            with self.render.profiler.measure('overlay_after'):
                self.__prepareGuiOverlayRebuild__()
                self.__after__()
            if loading:
                self.render.tick_loading()

            with self.render.profiler.measure('overlay_include'):
                self.__includeAllAgain__()
                sorted_shapes = sorted(
                    self.shapes,
                    key=lambda x: x[1] if isinstance(x, tuple) else 0,
                )
                self.shapes = [x[0] if isinstance(x, tuple) else x for x in sorted_shapes]
            if loading:
                self.render.tick_loading()

            with self.render.profiler.measure('overlay_paint'):
                self.attrmap.setAttr('backgroundColor', (0, 0, 0, 0))
                surface = self.__pillowPaint__()
            if loading:
                self.render.tick_loading()

            return surface

        return overlay

    def __complete_deferred_start__(self):
        self.__addInnerContent__()
        self.__finish_start_setup__()
        self._defer_gui_prep = False

    def __start__(self, prepare_window=False):

        self.showProgressBar = False
        self.printDebugInfo = False

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

        # self.render.SCL -= 300
        self.render.SCL -= 200

        self._defer_gui_prep = False
        if prepare_window:
            self.render.prepareGuiWindow()
            self.render.begin_loading_screen()
            self._defer_gui_prep = True
        else:
            self.__addInnerContent__()
            self.__finish_start_setup__()

        return self.__make_overlay__()


    def save(self, fname:Union[str, BytesIO]):

        self.setAttr('guiWidth', self.getAttr('width'))
        self.setAttr('guiHeight', self.getAttr('height'))

        self.showProgressBar = False
        self.printDebugInfo = False 

        overlay = self.__start__()

        self.render.debugDrawOverlay = False

        image = self.render.render(overlay)
        image = image.crop(getbbox(image, self.backgroundColor))
        
        padding = self.getAttr('outerPadding')
        largeImage = Image.new(
            'RGBA', 
            (image.size[0]+padding[0]+padding[2], image.size[1]+padding[1]+padding[3]), 
            color=self.backgroundColor
        )
        largeImage.paste(image, (padding[0], padding[1]))

        image = largeImage

        if fname == None:
            pass
        elif fname is str:
            image.save(fname)
        else:
            image.save(fname, format="png")

        return image

    def show(self, gui=True):

        if gui:
            overlay = self.__start__(prepare_window=True)
            self.render.debugDrawOverlay = True
            self.render.gui(overlay, plot=self)
        else:
            self.save(None).show()

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


    def scaled3D(self, x: int, y: int, z: int) -> tuple:
        """
        Transform user coordinates to normalized 3D space.
        
        Converts from user data coordinates to the normalized cube space
        used internally by the 3D renderer. Each axis is independently
        scaled according to the plot bounds and size ratios.
        
        Parameters
        ----------
        x, y, z : int
            Coordinates in user data space
            
        Returns
        -------
        tuple
            Coordinates in normalized 3D space [-0.5*size, +0.5*size]
        """
        return np.array((
            self.size[0] * (x - self.window[0]) / self.windowAxisLength[0],
            self.size[1] * (y - self.window[2]) / self.windowAxisLength[1],
            self.size[2] * (z - self.window[4]) / self.windowAxisLength[2]
        ))

    def pixel(self, x: int, y: int, z: int) -> tuple:
        """
        Transform user coordinates to final 3D render coordinates.
        
        This is the main coordinate transformation function used throughout
        the plotting system. It scales user data coordinates and applies
        the cube centering offset.
        
        Parameters
        ----------
        x, y, z : int
            Coordinates in user data space
            
        Returns
        -------
        tuple
            Final 3D coordinates ready for rendering
        """
        return self.scaled3D(x, y, z) + self.offset

    
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
