
from numba import float64, int32
from numba.experimental import jitclass

@jitclass()
class Pointer:
    pos: int32

    def __init__(self):
        self.pos = -1

pointer_type = Pointer.class_type.instance_type
