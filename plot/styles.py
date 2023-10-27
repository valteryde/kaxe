
import pyglet as pg


# COLORS
WHITE = (255,255,255,255)
BLACK = (0,0,0,255)

colorNum = -1
def getRandomColor() -> tuple:
    global colorNum
    colorNum+=1
    return COLORS[colorNum%(len(COLORS))]

COLORS = [
    (91,200,175, 150),
    (222,107,72, 150),
    (8,45,15, 150),
    (247,197,72, 150),
    (6,71,137, 150),
]

# SYMBOLS
CIRCLE = 'o'
RECTANGLE = 'RECT'
TRIANGLE = 'TRI'
STAR = 'STAR'
