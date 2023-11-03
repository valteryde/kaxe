
from PIL import Image, ImageDraw, ImageFont
import pyglet as pg
from .styles import *
import os
from .shapes import *

basePath = os.path.join(os.path.split(os.path.abspath(__name__))[0], 'kaxe')

class Text(Shape):
    
    def __init__(self, text:str, x:int, y:int, fontSize:int=16, color=(0,0,0,255), rotate:int=0, batch:Batch=None, anchor_x:str="center", anchor_y:str="center", *args, **kwargs):
        self.batch = batch
        self.x = x
        self.y = y
        self.color = color
        self.rotate = rotate
        self.fontSize = fontSize
        self.text = text
        super().__init__()
        if batch: batch.add(self)

        # make pil image
        winSize = (self.fontSize*2*len(text),self.fontSize*2*len(text))
        pilImage = Image.new("RGBA", winSize, color=(0,0,0,0))
        draw = ImageDraw.Draw(pilImage)
        font = ImageFont.truetype(os.path.join(basePath,"resource","computer-modern-family","cmu.serif-roman.ttf"), self.fontSize)
        #draw.fontmode = "1" # this apparently sets (anti)aliasing.
        draw.text((winSize[0]//2, winSize[1]//2), text, color, font=font)
        pilImage = pilImage.rotate(self.rotate)
        self.pilImage = pilImage.crop(pilImage.getbbox())
        
        # pilImage = pilImage.transpose(Image.FLIP_TOP_BOTTOM)
        
        self.pilImage.save('.__textImage__.png')
        self.img = pg.image.load('.__textImage__.png')

        self.width = self.img.width
        self.height = self.img.height

        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.__offset__ = [0,0]
        if anchor_x == "center":
            self.__offset__[0] = self.pilImage.width/2
        if anchor_y == "center":
            self.__offset__[1] = self.pilImage.height/2

        os.remove('.__textImage__.png')

        if rotate > 0:
            pass


    def __repr__(self):
        return '{}'.format(self.text)


    def getBoundingBox(self):
        return [self.width, self.height]


    def drawPyglet(self):
        pass


    def drawPillow(self, surface):
        [self.y] = flipHorizontal(surface, self.y+self.__offset__[1])
        blitImageToSurface(surface, self.pilImage, (int(self.x)-self.__offset__[0], int(self.y)))


def getTextDimension(text, fontSize ,*args, **kwargs):
    label = Text(*args, text=str(text), x=0, y=0, fontSize=fontSize, **kwargs)
    return label.width, label.height
