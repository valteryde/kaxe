
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import os
from stl import mesh
import numpy as np
import time
from math import radians, sin, cos
from typing import Union
from .camera import Camera
from PIL import Image
from .objects.triangle import Triangle
from .objects.line import Line3D
import psutil
process = psutil.Process()
import fondi
import sys

rotation = [330, 290]

class TriangleArray:

    def __init__(self):
        self.vectors = np.array([], dtype=np.float32)
        self.colors = np.array([], dtype=np.float32)
        self.normals = np.array([], dtype=np.float32)
        self.freespaces = []

        self.tempVectors = []
        self.tempColors = []
        self.tempNormals = []

    def finalizeAppend(self):
        self.vectors = np.append(self.vectors, np.array(self.tempVectors).astype(np.float32))
        self.colors = np.append(self.colors, np.array(self.tempColors).astype(np.float32))
        self.normals = np.append(self.normals, np.array(self.tempNormals).astype(np.float32))

        self.tempColors.clear()
        self.tempVectors.clear()
        self.tempNormals.clear()

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
        rotation[1] += dy
        rotation[0] += dx
    last_mouse[:] = [x, y]

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


class OpenGLRender:
    def __init__(self, width=500, height=500, cameraAngle:Union[tuple, list]=(0,0), w:int=None, light=[0,0,0], backgroundColor=(255,255,255,255)):
        self.width = width
        self.height = height

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

        self.objects3d = []
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


    def pixel(self, x, y, z):
        return self.camera.project(np.array((x,y,z))*self.SCL) + self.O


    def add3DObject(self, obj):

        obj.hidden = False
        self.objects3d.append(obj)
        return obj

    def remove3DObject(self, obj):

        for pos in obj.getRemovableTriangles():
            self.removedObjects3d.append((obj, pos))
        return obj

    def loop(self):
        
        # get opengl window size
        self.width = glutGet(GLUT_WINDOW_WIDTH)
        self.height = glutGet(GLUT_WINDOW_HEIGHT)
        
        self.O = np.array((self.width//2, self.height//2)) # offset

        overlayImage = self.overlayFunction(rotation)

        self.refresh()

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

            overlay_np = np.array(overlayImage.convert("RGBA"))

            # overlay_np = np.transpose(overlay_np)
            h, w = overlay_np.shape[:2]
            # Flip vertically for OpenGL coordinates
            overlay_np = np.flipud(overlay_np)
            
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, self.width, 0, self.height, -1, 1)
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
        
        glutSwapBuffers()


    def __appendTriangle__(self, p1, p2, p3, color, normal, obj, tri:TriangleArray):

        if tri.freespaces:
            freepos = tri.freespaces.pop()
            tri.vectors[freepos:freepos+9] = np.array([p1, p2, p3]).flatten()
            colorfreepos = int(freepos*4/3)
            tri.colors[colorfreepos:colorfreepos+12] = np.array([color, color, color]).flatten()
            tri.normals[freepos:freepos+9] = np.array([normal, normal, normal]).flatten()
            obj._pos = freepos

        else:
            obj._pos = len(tri.vectors) + len(tri.tempVectors) * 3
            
            tri.tempVectors.extend((p1, p2, p3))
            tri.tempColors.extend([color, color, color])
            tri.tempNormals.extend([normal, normal, normal])



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

        pos = -1

        now = time.time()
        while len(self.objects3d)-1 > pos:
            pos += 1
            
            obj = self.objects3d[pos]
            
            if obj.hidden:
                continue

            if isinstance(obj, Triangle):

                # Add each vertex separately to ensure a flat array
                p1 = np.array(obj.p1) * scale
                p2 = np.array(obj.p2) * scale
                p3 = np.array(obj.p3) * scale
                # Add color for each vertex
                color = np.array(obj.color[:4]) / 255
                
                # Calculate the normal vector for the triangle
                normal = np.cross(p2 - p1, p3 - p1)
                normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else normal
                normal = normal.astype(np.float32)
                
                if obj.ableToUseLight:
                    self.__appendTriangle__(p1, p2, p3, color, normal, obj, self.triLight)
                else:
                    self.__appendTriangle__(p1, p2, p3, color, normal, obj, self.triNoLight)

            if isinstance(obj, Line3D):

                now = time.time()

                # Translate to Line
                # Represent the 3D line as a thin cylinder (approximated by triangles)
                p1 = np.array(obj.p1)
                p2 = np.array(obj.p2)
                direction = p2 - p1
                length = np.linalg.norm(direction)
                if length == 0:
                    # Degenerate line, skip
                    continue

                direction = direction / length
                # Find a perpendicular vector in 3D (arbitrary, but consistent)
                if not np.allclose(direction, [0, 0, 1]):
                    perp = np.cross(direction, [0, 0, 1])
                else:
                    perp = np.cross(direction, [0, 1, 0])
                perp = perp / np.linalg.norm(perp)

                # Create a second perpendicular vector to form a basis
                perp2 = np.cross(direction, perp)
                perp2 = perp2 / np.linalg.norm(perp2)

                # Cylinder parameters
                radius = obj.width / max(self.width, self.height)
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
                    tri = Triangle(v00, v01, v10, obj.color, ableToUseLight=obj.ableToUseLight)
                    self.objects3d.append(tri)
                    obj._triangles.append(tri)
                    tri = Triangle(v10, v01, v11, obj.color, ableToUseLight=obj.ableToUseLight)
                    self.objects3d.append(tri)
                    obj._triangles.append(tri)

                # Optionally, cap the ends (disks)
                for i in range(1, segments - 1):
                    tri = Triangle(circle1[0], circle1[i], circle1[i + 1], obj.color, ableToUseLight=obj.ableToUseLight)
                    self.objects3d.append(tri)
                    obj._triangles.append(tri)
                    tri = Triangle(circle2[0], circle2[i + 1], circle2[i], obj.color, ableToUseLight=obj.ableToUseLight)
                    self.objects3d.append(tri)
                    obj._triangles.append(tri)

                # print((time.time() - now) * 1000)

        self.objects3d.clear()
        self.triLight.finalizeAppend()
        self.triNoLight.finalizeAppend()

        # print(len(self.triNoLight.vectors))


    def gui(self, overlay):
        global dragging, last_mouse

        self.overlayFunction = overlay
        
        dragging = [False]
        last_mouse = [0, 0]

        def close():
            print("Closing window...")
            os._exit(0)

        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(b"Kaxe")

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glutDisplayFunc(self.loop)
        glutReshapeFunc(reshape)
        glutMouseFunc(mouse_func)
        glutMotionFunc(motion_func)
        glutIdleFunc(idle)
        def keyboard_func(key, *_):
            if key == b'\x1b':  # ESC key
                close()

        glutKeyboardFunc(keyboard_func)
        # Remove glutWMCloseFunc if not available in your GLUT implementation
        try:
            glutWMCloseFunc(close)  # Register window close callback (not available in standard GLUT)
        except Exception:
            pass
        
        glutMainLoop()


    def render(self, overlay):
       
        self.overlayFunction = overlay

        # Initialize GLUT in off-screen mode
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow(b"Kaxe Offscreen")
        # glutHideWindow()  # Hide the window for off-screen rendering

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
        glutDestroyWindow(window)

        self.image = image
        return self.image