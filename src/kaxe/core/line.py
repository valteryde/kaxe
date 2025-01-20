
from numba import jit
import numpy as np

# DRAW LINES
@jit
def trapez(y,y0,w):
    return np.clip(np.minimum(y+1+w/2-y0, -y+1+w/2+y0),0,1)

def weighted_line(r0, c0, r1, c1, w, rmin=0, rmax=np.inf):
    
    if r0 == r1 and c0 == c1:
        return [], [], []

    # The algorithm below works fine if c1 >= c0 and c1-c0 >= abs(r1-r0).
    # If either of these cases are violated, do some switches.
    if abs(c1-c0) < abs(r1-r0):
        # Switch x and y, and switch again when returning.
        xx, yy, val = weighted_line(c0, r0, c1, r1, w, rmin=rmin, rmax=rmax)
        return (yy, xx, val)

    # At this point we know that the distance in columns (x) is greater
    # than that in rows (y). Possibly one more switch if c0 > c1.
    if c0 > c1:
        return weighted_line(r1, c1, r0, c0, w, rmin=rmin, rmax=rmax)

    # The following is now always < 1 in abs
    slope = (r1-r0) / (c1-c0)

    # Adjust weight by the slope
    w *= np.sqrt(1+np.abs(slope)) / 2

    # We write y as a function of x, because the slope is always <= 1
    # (in absolute value)
    x = np.arange(c0, c1+1, dtype=float)
    y = x * slope + (c1*r0-c0*r1) / (c1-c0)

    # Now instead of 2 values for y, we have 2*np.ceil(w/2).
    # All values are 1 except the upmost and bottommost.
    thickness = np.ceil(w/2)
    yy = (np.floor(y).reshape(-1,1) + np.arange(-thickness-1,thickness+2).reshape(1,-1))
    xx = np.repeat(x, yy.shape[1])
    vals = trapez(yy, y.reshape(-1,1), w).flatten()

    yy = yy.flatten()

    # Exclude useless parts and those outside of the interval
    # to avoid parts outside of the picture
    mask = np.logical_and.reduce((yy >= rmin, yy < rmax, vals > 0))

    return (yy[mask].astype(int), xx[mask].astype(int), vals[mask])

@jit
def colorBlend(ar, ag, ab, aa, br, bg, bb, ba):
    # even faster but only works when all values are in range 0 to 255
    
    alpha = (255 - (255 - ba)*(255 - aa))
    red   = (br   * (255 - aa) + ar   * aa) / 255
    green = (bg * (255 - aa) + ag * aa) / 255
    blue  = (bb  * (255 - aa) + ab  * aa) / 255

    return (int(red), int(green), int(blue), int(alpha))


def drawLineOnPillowImage(
            surface,
            x0,
            y0,
            x1,
            y1,
            color,
            thickness
        ):
    
    a, b, c = weighted_line(x0, y0, x1, y1, thickness)

    pixels = surface.load()

    if len(color) < 4:
        color = list(color)
        color.append(255)


    for i in range(len(a)):

        try:
            pos = (a[i], b[i])
            newcolor = colorBlend(*color[:3], int(color[3]*c[i]), *pixels[pos])
            pixels[pos] = tuple(newcolor)
        except IndexError:
            pass