
from .camera import Camera
from PIL import Image
import math
from numpy import array, empty
from typing import Union
import tqdm

class Render:
    def __init__(self, width=500, height=500, cameraAngle:Union[tuple, list]=(0,0), w:int=None):
        self.width = width
        self.height = height

        self.camera = Camera()
        if w: self.camera.w = w
        self.image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        self.image = array(self.image)
        self.camera.satelite(*cameraAngle)

        self.backgroundColor = (255,255,255,0)

        self.objects3d = []

        self.SCL = self.width//10 # pixel scale (tilfældigt)
        self.SCL = 1 # pixel scale (tilfældigt)
        self.O = array((self.width//2, self.height//2)) # offset

    
    def pixel(self, x, y, z):
        return self.camera.project((x,y,z)) * self.SCL + self.O


    def add3DObject(self, obj):
        self.objects3d.append(obj)
        return obj

    
    def drawv2(self):
        self.zbuffer = empty((self.width, self.height))
        self.zbuffer.fill(math.inf)

        # stores index for material
        self.abuffer = empty((self.width, self.height))
        self.abuffer.fill(-1)

        bar = tqdm.tqdm(total=len(self.objects3d), desc="3D compute")
        for index, obj in enumerate(self.objects3d):
            obj.drawTozBuffer(self, index)
            bar.update()
        bar.close()
        
        # draw to image
        bar = tqdm.tqdm(total=self.width*self.height, desc="3D Draw")
        for x in range(self.width):
            for y in range(self.height):

                i = self.abuffer[y][x]
                if i >= 0:
                    self.image[y][x] = self.objects3d[int(self.abuffer[y][x])].getColor(self, x,y)
                else:
                    self.image[y][x] = self.backgroundColor

            bar.update(self.height)
        bar.close()


    def render(self, objects=[]):

        # get 3dobjects from objects
        for obj in objects:
            obj.render(self)

        # sort and draw?
        self.drawv2()

        self.image = Image.fromarray(self.image)
        self.image = self.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        self.abuffer = []
        self.zbuffer = []

        return self.image
