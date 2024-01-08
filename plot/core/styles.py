
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
class StyleShape:

    """"
    HVIS DEN IKKE ER defineret i defaults så brug parent. Og hvis parent hellere ikke har den i defaults
    så brug parents parent og så videre indtil der findes en
    """

    # defaults = {}
    # inheritable = {}

    styles = {}
    name = None

    def __init__(self):
        
        self.styles["base"] = {}
        for style in self.defaults:
            self.styles["base"][style] = None


    def style(self, styles:dict={}, **kstyles):
        
        def set(styles, args, val):
            if len(args) == 1:
                styles[args[0]] = val
                return
            set(styles[args[0]], args[1:], val)


        styles = {**styles, **kstyles}
        for key in styles:
            
            style = key.split('.')

            if len(style) == 1:
                style = ('base', style[0])

            set(self.styles, style, styles[key])
            
        print(self.styles)
        
        return self


    def getStyleAttr(self, attr):
        """
        return value from attribute
        """
        # tjek om objektet selv har attributen
        if self.styles["base"].get(attr) and self.styles["base"][attr] is not None:
            return self.styles["base"][attr]

        # tjek om parent har attributen
        if (
            self.styles.get('parent') and  
            self.styles["parent"].styles.get(self.name) and 
            self.styles["parent"].styles[self.name].get(attr) and 
            self.styles["parent"].styles[self.name][attr] is not None
            ):
            return self.styles["parent"].styles[self.name][attr]

        # tjek om den er i defaults
        if self.defaults.get(attr):
            return self.defaults[attr]
    
        # inherit from parents attribute
        if self.styles.get('parent'):
            return self.styles["parent"].getStyleAttr(attr)


    def __inherit__(self, parent):
        """
        get styles from parent
        """
        self.styles["parent"] = parent


    def __expose__(self, child):
        """
        make style from child avaliable from parent through style method
        """
        
        obj = {}
        for style in child.defaults:
            obj[style] = None

        self.styles[child.name] = obj # shallow copy


    def printStyles(self):
        for key in self.styles:
            print(f'{bcolors.OKBLUE}{key}{bcolors.ENDC}')

            for style in self.styles[key]:
                nstyles = self.styles[key][style]

                if key != "base" and key != "parent":
                    stylef = f'{key}.{style}'
                    
                    if self.styles[key].get(style):
                        print(f'    {bcolors.OKGREEN}{stylef}: {bcolors.OKCYAN}{self.styles[key][style]}{bcolors.ENDC}')
                    else:
                        print(f'    {bcolors.OKGREEN}{stylef}: {bcolors.WARNING}NaN{bcolors.ENDC}')
                    continue

                if nstyles is None:
                    print(f'    {bcolors.OKGREEN}{style}: {bcolors.ENDC}{self.getStyleAttr(style)}')
                else:
                    print(f'    {bcolors.OKGREEN}{style}: {bcolors.OKCYAN}{None}{bcolors.ENDC}')

        return self
