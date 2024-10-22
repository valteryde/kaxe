
from core.camera import Camera
from core.objects.line import Line3D
from core.objects.triangle import Triangle
from core.objects.point import  Point3D
from core.helper import rc
from core.render import Render

class Axis:

    def __init__(self):
        self.x = Line3D( (0,0,0), (8,0,0), (0,0,0,255) ) #x rød
        self.y = Line3D( (0,0,0), (0,8,0), (0,0,0,255))  #y grøn
        self.z = Line3D( (0,0,0), (0,0,8), (0,0,0,255) ) #z blå
    
    def render(self, render:Render):
        render.add3DObject(self.x)
        render.add3DObject(self.y)
        render.add3DObject(self.z)


class Rectangle:
    def __init__(self, x, y, z, width, height):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height


    def render(self, render:Render):
        cam = render.camera

        p1 = (self.x, self.y, self.z)
        p2 = (self.x+self.width, self.y, self.z)
        p3 = (self.x, self.y+self.height, self.z)
        p4 = (self.x+self.width, self.y+self.height, self.z)

        render.add3DObject(Triangle(p1, p2, p3, color=rc()))
        render.add3DObject(Triangle(p3, p2, p4, color=rc()))
        
        p1 = cam.project(p1)
        p2 = cam.project(p2)
        p3 = cam.project(p3)
        p4 = cam.project(p4)

        # drawDot(render.image, p1)
        # drawDot(render.image, p2)
        # drawDot(render.image, p3)
        # drawDot(render.image, p4)


class Box:

    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth


    def render(self, render:Render):

        p1 = (self.x, self.y, self.z)
        p2 = (self.x+self.width, self.y, self.z)
        p3 = (self.x, self.y+self.height, self.z)
        p4 = (self.x, self.y, self.z+self.depth)
        p5 = (self.x+self.width, self.y+self.height, self.z)
        p6 = (self.x+self.width, self.y, self.z+self.depth)
        p7 = (self.x+self.width, self.y+self.height, self.z+self.depth)
        p8 = (self.x, self.y+self.height, self.z+self.depth)

        render.add3DObject(Triangle(p1, p2, p5, color=rc()))
        render.add3DObject(Triangle(p1, p2, p5, color=rc()))
        #render.add3DObject(Triangle(p3, p1, p5, color=rc()))

        render.add3DObject(Triangle(p1, p3, p4, color=rc()))
        render.add3DObject(Triangle(p3, p4, p8, color=rc()))

        render.add3DObject(Triangle(p1, p2, p4, color=rc()))
        render.add3DObject(Triangle(p2, p4, p6, color=rc()))

        render.add3DObject(Triangle(p4, p6, p7, color=rc()))
        render.add3DObject(Triangle(p7, p4, p8, color=rc()))

        render.add3DObject(Triangle(p2, p5, p6, color=rc()))
        render.add3DObject(Triangle(p6, p5, p7, color=rc()))
        
        render.add3DObject(Triangle(p3, p5, p7, color=rc()))
        render.add3DObject(Triangle(p3, p7, p8, color=rc()))
        
        # p1 = cam.project(p1)
        # p2 = cam.project(p2)
        # p3 = cam.project(p3)
        # p4 = cam.project(p4)
        # p5 = cam.project(p5)
        # p6 = cam.project(p6)
        # p7 = cam.project(p7)
        # p8 = cam.project(p8)

        # drawDot(render.image, p1)
        # drawDot(render.image, p2)
        # drawDot(render.image, p3)
        # drawDot(render.image, p4)
        # drawDot(render.image, p5)
        # drawDot(render.image, p6)
        # drawDot(render.image, p7)
        # drawDot(render.image, p8)

        # drawLine(render.image, p1, p2) #1
        # drawLine(render.image, p2, p5) #2
        # drawLine(render.image, p2, p6) #3     
        # drawLine(render.image, p5, p7) #4
        # drawLine(render.image, p6, p7) #5
        # drawLine(render.image, p1, p3) #6
        # drawLine(render.image, p3, p8) #7
        # drawLine(render.image, p1, p4) #8
        # drawLine(render.image, p4, p6) #9
        # drawLine(render.image, p7, p8) #10
        # drawLine(render.image, p4, p8) #11
        # drawLine(render.image, p3, p5) #12


class Point:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius


    def render(self, render:Render):
        render.add3DObject(Point3D(self.x, self.y, self.z, self.radius, color=rc()))
    

class PointPlane:

    def __init__(self, points:list):
        self.points = points
        self.pointRadius = 2

    def render(self, render:Render):
        
        for x, y, z in self.points:
            render.add3DObject(Point3D(x, y, z, self.pointRadius, color=rc()))
