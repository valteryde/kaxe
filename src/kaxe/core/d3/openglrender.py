
from OpenGL.GL import *
from OpenGL.error import GLError
import os
from stl import mesh
import numpy as np
import time
from typing import Union
from .camera import Camera
from PIL import Image
from .objects.triangle import Triangle, Triangle3D
from .objects.line import Line3D, FlatLine3D, Line3DObject, FlatLine3DObject
from .objects.point import Point3D, Point3DObject
import psutil
process = psutil.Process()
import sys
import sdl2
import sdl2.ext
import sdl2.video
import ctypes
from ..fileloader import loadFile
import cv2
from ..profiler import Profiler
from ..helper import to_numpy
from .hud import ViewportHud

rotation = [330, 290]
AUTO_SPIN_MAX_SPEED = 30.0   # deg/s
AUTO_SPIN_RAMP_TAU = 0.9     # s, exponential ease-in time constant

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
MSAA_SAMPLES = 4


def configure_gl_context_attributes():
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 1)
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_MULTISAMPLEBUFFERS, 1)
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_MULTISAMPLESAMPLES, MSAA_SAMPLES)


def enable_multisample():
    glEnable(GL_MULTISAMPLE)


def gui_window_flags():
    return (
        sdl2.SDL_WINDOW_OPENGL
        | sdl2.SDL_WINDOW_RESIZABLE
        | sdl2.SDL_WINDOW_HIDDEN
    )


def _cleanup_offscreen_resources(resources):
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    for kind, obj_id in reversed(resources):
        if kind == "fbo":
            glDeleteFramebuffers(1, [obj_id])
        elif kind == "tex":
            glDeleteTextures(1, [obj_id])
        elif kind == "rbo":
            glDeleteRenderbuffers(1, [obj_id])


def _setup_offscreen_framebuffers(width, height):
    resources = []
    resolve_fbo = glGenFramebuffers(1)
    resources.append(("fbo", resolve_fbo))
    glBindFramebuffer(GL_FRAMEBUFFER, resolve_fbo)

    tex = glGenTextures(1)
    resources.append(("tex", tex))
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glFramebufferTexture2D(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0
    )

    resolve_depth = glGenRenderbuffers(1)
    resources.append(("rbo", resolve_depth))
    glBindRenderbuffer(GL_RENDERBUFFER, resolve_depth)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
    glFramebufferRenderbuffer(
        GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, resolve_depth
    )

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        _cleanup_offscreen_resources(resources)
        raise RuntimeError("Resolve framebuffer is not complete")

    draw_fbo = resolve_fbo

    if MSAA_SAMPLES > 1:
        try:
            ms_fbo = glGenFramebuffers(1)
            ms_color = glGenRenderbuffers(1)
            ms_depth = glGenRenderbuffers(1)
            ms_resources = [
                ("fbo", ms_fbo),
                ("rbo", ms_color),
                ("rbo", ms_depth),
            ]

            glBindFramebuffer(GL_FRAMEBUFFER, ms_fbo)
            glBindRenderbuffer(GL_RENDERBUFFER, ms_color)
            glRenderbufferStorageMultisample(
                GL_RENDERBUFFER, MSAA_SAMPLES, GL_RGBA8, width, height
            )
            glFramebufferRenderbuffer(
                GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, ms_color
            )
            glBindRenderbuffer(GL_RENDERBUFFER, ms_depth)
            glRenderbufferStorageMultisample(
                GL_RENDERBUFFER, MSAA_SAMPLES, GL_DEPTH_COMPONENT, width, height
            )
            glFramebufferRenderbuffer(
                GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, ms_depth
            )

            if glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE:
                draw_fbo = ms_fbo
                resources.extend(ms_resources)
        except (AttributeError, GLError):
            glBindFramebuffer(GL_FRAMEBUFFER, resolve_fbo)

    return draw_fbo, resolve_fbo, resources


def _resolve_offscreen_framebuffer(draw_fbo, resolve_fbo, width, height):
    if draw_fbo == resolve_fbo:
        glBindFramebuffer(GL_FRAMEBUFFER, resolve_fbo)
        return

    glBindFramebuffer(GL_READ_FRAMEBUFFER, draw_fbo)
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, resolve_fbo)
    glBlitFramebuffer(
        0, 0, width, height,
        0, 0, width, height,
        GL_COLOR_BUFFER_BIT,
        GL_NEAREST,
    )
    glBindFramebuffer(GL_FRAMEBUFFER, resolve_fbo)


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


def _triangle_cross_normals(p1s, p2s, p3s):
    ax = p2s[:, 0] - p1s[:, 0]
    ay = p2s[:, 1] - p1s[:, 1]
    az = p2s[:, 2] - p1s[:, 2]
    bx = p3s[:, 0] - p1s[:, 0]
    by = p3s[:, 1] - p1s[:, 1]
    bz = p3s[:, 2] - p1s[:, 2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    return nx, ny, nz


def _mesh_normal_is_horizontal(dep_var, p1, p2, p3):
    ax, ay, az = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    bx, by, bz = p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    if dep_var == 0:
        return np.isclose(nx, 0) and np.isclose(ny, 0) and not np.isclose(nz, 0)
    if dep_var == 1:
        return np.isclose(nx, 0) and not np.isclose(ny, 0) and np.isclose(nz, 0)
    return not np.isclose(nx, 0) and np.isclose(ny, 0) and np.isclose(nz, 0)


def _mesh_normal_is_horizontal_mask(dep_var, p1s, p2s, p3s):
    nx, ny, nz = _triangle_cross_normals(p1s, p2s, p3s)
    if dep_var == 0:
        return np.isclose(nx, 0) & np.isclose(ny, 0) & ~np.isclose(nz, 0)
    if dep_var == 1:
        return np.isclose(nx, 0) & ~np.isclose(ny, 0) & np.isclose(nz, 0)
    return ~np.isclose(nx, 0) & np.isclose(ny, 0) & np.isclose(nz, 0)


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


def motion_func(x, y):
    if dragging[0]:
        mouse_drag(x, y)

typesRegistry = {
    "point3d": Point3DObject,
    "triangle3d": Triangle3D,
    "line3d": Line3DObject,
    "flatline3d": FlatLine3DObject,
}


class OpenGLRender:
    def __init__(
        self,
        width,
        height,
        cameraAngle: Union[tuple, list] = (0, 0),
        w: int = None,
        light: list = [0, 0, 0],
        backgroundColor=(255, 255, 255, 255),
        guiwidth: int = 1000,
        guiheight: int = 750,
    ):
        self.width = width
        self.height = height

        self.guiRatio = min(guiwidth / height, guiheight / width, 1)

        self.guiWidth = int(round(width * self.guiRatio))
        self.guiHeight = int(round(height * self.guiRatio))

        self.skipObjectUpdate = False
        self.count = 0
        self.showHud = False
        self.debugDrawOverlay = False
        self.profiler_report = False
        self.autoRotate = False
        self.hud = ViewportHud()

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

        self._hud_fps = 0

        self.objects3d = dict()
        
        # Initialize profiler for performance measurements
        self.profiler = Profiler("OpenGLRender")

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

    def _draw_screen_overlay(self, overlay_np, x, y):
        h, w = overlay_np.shape[:2]

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
        glRasterPos2i(x, y)
        glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, np.flipud(overlay_np))
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def loop(self):
        self.profiler.start("inner_loop")
        
        self.O = np.array((self.width//2, self.height//2)) # offset

        with self.profiler.measure("overlay_function"):
            overlayImage = self.overlayFunction(rotation) # 24 ms

        with self.profiler.measure("refresh"):
            self.refresh()

        self.profiler.start("fps_calculation")
        self.frames += 1
        self.totalframes += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_in_mb = mem_info.rss / 1024 / 1024
            self._hud_fps = self.frames
            self.hud.update_stats(self._hud_fps, mem_in_mb)
            self.frames = 0
            self.last_time = current_time

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
                    self._draw_screen_overlay(overlay_np, x_offset, y_offset)

        if self.showHud or self.debugDrawOverlay:
            with self.profiler.measure("hud_overlay"):
                hud_np = self.hud.build(
                    (rotation[0], rotation[1]),
                    self.autoRotate,
                    self.guiWidth,
                    self.guiHeight,
                )
                self._draw_screen_overlay(hud_np, 0, 0)

        self.profiler.end("inner_loop")    
        
        

    def refresh(self):

        with self.profiler.measure("clear_triangles"):
            self.count += 1
            if self.skipObjectUpdate:
                return

            for obj, pos in self.removedObjects3d:
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
            self.triLight.finalizeAppend()
            self.triNoLight.finalizeAppend()

    def quit(self, gl_context, window):
        sdl2.SDL_GL_DeleteContext(gl_context)
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()


    def gui(self, overlay=None, plot=None):
        global dragging, last_mouse

        self.overlayFunction = overlay
        
        dragging = [False]
        last_mouse = [0, 0]

        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            print("SDL_Init Error:", sdl2.SDL_GetError())
            return 1

        configure_gl_context_attributes()

        window = sdl2.SDL_CreateWindow(
            b"Kaxe",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self.guiWidth,
            self.guiHeight,
            gui_window_flags(),
        )

        self.__setIcon__(window)

        if not window:
            print("SDL_CreateWindow Error:", sdl2.SDL_GetError())
            return 1

        gl_context = sdl2.SDL_GL_CreateContext(window)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        enable_multisample()
        init_display_state(self.backgroundColor)

        if plot is not None:
            plot.__complete_gui_prep__()

        reshape(self.guiWidth, self.guiHeight)
        self.loop()
        sdl2.SDL_GL_SwapWindow(window)
        sdl2.SDL_ShowWindow(window)

        idle = False
        is_fullscreen = False
        running = True
        event = sdl2.SDL_Event()

        lasttime = time.time()
        dt = 0
        auto_spin_speed = 0.0

        while running:
            
            self.profiler.start("main_loop")

            dt = min((time.time() - lasttime) * 1000, 50.0)
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
                        auto_spin_speed = 0.0
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
                dt_sec = dt / 1000.0
                blend = 1.0 - np.exp(-dt_sec / AUTO_SPIN_RAMP_TAU)
                auto_spin_speed += (AUTO_SPIN_MAX_SPEED - auto_spin_speed) * blend
                rotation[0] += auto_spin_speed * dt_sec
            else:
                auto_spin_speed = 0.0

            self.autoRotate = idle

            if running:
                reshape(self.guiWidth, self.guiHeight)
                self.loop()

            self.profiler.end("main_loop")

            sdl2.SDL_GL_SwapWindow(window)
            
            # Print profiler report periodically when explicitly enabled
            if self.profiler_report and self.totalframes % 120 == 0 and self.totalframes > 0:
                print(self.profiler.get_report(sort_by='average'))
                print("=" * 50)
                self.profiler.reset()
            

            


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

        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError("SDL_Init Error: " + str(sdl2.SDL_GetError()))

        configure_gl_context_attributes()

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
        enable_multisample()
        init_display_state(self.backgroundColor)

        draw_fbo, resolve_fbo, resources = _setup_offscreen_framebuffers(
            self.width, self.height
        )

        glBindFramebuffer(GL_FRAMEBUFFER, draw_fbo)
        reshape(self.width, self.height)
        self.loop()
        _resolve_offscreen_framebuffer(draw_fbo, resolve_fbo, self.width, self.height)

        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        pixels = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGBA", (self.width, self.height), pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        _cleanup_offscreen_resources(resources)
        sdl2.SDL_GL_DeleteContext(gl_context)
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()

        self.image = image
        return self.image
