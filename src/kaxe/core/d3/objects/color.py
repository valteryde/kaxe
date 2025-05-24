
from ...line import colorBlend
from numba import njit, uint8, float32


@njit
def setColor(c1, c2):
    return (c1[0], c1[1], c1[2], c1[3]), (c2[0], c2[1], c2[2], c2[3])

@njit
def blendColors(fg, bg):
    a_fg = float32(fg[3]) / float32(255.0)  # Normalize foreground alpha
    a_bg = float32(1.0) - a_fg              # Background contribution
    
    r = uint8(fg[0] * a_fg + bg[0] * a_bg)
    g = uint8(fg[1] * a_fg + bg[1] * a_bg)
    b = uint8(fg[2] * a_fg + bg[2] * a_bg)
    a = uint8((fg[3] + bg[3])/2)  # Preserve foreground alpha as uint8
    
    return (r, g, b, a)


@njit
def addColorToBuffers(zbuffer, colorbuffer, y, x, z, color):
    if zbuffer[y][x] > z:
        if color[3] == 255:
            colorbuffer[y][x] = color
        else:
            colorbuffer[y][x] = blendColors(color, colorbuffer[y][x])
        zbuffer[y][x] = z
    elif colorbuffer[y][x][3] < 255:
        colorbuffer[y][x] = blendColors(color, colorbuffer[y][x])
