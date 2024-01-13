
from .core.helper import *
from .core.axis import *
from .core.window import Window
import math
from .standard import Plot

XYPLOT = 'xy'

class LogPlot(Plot):
    
    def __init__(self,  window:list=None, firstAxisLog=False, secondAxisLog=True): # |
        super().__init__(window)
        self.identity = XYPLOT

        """
        window:tuple [x0, x1, y0, y1] axis
        """
        
        def log(x):
            try:
                return math.log(x, 10)
            except ValueError:
                return 0

        self.firstAxisLog = firstAxisLog
        self.secondAxisLog = secondAxisLog

        if firstAxisLog:
            self.xtrans = log
            self.xtransinv = lambda x: 10**x
        else:
            self.xtrans = lambda x: x
            self.xtransinv = lambda x: x

        if secondAxisLog:
            self.ytrans = log
            self.ytransinv = lambda x: 10**x
        else:
            self.ytrans = lambda x: x
            self.ytransinv = lambda x: x


    def __setAxisPos__(self):
        self.firstAxis.addStartAndEnd(self.windowAxis[0], self.windowAxis[1])
        self.secondAxis.addStartAndEnd(self.windowAxis[2], self.windowAxis[3])
        self.offset[0] += self.windowAxis[0] * self.scale[0]
        self.offset[1] += self.windowAxis[2] * self.scale[1]

        if self.secondAxis.hasNull and self.firstAxisLog:
            self.firstAxis.setPos(self.translate(self.windowAxis[0],0), self.translate(self.windowAxis[1],0))

        elif self.secondAxis.endNumber < 0:
            self.firstAxis.setPos(self.translate(self.windowAxis[0],self.windowAxis[3]), self.translate(self.windowAxis[1],self.windowAxis[3]))
        else:
            self.firstAxis.setPos(self.translate(self.windowAxis[0],self.windowAxis[2]), self.translate(self.windowAxis[1],self.windowAxis[2]))

        self.firstAxis.finalize(self)

        if self.firstAxis.hasNull and self.secondAxisLog:
            self.secondAxis.setPos(self.translate(0,self.windowAxis[2]), self.translate(0,self.windowAxis[3]))

        elif self.firstAxis.endNumber < 0:
            self.secondAxis.setPos(self.translate(self.windowAxis[1],self.windowAxis[2]), self.translate(self.windowAxis[1],self.windowAxis[3]))

        else:
            self.secondAxis.setPos(self.translate(self.windowAxis[0],self.windowAxis[2]), self.translate(self.windowAxis[0],self.windowAxis[3]))

        self.secondAxis.finalize(self)


    def __prepare__(self):
        # finish making plot
        # fit "plot" into window

        self.windowAxis[0] = self.xtrans(self.windowAxis[0])
        self.windowAxis[1] = self.xtrans(self.windowAxis[1])
        self.windowAxis[2] = self.ytrans(self.windowAxis[2])
        self.windowAxis[3] = self.ytrans(self.windowAxis[3])

        xLength = self.windowAxis[1] - self.windowAxis[0]
        yLength = self.windowAxis[3] - self.windowAxis[2]
        self.scale = [self.width/xLength,self.height/yLength]

        self.__setAxisPos__()

        self.windowBox = (
            self.padding[0], 
            self.padding[1], 
            self.width+self.padding[0], 
            self.height+self.padding[1]
        )


        firstAxisMarkers = self.firstAxis.computeMarkersAutomatic(self)

        for marker in firstAxisMarkers:
            marker["text"] = str(koundTeX(self.xtransinv(marker["pos"])))

        self.firstAxis.addMarkersToAxis(firstAxisMarkers, self)


        secondAxisMarkers = self.secondAxis.computeMarkersAutomatic(self)

        for marker in secondAxisMarkers:
            marker["text"] = str(koundTeX(self.ytransinv(marker["pos"])))

        self.secondAxis.addMarkersToAxis(secondAxisMarkers, self)


    # translations
    def pixel(self, x:int, y:int) -> tuple:
        """
        para: abstract value
        return: pixel values according to axis
        """
        
        return self.translate(self.xtrans(x),self.ytrans(y))


    def inversepixel(self, x:int, y:int):
        """
        para: pixel values according to axis
        return abstract value
        """
        return self.inversetranslate(self.xtransinv(x),self.ytransinv(y))
