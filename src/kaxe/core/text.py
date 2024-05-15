
from PIL import Image
from .styles import *
import os
from .shapes import *
from fondi import MathText
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.rotate.html
from scipy.ndimage import rotate as rotate_image
import numpy as np


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

        # translate str "$math$ + normaltext" to "math + \\text{normaltext}"
        res = ''
        open_ = 0
        word = ''
        for char in text:
            if char == '$' and open_:
                open_ = False
                continue
            elif char == '$' and not open_:
                open_ = True
                if len(word) > 0: res += '\\text{' + word + '}'
                word = ''
                continue
        
            if open_:
                res += char
            else:
                word += char

        if len(word) > 0: res += '\\text{' + word + '}'

        text = res

        # make pil image
        pilImage = MathText(text, self.fontSize, self.color).image
        
        iarr = np.array(pilImage)
        self.pilImage = Image.fromarray(rotate_image(iarr, self.rotate))

        self.img = self.pilImage

        self.width = self.img.width
        self.height = self.img.height

        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.__offset__ = [0,0]
        if anchor_x == "center":
            self.__offset__[0] = self.pilImage.width/2
        if anchor_y == "center":
            self.__offset__[1] = self.pilImage.height/2

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
