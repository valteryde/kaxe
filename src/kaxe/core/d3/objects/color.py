
from ...line import colorBlend
from numba import njit, uint8, float32

@njit
def alphaComposite(c1, c2):
    return colorBlend(c1[0], c1[1], c1[2], 255-c2[3], c2[0], c2[1], c2[2], c2[3])


@njit
def blend_colors(color1, color2):
    """
    Blend two RGB colors using alpha blending and return an RGBA color.
    
    Parameters:
        color1: tuple of three ints (0-255), the background color (e.g., (255, 0, 0) for red)
        color2: tuple of three ints (0-255), the foreground color (e.g., (0, 0, 255) for blue)
        alpha: float (0.0 to 1.0), the blending factor (opacity of color2 over color1)
    
    Returns:
        tuple of four ints (r, g, b, 255), the blended color with full opacity
    """
    # Unpack the RGB components of both colors
    r1, g1, b1, alpha = color1
    r2, g2, b2, _ = color2
    
    alpha /= 255

    # Compute blended RGB values using alpha blending
    r = round(r1 * (1 - alpha) + r2 * alpha)
    g = round(g1 * (1 - alpha) + g2 * alpha)
    b = round(b1 * (1 - alpha) + b2 * alpha)
    
    # Clamp values to ensure they stay within the valid range of 0-255
    r = int(max(0, min(255, r)))
    g = int(max(0, min(255, g)))
    b = int(max(0, min(255, b)))
    
    # Return the blended color as an RGBA tuple with alpha set to 255 (fully opaque)
    return (r, g, b, 255)


@njit
def addColorToBuffers(zbuffer, colorbuffer, y, x, z, color):
    if zbuffer[y][x] > z:
        if color[3] == 255:
            colorbuffer[y][x] = color
        else:
            colorbuffer[y][x] = blend_colors(color, colorbuffer[y][x])
        zbuffer[y][x] = z
    elif colorbuffer[y][x][3] < 255:
        colorbuffer[y][x] = blend_colors(colorbuffer[y][x], color)


@njit
def setColor(c1, c2):
    return (c1[0], c1[1], c1[2], c1[3]), (c2[0], c2[1], c2[2], c2[3])

@njit
def blend_colors(fg, bg):
    a_fg = float32(fg[3]) / float32(255.0)  # Normalize foreground alpha
    a_bg = float32(1.0) - a_fg              # Background contribution
    
    r = uint8(fg[0] * a_fg + bg[0] * a_bg)
    g = uint8(fg[1] * a_fg + bg[1] * a_bg)
    b = uint8(fg[2] * a_fg + bg[2] * a_bg)
    a = uint8(fg[3])  # Preserve foreground alpha as uint8
    
    return (r, g, b, a)


@njit
def addColorToBuffers(zbuffer, colorbuffer, y, x, z, color):
    if zbuffer[y][x] > z:
        if color[3] == 255:
            colorbuffer[y][x] = color
        else:
            colorbuffer[y][x] = blend_colors(color, colorbuffer[y][x])
        zbuffer[y][x] = z
    elif colorbuffer[y][x][3] < 255:
        colorbuffer[y][x] = blend_colors(color, colorbuffer[y][x])
