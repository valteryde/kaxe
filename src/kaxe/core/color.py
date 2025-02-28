
from PIL import ImageColor
import math
import numpy as np
from typing import Union


class Colormap:
    """
    A class to represent a colormap that interpolates colors from a gradient.
    
    Parameters
    ----------
    colorGradientSteps : Union[list, tuple]
        A list or tuple of colors representing the gradient steps. Colors can be in hexadecimal string format or RGBA arrays.    
    """

    def __init__(self, colorGradientSteps:Union[list, tuple]):
        self.colorGradientSteps = colorGradientSteps
        for i, phex in enumerate(colorGradientSteps):
            if type(phex) is str:
                self.colorGradientSteps[i] = np.array(ImageColor.getcolor(phex, "RGBA"))
            else:
                self.colorGradientSteps[i] = np.array(self.colorGradientSteps[i])

    
    def getColor(self, value:Union[int, float], start:Union[int, float], end:Union[int, float]):
        """
        Get the interpolated color from the color gradient steps based on the input value.
        
        Parameters
        ----------
        value : Union[int, float]
            The value for which the color needs to be determined.
        start : Union[int, float]
            The start value of the range.
        end : Union[int, float]
            The end value of the range.
        
        Returns
        -------
        color
            The interpolated color from the color gradient steps.
        
        Notes
        -----
        - If `value` is less than `start`, the first color in the gradient steps is returned.
        - If `value` is greater than `end`, the last color in the gradient steps is returned.
        - The interpolation is linear between the two nearest colors in the gradient steps.
        
        Examples
        --------
        >>> cmap.getColor(3.5, 0, 10)
            (125, 215, 51, 255)
        """
        

        if value < start:
            return self.colorGradientSteps[0]
        if value > end:
            return self.colorGradientSteps[-1]

        x = ((value - start) / (end - start)) * (len(self.colorGradientSteps) - 1)
        x0 = math.floor(x)
        x1 = math.ceil(x)

        x -= x0
        return tuple(round(i) for i in (1 - x) * self.colorGradientSteps[x0] + (x) * self.colorGradientSteps[x1])


class SingleColormap(Colormap):
    """
    SingleColormap is a subclass of Colormap that generates a colormap based on a single color.
    
    Parameters
    ----------
    color : str or list or tuple
        The base color for the colormap. If a string is provided, it should be a hex color code.
        If a list or tuple is provided, it should contain RGB or RGBA values.
    diff : list, optional
        A list containing two float values that define the range of color differences.
        Default is [0.3, 0.7].
    
    See also
    --------
    kaxe.Colormap
    """
    

    def __init__(self, color, diff=[0.3, 0.7]):

        if type(color) is str:
            color = np.array(ImageColor.getcolor(hex, "RGBA"))

        if len(color) == 3:
            color = np.array((*color, 255))
        
        self.color = color
        self.diff = diff
        len_ = self.diff[1] - self.diff[0]

        n = 10

        arr = [np.array((*(color*(self.diff[0]+len_*(i/n)))[:3], 255)) for i in range(n+1)]
        arr.reverse()

        super().__init__(arr)


class Colormaps:
    """
    A collection of predefined colormaps for various color schemes.
    
    Attributes
    ----------
    standard : Colormap
        A colormap with a standard set of colors.
    green : Colormap
        A colormap with various shades of green.
    brown : Colormap
        A colormap with various shades of brown.
    blue : Colormap
        A colormap with various shades of blue.
    yellow : Colormap
        A colormap with various shades of yellow.
    cream : Colormap
        A colormap with a cream color scheme.
    red : SingleColormap
        A single color colormap with the color red.
    """


    standard = Colormap([
        "#AFE3C0",
        "#90C290",
        "#FF5154",
        "#91A6FF",
        "#FAFF7F",
        "#ED7D3A",
    ])
    green = Colormap([
        "#004b23",
        "#006400",
        "#007200",
        "#008000",
        "#38b000",
        "#70e000",
        "#9ef01a",
        "#ccff33"
    ])

    brown = Colormap([
        "#6f1d1b",
        "#bb9457",
        "#432818",
        "#99582a",
        "#ffe6a7"
    ])

    blue = Colormap([
        "#7400b8",
        "#6930c3",
        "#5e60ce",
        "#5390d9",
        "#4ea8de",
        "#48bfe3",
        "#56cfe1",
        "#64dfdf",
        "#72efdd",
        "#80ffdb"
    ])

    yellow = Colormap([
        "#ff7b00",
        "#ff8800",
        "#ff9500",
        "#ffa200",
        "#ffaa00",
        "#ffb700",
        "#ffc300",
        "#ffd000",
        "#ffdd00",
        "#ffea00"
    ])

    cream = Colormap([
        "#780000",
        "#c1121f",
        "#fdf0d5",
        "#003049",
        "#669bbc"
    ])

    red = SingleColormap((255, 0, 0))
