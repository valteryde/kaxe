
from PIL import Image
from .styles import *
import os
from .shapes import *
from fondi import MathText
import numpy as np

textImageCache = {}
mathtextCache = {}
maxTextCacheSize = 100


def _cache_get(cache: dict, key):
    if key not in cache:
        return None
    value = cache.pop(key)
    cache[key] = value
    return value


def _cache_set(cache: dict, key, value, max_size=maxTextCacheSize):
    if key in cache:
        cache.pop(key)
    elif len(cache) >= max_size:
        cache.pop(next(iter(cache)))
    cache[key] = value


def _parse_kaxe_text(text: str) -> str:
    """Translate kaxe $math$ syntax to fondi LaTeX string."""
    res = ''
    open_ = 0
    word = ''
    for char in text:
        if char == '$' and open_:
            open_ = False
            continue
        elif char == '$' and not open_:
            open_ = True
            if len(word) > 0:
                res += '\\text{' + word + '}'
            word = ''
            continue

        if open_:
            res += char
        else:
            word += char

    if len(word) > 0:
        res += '\\text{' + word + '}'
    return res


def _get_mathtext(latex: str, fontSize: int, color: tuple) -> MathText:
    key = str(latex), fontSize, tuple(color)
    cached = _cache_get(mathtextCache, key)
    if cached is not None:
        return cached
    mt = MathText(latex, fontSize, color)
    _cache_set(mathtextCache, key, mt)
    return mt


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
                 anchor_y:str="center", 
                 cacheImage=True,
                 clip_box=None,
                 *args, **kwargs
        ):
        
        self.batch = batch
        self.clip_box = list(clip_box) if clip_box is not None else None
        self.color = color
        self.rotate = rotate
        self.fontSize = fontSize
        self.text = text
        super().__init__()
        if batch: batch.add(self)

        self.latex = _parse_kaxe_text(text)
        self._mathtext = _get_mathtext(self.latex, self.fontSize, self.color)

        key = str(self.latex), fontSize, tuple(color)
        cachedImage = _cache_get(textImageCache, key)
        if cachedImage:
            pilImage = cachedImage
        else:
            pilImage = self._mathtext.to_pil()
            _cache_set(textImageCache, key, pilImage)

        self.img = pilImage.rotate(self.rotate, expand=True)

        self.width = self.img.width
        self.height = self.img.height

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

    def setCenterPos(self, x, y):
        self.__center__ = [x, y]
        if self.anchor_x == "center":
            self.__leftTop__ = [x - self.width / 2, None]
        else:
            self.__leftTop__ = [x, None]
            self.__center__[0] = x + self.width / 2

        if self.anchor_y == "center":
            self.__leftTop__[1] = y - self.height / 2
        else:
            self.__leftTop__[1] = y
            self.__center__[1] = y + self.height / 2

    
    def getLeftTopPos(self):
        return self.__leftTop__

    
    def setLeftTopPos(self, x, y):
        self.__leftTop__[0] = x
        self.__leftTop__[1] = y
        self.__center__[0] = self.__leftTop__[0] - self.width/2 # føler ikke det burde være sådan her
        self.__center__[1] = self.__leftTop__[1] - self.height/2


    def _pil_clip_box(self, surface):
        if self.clip_box is None:
            return None
        left, top, right, bottom = self.clip_box
        return [
            left,
            surface.height - bottom,
            right,
            surface.height - top,
        ]

    def drawPillow(self, surface):
        [y] = flipHorizontal(surface, self.__center__[1] + self.height/2)
        if self.clip_box is not None:
            blit_image_clipped(
                surface,
                self.img,
                self.__leftTop__[0],
                y,
                self._pil_clip_box(surface),
            )
        else:
            blitImageToSurface(surface, self.img, (self.__leftTop__[0], y))

    def drawSvg(self, doc):
        kaxe_top = self.__center__[1] + self.height / 2
        svg_top = doc.flip_y(kaxe_top)
        rotate_center = (
            self.__leftTop__[0] + self.width / 2,
            svg_top + self.height / 2,
        )

        if hasattr(self._mathtext, "scene"):
            scene = self._mathtext.scene()
            # Center the unrotated fondi scene on the rendered (rotated) bbox, matching Pillow.
            scene_left = rotate_center[0] - scene.width / 2
            scene_top = rotate_center[1] - scene.height / 2
            doc.add_fondi_scene(
                scene,
                scene_left,
                scene_top,
                rotate=self.rotate,
                rotate_center=rotate_center,
                clip_box=self.clip_box,
            )
            return

        doc.add_image(
            self.img,
            self.__leftTop__[0],
            kaxe_top,
            y_coord="top",
            rotate=self.rotate,
            rotate_center=rotate_center,
            clip_box=self.clip_box,
        )


    def push(self, x, y):
        if np.isnan(x) or np.isnan(y):
            return
        
        self.__center__[0] += int(x)
        self.__center__[1] += int(y)
        self.__leftTop__[0] += int(x)
        self.__leftTop__[1] += int(y)
        if self.clip_box is not None:
            self.clip_box[0] += int(x)
            self.clip_box[1] += int(y)
            self.clip_box[2] += int(x)
            self.clip_box[3] += int(y)


    def getIncludeArguments(self):
        return (*self.getCenterPos(), self.width, self.height)


def getTextDimension(text, fontSize ,*args, **kwargs):
    label = Text(*args, text=str(text), x=0, y=0, fontSize=fontSize, **kwargs)
    return label.width, label.height
