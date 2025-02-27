
from PIL import Image
from .styles import *
import os
from .shapes import *
from fondi import MathText
import numpy as np


class Text(Shape):
    
    def __init__(self, 
                 text:str, 
                 x:int, 
                 y:int, 
                 fontSize:int=16, 
                 color=(0,0,0,255), 
                 rotate:int=0, 
                 batch:Batch=None, 
                 anchor_x:str="center", 
                 anchor_y:str="center", *args, **kwargs
        ):
        
        self.batch = batch
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
        # width = pilImage.width 
        # height = pilImage.height 

        self.img = pilImage.rotate(self.rotate, expand=True)

        # newCenterFromTopLeft = np.array([[math.cos(self.rotate), -math.sin(self.rotate)], [math.sin(self.rotate), math.cos(self.rotate)]]) @ np.array((width/2, height/2))

        self.width = self.img.width
        self.height = self.img.height

        # revert positions from rotation
        # self.x -= newCenterFromTopLeft[0] - pilImage.width
        # self.y -= newCenterFromTopLeft[1] - pilImage.height

        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        
        if anchor_x == "center":
            self.__leftTop__ = [x - self.width/2, None]
            self.__center__ = [x, None]
        else:
            self.__leftTop__ = [x, None]
            self.__center__ = [x + self.width/2, None]

        if anchor_y == "center":
            self.__leftTop__[1] = y - self.height/2
            self.__center__[1] = y
        else:
            self.__leftTop__[1] = y
            self.__center__[1] = y + self.height/2


    def __repr__(self):
        return '<Text: {}>'.format(self.text)


    def getBoundingBox(self):
        # returns pos and size (idk why)
        return [
            int(self.__leftTop__[0]), 
            int(self.__leftTop__[1]), 
            int(self.width), 
            int(self.height)
        ]


    def getCenterPos(self):
        return self.__center__

    
    def getLeftTopPos(self):
        return self.__leftTop__

    
    def setLeftTopPos(self, x, y):
        self.__leftTop__[0] = x
        self.__leftTop__[1] = y
        self.__center__[0] = self.__leftTop__[0] - self.width/2 # føler ikke det burde være sådan her
        self.__center__[1] = self.__leftTop__[1] - self.height/2


    def drawPillow(self, surface):
        [y] = flipHorizontal(surface, self.__center__[1] + self.height/2)
        blitImageToSurface(surface, self.img, (self.__leftTop__[0], y))


    def push(self, x, y):
        if np.isnan(x) or np.isnan(y):
            return
        
        self.__center__[0] += int(x)
        self.__center__[1] += int(y)
        self.__leftTop__[0] += int(x)
        self.__leftTop__[1] += int(y)


    def getIncludeArguments(self):
        return (*self.getCenterPos(), self.width, self.height)


def getTextDimension(text, fontSize ,*args, **kwargs):
    label = Text(*args, text=str(text), x=0, y=0, fontSize=fontSize, **kwargs)
    return label.width, label.height
