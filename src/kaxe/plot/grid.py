
from io import BytesIO
from ..core.styles import AttrObject, AttrMap
from ..core.window import *
from ..core.legend import LegendBox
from typing import Union
from PIL import Image
from .d3 import XYZPLOT

class Grid(AttrObject):
    """
    Assemble multiple plots in one image.
    
    Examples
    --------
    >>> grid = kaxe.Grid()
    >>> grid.style(width=500, height=500)
    >>> grid.addRow(plt1, plt2)
    >>> grid.addColumn(plt3, plt4)
    >>> grid.show()
    >>> grid.save('fname.png')

    """

    name = "Grid"

    def __init__(self):
        super().__init__()

        self.grid = []
        self.gridGap = [20, 20]

        # styles
        self.attrmap = AttrMap()
        self.attrmap.default(attr='width', value=2500)
        self.attrmap.default(attr='height', value=2000)
        self.attrmap.default(attr='backgroundColor', value=(255,255,255,255))
        self.attrmap.default(attr='outerPadding', value=[10,10,10,10])
        self.attrmap.default(attr='fontSize', value=50)
        self.attrmap.default(attr='color', value=(0,0,0,255))
        self.setAttrMap(self.attrmap)
        self.attrmap.submit(LegendBox)

        self.style = self.attrmap.style # for backwards compatibility

        self.__legends = []
        self.padding = [0,0,0,0]

        self.__bakedImage__ = False
        self.laterDraws = []


    def help(self):
        print('Please also see the style docstring or style for each plotting window')
        print(self.style.__doc__)


    def legends(self, *legends):
        """
        Set the legends for the grid. All information must be provided for a legend.
        
        Parameters
        ----------
        *legends : list[tuple]
            Diffrent legends consisting of a label, color and symboltype
        
        Examples
        --------
        >>> grid.legends(
            ("A legend", kaxe.Symbol.CROSS, color1),
            ...
            ("N legend", kaxe.Symbol.CIRCLE, colorn),
        )
        """
        
        self.__legends = legends



    def __bake__(self):
        """
        only supports pillow images

        TODO: Clean up
        """

        grid = self.grid
        gridSize = ((max([len(i) for i in grid])), len(grid))
        self.width, self.height = self.getAttr('width'), self.getAttr('height')
        self.outerPadding = self.getAttr('outerPadding')

        # styles values
        cellWidth, cellHeight = self.width//gridSize[0], self.height//gridSize[1]

        # calculated values        
        height = 0
        leftpadding = 0
        rightpadding = 0
        toppadding = 0
        bottompadding = 0
        gapcol = 0

        # add styles to window
        # and calculate sizes
        maxWidth = 0
        for row in grid:
            
            maxHeight = 0
            
            for colNum, plot in enumerate(row):
                
                plot.style(width=cellWidth, height=cellHeight)
                plot.style(outerPadding=self.outerPadding)

                memfile = BytesIO()
                plot.showProgressBar = False
                plot.printDebugInfo = False

                if plot == XYZPLOT:
                    plot.forceWidthHeight = True

                plot.save(memfile)
                plot.__ioBytes = memfile

                w, h = plot.getSize()
                maxWidth = max(w, maxWidth)
                
                maxHeight = max(h, maxHeight)
                
                # calculate paddings
                if colNum == 0:
                    leftpadding = max(leftpadding, plot.padding[0])
                    bottompadding = max(bottompadding, plot.padding[1])
                
                # calculate gaps
                else: # "låner"/genbruger lige else her
                    
                    # Da den næste ikke er lavet bruges den forrige
                    gapcol = max(gapcol, plot.padding[0] + row[colNum - 1].padding[2])

                if colNum == len(row)-1:
                    rightpadding = max(rightpadding, plot.padding[2])
                    toppadding = max(toppadding, plot.padding[3])

            height += maxHeight
        
        largetsRowNumber = max(len(i) for i in grid)
        width = gapcol * (largetsRowNumber - 1) + largetsRowNumber * cellWidth + leftpadding + rightpadding

        size = (
            width + self.outerPadding[0] + self.outerPadding[2],
            height + self.outerPadding[1] + self.outerPadding[3] + toppadding
        )
        
        # Add legend
        if self.__legends:
            self.legendbox = LegendBox()
            for d in self.__legends:
                self.legendbox.add(*d)

            legendBoxImage = self.legendbox.finalize(self, sneaky=True)

            size = (
                size[0],
                size[1] + legendBoxImage.height + self.legendbox.getAttr('topMargin'),
            )

        image = Image.new('RGBA', size, self.getAttr('backgroundColor'))

        if self.__legends:
            image.alpha_composite(legendBoxImage, (image.width//2 - legendBoxImage.width//2, image.height - legendBoxImage.height - self.outerPadding[3]))

        # TEGNER!
        # add plots to grid image
        y = toppadding + self.outerPadding[1]

        for row in grid:

            maxHeight = 0
            x = leftpadding + self.outerPadding[0]

            for plot in row:
                """
                Is a little ineffecient to write and then read from memory with png extenseion
                but here goes.
                """

                w, h = plot.getSize()

                img = Image.open(plot.__ioBytes)
                image.paste(img, (x - plot.padding[0], y - plot.padding[3]))
            
                x += cellWidth + gapcol
                maxHeight = max(maxHeight, h)

            y += maxHeight

        self.__bakedImage__ = image

        return image

    
    def addRow(self, *row:list):
        """
        Adds a row of plots to the grid.

        Parameters
        ----------
        row : list
            A list of plots to be added as a row in the grid.

        """

        self.grid.append(row)


    def addColumn(self, *column:list):
        """
        Adds a column of plots to the grid.

        Parameters
        ----------
        column : list
            A list of plots to be added as a column in the grid.
        """

        for i, plot in enumerate(column):
            
            if i >= len(self.grid):
                self.grid.append([])

            self.grid[i].append(plot)

    
    def save(self, fpath:str):
        
        if self.__bakedImage__:
            self.__bakedImage__.save(fpath)
            return

        img = self.__bake__()
        
        if fpath is str:
            img.save(fpath)
        else:
            img.save(fpath, format="png")


    def show(self):
        """
        Show the current image using `Pillow.Image.Show`
        
        If a cached image is available, it will be used to save the file.
        Otherwise, the image will be generated and then saved.

        Examples
        --------
        >>> plt.show( )
        """

        fname = 'plot{}.png'.format(''.join([str(randint(0,9)) for i in range(10)]))

        if terminaltype != "terminal":
            self.save(fname)
            i = display.Image(filename=fname, width=800, unconfined=True)
            display.display(i)
            os.remove(fname)

        else:
            
            self.save(fname)
            pilImage = Image.open(fname)
            pilImage.show()
            os.remove(fname)

        return fname


    def getSize(self):
        return self.__bakedImage__.size
