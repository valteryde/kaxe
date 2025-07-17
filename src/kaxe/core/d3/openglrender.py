
from OpenGL.GL import *
# from OpenGL.GLU import *
from OpenGL.GLUT import *
import os
from stl import mesh
import numpy as np
import time
from math import radians, sin, cos
from typing import Union
from .camera import Camera
from PIL import Image
from .objects.triangle import Triangle, Triangle3DNumba
from .objects.line import Line3D, FlatLine3D, Line3DNumba, FlatLine3DNumba
from .objects.point import Point3D, Point3DNumba
import psutil
process = psutil.Process()
import fondi
import sys
import sdl2
import sdl2.ext
import sdl2.video
import ctypes
from ..fileloader import loadFile
from numba import jit, njit
from numba.experimental import jitclass
from numba import int32, float64, float32
from numba.types import ListType
from numba.typed import List
from typing import DefaultDict


rotation = [330, 290]

N_0_0_1 = np.array([0, 0, 1], dtype=np.int32)
N_0_0_M1 = np.array([0, 0, -1], dtype=np.int32)
N_0_1_0 = np.array([0, 1, 0], dtype=np.int32)
fN_0_0_1 = np.array([0.0, 0.0, 1.0], dtype=np.float64)

def finalizeTriangleArrayAppend(tri):
    tri.vectors = np.append(tri.vectors, np.array(tri.tempVectors).astype(np.float32))
    tri.colors = np.append(tri.colors, np.array(tri.tempColors).astype(np.float32))
    tri.normals = np.append(tri.normals, np.array(tri.tempNormals).astype(np.float32))

    tri.tempColors.clear()
    tri.tempVectors.clear()
    tri.tempNormals.clear()


@jitclass()
class TriangleArray:
    vectors: float32[:]
    colors: float32[:]
    normals: float32[:]
    freespaces: ListType(int32)
    tempVectors: ListType(float64[:])
    tempColors: ListType(float64[:])
    tempNormals: ListType(float64[:])

    def __init__(self):
        self.vectors = np.empty(0, dtype=np.float32)
        self.colors = np.empty(0, dtype=np.float32)
        self.normals = np.empty(0, dtype=np.float32)
        
        self.freespaces = List.empty_list(int32)

        self.tempVectors = List.empty_list(float64[:])
        self.tempColors = List.empty_list(float64[:])
        self.tempNormals = List.empty_list(float64[:])

    
    def remove(self, pos):
        if pos == None:
            return

        self.freespaces.append(pos)
        for i in range(9):
            self.vectors[pos+i] = 0


def display(triLight:TriangleArray, triNoLight:TriangleArray):

    glClearColor(1.0, 1.0, 1.0, 1.0); #RGBA

    # Set light color
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # glLightfv(GL_LIGHT0, GL_POSITION, spot_position)
    # glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, spot_direction)
    # glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, spot_cutoff)
    glShadeModel(GL_SMOOTH)
    # glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, spot_exponent)

    # Dim the light by reducing the intensity of ambient, diffuse, and specular
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.6, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])

    glEnable(GL_COLOR_MATERIAL)
    # glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glRotatef(rotation[1], 1, 0, 0)
    glRotatef(rotation[0], 0, 0, 1)
    
    ###### Lightning ######
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    vertices = triLight.vectors.reshape(-1, 3)#.astype(np.float32)
    colors = triLight.colors.reshape(-1, 4)#.astype(np.float32)  # Use 4 channels for RGBA
    normals = triLight.normals.reshape(-1, 3)#.astype(np.float32)

    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glColorPointer(4, GL_FLOAT, 0, colors)  # 4 for RGBA
    glNormalPointer(GL_FLOAT, 0, normals)

    glDrawArrays(GL_TRIANGLES, 0, len(vertices))

    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

    glDisable(GL_BLEND)

    ###### Triangle NOT affected by lighting ######
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

    vertices = triNoLight.vectors.reshape(-1, 3)#.astype(np.float32)
    colors = triNoLight.colors.reshape(-1, 4)#.astype(np.float32)  # Use 4 channels for RGBA

    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glColorPointer(4, GL_FLOAT, 0, colors)  # 4 for RGBA
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

    
def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-width / 2, width / 2, -height / 2, height / 2, -5000, 10000.0)
    glMatrixMode(GL_MODELVIEW)


def mouse_drag(x, y):
    # GLUT does not provide dx, dy directly, so store last position
    global last_mouse
    if last_mouse is not None:
        dx = x - last_mouse[0]
        dy = y - last_mouse[1]
        
        set_rotation_from_diff(dx, dy)

    last_mouse[:] = [x, y]

def set_rotation_from_diff(dx, dy):
    rotation[1] += dy
    rotation[0] += dx

    if rotation[1] % 45 == 0:
        if dy > 0:
            rotation[1] = rotation[1] + 1
        else:
            rotation[1] = rotation[1] - 1

    if rotation[0] % 45 == 0:
        if dx > 0:
            rotation[0] = rotation[0] + 1
        else:
            rotation[0] = rotation[0] - 1

@jit
def appendTriangle(p1, p2, p3, color, normal, obj, tri:TriangleArray):

    if len(tri.freespaces) > 0:
        freepos = tri.freespaces.pop()
        for i in range(3):
            tri.vectors[freepos + 3*i + 0] = p1[i]
            tri.vectors[freepos + 3*i + 1] = p2[i]
            tri.vectors[freepos + 3*i + 2] = p3[i]
        
        colorfreepos = int(freepos*4/3)

        # manual unroll måske 
        for i in range(3):  # Repeat color 3 times
            for j in range(4):  # Each color has 4 components (e.g. RGBA)
                tri.colors[colorfreepos + i * 4 + j] = color[j]
        
        for i in range(3):
            tri.normals[freepos + 3*i + 0] = normal[i]
            tri.normals[freepos + 3*i + 1] = normal[i]
            tri.normals[freepos + 3*i + 2] = normal[i]
        
        obj._pos = freepos

    else:
        obj._pos = len(tri.vectors) + len(tri.tempVectors) * 3
        
        color = color.astype(np.float64)
        normal = normal.astype(np.float64)

        tri.tempVectors.append(p1.astype(np.float64))
        tri.tempVectors.append(p2.astype(np.float64))
        tri.tempVectors.append(p3.astype(np.float64))
        for i in range(3):
            tri.tempColors.append(color)

        for i in range(3):
            tri.tempNormals.append(normal)

@njit
def is_close_vec(a, b, tol=1e-8):
    for i in range(len(a)):
        if abs(a[i] - b[i]) > tol:
            return False
    return True

@njit
def norm2(vec):
    return np.sqrt(np.sum(vec * vec))

@njit(cache=True)
def retrieveAndAppendTriangles(triangle3d, line3d, flatline3d, point3d, scale=0, width=0, height=0, triLight=TriangleArray(), triNoLight=TriangleArray()):

    MAX_WIDTH_HEIGHT = np.max(np.array([width, height]))

    for obj in line3d:
        
        # Translate to Line
        # Represent the 3D line as a thin cylinder (approximated by triangles)
        p1 = obj.p1
        p2 = obj.p2
        direction = p2 - p1
        length = np.linalg.norm(direction)
        if length == 0:
            # Degenerate line, skip
            continue

        direction = direction / length
        # Find a perpendicular vector in 3D (arbitrary, but consistent)
        if not is_close_vec(direction, N_0_0_1):
            perp = np.cross(direction, N_0_0_1)
        else:
            perp = np.cross(direction, N_0_1_0)
        perp = perp / np.linalg.norm(perp)

        # Create a second perpendicular vector to form a basis
        perp2 = np.cross(direction, perp)
        perp2 = perp2 / np.linalg.norm(perp2)

        # Cylinder parameters
        radius = obj.width / MAX_WIDTH_HEIGHT
        segments = 12  # Increase for smoother cylinder

        # Generate circle points at both ends
        circle1 = []
        circle2 = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            offset = radius * (np.cos(angle) * perp + np.sin(angle) * perp2)
            circle1.append(p1 + offset)
            circle2.append(p2 + offset)
        
        # Create side triangles
        for i in range(segments):
            next_i = (i + 1) % segments
            v00 = circle1[i]
            v01 = circle1[next_i]
            v10 = circle2[i]
            v11 = circle2[next_i]
            # Two triangles per segment
            
            # FIXME : virker ikke endnu
            tri = Triangle3DNumba(v00, v01, v10, obj.color, obj.ableToUseLight)
            triangle3d.append(tri)
            # obj._triangles.append(tri)
            tri = Triangle3DNumba(v10, v01, v11, obj.color, obj.ableToUseLight)
            triangle3d.append(tri)
            # obj._triangles.append(tri)


        # Optionally, cap the ends (disks)
        for i in range(1, segments - 1):
            continue
            tri = Triangle(circle1[0], circle1[i], circle1[i + 1], obj.color, ableToUseLight=obj.ableToUseLight)
            objects3d.append(tri)
            obj._triangles.append(tri)
            tri = Triangle(circle2[0], circle2[i + 1], circle2[i], obj.color, ableToUseLight=obj.ableToUseLight)
            objects3d.append(tri)
            obj._triangles.append(tri)

    for obj in point3d:
        # Render Point3D as a small sphere (approximated by triangles)

        center = obj.pos
        radius = 2* obj.radius / MAX_WIDTH_HEIGHT
        segments = 4

        # Draw a flat circle in the XY plane
        for i in range(segments):
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments

            v1 = center
            v2 = center + radius * np.array([np.cos(angle1), np.sin(angle1), 0])
            v3 = center + radius * np.array([np.cos(angle2), np.sin(angle2), 0])

            tri = Triangle3DNumba(v1, v2, v3, obj.color, obj.ableToUseLight)
            triangle3d.append(tri)
            # obj._triangles.append(tri)


    for obj in flatline3d:
        
        # FlatLine3D is rendered as a thin rectangle (two triangles)
        p1 = obj.p1
        p2 = obj.p2
        n = obj.n
        width = obj.width / MAX_WIDTH_HEIGHT

        # Find a perpendicular vector to n and (p2-p1)
        direction = p2 - p1
        if norm2(direction) == 0:
            continue
        direction = direction / norm2(direction)
        perp = np.cross(direction, n)
        if norm2(perp) == 0:
            perp = fN_0_0_1
        perp = perp / norm2(perp)

        offset = perp * width / 2

        v1 = p1 + offset
        v2 = p1 - offset
        v3 = p2 + offset
        v4 = p2 - offset

        color = obj.color[:4] / 255
        normal = n.astype(np.float32)

        # Two triangles for the rectangle

        tri1 = Triangle3DNumba(v1, v2, v3, obj.color, obj.ableToUseLight)
        triangle3d.append(tri1)
        # obj._triangles.append(tri1)
        tri2 = Triangle3DNumba(v3, v2, v4, obj.color, obj.ableToUseLight)
        triangle3d.append(tri2)
        # obj._triangles.append(tri2)

    for obj in triangle3d:

        # Add each vertex separately to ensure a flat array
        p1 = obj.p1 * scale
        p2 = obj.p2 * scale
        p3 = obj.p3 * scale
        # Add color for each vertex
        color = obj.color[:4] / 255
        
        # Calculate the normal vector for the triangle
        normal = np.cross(p2 - p1, p3 - p1)
        normal = normal / norm2(normal) if norm2(normal) != 0 else normal
        normal = normal.astype(np.float32)
        
        if obj.ableToUseLight:
            appendTriangle(p1, p2, p3, color, normal, obj, triLight)
        else:
            appendTriangle(p1, p2, p3, color, normal, obj, triNoLight)



def mouse_func(button, state, x, y):
    global dragging
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            dragging[0] = True
            last_mouse[:] = [x, y]
        else:
            dragging[0] = False

def motion_func(x, y):
    if dragging[0]:
        mouse_drag(x, y)

def idle():
    # rotation[0] += 0.5
    # rotation[1] += 0.5
    glutPostRedisplay()


typesRegistry = {
    "point3d": Point3DNumba,
    "triangle3d": Triangle3DNumba,
    "line3d": Line3DNumba,
    "flatline3d": FlatLine3DNumba,
}

class OpenGLRender:
    def __init__(self, width, height, cameraAngle:Union[tuple, list]=(0,0), w:int=None, light=[0,0,0], backgroundColor=(255,255,255,255)):
        self.width = width
        self.height = height

        guiwidth, guiheight = 1000, 750

        self.guiRatio = min(guiwidth / height, guiheight / width, 1)

        self.guiWidth = int(round(width * self.guiRatio))
        self.guiHeight = int(round(height * self.guiRatio))

        self.skipObjectUpdate = False
        self.count = 0
        self.debugDrawOverlay = False

        self.lightDirection = np.array([float(i) for i in light])
        self.useLight = any(light)

        self.backgroundColor = backgroundColor
        self.camera = Camera()
        if w: self.camera.w = w
        self.image = Image.new('RGBA', (self.width, self.height), self.backgroundColor)
        self.image = np.array(self.image)
        self.camera.satelite(*cameraAngle)

        self.removedObjects3d = []

        self.SCL = self.width//10 # pixel scale (tilfældigt)
        self.SCL = 1 # pixel scale (tilfældigt)
        self.O = np.array((self.width//2, self.height//2)) # offset

        self.last_time = time.time()
        self.frames = 0
        self.overlayFunction = None

        self.triLight = TriangleArray()
        self.triNoLight = TriangleArray()

        self.fpsimage = Image.new('RGBA', (0, 0))
        self.memimage = Image.new('RGBA', (0, 0))

        self.objects3d = dict()



    def pixel(self, x, y, z):
        return self.camera.project(np.array((x,y,z))*self.SCL) + self.O


    def add3DObject(self, obj):

        obj.hidden = True
        
        if self.objects3d.get(obj.tp) is None:
            self.objects3d[obj.tp] = List.empty_list(typesRegistry[obj.tp].class_type.instance_type)
            self.objects3d[obj.tp].append(obj)
        else:
            self.objects3d[obj.tp].append(obj)

        return obj

    def remove3DObject(self, obj):

        for pos in obj.getRemovableTriangles():
            self.removedObjects3d.append((obj, pos))
        return obj

    def loop(self):
                
        self.O = np.array((self.width//2, self.height//2)) # offset

        overlayImage = self.overlayFunction(rotation)

        now = time.time()
        self.refresh()
        print(time.time() - now, 's to refresh')

        self.frames += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            
            self.fpsimage = fondi.MathText("\\text{FPS:}" + f" {self.frames}", 32, (255,0,0,255)).image
            self.fpsimage = self.fpsimage.transpose(Image.Transpose.ROTATE_270)

            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_in_mb = mem_info.rss / 1024 / 1024  # rss = Resident Set Size

            self.memimage = fondi.MathText("\\text{Memory:}"+ f" {mem_in_mb:.2f}"+ "\\text{MB}", 32, (255,0,0,255)).image
            self.memimage = self.memimage.transpose(Image.Transpose.ROTATE_270)

            self.frames = 0
            self.last_time = current_time

        if self.debugDrawOverlay:
            margin = 10
            overlayImage.paste(self.fpsimage, (margin, margin))
            overlayImage.paste(self.memimage, (self.fpsimage.width+margin, margin))

        display(self.triLight, self.triNoLight)

        if overlayImage is not None:

            # Convert Pillow image to RGBA and numpy array
            overlayImage = overlayImage.transpose(Image.Transpose.ROTATE_90)
            
            # Resize Pillow Image
            overlayImage = overlayImage.resize((self.guiWidth, self.guiHeight), Image.LANCZOS)

            overlay_np = np.array(overlayImage.convert("RGBA"))

            # overlay_np = np.transpose(overlay_np)
            h, w = overlay_np.shape[:2]
            # Flip vertically for OpenGL coordinates
            overlay_np = np.flipud(overlay_np)
            
            # Resize the image to match the OpenGL viewport

            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, self.guiWidth, 0, self.guiHeight, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_DEPTH_TEST)
            glRasterPos2i(0, 0)
            glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, overlay_np)
            glEnable(GL_DEPTH_TEST)
            glDisable(GL_BLEND)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)


    def refresh(self):

        self.count += 1
        if self.skipObjectUpdate:
            self.objects3d.clear()
            return

        # remove triangles
        # Remove triangles whose indices are in self.removedObjects3d
        for obj, pos in self.removedObjects3d:
            # Convert to set for faster lookup
            # if pos == None:
            #     obj.hidden = True
            #     continue

            if obj.ableToUseLight:
                self.triLight.remove(pos)
            else:
                self.triNoLight.remove(pos)

        self.removedObjects3d.clear()

        # add triangles

        scale = self.SCL

        kwargs = {}
        for key in typesRegistry:
            kwargs[key] = self.objects3d.get(key, List.empty_list(typesRegistry[key].class_type.instance_type))

        retrieveAndAppendTriangles(**kwargs,
            scale=scale, 
            width=self.width, 
            height=self.height, 
            triLight=self.triLight, 
            triNoLight=self.triNoLight
        )

        self.objects3d.clear()
        finalizeTriangleArrayAppend(self.triLight)
        finalizeTriangleArrayAppend(self.triNoLight)


    def quit(self, gl_context, window):
        sdl2.SDL_GL_DeleteContext(gl_context)
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()

    def gui(self, overlay):
        global dragging, last_mouse

        self.overlayFunction = overlay
        
        dragging = [False]
        last_mouse = [0, 0]

        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            print("SDL_Init Error:", sdl2.SDL_GetError())
            return 1

        # OpenGL 2.1 context
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 1)

        window = sdl2.SDL_CreateWindow(b"Kaxe",
                                    sdl2.SDL_WINDOWPOS_CENTERED,
                                    sdl2.SDL_WINDOWPOS_CENTERED,
                                    self.guiWidth, self.guiHeight,
                                    sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_SHOWN)

        self.__setIcon__(window)

        if not window:
            print("SDL_CreateWindow Error:", sdl2.SDL_GetError())
            return 1

        gl_context = sdl2.SDL_GL_CreateContext(window)
        idle = False

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        is_fullscreen = False
        running = True
        event = sdl2.SDL_Event()

        lasttime = time.time()
        dt = 0
        comma_rotation = 0

        while running:
            dt = (time.time() - lasttime) * 1000
            lasttime = time.time()
            while sdl2.SDL_PollEvent(event):
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    self.quit(gl_context, window)
                    sys.exit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        self.quit(gl_context, window)
                        running = False
                        sys.exit()
                    
                    if event.key.keysym.sym == sdl2.SDLK_RETURN and (event.key.keysym.mod & sdl2.KMOD_ALT):
                        # Toggle fullscreen on Alt+Enter
                        if not is_fullscreen:
                            sdl2.SDL_SetWindowFullscreen(window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
                            is_fullscreen = True
                        else:
                            sdl2.SDL_SetWindowFullscreen(window, 0)
                            is_fullscreen = False
                    
                    if event.key.keysym.sym == sdl2.SDLK_SPACE:
                        idle = True

                elif event.type == sdl2.SDL_WINDOWEVENT:
                    if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                        width = event.window.data1
                        height = event.window.data2
                        glViewport(0, 0, width, height)
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    if event.button.button == sdl2.SDL_BUTTON_LEFT:
                        dragging[0] = True
                        idle = False
                        last_mouse[:] = [event.button.x, event.button.y]
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    if event.button.button == sdl2.SDL_BUTTON_LEFT:
                        dragging[0] = False

                elif event.type == sdl2.SDL_MOUSEMOTION:
                    if dragging[0]:
                        motion_func(event.motion.x, event.motion.y)
            
            width = ctypes.c_int()
            height = ctypes.c_int()

            sdl2.SDL_GetWindowSize(window, ctypes.byref(width), ctypes.byref(height))

            self.guiWidth = width.value
            self.guiHeight = height.value

            self.width = int(round(self.guiWidth / self.guiRatio))
            self.height = int(round(self.guiHeight / self.guiRatio))

            if idle:
                d = dt/30

                if np.floor(d+comma_rotation) == 0:
                    comma_rotation += d
                
                else:
                    set_rotation_from_diff(np.floor(d+comma_rotation), 0)
                    comma_rotation = 0

            if running:
                reshape(self.guiWidth, self.guiHeight)
                self.loop()

            sdl2.SDL_GL_SwapWindow(window)


    def __setIcon__(self, window):
        file = loadFile("logo-small.png")
        fpath = ".temp-logo.png"
        Image.open(file).convert("RGBA").save(fpath, format="PNG")
        file = sdl2.ext.load_image(fpath)
        sdl2.SDL_SetWindowIcon(window, file)
        os.remove(fpath)


    def render(self, overlay):
       
        self.overlayFunction = overlay
        self.guiRatio = 1
        self.guiWidth = self.width
        self.guiHeight = self.height

        # Initialize SDL2 with OpenGL context for off-screen rendering
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError("SDL_Init Error: " + str(sdl2.SDL_GetError()))

        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 1)

        window = sdl2.SDL_CreateWindow(
            b"Kaxe Offscreen",
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            self.width, self.height,
            sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_HIDDEN
        )
        if not window:
            sdl2.SDL_Quit()
            raise RuntimeError("SDL_CreateWindow Error: " + str(sdl2.SDL_GetError()))

        self.__setIcon__(window)

        gl_context = sdl2.SDL_GL_CreateContext(window)
        sdl2.SDL_GL_MakeCurrent(window, gl_context)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # Set up a framebuffer object (FBO) for off-screen rendering
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

        # Create a texture to render to
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0)

        # Create a renderbuffer for depth
        rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glDeleteFramebuffers(1, [fbo])
            glDeleteTextures([tex])
            glDeleteRenderbuffers(1, [rbo])
            sdl2.SDL_GL_DeleteContext(gl_context)
            sdl2.SDL_DestroyWindow(window)
            sdl2.SDL_Quit()
            raise RuntimeError("Framebuffer is not complete")

        # Render the scene
        reshape(self.width, self.height)
        self.loop()

        # Read pixels from the framebuffer
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        pixels = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGBA", (self.width, self.height), pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Clean up
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glDeleteFramebuffers(1, [fbo])
        glDeleteTextures([tex])
        glDeleteRenderbuffers(1, [rbo])
        sdl2.SDL_GL_DeleteContext(gl_context)
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()

        self.image = image
        return self.image
