"""
Plot3D window: OpenGL rendering with per-frame 2D overlay.
"""

import logging
import math
import sys
import time
from io import BytesIO
from typing import Optional, Union

import numpy as np
import tqdm
from PIL import Image

from ...core.helper import insideBox, getbbox
from ...core.window import Window, settings
from ...core.svg import infer_format, is_file_path
from ...core.shapes import ImageShape, shapes
from ...core.axis import Axis
from ...core.marker import Marker
from ...core.styles import ComputedAttribute
from ...core.d3.openglrender import OpenGLRender
from ...core.d3.helper import formatColor

from ..constants import XYZPLOT
from .axes import Plot3DAxesMixin


class Plot3D(Plot3DAxesMixin, Window):
    supports_vector_export = False

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
            guiwidth=self.getAttr('guiWidth'),
            guiheight=self.getAttr('guiHeight'),
            cameraAngle=[
                math.radians(self.rotation[0] + 90),  # Azimuth angle (horizontal rotation)
                math.radians(self.rotation[1])        # Elevation angle (vertical tilt)
            ],
            light=self.light,
            backgroundColor=self.backgroundColor
        )
        self._paint_profiler = self.render.profiler
    
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

    def __pillowPaint__(self, fname=None):
        prof = self.render.profiler
        prof.start('window_pillow_paint_start')

        startTime = time.time()
        if self.showProgressBar: pbar = tqdm.tqdm(total=len(self.shapes), desc='Decorating')

        winSize = self.width+self.padding[0]+self.padding[2], self.height+self.padding[1]+self.padding[3]
        surface = Image.new('RGBA', winSize)

        if self.getAttr('backgroundColor')[3] != 0:
            background = shapes.Rectangle(0, 0, winSize[0], winSize[1], color=self.getAttr('backgroundColor'))
            background.draw(surface)

        prof.end('window_pillow_paint_start')
        prof.start('window_paint')
        for shape in self.shapes:
            shape.draw(surface)
            if self.showProgressBar: pbar.update()
        prof.end('window_paint')

        if fname is not None:
            if fname is str:
                surface.save(fname)
            else:
                surface.save(fname, format="png")

        if self.showProgressBar: pbar.close()
        if self.printDebugInfo:
            import logging
            logging.info('Painted in {}s'.format(str(round(time.time() - startTime, 4))))

        return surface

    def __addInnerContent__(self):
        prof = self.render.profiler
        with prof.measure('finalize_objects'):
            for obj in self.objects:
                with prof.measure('finalize_object'):
                    self.__callFinalizeObject__(obj)
                self.addDrawingFunction(obj)

    def __finish_start_setup__(self):
        self.originalShapes = self.shapes.copy()
        self._overlay_font_size = self.getAttr('fontSize')
        self.lastRender = 0

    def __make_overlay__(self):
        def overlay(rotation=self.rotation):
            with self.render.profiler.measure('overlay_init'):
                self.__setupGuiOverlayFrame__(rotation)

            with self.render.profiler.measure('overlay_after'):
                self.__prepareGuiOverlayRebuild__()
                self.__after__()

            with self.render.profiler.measure('overlay_include'):
                self.__includeAllAgain__()
                sorted_shapes = sorted(
                    self.shapes,
                    key=lambda x: x[1] if isinstance(x, tuple) else 0,
                )
                self.shapes = [x[0] if isinstance(x, tuple) else x for x in sorted_shapes]

            with self.render.profiler.measure('overlay_paint'):
                self.attrmap.setAttr('backgroundColor', (0, 0, 0, 0))
                surface = self.__pillowPaint__()

            return surface

        return overlay

    def __complete_gui_prep__(self):
        self.__addInnerContent__()
        self.__finish_start_setup__()

    def __start__(self, for_gui=False):

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

        self.render.SCL -= 200

        if not for_gui:
            self.__complete_gui_prep__()

        return self.__make_overlay__()


    def save(self, fname: Union[str, BytesIO], format: Optional[str] = None, *, project: Optional[str] = None):
        if project is not None:
            raise NotImplementedError(
                "3D plot project files are not supported in .kaxe v1"
            )

        self.setAttr('guiWidth', self.getAttr('width'))
        self.setAttr('guiHeight', self.getAttr('height'))

        self.showProgressBar = False
        self.printDebugInfo = False 

        overlay = self.__start__()

        self.render.showHud = False

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

        if fname is None:
            return image

        fmt = infer_format(fname, format)
        if fmt == "pdf":
            from ...core.svg_pdf import image_to_pdf_page
            image_to_pdf_page(image, fname)
            return image

        if is_file_path(fname):
            image.save(fname)
        else:
            image.save(fname, format="png")

        return image

    def show(self, gui=True):

        if gui:
            overlay = self.__start__(for_gui=True)
            self.render.showHud = True
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

