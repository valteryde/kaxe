
import copy
from types import MappingProxyType

# COLORS
WHITE = (255,255,255,255)
BLACK = (0,0,0,255)

colorNum = -1
def getRandomColor() -> tuple:
    global colorNum
    colorNum+=1
    return COLORS[colorNum%(len(COLORS))]

def resetColor() -> None:
    global colorNum
    colorNum = -1


COLORS = [
    (222,107,72, 255),
    (91,200,175, 255),
    (8,45,15, 255),
    (247,197,72, 255),
    (6,71,137, 255),
    (251, 111, 146),
    (0, 53,102),
    (188, 108,37),
    (33, 104, 105),
]

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
        self.__attrs__ = {}
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

        if type(obj) is str:
            self.__set__(self.__defaults__,obj, attr, value)
            
        elif obj:
            self.__set__(self.__defaults__, obj.name, attr, value)
        
        else:            
            self.__defaults__['global'][attr] = value
    

    def print(self):
        print(self.__defaults__)
        print(self.__attrs__)


    def setAttr(self, attr, value, obj=None):
        """
        either sumbit by passing an object and retrieve global style
        """

        if type(obj) is str:
            self.__set__(self.__attrs__,obj, attr, value)
            
        elif obj:
            self.__set__(self.__attrs__, obj.name, attr, value)
        
        elif '.' in attr:            
            key, attr = attr.split('.')
            self.__set__(self.__attrs__, key, attr, value)

        else:
            self.__attrs__['global'][attr] = value


    # retrieve a style
    def getAttr(self, attr:str, obj=None):
        """
        either passing an object and retrieve global type stylesheet
        or pass and global variable and retrieve global setting
        """

        # simple quick parse
        if '.' in attr:
            key, attr = attr.split('.')

        else:
            key, attr = 'global', attr

        
        # check object first
        if obj and key == 'global':

            rattr = self.__attrs__.get(obj, {}).get(attr)
            if rattr is not None: return rattr


        # check global from attribute map
        rattr = self.__attrs__.get(key, {}).get(attr)
        if rattr is not None: return rattr


        # object default
        if obj and key == 'global':
        
            rattr = self.__defaults__.get(obj, {}).get(attr)
            if rattr is not None: return rattr


        # global default
        rattr = self.__defaults__.get(key, {}).get(attr)
        if rattr is not None: return rattr

    
    # API to pass along to user
    def styles(self, styles:dict={}, **kstyles):
        print('hejsa')



class AttrObject:
    defaults = {}

    def __init__(self):
        self.__attrs__ = {}
        self.attrmapRef = None

    def setAttrMap(self, attrmap):
        self.attrmapRef = attrmap


    def getAttr(self, attr:str, attrmap:AttrMap|None=None):
        """
        check own stylesheet
        check global stylesheet
        prioritize own attributes
        """

        if not attrmap:
            attrmap = self.attrmapRef

        rattr = self.__attrs__.get(attr, None)
        if rattr: return rattr

        return attrmap.getAttr(attr, self.name)
    
    
    def setAttr(self, attr, value):
        self.__attrs__[attr] = value



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

