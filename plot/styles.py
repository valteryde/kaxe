
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
    (91,200,175, 255),
    (222,107,72, 255),
    (8,45,15, 255),
    (247,197,72, 255),
    (6,71,137, 255),
]
