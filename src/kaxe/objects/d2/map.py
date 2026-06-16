
import numpy as np
from ..mapdata import heatcolormap
import math
from PIL import Image
from ...core.shapes import shapes
from ...core.text import Text
from ...core.round import koundTeX
from ...plot import identities
from typing import Callable, Union
from ...core.color import Colormaps
from ...core.bounds import DEFAULT_DOMAIN_2D


class ColorScale:
    """
    ColorScale to be added in the right middle of the window

    Supports all plots

    Parameters
    ----------
    lower : Union[float, int, tuple]
        The lower bound of the color scale. Can be a number or a tuple of length 2 with value and title as values.
    upper : Union[float, int, tuple]
        The upper bound of the color scale. Can be a number or a tuple of length 2 with value and title as values.
    cmap : Colormaps, optional
        The colormap to use for the color scale. Default is Colormaps.standard.
    width : Union[int, None], optional
        The width of the color scale. Default is None.

    """

    def __init__(self, lower:Union[float, int, tuple], upper:Union[float, int, tuple], cmap=Colormaps.standard, width:Union[int, None]=None, title:Union[str, None]=None):
        """
        lower and upper can both be a number or a tuple of length 2 with value and title as values
        """
        self.digits = 200

        if type(lower) in [list, tuple]:
            self.lower = lower[0]
            self.lowerTitle = lower[1]
        else:
            self.lower = lower
            self.lowerTitle = str(koundTeX(round(self.lower, self.digits)))

        if type(upper) in [list, tuple]:
            self.upper = upper[0]
            self.upperTitle = upper[1]
        else:
            self.upper = upper
            self.upperTitle = str(koundTeX(round(self.upper, self.digits)))

        self.cmap = cmap
        self.supports = [identities.XYPLOT, identities.XYZPLOT]
        self.batch = shapes.Batch()
        self.width = width
        self.title = title


    def finalize(self, parent):
        fontsize = parent.getAttr('fontSize')
        leftMargin = fontsize # TODO: Style

        windowHeight = parent.windowBox[3] - parent.windowBox[1]
        height = int(windowHeight * 0.8)

        if not self.width:
            self.width = fontsize*2
        
        width = self.width # doven

        self.pos = (parent.windowBox[2], parent.padding[1] + windowHeight//2 - height//2)

        # spild af CPU her, men nemmere at læse, 
        # altså det ville jo være bedre at lave et billed og bare loade det hver gang
        arr = [self.cmap.getColor(self.upper - (i / height) * (self.upper - self.lower), self.lower, self.upper) for i in range(height)]
        arr = [[i]*width for i in arr]

        
        # bottom text
        self.lowerText = Text(
            self.lowerTitle, 
            0, 
            0, 
            batch=self.batch, 
            anchor_x='center', 
            anchor_y='top',
            fontSize=fontsize
        )
        
        self.lowerText.setLeftTopPos(self.pos[0]+width/2-self.lowerText.width//2, self.pos[1])


        # top text
        self.upperText = Text(
            self.upperTitle,
            self.pos[0]+width/2, 
            self.pos[1]+height, 
            batch=self.batch, 
            anchor_x='center', 
            anchor_y='',
            fontSize=fontsize
        )


        # add margin between text and axis        
        self.upperText.push(0, fontsize/8)
        self.lowerText.push(0, -fontsize/8)

        # parent.addPaddingCondition(right=width+scaleLeftMargin)

        self.img = shapes.ImageArray(np.array(arr, np.uint8), *self.pos, batch=self.batch)
        

        if self.title:
            
            # Push the colorscale to make space for the title
            for el in [self.img, self.lowerText, self.upperText]:
                el.push(fontsize*1.5, 0)

            self.titleText = Text(
                self.title,
                self.pos[0]+width/2 - fontsize / 2,  # add a small fontSize/2 gap
                self.pos[1]+height/2, 
                batch=self.batch, 
                rotate=90,
                anchor_x='center',
                anchor_y='center',
                fontSize=fontsize
            )

            # self.titleText.push(0, -self.titleText.height/2)

        # add space
        lx, ly = self.lowerText.getLeftTopPos()
        ux, uy = self.upperText.getLeftTopPos()

        mx = min(lx, ux, self.pos[0])
        off = self.pos[0] - mx

        # add margin
        self.batch.push(leftMargin+off, 0)



        parent.include(self.pos[0]+width/2, self.pos[1]+height/2, width, height)
        parent.includeElement(self.upperText)
        parent.includeElement(self.lowerText)
        # parent.includeElement(self.titleText) if self.title else None
        #parent.hasColorScale = True


    def push(self, x, y):
        self.batch.push(x, y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)


class HeatMap:
    """
    A class to represent a heatmap visualization.
    
    Parameters
    ----------
    data : list of list of float or int
        A 2D list containing the data values for the heatmap.
    cmap : Colormap, optional
        A colormap instance to map data values to colors (default is Colormaps.standard).
    unitPerPixel : list of float, optional
        A list containing the width and height of each pixel in the heatmap in terms of the unit space (default is [1, 1]).
    position : list or tuple, optional
        The (x, y) position of the bottom-left corner of the heatmap in the unit space (default is (0, 0)).
    minValue : float or int, optional
        The minimum value for the heatmap. If not provided, it is calculated from the data.
    maxValue : float or int, optional
        The maximum value for the heatmap. If not provided, it is calculated from the data.
    """

    def __init__(self, 
                data,
                cmap=Colormaps.standard, 
                unitPerPixel:list[float]=[1,1],
                position:Union[list, tuple]=(0,0),
                minValue = None,
                maxValue = None
        ):
        
        self.batch = shapes.Batch()
        self.cmap = cmap
        
        self.data = data
        self.unitPerPixel = unitPerPixel
        self.position = position

        # max, min
        if minValue:
            self.minValue = minValue
        else:
            self.minValue = min([min(row) for row in self.data])

        if maxValue:
            self.maxValue = maxValue
        else:
            self.maxValue = max([max(row) for row in self.data])

        self.farRight = position[0]
        self.farLeft = position[0] + len(data[0]) * self.unitPerPixel[0]
        self.farBottom = position[1]
        self.farTop = position[1] + len(data) * self.unitPerPixel[1]
        
        self.supports = [identities.XYPLOT]

    @classmethod
    def fromFunction(
        cls,
        f: Callable,
        numSamples: int = 100,
        domain=None,
        cmap=Colormaps.standard,
        minValue=None,
        maxValue=None,
        *args,
        **kwargs,
    ):
        """
        Build a heatmap by sampling a 2D function on a regular grid.

        Parameters
        ----------
        f : callable
            Function ``f(x, y)`` returning the value at each grid point.
            May accept numpy arrays for vectorized evaluation.
        numSamples : int, optional
            Number of cells per axis (default is 100).
        domain : tuple, optional
            Placement region ``(x0, x1, y0, y1)`` in plot coordinates
            (default is ``(-10, 10, -10, 10)``).
        cmap : Colormap, optional
            Colormap for value-to-color mapping.
        minValue : float or int, optional
            Minimum value for the color scale. Calculated from data if omitted.
        maxValue : float or int, optional
            Maximum value for the color scale. Calculated from data if omitted.
        *args
            Additional positional arguments passed to ``f``.
        **kwargs
            Additional keyword arguments passed to ``f``.

        Returns
        -------
        HeatMap

        Examples
        --------
        >>> import math
        >>> hm = kaxe.HeatMap.fromFunction(
        ...     lambda x, y: math.sin(x) * math.cos(y),
        ...     numSamples=100,
        ...     domain=(-10, 10, -10, 10),
        ... )
        >>> plt.add(hm)
        """
        if domain is None:
            domain = DEFAULT_DOMAIN_2D
        x0, x1, y0, y1 = domain
        n = numSamples
        dx = (x1 - x0) / n
        dy = (y1 - y0) / n

        xs = np.linspace(x0 + dx / 2, x1 - dx / 2, n)
        ys = np.linspace(y0 + dy / 2, y1 - dy / 2, n)

        data = None
        try:
            x_grid, y_grid = np.meshgrid(xs, ys)
            z_vals = np.asarray(f(x_grid, y_grid, *args, **kwargs), dtype=np.float64)
            if z_vals.shape == (n, n):
                data = z_vals.tolist()
        except Exception:
            pass

        if data is None:
            data = [
                [float(f(x, y, *args, **kwargs)) for x in xs]
                for y in ys
            ]

        return cls(
            data,
            cmap=cmap,
            unitPerPixel=[dx, dy],
            position=(x0, y0),
            minValue=minValue,
            maxValue=maxValue,
        )

    def finalize(self, parent):
        nrows = len(self.data)
        if nrows == 0:
            return
        ncols = len(self.data[0])
        if ncols == 0:
            return

        x0, y0 = self.position
        x1 = x0 + ncols * self.unitPerPixel[0]
        y1 = y0 + nrows * self.unitPerPixel[1]

        px0, py0 = parent.pixel(x0, y0)
        px1, py1 = parent.pixel(x1, y1)

        left = int(math.floor(px0))
        bottom = int(math.floor(py0))
        right = int(math.ceil(px1))
        top = int(math.ceil(py1))
        pw = max(right - left, 1)
        ph = max(top - bottom, 1)

        rgba = self.cmap.map_array(
            np.asarray(self.data, dtype=np.float64),
            self.minValue,
            self.maxValue,
        )
        rgba = rgba[::-1]

        img = Image.fromarray(rgba)
        if (pw, ph) != (ncols, nrows):
            img = img.resize((pw, ph), Image.NEAREST)

        wb = parent.windowBox
        clip_l = max(left, wb[0])
        clip_b = max(bottom, wb[1])
        clip_r = min(left + pw, wb[2])
        clip_t = min(bottom + ph, wb[3])
        if clip_l >= clip_r or clip_b >= clip_t:
            return

        if (clip_l, clip_b, clip_r, clip_t) != (left, bottom, left + pw, bottom + ph):
            src_left = clip_l - left
            src_right = clip_r - left
            src_top = ph - (clip_t - bottom)
            src_bottom = ph - (clip_b - bottom)
            img = img.crop((src_left, src_top, src_right, src_bottom))
            left, bottom = clip_l, clip_b

        self.img = shapes.ImageArray(np.asarray(img), left, bottom, batch=self.batch)
        
    
    def addColorScale(self, parent, digits=64):
        """
        Adds a color scale to the specified parent object.

        This method creates a `ColorScale` object using the instance's minimum 
        and maximum values (`self.minValue` and `self.maxValue`) and colormap 
        (`self.cmap`), then adds it to the provided parent object.

        Parameters
        ----------
        parent : object
            The object to which the color scale will be added. It must 
            have an `add` method that accepts a `ColorScale` object.
        digits : int
            Number of digits to display

        Returns
        -------
        HeatMap
            The instance of the class, allowing for method chaining.
        """
        
        parent.add(ColorScale(round(self.minValue, digits), round(self.maxValue, digits), cmap=self.cmap))
        
        return self


    def push(self, x, y):
        self.batch.push(x, y)


    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)