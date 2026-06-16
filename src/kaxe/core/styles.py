
import copy
from types import MappingProxyType, FunctionType
import math

from .color import is_color_attr
from .palette import DEFAULT_SERIES_COLORS, apply_series_palette

# COLORS
WHITE = (255,255,255,255)
BLACK = (0,0,0,255)

colorNum = -1
colors = list(DEFAULT_SERIES_COLORS)


def _series_palette() -> list:
    return colors


def _palette_color_at(index: int) -> tuple:
    palette = _series_palette()
    return palette[index % len(palette)]


def getRandomColor() -> tuple:
    """Return the next color from Kaxe's default series palette.

    Colors rotate through the built-in Okabe–Ito palette. Each plot window
    maintains its own cycle for objects added without an explicit color; this
    global function is for manual use (e.g. ``color=kaxe.getRandomColor()``).
    Call :func:`resetColor` to restart the global cycle manually.

    Returns
    -------
    tuple
        RGBA color tuple, e.g. ``(230, 159, 0, 255)``.
    """
    global colorNum
    colorNum += 1
    return _palette_color_at(colorNum)


def resetColor() -> None:
    """Reset the global series color cycle to before the first palette color."""
    global colorNum
    colorNum = -1


def _apply_function2d_color(obj, color: tuple) -> None:
    from .color import to_rgba
    obj.color = to_rgba(color)
    obj.legendColor = obj.color
    if len(obj.color) > 3:
        obj.fillcolor = (*obj.color[:3], int(obj.color[3] * 0.5))
    else:
        obj.fillcolor = (*obj.color, 175)


def _apply_fill_color(obj, color: tuple) -> None:
    from .color import to_rgba
    rgba = list(to_rgba(color))
    if len(rgba) > 3:
        rgba[3] = 100
    else:
        rgba.append(100)
    obj.color = tuple(rgba)
    obj.legendColor = obj.color


def assign_series_color(plot, obj) -> None:
    """Assign the next series palette color from *plot* when the object defers color."""
    if getattr(obj, 'randomColor', False):
        count = getattr(obj, '_autoColorCount', 1)
        obj.color = [plot.nextSeriesColor() for _ in range(count)]
        obj.legendColor = obj.color[0]
        obj.randomColor = False
        return

    if not getattr(obj, '_autoSeriesColor', False):
        return

    color = plot.nextSeriesColor()
    obj._autoSeriesColor = False

    if type(obj).__name__ == 'Function2D':
        _apply_function2d_color(obj, color)
    elif type(obj).__name__ == 'Fill':
        _apply_fill_color(obj, color)
    else:
        from .color import Colormap, to_rgba
        obj.color = to_rgba(color)
        obj.legendColor = obj.color
        if type(obj.color) is Colormap:
            obj.legendColor = obj.color.getColor(0, 1, 2)


def isLightOrDark(rgbColor=[0,128,255,255]):
    [r,g,b,*a]=rgbColor
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp>127.5):
        return True
    return False


def setDefaultColors(colorList:list):
    """Replace the global default series palette.

    Parameters
    ----------
    colorList : list
        Colors for the series cycle. Entries may be RGBA tuples or hex/named
        color strings (see :func:`kaxe.to_rgba`).
    """
    global colors
    colors = apply_series_palette(colorList)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


lowerFirstLetter = lambda s: s[:1].lower() + s[1:] if s else ''


# ********* NEW ************
class AttrMap:
    
    def __init__(self):
        self.__attrs__ = {'global':{}}
        self.__defaults__ = {'global':{}}

    
    def submit(self, obj):
        """
        submit whole object and append use default method on all defaults in object
        """

        for attr in obj.defaults:
            self.default(attr, obj.defaults[attr], obj=obj)


    def __set__(self, d, key, attr, val):
        if d.get(key):
            d[key][attr] = val
        else:
            d[key] = {attr:val}

    
    def default(self, attr:str, value, obj=None):

        if type(value) is ComputedAttribute:
            value.setAttrMap(self)

        if type(obj) is str:
            self.__set__(self.__defaults__, obj.lower(), attr, value)
            
        elif obj:
            self.__set__(self.__defaults__, obj.name.lower(), attr, value)
        
        else:            
            self.__defaults__['global'][attr] = value
    

    def setAttr(self, attr, value, obj=None):
        """
        either sumbit by passing an object and retrieve global style
        """

        if type(value) is not ComputedAttribute and is_color_attr(attr):
            from .color import normalize_color_value
            value = normalize_color_value(value)

        if type(value) is ComputedAttribute:
            value.setAttrMap(self)

        if type(obj) is str:
            self.__set__(self.__attrs__,obj.lower(), attr, value)
            
        elif obj:
            self.__set__(self.__attrs__, obj.name.lower(), attr, value)
        
        elif '.' in attr:         
            key, attr = attr.split('.')
            self.__set__(self.__attrs__, key.lower(), attr, value)

        else:
            self.__attrs__['global'][attr] = value


    # retrieve a style
    def getAttr(self, attr:str, obj=None):
        attrvalue = self.__getAttr__(attr, obj)
        
        if type(attrvalue) is ComputedAttribute:
            attrvalue.setAttrMap(self)
            return attrvalue.get()
        
        return attrvalue


    def __getAttr__(self, attr:str, obj=None):
        """
        either passing an object and retrieve global type stylesheet
        or pass and global variable and retrieve global setting
        """

        # simple quick parse
        if '.' in attr:
            key, attr = attr.split('.')

        else:
            key, attr = 'global', attr

        key = key.lower()
        if obj: obj = obj.lower()
        
        # check object first
        if obj and key == 'global':
            rattr = self.__attrs__.get(obj, {}).get(attr)
            if rattr is not None: return rattr
        
        # default object
        if obj is not None:
            rattr = self.__defaults__.get(obj, {}).get(attr)
            if rattr is not None: return rattr
        

        # check global from attribute map
        rattr = self.__attrs__.get(key, {}).get(attr)
        if rattr is not None: return rattr
        
        
        # global default
        rattr = self.__defaults__.get(key, {}).get(attr)
        if rattr is not None: return rattr

    
    # API to pass along to user    
    def style(self, styles:dict={}, **kstyles):
        """
        Set multiple styles for the object.
        
        Parameters
        ----------
        styles : dict, optional
            A dictionary of styles to set. Default is an empty dictionary.
        **kstyles : keyword arguments
            Additional styles to set as keyword arguments.

        Examples
        --------
        >>> plt.style(color=(255,0,0,255), fontSize=128)
        >>> plt.style({'marker.tickWidth': 10}, fontSize=64)
        
        See also
        --------
        Kaxe.Plot.help

        """

        astyles = {**styles, **kstyles}
        for key in astyles:
            self.setAttr(key, astyles[key])


    def help(self):
        """
        Prints all available styles.
                
        Examples
        --------
        >>> plt.help()
        """
        

        print(f'{bcolors.BOLD}Styles{bcolors.ENDC}')

        for key in self.__defaults__:
            
            print(f'{bcolors.OKBLUE}{key}{bcolors.ENDC}')
            for attr in self.__defaults__[key]:
                
                if key == "global":
                    s = attr
                else:
                    s = f'{key}.{attr}'

                rattr = self.__attrs__.get(key, {}).get(attr)
                print(f'    {bcolors.OKGREEN}{s}:{bcolors.ENDC} {self.__defaults__[key][attr]}')


class AttrObject:
    defaults = {}

    def __init__(self):
        self.__attrs__ = {}
        self.attrmapRef = None

    def setAttrMap(self, attrmap):
        self.attrmapRef = attrmap


    def getAttr(self, attr:str, attrmap:AttrMap=None):

        if not attrmap:
            attrmap = self.attrmapRef

        attrvalue = self.__getAttr__(attr, attrmap)
        if type(attrvalue) is ComputedAttribute:
            attrvalue.setAttrMap(attrmap)
            return attrvalue.get()
        return attrvalue


    def __getAttr__(self, attr:str, attrmap:AttrMap):
        """
        check own stylesheet
        check global stylesheet
        prioritize own attributes
        """
        
        rattr = self.__attrs__.get(attr, None)
        if rattr is not None: return rattr

        return attrmap.getAttr(attr, self.name)
    
    
    def setAttr(self, attr=None, value=None, **kwargs):
        
        if kwargs:
            key = list(kwargs.keys())[0]
            self.__attrs__[key] = kwargs[key]
            return

        self.__attrs__[attr] = value


class ComputedAttribute:

    def __init__(self, func:FunctionType):
        self.func = func

    def setAttrMap(self, attrmap):
        self.attrmapRef = attrmap

    def get(self):
        return self.func(self.attrmapRef)

    def __str__(self):
        return str(self.get())

    def __repr__(self):
        return 'computable value'



"""
USECASES

obj1.setStyle('color', 'black')
obj1.getStyle('color') -> 'black'

obj2.getStyle('color') -> defaults to global color value

stylemap.setStyle('obj1.color', 'red')
obj1.getStyle('color') -> 'black' #still defaults to own stylesheet
obj2.getStyle('color) -> 'red'

# if an value is not set 
obj1.getStyle('fontSize') -> return global defaults
obj1.getStyle(obj1, 'fontSize') -> return obj defaults

obj1.getStyle('not-a-real-value') -> None
"""