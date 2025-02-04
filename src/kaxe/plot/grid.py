
from io import BytesIO
from ..core.window import Window
from typing import Union
from PIL import Image

class Grid(Window):
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

    def __init__(self):

        self.grid = []
        self.gridGap = [20, 20]

        # styles
        self.width = 2000
        self.height = 1500
        self.backgroundColor = (255,255,255,255)
        self.outerPadding = [10, 10, 10, 10]

        self.__bakedImage__ = False


    def help(self):
        print('Please see style docstring or style for each plotting window:')
        print(self.style.__doc__)
    

    def style(self, 
              width:Union[int, float, None]=None, 
              height:Union[int, float, None]=None,
              outerPadding:Union[tuple, list]=None,
              gridGap:Union[list, tuple]=None,
              backgroundColor:Union[tuple, list]=None,
        ):
        """
        Adds style to grid
        
        Paramters
        ---------
        width : int, float, optional
            The width of each plot in the grid.
        height : int, float, optional
            The height of each plot in the grid.
        outerPadding : tuple, list, optional
            The outer padding of the grid in the format (left, top, right, bottom).
        gridGap : list, tuple, optional
            The gap between grid elements. This is currently not in use
        backgroundColor : tuple, list, optional
            The background color of the grid in RGBA format.

        """

        if width:
            self.width = width

        if height:
            self.height = height

        # currently does nothing
        # if gridGap:
        #     self.gridGap = gridGap

        if backgroundColor:
            self.backgroundColor = backgroundColor

        if outerPadding:
            self.outerPadding = outerPadding


    def __bake__(self):
        """
        only supports pillow images

        TODO: Clean up
        """

        grid = self.grid

        # calculated values        
        height = 0
        leftpadding = 0
        rightpadding = 0
        toppadding = 0
        bottompadding = 0
        gapcol = 0

        # add styles to window
        # and calculate sizes
        for row in grid:
            
            maxHeight = 0
            
            for colNum, plot in enumerate(row):
                
                plot.style(width=self.width, height=self.height)
                plot.style(outerPadding=[10,10,10,10])

                memfile = BytesIO()
                plot.showProgressBar = False
                plot.printDebugInfo = False
                plot.save(memfile)
                plot.__ioBytes = memfile

                w, h = plot.getSize()
                
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
        
        width = gapcol * (len(row) - 1) + len(row) * self.width + leftpadding + rightpadding
        
        size = (
            width + self.outerPadding[0] + self.outerPadding[2],
            height + self.outerPadding[1] + self.outerPadding[3] + toppadding
        )
        
        image = Image.new('RGBA', size, self.backgroundColor)

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
            
                x += self.width + gapcol
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
        img.save(fpath)


    
    # def show(self):
    #     if self.__bakedImage__:
    #         self.__bakedImage__.show()
    #         return

    #     img = self.__bake__()
    #     img.show()
