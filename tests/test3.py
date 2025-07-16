from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import os
from stl import mesh
import numpy as np
import time
from math import radians, sin, cos

rotation = [0, 0]

def load_obj(filename):
    # Load STL file using numpy-stl
    m = mesh.Mesh.from_file(filename)

    # Center and scale the mesh to fit in a unit cube at the origin
    min_ = np.min(m.vectors, axis=(0, 1))
    max_ = np.max(m.vectors, axis=(0, 1))
    center = (min_ + max_) / 2
    scale = 1.0 / np.max(max_ - min_) * 4
    m.vectors = (m.vectors - center) * scale

    def draw():
        # Example: assign a color per vertex (repeat or random for demonstration)
        num_vertices = m.vectors.reshape(-1, 3).shape[0]
        # Example: cycle through a list of colors
        color_list = np.array([
            [1., 0., 0.],  # light blue
        ], dtype=np.float32)
        colors = np.tile(color_list, (num_vertices // len(color_list) + 1, 1))[:num_vertices]

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        vertices = m.vectors.reshape(-1, 3).astype(np.float32)
        glVertexPointer(3, GL_FLOAT, 0, vertices)
        glColorPointer(3, GL_FLOAT, 0, colors)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    return draw

model_draw = load_obj("tests/Eiffel_tower_sample.STL")

def display():
    glClearColor(1.0, 1.0, 1.0, 1.0); #RGBA

    # Set light color
    light_ambient = [1.0, 1.0, 1.0, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1]
    light_specular = [1.0, 1.0, 1.0, 1]
    # glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    # glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    # glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    # Set material properties
    mat_specular = [1.0, 0.0, 0.0, 1.0]
    mat_shininess = [0.0]
    # glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    # glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
    # Set light position fixed in world space (not affected by model rotation)
    light_pos = [0.0, 0.0, 10.0, 0.0]
    # glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -10)
    glRotatef(rotation[0], 1, 0, 0)
    glRotatef(rotation[1], 0, 1, 0)
    model_draw()
    glutSwapBuffers()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def mouse_drag(x, y):
    # GLUT does not provide dx, dy directly, so store last position
    global last_mouse
    if last_mouse is not None:
        dx = x - last_mouse[0]
        dy = y - last_mouse[1]
        rotation[0] += dy
        rotation[1] += dx
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

if __name__ == "__main__":

    dragging = [False]
    last_mouse = [0, 0]

    def close():
        print("Closing window...")
        os._exit(0)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(720, 480)
    glutCreateWindow(b"PyOpenGL Cube")

    glEnable(GL_DEPTH_TEST)
    # glEnable(GL_LIGHTING)
    # glEnable(GL_LIGHT0)

    glutDisplayFunc(display)
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
