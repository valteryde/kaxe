
from ..plot import shapes
from ..plot import styles
from ..plot.helper import *

class ReadOff:

    def __init__(self, x, y, color:tuple=styles.BLACK, width:int=2):
        self.batch = shapes.Batch()
        self.x = x
        self.y = y
        self.color = color
        self.width = width

    
    def finalize(self, parent):
        pos = parent.pixel(self.x, self.y)
        self.circle = shapes.Circle(pos[0], pos[1], 10, self.color, batch=self.batch)

        p1 = parent.pixel(self.x, 0)
        p2 = parent.pixel(0, self.y)
        
        if parent.untrueAxis: # dermed også standard basis
            pass
            # v1 = vdiff(pos, p1)
            # pos = parent.line(pos, (-v1[1], v1[0]))
            # print(pos)
        
        #else: ikke testet else igennem

        

        self.line1 = shapes.Line(*pos,*p1, self.color, width=self.width, batch=self.batch)
        self.line2 = shapes.Line(*pos,*p2, self.color, width=self.width, batch=self.batch)


    def push(self, dx, dy):
        self.x += dx
        self.y += dy
        self.batch.push(dx, dy)

    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)