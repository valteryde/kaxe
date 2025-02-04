
import copy
from types import MappingProxyType, FunctionType
import math

# COLORS
WHITE = (255,255,255,255)
BLACK = (0,0,0,255)

colorNum = -1
def getRandomColor() -> tuple:
    global colorNum
    colorNum+=1
    return colors[colorNum%(len(colors))]

def resetColor() -> None:
    """
    Resets the global color number to its initial state.
    This function sets the global variable `colorNum` to -1, effectively
    resetting any color-related state that depends on this variable.

    Note
    ----
    This resets all plot color progress

    """

    global colorNum
    colorNum = -1


def isLightOrDark(rgbColor=[0,128,255,255]):
    [r,g,b,*a]=rgbColor
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp>127.5):
        return True
    return False


colors = [
    (222,107,72, 255),
    (91,200,175, 255),
    (6,71,137, 255),
    (8,45,15, 255),
    # (247,197,72, 255),
    (251, 111, 146),
    (0, 53,102),
    (188, 108,37),
    (33, 104, 105),
]

def setDefaultColors(colorList:list):
    """
    Set the global default colors for all plots
    
    Parameters
    ----------
    colorList : list
        A list of colors to be set as the default colors.
    
    Notes
    -----
    This function sets the global variable `colors` to the provided list of colors.
    """

    global colors
    colors = colorList


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
        >>> plt.styles(color=(255,0,0,255), fontSize=128)
        >>> plt.styles({'marker.tickWidth': 10}, fontSize=64)
        
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