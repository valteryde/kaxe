
from OpenGL.GL import *
# from OpenGL.GLU import *
from OpenGL.GLUT import *
import os
from stl import mesh
import numpy as np
import time
from math import radians, sin, cos, pi
from typing import Union
from .camera import Camera
from PIL import Image
from .objects.triangle import Triangle, Triangle3D
from .objects.line import Line3D, FlatLine3D, Line3DObject, FlatLine3DObject
from .objects.point import Point3D, Point3DObject
import psutil
process = psutil.Process()
import fondi
import sys
import sdl2
import sdl2.ext
import sdl2.video
import ctypes
from ..fileloader import loadFile
from typing import DefaultDict
import cv2
from ..styles import colors as kaxe_colors
from ..profiler import Profiler
from ..helper import to_numpy

rotation = [330, 290]

N_0_0_1 = np.array([0, 0, 1], dtype=np.int32)
N_0_0_M1 = np.array([0, 0, -1], dtype=np.int32)
N_0_1_0 = np.array([0, 1, 0], dtype=np.int32)
fN_0_0_1 = np.array([0.0, 0.0, 1.0], dtype=np.float64)


class TriangleArray:

    def __init__(self, initial_capacity=10000):
        # Pre-allocate arrays with initial capacity
        self.capacity = initial_capacity * 3  # 3 coordinates per vertex
        self.color_capacity = initial_capacity * 4  # 4 components per color (RGBA)
        self.normal_capacity = initial_capacity * 3  # 3 components per normal

        self.vectors = np.zeros(self.capacity, dtype=np.float32)
        self.colors = np.zeros(self.color_capacity, dtype=np.float32)
        self.normals = np.zeros(self.normal_capacity, dtype=np.float32)

        self.current_size = 0
        self.color_current_size = 0
        self.normal_current_size = 0

        self.freespaces = []
        self.tempVectors = []
        self.tempColors = []
        self.tempNormals = []

    
    def remove(self, pos):
        if pos == None:
            return

        self.freespaces.append(pos)
        for i in range(9):
            self.vectors[pos+i] = 0


    # def finalizeAppend(self):
    #     self.vectors = np.append(self.vectors, self.tempVectors)
    #     self.colors = np.append(self.colors, self.tempColors)
    #     self.normals = np.append(self.normals, self.tempNormals)

    #     self.tempColors.clear()
    #     self.tempVectors.clear()
    #     self.tempNormals.clear()

    def finalizeAppend(self):
        # Check if we need to expand capacity
        n = len(self.tempVectors)
        c = len(self.tempColors)
        m = len(self.tempNormals)
        
        needed_vector_size = self.current_size + 3 * n
        needed_color_size = self.color_current_size + 4 * c
        needed_normal_size = self.normal_current_size + 3 * m
        
        # Expand arrays if needed (double capacity)
        if needed_vector_size > self.capacity:
            new_capacity = max(needed_vector_size, self.capacity * 2)
            new_vectors = np.zeros(new_capacity, dtype=np.float32)
            new_vectors[:self.current_size] = self.vectors[:self.current_size]
            self.vectors = new_vectors
            self.capacity = new_capacity
            
        if needed_color_size > self.color_capacity:
            new_color_capacity = max(needed_color_size, self.color_capacity * 2)
            new_colors = np.zeros(new_color_capacity, dtype=np.float32)
            new_colors[:self.color_current_size] = self.colors[:self.color_current_size]
            self.colors = new_colors
            self.color_capacity = new_color_capacity
            
        if needed_normal_size > self.normal_capacity:
            new_normal_capacity = max(needed_normal_size, self.normal_capacity * 2)
            new_normals = np.zeros(new_normal_capacity, dtype=np.float32)
            new_normals[:self.normal_current_size] = self.normals[:self.normal_current_size]
            self.normals = new_normals
            self.normal_capacity = new_normal_capacity
        
        if n:
            flat_vectors = np.concatenate(self.tempVectors).astype(np.float32, copy=False)
            end = self.current_size + flat_vectors.size
            self.vectors[self.current_size:end] = flat_vectors
            self.current_size = end

        if c:
            flat_colors = np.stack(self.tempColors).astype(np.float32, copy=False).reshape(-1)
            end = self.color_current_size + flat_colors.size
            self.colors[self.color_current_size:end] = flat_colors
            self.color_current_size = end

        if m:
            flat_normals = np.stack(self.tempNormals).astype(np.float32, copy=False).reshape(-1)
            end = self.normal_current_size + flat_normals.size
            self.normals[self.normal_current_size:end] = flat_normals
            self.normal_current_size = end

        self.tempVectors.clear()
        self.tempColors.clear()
        self.tempNormals.clear()


_display_initialized = False

def set_clear_color(backgroundColor=(255, 255, 255, 255)):
    r, g, b, a = (c / 255.0 for c in backgroundColor[:4])
    glClearColor(r, g, b, a)

def init_display_state(backgroundColor=(255, 255, 255, 255)):
    global _display_initialized

    set_clear_color(backgroundColor)
    if _display_initialized:
        return

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.6, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
    glEnable(GL_COLOR_MATERIAL)
    _display_initialized = True


def display(triLight:TriangleArray, triNoLight:TriangleArray, backgroundColor=(255, 255, 255, 255)):
    set_clear_color(backgroundColor)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glRotatef(rotation[1], 1, 0, 0)
    glRotatef(rotation[0], 0, 0, 1)
    
    ###### Lightning ######
    light_count = triLight.current_size // 3
    if light_count:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        vertices = triLight.vectors[:triLight.current_size].reshape(-1, 3)
        colors = triLight.colors[:triLight.color_current_size].reshape(-1, 4)
        normals = triLight.normals[:triLight.normal_current_size].reshape(-1, 3)

        glVertexPointer(3, GL_FLOAT, 0, vertices)
        glColorPointer(4, GL_FLOAT, 0, colors)
        glNormalPointer(GL_FLOAT, 0, normals)
        glDrawArrays(GL_TRIANGLES, 0, light_count)

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisable(GL_BLEND)

    ###### Triangle NOT affected by lighting ######
    no_light_count = triNoLight.current_size // 3
    if no_light_count:
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        vertices = triNoLight.vectors[:triNoLight.current_size].reshape(-1, 3)
        colors = triNoLight.colors[:triNoLight.color_current_size].reshape(-1, 4)

        glVertexPointer(3, GL_FLOAT, 0, vertices)
        glColorPointer(4, GL_FLOAT, 0, colors)
        glDrawArrays(GL_TRIANGLES, 0, no_light_count)
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

def appendTriangle(p1, p2, p3, color, normal, obj, tri: TriangleArray):

    if tri.freespaces:
        freepos = tri.freespaces.pop()
        tri.vectors[freepos:freepos + 3] = p1
        tri.vectors[freepos + 3:freepos + 6] = p2
        tri.vectors[freepos + 6:freepos + 9] = p3

        colorfreepos = int(freepos * 4 / 3)
        for i in range(3):
            tri.colors[colorfreepos + i * 4:colorfreepos + i * 4 + 4] = color

        for i in range(3):
            tri.normals[freepos + i:freepos + i + 3] = normal
            tri.normals[freepos + 3 + i:freepos + 6 + i] = normal
            tri.normals[freepos + 6 + i:freepos + 9 + i] = normal

        obj.pointer.pos = freepos

    else:
        obj.pointer.pos = tri.current_size + len(tri.tempVectors) * 3

        color = np.asarray(color, dtype=np.float32)
        normal = np.asarray(normal, dtype=np.float32)

        tri.tempVectors.append(np.asarray(p1, dtype=np.float32))
        tri.tempVectors.append(np.asarray(p2, dtype=np.float32))
        tri.tempVectors.append(np.asarray(p3, dtype=np.float32))
        for _ in range(3):
            tri.tempColors.append(color)
            tri.tempNormals.append(normal)


def is_close_vec(a, b, tol=1e-8):
    return np.all(np.abs(np.asarray(a) - np.asarray(b)) <= tol)


def norm2(vec):
    return np.sqrt(np.sum(vec * vec))


def _mesh_normal_is_horizontal(dep_var, p1, p2, p3):
    nx = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])
    ny = (p2[1] - p1[1]) * (p3[2] - p1[2]) - (p3[1] - p1[1]) * (p2[2] - p1[2])
    nz = (p2[0] - p1[0]) * (p3[2] - p1[2]) - (p3[0] - p1[0]) * (p2[2] - p1[2])
    if dep_var == 0:
        return abs(nx) < 1e-8 and abs(ny) < 1e-8 and (not abs(nz) < 1e-8)
    if dep_var == 1:
        return abs(nx) < 1e-8 and (not abs(ny) < 1e-8) and abs(nz) < 1e-8
    return (not abs(nx) < 1e-8) and abs(ny) < 1e-8 and abs(nz) < 1e-8


def _mesh_normal_is_horizontal_mask(dep_var, p1s, p2s, p3s):
    nx = (p2s[:, 0] - p1s[:, 0]) * (p3s[:, 1] - p1s[:, 1]) - (p3s[:, 0] - p1s[:, 0]) * (p2s[:, 1] - p1s[:, 1])
    ny = (p2s[:, 1] - p1s[:, 1]) * (p3s[:, 2] - p1s[:, 2]) - (p3s[:, 1] - p1s[:, 1]) * (p2s[:, 2] - p1s[:, 2])
    nz = (p2s[:, 0] - p1s[:, 0]) * (p3s[:, 2] - p1s[:, 2]) - (p3s[:, 0] - p1s[:, 0]) * (p2s[:, 2] - p1s[:, 2])
    eps = 1e-8
    if dep_var == 0:
        return (np.abs(nx) < eps) & (np.abs(ny) < eps) & (np.abs(nz) >= eps)
    if dep_var == 1:
        return (np.abs(nx) < eps) & (np.abs(ny) >= eps) & (np.abs(nz) < eps)
    return (np.abs(nx) >= eps) & (np.abs(ny) < eps) & (np.abs(nz) < eps)


def _grow_array(array, current_size, needed_size, current_capacity):
    if needed_size <= current_capacity:
        return array, current_capacity
    new_capacity = max(needed_size, current_capacity * 2)
    new_array = np.zeros(new_capacity, dtype=array.dtype)
    new_array[:current_size] = array[:current_size]
    return new_array, new_capacity


def append_surface_mesh(tri, scale, p1s, p2s, p3s, colors, dep_var, realpoint_flags):
    if p1s.shape[0] == 0:
        return

    horizontal = _mesh_normal_is_horizontal_mask(dep_var, p1s, p2s, p3s)
    keep = realpoint_flags | ~horizontal
    if not np.any(keep):
        return

    p1 = (p1s[keep] * scale).astype(np.float32, copy=False)
    p2 = (p2s[keep] * scale).astype(np.float32, copy=False)
    p3 = (p3s[keep] * scale).astype(np.float32, copy=False)
    colors = colors[keep]

    normals = np.cross(p2 - p1, p3 - p1)
    lens = np.linalg.norm(normals, axis=1, keepdims=True)
    np.divide(normals, lens, out=normals, where=lens != 0)
    normals = normals.astype(np.float32)

    vert_flat = np.column_stack([p1, p2, p3]).reshape(-1)
    color_flat = np.repeat(colors, 3, axis=0).reshape(-1)
    normal_flat = np.repeat(normals, 3, axis=0).reshape(-1)

    needed_vector = tri.current_size + vert_flat.size
    needed_color = tri.color_current_size + color_flat.size
    needed_normal = tri.normal_current_size + normal_flat.size

    tri.vectors, tri.capacity = _grow_array(tri.vectors, tri.current_size, needed_vector, tri.capacity)
    tri.colors, tri.color_capacity = _grow_array(tri.colors, tri.color_current_size, needed_color, tri.color_capacity)
    tri.normals, tri.normal_capacity = _grow_array(tri.normals, tri.normal_current_size, needed_normal, tri.normal_capacity)

    end_v = tri.current_size + vert_flat.size
    tri.vectors[tri.current_size:end_v] = vert_flat
    tri.current_size = end_v

    end_c = tri.color_current_size + color_flat.size
    tri.colors[tri.color_current_size:end_c] = color_flat
    tri.color_current_size = end_c

    end_n = tri.normal_current_size + normal_flat.size
    tri.normals[tri.normal_current_size:end_n] = normal_flat
    tri.normal_current_size = end_n


def append_colored_triangles(tri, scale, p1s, p2s, p3s, colors, objs=None):
    if p1s.shape[0] == 0:
        return

    p1 = (p1s * scale).astype(np.float32, copy=False)
    p2 = (p2s * scale).astype(np.float32, copy=False)
    p3 = (p3s * scale).astype(np.float32, copy=False)
    colors = np.asarray(colors, dtype=np.float32)

    normals = np.cross(p2 - p1, p3 - p1)
    lens = np.linalg.norm(normals, axis=1, keepdims=True)
    np.divide(normals, lens, out=normals, where=lens != 0)
    normals = normals.astype(np.float32)

    vert_flat = np.column_stack([p1, p2, p3]).reshape(-1)
    color_flat = np.repeat(colors, 3, axis=0).reshape(-1)
    normal_flat = np.repeat(normals, 3, axis=0).reshape(-1)

    needed_vector = tri.current_size + vert_flat.size
    needed_color = tri.color_current_size + color_flat.size
    needed_normal = tri.normal_current_size + normal_flat.size

    tri.vectors, tri.capacity = _grow_array(tri.vectors, tri.current_size, needed_vector, tri.capacity)
    tri.colors, tri.color_capacity = _grow_array(tri.colors, tri.color_current_size, needed_color, tri.color_capacity)
    tri.normals, tri.normal_capacity = _grow_array(tri.normals, tri.normal_current_size, needed_normal, tri.normal_capacity)

    start_pos = tri.current_size
    end_v = start_pos + vert_flat.size
    tri.vectors[start_pos:end_v] = vert_flat
    tri.current_size = end_v

    end_c = tri.color_current_size + color_flat.size
    tri.colors[tri.color_current_size:end_c] = color_flat
    tri.color_current_size = end_c

    end_n = tri.normal_current_size + normal_flat.size
    tri.normals[tri.normal_current_size:end_n] = normal_flat
    tri.normal_current_size = end_n

    if objs is not None:
        for i, obj in enumerate(objs):
            obj.pointer.pos = start_pos + i * 9


def build_triangle3d_primitives(line3d, point3d, flatline3d, triangle3d, width, height):

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
        segments = 24  # Increase for smoother cylinder

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
            
            tri = Triangle3D(v00, v01, v10, obj.color, obj.ableToUseLight)
            triangle3d.append(tri)
            obj._triangles.append(tri.pointer)
            tri = Triangle3D(v10, v01, v11, obj.color, obj.ableToUseLight)
            triangle3d.append(tri)
            obj._triangles.append(tri.pointer)


        # Optionally, cap the ends (disks)
        for i in range(1, segments - 1):
            tri = Triangle3D(circle1[0], circle1[i], circle1[i + 1], obj.color, obj.ableToUseLight)
            triangle3d.append(tri)
            obj._triangles.append(tri.pointer)

            tri = Triangle3D(circle2[0], circle2[i + 1], circle2[i], obj.color, obj.ableToUseLight)
            triangle3d.append(tri)
            obj._triangles.append(tri.pointer)


    for obj in point3d:
        
        # Render Point3D as a small sphere (approximated by triangles)

        center = obj.pos
        radius = 2* obj.radius / MAX_WIDTH_HEIGHT
        segments = 8

        # Draw a flat circle in the XY plane
        for i in range(segments):
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments

            v1 = center
            v2 = center + radius * np.array([np.cos(angle1), np.sin(angle1), 0])
            v3 = center + radius * np.array([np.cos(angle2), np.sin(angle2), 0])

            tri = Triangle3D(v1, v2, v3, obj.color, obj.ableToUseLight)
            obj._triangles.append(tri.pointer)
            triangle3d.append(tri)


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

        # Two triangles for the rectangle
        tri1 = Triangle3D(v1, v2, v3, obj.color, obj.ableToUseLight)
        triangle3d.append(tri1)
        obj._triangles.append(tri1.pointer)
        tri2 = Triangle3D(v3, v2, v4, obj.color, obj.ableToUseLight)
        triangle3d.append(tri2)
        obj._triangles.append(tri2.pointer)


def append_triangle3d_objects(triangle3d, scale, triLight, triNoLight, start_idx, end_idx):
    if start_idx >= end_idx:
        return

    batch = triangle3d[start_idx:end_idx]
    p1s = np.stack([obj.p1 for obj in batch]).astype(np.float32, copy=False)
    p2s = np.stack([obj.p2 for obj in batch]).astype(np.float32, copy=False)
    p3s = np.stack([obj.p3 for obj in batch]).astype(np.float32, copy=False)
    colors = np.stack([obj.color[:4] / 255.0 for obj in batch]).astype(np.float32, copy=False)
    light_mask = np.fromiter((obj.ableToUseLight for obj in batch), dtype=np.bool_, count=len(batch))

    for mask, target in ((True, triLight), (False, triNoLight)):
        sel = light_mask == mask
        if not np.any(sel):
            continue
        idxs = np.nonzero(sel)[0]
        objs = [batch[i] for i in idxs]
        append_colored_triangles(
            target,
            scale,
            p1s[sel],
            p2s[sel],
            p3s[sel],
            colors[sel],
            objs,
        )


def retrieveAndAppendTriangles(triangle3d, line3d, flatline3d, point3d, scale=0, width=0, height=0, triLight=None, triNoLight=None):
    if triLight is None:
        triLight = TriangleArray()
    if triNoLight is None:
        triNoLight = TriangleArray()

    build_triangle3d_primitives(line3d, point3d, flatline3d, triangle3d, width, height)
    append_triangle3d_objects(triangle3d, scale, triLight, triNoLight, 0, len(triangle3d))



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
    "point3d": Point3DObject,
    "triangle3d": Triangle3D,
    "line3d": Line3DObject,
    "flatline3d": FlatLine3DObject,
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
        self.totalframes = 0
        self.overlayFunction = None

        self.triLight = TriangleArray()
        self.triNoLight = TriangleArray()

        self.fpsimage = Image.new('RGBA', (0, 0))
        self.memimage = Image.new('RGBA', (0, 0))

        self.objects3d = dict()
        
        # Initialize profiler for performance measurements
        self.profiler = Profiler("OpenGLRender")

        self._gui_window = None
        self._gui_gl_context = None
        self._loading_start = time.time()
        self._loading_last_frame = 0.0
        self._loading_bootstrap = False

    @property
    def loading_screen_active(self):
        return self._gui_window is not None and self._loading_bootstrap

    def pumpGuiEvents(self):
        if self._gui_window is None:
            return

        sdl2.SDL_PumpEvents()
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event):
            if event.type == sdl2.SDL_QUIT:
                self.quit(self._gui_gl_context, self._gui_window)
                sys.exit(0)

    def _draw_gl_disc(self, cx, cy, radius, color, segments=14):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        r, g, b, a = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, color[3] / 255.0)
        glColor4f(r, g, b, a)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for seg in range(segments + 1):
            angle = 2.0 * pi * seg / segments
            glVertex2f(cx + cos(angle) * radius, cy + sin(angle) * radius)
        glEnd()

    def _draw_loading_frame(self):
        if self._gui_window is None:
            return

        sdl2.SDL_GL_MakeCurrent(self._gui_window, self._gui_gl_context)
        set_clear_color(self.backgroundColor)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.guiWidth, self.guiHeight, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)

        dot_count = min(5, len(kaxe_colors))
        dot_radius = 7
        dot_gap = 20
        bounce_height = 12
        speed = 5.5
        t = time.time() - self._loading_start

        row_width = (dot_count - 1) * dot_gap
        start_x = (self.guiWidth - row_width) / 2.0
        center_y = self.guiHeight / 2.0

        for i in range(dot_count):
            cx = start_x + i * dot_gap
            cy = center_y - sin(t * speed + i * 0.85) * bounce_height
            self._draw_gl_disc(cx, cy, dot_radius, kaxe_colors[i])

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glFinish()
        sdl2.SDL_GL_SwapWindow(self._gui_window)
        sdl2.SDL_ShowWindow(self._gui_window)
        sdl2.SDL_PumpEvents()

    def begin_loading_screen(self):
        if self._gui_window is None:
            return
        self._loading_bootstrap = True
        self._loading_start = time.time()
        self._loading_last_frame = 0.0
        self._draw_loading_frame()
        self.pumpGuiEvents()

    def end_loading_screen(self):
        self._loading_bootstrap = False

    def tick_loading(self, fps=60):
        if self._gui_window is None or not self._loading_bootstrap:
            return
        now = time.time()
        if now - self._loading_last_frame < 1.0 / fps:
            return
        self._loading_last_frame = now
        self._draw_loading_frame()
        self.pumpGuiEvents()

    def tick_loading_if_due(self, fps=60):
        self.tick_loading(fps=fps)

    def warmup_render_kernels(self):
        self.tick_loading()

    def showLoadingScreen(self):
        self._draw_loading_frame()
        self.pumpGuiEvents()

    def pixel(self, x, y, z):
        return self.camera.project(np.array((x,y,z))*self.SCL) + self.O


    def addMeshTriangles(self, p1s, p2s, p3s, colors, dep_var, realpoint_flags, use_light=True):
        scale = self.SCL * self.guiRatio
        target = self.triLight if use_light else self.triNoLight
        p1s = np.asarray(p1s, dtype=np.float32)
        p2s = np.asarray(p2s, dtype=np.float32)
        p3s = np.asarray(p3s, dtype=np.float32)
        colors = np.asarray(colors, dtype=np.float32)
        realpoint_flags = np.asarray(realpoint_flags, dtype=np.bool_)

        if self._loading_bootstrap:
            chunk_size = 150000
            for start in range(0, p1s.shape[0], chunk_size):
                end = min(start + chunk_size, p1s.shape[0])
                append_surface_mesh(
                    target,
                    scale,
                    p1s[start:end],
                    p2s[start:end],
                    p3s[start:end],
                    colors[start:end],
                    dep_var,
                    realpoint_flags[start:end],
                )
                self.tick_loading()
        else:
            append_surface_mesh(
                target,
                scale,
                p1s,
                p2s,
                p3s,
                colors,
                dep_var,
                realpoint_flags,
            )

    def add3DObject(self, obj):

        obj.hidden = True
        
        if obj.tp not in self.objects3d:
            self.objects3d[obj.tp] = []
        self.objects3d[obj.tp].append(obj)

        return obj

    def remove3DObject(self, obj):

        for pos in obj.getRemovableTriangles():
            self.removedObjects3d.append((obj, pos))
        return obj

    def _overlay_to_numpy(self, overlayImage):
        if isinstance(overlayImage, np.ndarray):
            overlay_np = overlayImage
        else:
            with self.profiler.measure("numpy_conversion"):
                overlay_np = to_numpy(overlayImage)

        with self.profiler.measure("overlay_crop"):
            if overlay_np.shape[1] > self.width or overlay_np.shape[0] > self.height:
                overlay_np = overlay_np[:self.height, :self.width]

        with self.profiler.measure("opencv_resize"):
            if overlay_np.shape[1] != self.guiWidth or overlay_np.shape[0] != self.guiHeight:
                overlay_np = cv2.resize(
                    overlay_np,
                    (self.guiWidth, self.guiHeight),
                    interpolation=cv2.INTER_LINEAR,
                )

        return overlay_np

    def loop(self):
        self.profiler.start("inner_loop")
        
        self.O = np.array((self.width//2, self.height//2)) # offset
        loading = self._loading_bootstrap
        if loading:
            self.tick_loading()

        with self.profiler.measure("overlay_function"):
            overlayImage = self.overlayFunction(rotation) # 24 ms

        if loading:
            self.tick_loading()

        with self.profiler.measure("refresh"):
            self.refresh()

        if loading:
            self.end_loading_screen()

        self.profiler.start("fps_calculation")
        self.frames += 1
        self.totalframes += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            
            self.fpsimage = fondi.MathText("\\text{FPS:}" + f" {self.frames}", 32, (255,0,0,255)).image

            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_in_mb = mem_info.rss / 1024 / 1024  # rss = Resident Set Size

            self.memimage = fondi.MathText("\\text{Memory:}"+ f" {mem_in_mb:.2f}"+ "\\text{MB}", 32, (255,0,0,255)).image

            self.frames = 0
            self.last_time = current_time

        if self.debugDrawOverlay:
            margin = 10
            if isinstance(overlayImage, np.ndarray):
                fps_np = np.asarray(self.fpsimage)
                mem_np = np.asarray(self.memimage)
                fh, fw = fps_np.shape[:2]
                mh, mw = mem_np.shape[:2]
                overlayImage[margin:margin + fh, margin:margin + fw] = fps_np
                overlayImage[margin + fh + margin:margin + fh + margin + mh, margin:margin + mw] = mem_np
            else:
                overlayImage.paste(self.fpsimage, (margin, margin))
                overlayImage.paste(self.memimage, (margin, self.fpsimage.height+margin))
        self.profiler.end("fps_calculation")

        with self.profiler.measure("display_render"):
            display(self.triLight, self.triNoLight, self.backgroundColor)


        if overlayImage is not None:
            with self.profiler.measure("overlay_processing"):
                overlay_np = self._overlay_to_numpy(overlayImage)

                with self.profiler.measure("opengl_overlay"):
                    h, w = overlay_np.shape[:2]
                    x_offset = (self.guiWidth - w) // 2
                    y_offset = (self.guiHeight - h) // 2

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
                    glRasterPos2i(x_offset, y_offset)
                    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, np.flipud(overlay_np))
                    glEnable(GL_DEPTH_TEST)
                    glDisable(GL_BLEND)
                    glPopMatrix()
                    glMatrixMode(GL_PROJECTION)
                    glPopMatrix()
                    glMatrixMode(GL_MODELVIEW)


        self.profiler.end("inner_loop")    
        
        

    def refresh(self):

        with self.profiler.measure("clear_triangles"):
            self.count += 1
            if self.skipObjectUpdate:
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

        with self.profiler.measure('retrieve_and_append'):
            scale = self.SCL * self.guiRatio

            kwargs = {}
            for key in typesRegistry:
                kwargs[key] = self.objects3d.get(key, [])

            if self._loading_bootstrap:
                self.tick_loading()
                with self.profiler.measure('build_primitives'):
                    build_triangle3d_primitives(
                        kwargs["line3d"],
                        kwargs["point3d"],
                        kwargs["flatline3d"],
                        kwargs["triangle3d"],
                        self.width,
                        self.height,
                    )
                self.tick_loading()
                triangle_count = len(kwargs["triangle3d"])
                batch_size = 2000
                with self.profiler.measure('append_triangles'):
                    for start in range(0, triangle_count, batch_size):
                        end = min(start + batch_size, triangle_count)
                        append_triangle3d_objects(
                            kwargs["triangle3d"],
                            scale,
                            self.triLight,
                            self.triNoLight,
                            start,
                            end,
                        )
                        if start == 0:
                            self.tick_loading()
            else:
                with self.profiler.measure('build_primitives'):
                    build_triangle3d_primitives(
                        kwargs["line3d"],
                        kwargs["point3d"],
                        kwargs["flatline3d"],
                        kwargs["triangle3d"],
                        self.width,
                        self.height,
                    )
                with self.profiler.measure('append_triangles'):
                    append_triangle3d_objects(
                        kwargs["triangle3d"],
                        scale,
                        self.triLight,
                        self.triNoLight,
                        0,
                        len(kwargs["triangle3d"]),
                    )

        with self.profiler.measure("clear_objects"):
            self.objects3d.clear()
        
        
        with self.profiler.measure("finalize_append"):
            if self._loading_bootstrap:
                self.tick_loading()
            self.triLight.finalizeAppend()
            if self._loading_bootstrap:
                self.tick_loading()
            self.triNoLight.finalizeAppend()
            if self._loading_bootstrap:
                self.tick_loading()
        
        # Reset arrays for next frame (keep capacity but reset size)
        # Note: Comment this out if you want to accumulate triangles across frames
        # self.triLight.reset()
        # self.triNoLight.reset()


    def prepareGuiWindow(self):
        if self._gui_window is not None:
            return

        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError("SDL_Init Error: " + str(sdl2.SDL_GetError()))

        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 1)

        window = sdl2.SDL_CreateWindow(
            b"Kaxe",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self.guiWidth,
            self.guiHeight,
            sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_HIDDEN,
        )
        if not window:
            raise RuntimeError("SDL_CreateWindow Error: " + str(sdl2.SDL_GetError()))

        self.__setIcon__(window)
        gl_context = sdl2.SDL_GL_CreateContext(window)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        init_display_state(self.backgroundColor)

        self._gui_window = window
        self._gui_gl_context = gl_context

    def presentGuiWindow(self):
        self.begin_loading_screen()

    def quit(self, gl_context, window):
        sdl2.SDL_GL_DeleteContext(gl_context)
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()


    def gui(self, overlay=None, plot=None):
        global dragging, last_mouse

        if plot is not None and getattr(plot, "_defer_gui_prep", False):
            plot.render.warmup_render_kernels()
            plot.__complete_deferred_start__()
            overlay = plot.__make_overlay__()

        self.overlayFunction = overlay
        
        dragging = [False]
        last_mouse = [0, 0]

        if self._gui_window is None:
            if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
                print("SDL_Init Error:", sdl2.SDL_GetError())
                return 1

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

            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            init_display_state(self.backgroundColor)
        else:
            window = self._gui_window
            gl_context = self._gui_gl_context
            sdl2.SDL_GL_MakeCurrent(window, gl_context)
            sdl2.SDL_ShowWindow(window)

        if self._loading_bootstrap:
            self.tick_loading()

        idle = False
        is_fullscreen = False
        running = True
        event = sdl2.SDL_Event()

        lasttime = time.time()
        dt = 0
        comma_rotation = 0

        while running:
            
            self.profiler.start("main_loop")

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

            self.profiler.end("main_loop")

            sdl2.SDL_GL_SwapWindow(window)
            
            # Print profiler report every 60 frames for performance analysis
            if self.totalframes % 120 == 0 and self.totalframes > 0:
                print(self.profiler.get_report(sort_by='average'))
                print("=" * 50)
                self.profiler.reset()  # Reset to start fresh measurements
            

            


    def get_performance_report(self, sort_by: str = 'duration') -> str:
        """Get a detailed performance report from the profiler."""
        return self.profiler.get_report(sort_by=sort_by)
    
    def export_performance_data(self, filename: str) -> None:
        """Export profiler data to CSV file."""
        self.profiler.export_csv(filename)
    
    def reset_profiler(self) -> None:
        """Reset profiler measurements."""
        self.profiler.reset()

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
        init_display_state(self.backgroundColor)

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
