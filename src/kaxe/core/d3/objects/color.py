
from ...line import colorBlend


def setColor(c1, c2):
    return (c1[0], c1[1], c1[2], c1[3]), (c2[0], c2[1], c2[2], c2[3])

def blendColors(fg, bg):
    a_fg = float(fg[3]) / 255.0
    a_bg = 1.0 - a_fg

    r = int(fg[0] * a_fg + bg[0] * a_bg)
    g = int(fg[1] * a_fg + bg[1] * a_bg)
    b = int(fg[2] * a_fg + bg[2] * a_bg)
    a = int((fg[3] + bg[3]) / 2)

    return (r, g, b, a)


def addColorToBuffers(zbuffer, colorbuffer, y, x, z, color):
    if zbuffer[y][x] > z:
        if color[3] == 255:
            colorbuffer[y][x] = color
        else:
            colorbuffer[y][x] = blendColors(color, colorbuffer[y][x])
        zbuffer[y][x] = z
    elif colorbuffer[y][x][3] < 255:
        colorbuffer[y][x] = blendColors(color, colorbuffer[y][x])
