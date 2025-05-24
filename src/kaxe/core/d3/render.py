
"""
Alpha compsite is created partly following this guide
https://learnwebgl.brown37.net/11_advanced_rendering/alpha_blending.html
"""

from .camera import Camera
from PIL import Image
import math
from numpy import array, empty
from typing import Union
import tqdm
import numpy as np
from ..window import settings

class Render:
    def __init__(self, width=500, height=500, cameraAngle:Union[tuple, list]=(0,0), w:int=None, light=[0,0,0], backgroundColor=(255,255,255,255)):
        self.width = width
        self.height = height
        self.lightDirection = np.array([float(i) for i in light])
        self.useLight = any(light)

        self.backgroundColor = backgroundColor
        self.camera = Camera()
        if w: self.camera.w = w
        self.image = Image.new('RGBA', (self.width, self.height), self.backgroundColor)
        self.image = array(self.image)
        self.camera.satelite(*cameraAngle)

        self.objects3d = []

        self.SCL = self.width//10 # pixel scale (tilfældigt)
        self.SCL = 1 # pixel scale (tilfældigt)
        self.O = array((self.width//2, self.height//2)) # offset

    
    def pixel(self, x, y, z):
        return self.camera.project((x,y,z)) * self.SCL + self.O


    def add3DObject(self, obj):
        self.objects3d.append(obj)
        return obj

    
    def draw(self):
        self.zbuffer = empty((self.width, self.height))
        self.zbuffer.fill(math.inf)

        # sort based on if contains alpha
        transparent = list(filter(lambda obj: obj.color[3] != 255, self.objects3d))
        nontransparent = list(filter(lambda obj: obj.color[3] == 255, self.objects3d))
        
        transparent.sort(key=lambda obj: obj.getZ(self.camera.R))
        
        self.objects3d = nontransparent + transparent

        
        showProgressBar = not settings["removeInfo"]
        if showProgressBar: bar = tqdm.tqdm(total=len(self.objects3d), desc="3D compute")
        for obj in self.objects3d:
            obj.draw(self)
            if showProgressBar: bar.update()
        if showProgressBar: bar.close()

    def render(self, objects=[]):

        # get 3dobjects from objects
        for obj in objects:
            obj.render(self)

        self.draw()

        self.image = Image.fromarray(self.image)
        self.image = self.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        self.abuffer = []
        self.zbuffer = []

        return self.image
