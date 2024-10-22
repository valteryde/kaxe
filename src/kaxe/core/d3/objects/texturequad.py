
import numpy as np
from numba import njit, jit
from .triangle import Triangle
from PIL import Image
import warnings
warnings.filterwarnings("ignore")


#@njit
def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype=np.cfloat)
    B = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)


# @njit
# def dist(a, b, p):
#     v = b - a
#     nx, ny = -v[1], v[0]
#     c = -nx * a[0] - ny * a[1]
#     return abs(nx * p[0] + ny * p[1] + c) / np.sqrt(v.dot(v))
    

class TextureQuad:

    def __init__(self, a1, a2, d):
        #anchor 1 and 2
        #direction d
        self.__loaded__ = False

        """
    
        a2
        __
        | \ 
        |  \  
        |   \ d
        |   /
        |__/
        a1

        """

        self.a1 = np.array(a1)
        self.a2 = np.array(a2)
        self.d = np.array(d)
        # width is included in 
        # height is included in length of self.p1 and self.p2


    def __load__(self, render):
        self.__loaded__ = True
        # no reason to load if not drawn

        img = Image.open('test.png')
        img = img.convert('RGBA')
        
        width, height = img.size
        
        # transpose bottom top
        img = img.transpose(1)

        # resize if to large
        if width > render.width or height > render.height:
            pass
        n = max(width/render.width, height/render.height)

        #n = 10
        #img = img.resize((round(n*width), round(n*height)))
        #img = img.resize((1000, 1000))

        # img.show()

        a1 = render.pixel(*self.a1)
        a2 = render.pixel(*self.a2)
        b1 = render.pixel(*self.b1)
        b2 = render.pixel(*self.b2)

        coeffs = find_coeffs([a1, a2, b1,  b2], [
            (0,0),
            (0,height),
            (width, 0),
            (width,height),
        ])

        img = img.transform((render.width, render.height), Image.PERSPECTIVE, coeffs,
                Image.BICUBIC)

        # img.show()

        self.bbox = img.getbbox()
        self.image = np.array(img.crop(self.bbox))
        self.imageHeight = len(self.image)
        self.imageWidth = len(self.image[0])


    def drawTozBuffer(self, render, index):

        # tegn dem til sidst!
        # self.flagHalfTransparent = False
    
        self.b1 = self.a1+self.d
        self.b2 = self.a2+self.d
        self.tri1 = Triangle(self.a1, self.a2, self.b1)
        self.tri2 = Triangle(self.a2, self.b1, self.b2)

        self.tri1.drawTozBuffer(render, index)
        self.tri2.drawTozBuffer(render, index)

    
    def getColor(self, render, x, y):
        if not self.__loaded__:
            self.__load__(render)
        
        ix, iy = x-self.bbox[0], y - self.bbox[1]

        ix = min(ix, self.imageWidth-1)
        iy = min(iy, self.imageHeight-1)

        return self.image[iy][ix]
    