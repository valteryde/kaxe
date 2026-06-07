
import math
import numbers
import time
import numpy as np
from PIL import Image

# math
def intersectLines(n1, p1, n2, p2):
    """
    n1: hat vector
    p1: position
    n2: hat vector
    p2: position
    """

    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]
    a1 = n1[0]
    a2 = n2[0]
    b1 = n1[1]
    b2 = n2[1]

    #x = ((-y1 + y2)*b1*b2 - b2*a1*x1 + x2*b1*a2)/(-a1*b2 + a2*b1)
    
    try:
        x = (a1*b2*x1 - a2*b1*x2 + b1*b2*y1 - b1*b2*y2)/(a1*b2 - a2*b1)
    except ZeroDivisionError: #parrallel
        return None
    try:
        y = (n1[0]*(x-p1[0]))/(-n1[1]) + p1[1]
    except ZeroDivisionError:
        y = (n2[0]*(x-p2[0]))/(-n2[1]) + p2[1]

    return x, y


def vdiff(v1, v2):
    return [v2[i]-v1[i] for i in range(len(v1))]


def vlen(v):
    return math.sqrt(sum([i**2 for i in v]))


def contour_label_angle(func, parent, px, py, polyline=None, tangent_window=40):
    """Readable tangent angle in degrees for ``Text.rotate`` at pixel (px, py).

    Uses the function gradient mapped into pixel space (matplotlib clabel style:
    arctan2 of the tangent vector in kaxe y-up coordinates, then keep text
    right-side up). The returned value is passed directly to ``Text.rotate`` /
    ``PIL.Image.rotate`` (SVG export negates internally to match).
    """
    del polyline, tangent_window

    x, y = parent.inversepixel(px, py)
    if x is None or y is None:
        return 0

    scale = max(abs(x), abs(y), 1.0)
    h = 1e-4 * scale

    try:
        fx = (func(x + h, y) - func(x - h, y)) / (2 * h)
        fy = (func(x, y + h) - func(x, y - h)) / (2 * h)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0

    tx, ty = -fy, fx
    if tx == 0 and ty == 0:
        return 0

    px0, py0 = parent.pixel(x, y)
    px1, py1 = parent.pixel(x + tx, y + ty)
    if px0 is None or py0 is None or px1 is None or py1 is None:
        return 0

    dx = px1 - px0
    dy = py1 - py0
    if dx == 0 and dy == 0:
        return 0

    rotation = math.degrees(math.atan2(dy, dx))
    rotation = (rotation + 90) % 180 - 90
    return rotation


def bbox_intersects_box(bbox, box_ltrb):
    """Return True if bbox intersects box_ltrb.

    ``bbox`` is ``(left, top, width, height)``; ``box_ltrb`` is
    ``[left, top, right, bottom]`` (same as ``windowBox``).
    """
    left, top, width, height = bbox
    right = left + width
    bottom = top + height
    box_left, box_top, box_right, box_bottom = box_ltrb
    return not (
        right <= box_left
        or left >= box_right
        or bottom <= box_top
        or top >= box_bottom
    )


def intersect_bbox_with_box(bbox, box_ltrb):
    """Return intersection of bbox with box_ltrb as (left, top, w, h), or None."""
    left, top, width, height = bbox
    right = left + width
    bottom = top + height
    box_left, box_top, box_right, box_bottom = box_ltrb

    ix0 = max(left, box_left)
    iy0 = max(top, box_top)
    ix1 = min(right, box_right)
    iy1 = min(bottom, box_bottom)

    if ix0 >= ix1 or iy0 >= iy1:
        return None
    return (int(ix0), int(iy0), int(ix1 - ix0), int(iy1 - iy0))


def bbox_overlaps(a, b, padding=0):
    """Return True if two axis-aligned boxes overlap.

    Each box is ``(left, top, width, height)`` as returned by ``Text.getBoundingBox()``.
    """
    ax, ay, aw, ah = a
    bx, by, bw, bh = b

    a_center = (ax + aw / 2, ay + ah / 2)
    b_center = (bx + bw / 2, by + bh / 2)
    a_size = (aw + 2 * padding, ah + 2 * padding)
    b_size = (bw + 2 * padding, bh + 2 * padding)

    a_top_right = (a_center[0] + a_size[0] / 2, a_center[1] + a_size[1] / 2)
    a_bottom_left = (a_center[0] - a_size[0] / 2, a_center[1] - a_size[1] / 2)
    b_top_right = (b_center[0] + b_size[0] / 2, b_center[1] + b_size[1] / 2)
    b_bottom_left = (b_center[0] - b_size[0] / 2, b_center[1] - b_size[1] / 2)

    return not (
        a_top_right[0] < b_bottom_left[0]
        or a_bottom_left[0] > b_top_right[0]
        or a_top_right[1] < b_bottom_left[1]
        or a_bottom_left[1] > b_top_right[1]
    )


def resample_polyline(points, spacing):
    """
    Emit points every `spacing` pixels along polyline arc length.

    Points are placed at uniform screen-space intervals by interpolating
    along segments, so output density is non-uniform in data/index space.
    """
    if spacing <= 0 or len(points) < 2:
        return list(points)

    result = [points[0]]
    dist_since_last = 0.0
    prev = points[0]

    for i in range(1, len(points)):
        cur = points[i]
        seg_dx = cur[0] - prev[0]
        seg_dy = cur[1] - prev[1]
        seg_len = math.hypot(seg_dx, seg_dy)

        if seg_len == 0:
            prev = cur
            continue

        pos_on_seg = 0.0
        while dist_since_last + (seg_len - pos_on_seg) >= spacing:
            need = spacing - dist_since_last
            pos_on_seg += need
            t = pos_on_seg / seg_len
            result.append((prev[0] + t * seg_dx, prev[1] + t * seg_dy))
            dist_since_last = 0.0

        dist_since_last += seg_len - pos_on_seg
        prev = cur

    last = points[-1]
    if result[-1] != last:
        result.append(last)

    return result


def vectorScalar(v, s):
    return [i*s for i in v]


def addVector(*vs):
    return [sum([vs[j][i] for j in range(len(vs))]) for i in range(len(vs[0]))]


def vectorMultipliciation(*vs):

    l = []
    for i in range(len(vs[0])):
        
        r = 1
        for n in vs:
            r *= n[i]

        l.append(r)

    return l


def angleBetweenVectors(v1, v2):
    return math.degrees(math.acos((v1[0]*v2[0]+v1[1]*v2[1])/(vlen(v1)*vlen(v2))))


# window math
def boxIntersectWithLine(box, nvector, pos):

    # special cases
    if nvector[0] == 0:
        return (box[0], pos[1]), (box[2],pos[1])

    if nvector[1] == 0:
        return (pos[0],box[1]), (pos[0],box[3])

    # general case
    p1 = intersectLines(nvector, pos, (1, 0), (box[0], 0))

    if p1[1] < box[1]:
        p1 = intersectLines(nvector, pos, (0, 1), (0, box[1]))
    elif p1[1] > box[3]:
        p1 = intersectLines(nvector, pos, (0, 1), (0, box[3]))

    p2 = intersectLines(nvector, pos, (1, 0), (box[2], 0))

    if p2[1] < box[1]:
        p2 = intersectLines(nvector, pos, (0, 1), (0, box[1]))
    elif p2[1] > box[3]:
        p2 = intersectLines(nvector, pos, (0, 1), (0, box[3]))

    return p1, p2

    # right = intersectLines(nvector, pos, (1, 0), (box[2], 0))
    
    # top = intersectLines(nvector, pos, (0, 1), (0, box[3]))
    
    # return 

def distPointLine(n, pos, point):
    c = -n[0] * pos[0] - n[1] * pos[1]

    return abs(n[0] * point[0] + n[1] * point[1] + c) / math.sqrt(n[0]**2+n[1]**2)


def halfWay(v1, v2):
    return addVector(v1, vectorScalar(vdiff(v1, v2), 1/2))



def insideBox(box, point):
    if round(point[0]) < box[0]:
        return False
    if round(point[0]) > box[2]:
        return False
    if round(point[1]) < box[1]:
        return False
    if round(point[1]) > box[3]:
        return False
    return True


def shell(a):
    def __shell__():
        return a

    return __shell__

def closeToZero(v, epsilon=0.001):
    return -epsilon < v < epsilon


def isRealNumber(x):
    if not isinstance(x, numbers.Real):
        return False
    if math.isnan(x):
        return False
    return True


def getbbox(image:Image.Image, needle:tuple) -> list:

    # Convert image to NumPy array and int16 to handle subtraction safely
    image_np = np.array(image).astype(np.int16)
    needle = np.array(needle, dtype=np.int16)
    tolerance = 1

    # Create a mask of pixels that are NOT equal to the needle
    diff = np.abs(image_np - needle)
    non_background_mask = np.any(diff > tolerance, axis=-1)  # True where pixel != needle

    # Find where non-background pixels are
    rows, cols = np.where(non_background_mask)

    if len(rows) == 0 or len(cols) == 0:
        return [0, 0, *image.size]
    else:
        y_min, y_max = rows.min(), rows.max()
        x_min, x_max = cols.min(), cols.max()
        bbox = (int(x_min), int(y_min), int(x_max + 1), int(y_max + 1))
        return bbox


def to_numpy(im):
    im.load()
    # unpack data
    e = Image._getencoder(im.mode, 'raw', im.mode)
    e.setimage(im.im, (0, 0) + im.size)

    # NumPy buffer for the result
    shape, typestr = Image._conv_type_shape(im)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        l, s, d = e.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise RuntimeError("encoder error %d in tobytes" % s)
    return data
