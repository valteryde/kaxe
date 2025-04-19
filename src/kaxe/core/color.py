
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
        colorGradientSteps = list(colorGradientSteps).copy()
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

    def setAlpha(self, alpha255):
        """
        Update the alpha (transparency) value for each color in the color gradient steps.
        
        Parameters
        ----------
        alpha255 : int
            The alpha value to set, ranging from 0 to 255, where 0 is fully transparent
            and 255 is fully opaque.
        
        Returns
        -------
        Colormap
        """
        
        return Colormap([
            np.array([*color[:3],alpha255]) for color in self.colorGradientSteps
        ])


class SingleColormap(Colormap):
    """
    SingleColormap is a subclass of Colormap that generates a colormap based on a single color.
    
    Parameters
    ----------
    color : str or list or tuple
        The base color for the colormap. If a string is provided, it should be a hex color code.
        If a list or tuple is provided, it should contain RGB or RGBA values.
    spread : float, optional
        A float larger than 1 describing the spread of the colors
        Default is [0.3, 0.7].
    total : int, optional
        The total colors in the colormap

    See also
    --------
    kaxe.Colormap
    """
    
    def __clamp__(self, v):
        return max(min(v, 255), 0)


    def __init__(self, color, spread=0.3, total=10):

        if type(color) is str:
            color = np.array(ImageColor.getcolor(hex, "RGBA"))

        if len(color) == 3:
            color = (*color, 255)
        
        color = np.array(color)

        self.color = color
        self.spread = spread
        self.total = total

        v = color * spread
        arr = []
        for i in range(self.total):
            newcolor = color + i*v/self.total - v/2

            newcolor = (
                self.__clamp__(newcolor[0]),
                self.__clamp__(newcolor[1]),
                self.__clamp__(newcolor[2]),
                color[3] # keep alpha as is
            )

            arr.append( newcolor )

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


    rainbow = Colormap(reversed([
        (133, 25, 15, 255), (143, 27, 17, 255), (152, 30, 19, 255),
        (159, 31, 20, 255), (171, 35, 23, 255), (180, 37, 25, 255),
        (190, 39, 27, 255), (200, 42, 29, 255), (212, 45, 31, 255),
        (221, 48, 33, 255), (228, 50, 34, 255), (234, 51, 35, 255),
        (234, 51, 35, 255), (234, 55, 36, 255), (234, 68, 37, 255),
        (235, 76, 39, 255), (235, 87, 41, 255), (236, 98, 42, 255),
        (236, 106, 44, 255), (237, 118, 47, 255), (238, 128, 49, 255),
        (239, 135, 51, 255), (240, 146, 53, 255), (241, 158, 56, 255),
        (242, 166, 59, 255), (243, 176, 61, 255), (244, 186, 64, 255),
        (245, 194, 66, 255), (247, 207, 70, 255), (248, 215, 72, 255),
        (250, 224, 75, 255), (251, 235, 78, 255), (253, 245, 81, 255),
        (255, 254, 84, 255), (247, 255, 84, 255), (235, 254, 83, 255),
        (227, 254, 82, 255), (217, 254, 81, 255), (207, 253, 81, 255),
        (198, 253, 80, 255), (186, 253, 79, 255), (177, 253, 79, 255),
        (168, 252, 85, 255), (158, 252, 95, 255), (146, 252, 107, 255),
        (137, 252, 115, 255), (129, 251, 124, 255), (118, 251, 134, 255),
        (117, 251, 142, 255), (117, 251, 154, 255), (117, 251, 163, 255),
        (117, 251, 172, 255), (117, 251, 183, 255), (117, 251, 193, 255),
        (117, 251, 202, 255), (117, 251, 211, 255), (117, 251, 223, 255),
        (117, 251, 231, 255), (117, 251, 241, 255), (117, 251, 250, 255),
        (117, 251, 253, 255), (111, 239, 252, 255), (107, 230, 252, 255),
        (102, 222, 251, 255), (97, 212, 250, 255), (92, 200, 250, 255),
        (88, 192, 249, 255), (83, 182, 249, 255), (79, 174, 248, 255),
        (74, 163, 248, 255), (68, 153, 248, 255), (64, 144, 247, 255),
        (60, 136, 247, 255), (54, 124, 247, 255), (49, 114, 246, 255),
        (45, 105, 246, 255), (40, 96, 246, 255), (35, 85, 246, 255),
        (31, 77, 245, 255), (25, 66, 245, 255), (21, 57, 245, 255),
        (17, 48, 245, 255), (11, 36, 245, 255), (7, 27, 245, 255),
        (4, 19, 245, 255), (1, 8, 245, 255), (0, 0, 245, 255),
        (0, 0, 243, 255), (0, 0, 234, 255), (0, 0, 225, 255),
        (0, 0, 215, 255), (0, 0, 204, 255), (0, 0, 195, 255),
        (0, 0, 187, 255), (0, 0, 175, 255), (0, 0, 165, 255),
        (0, 0, 156, 255), (0, 0, 147, 255), (0, 0, 139, 255)
    ]))