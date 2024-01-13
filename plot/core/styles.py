
import copy
from types import MappingProxyType, FunctionType

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
    def styles(self, styles:dict={}, **kstyles):

        astyles = {**styles, **kstyles}
        for key in astyles:
            self.setAttr(key, astyles[key])


    def help(self):
        print(f'{bcolors.BOLD}Styles{bcolors.ENDC}')

        for key in self.__defaults__:
            
            print(f'{bcolors.OKBLUE}{key}{bcolors.ENDC}')
            for attr in self.__defaults__[key]:
                
                if key == "global":
                    s = attr
                else:
                    s = f'{key}.{attr}'

                rattr = self.__attrs__.get(key, {}).get(attr)
                if rattr is None:
                    print(f'    {bcolors.OKGREEN}{s}:{bcolors.ENDC} {self.__defaults__[key][attr]}')
                else:
                    print(f'    {bcolors.OKGREEN}{s}:{bcolors.OKCYAN} {rattr}{bcolors.ENDC}')


class AttrObject:
    defaults = {}

    def __init__(self):
        self.__attrs__ = {}
        self.attrmapRef = None

    def setAttrMap(self, attrmap):
        self.attrmapRef = attrmap


    def getAttr(self, attr:str, attrmap:AttrMap|None=None):
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
        if rattr: return rattr

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