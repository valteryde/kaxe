
import numpy as np
import math
from scipy.spatial.transform import Rotation
from numpy import array

class Camera:

    def __init__(self):
        self.pos = np.array([0,0,0])
        self.angle = np.array([0,0,0])
        self.w = 999999
        self.scale = 1
        self.__calculateRotationMatrix__()
        
    
    def __calculateRotationMatrix__(self):
        self.R = Rotation.from_euler('zyx', self.angle).as_matrix()


    def project(self, pos):
        pos = array(pos)
        pos = pos - self.pos
        x, y, z = self.R @ np.array(pos)

        xm = (x * self.w) / (self.w + z)
        ym = (y * self.w) / (self.w + z)
        return array([xm*self.scale, ym*self.scale])


    def satelite(self, azimuth, zenith, d=2):

        self.scale = 1/d
        self.angle = array([azimuth, 0, zenith])

        self.__calculateRotationMatrix__()

    
    