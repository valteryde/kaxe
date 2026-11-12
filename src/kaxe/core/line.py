import math
import numpy as np
from PIL import Image
from .color import to_rgba

# DRAW LINES
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

def colorBlend(ar, ag, ab, aa, br, bg, bb, ba):
    # even faster but only works when all values are in range 0 to 255
    
    alpha = (255 - (255 - ba)*(255 - aa))
    red   = (br   * (255 - aa) + ar   * aa) / 255
    green = (bg * (255 - aa) + ag * aa) / 255
    blue  = (bb  * (255 - aa) + ab  * aa) / 255

    return int(red), int(green), int(blue), int(alpha)


def _blend_slice_rgba(region: np.ndarray, r: int, g: int, b: int, aa: np.ndarray) -> None:
    """Alpha-blend solid RGB with per-pixel alpha ``aa`` (0..255) onto RGBA uint8 ``region`` in-place."""
    inv = 255 - aa
    dst = region.astype(np.uint16)
    region[..., 0] = (dst[..., 0] * inv + r * aa) // 255
    region[..., 1] = (dst[..., 1] * inv + g * aa) // 255
    region[..., 2] = (dst[..., 2] * inv + b * aa) // 255
    region[..., 3] = 255 - ((255 - dst[..., 3]) * inv) // 255


def _axis_aligned_profile(pos: float, thickness: float, limit: int):
    """Return in-bounds pixel indices and trapez weights perpendicular to an axis-aligned line."""
    w_eff = float(thickness) * 0.5
    t_ceil = math.ceil(w_eff / 2.0)
    coords = (math.floor(pos) + np.arange(-t_ceil - 1, t_ceil + 2)).astype(int)
    vals = trapez(coords, pos, w_eff)
    mask = (coords >= 0) & (coords < limit) & (vals > 0)
    return coords[mask], vals[mask]


def _axis_aligned_span(p0: float, p1: float, limit: int):
    """Return clamped inclusive-exclusive integer span ``(lo, hi)`` along an axis-aligned line."""
    lo_f, hi_f = (p0, p1) if p0 <= p1 else (p1, p0)
    if hi_f < 0 or lo_f >= limit:
        return None
    clamped_lo = max(lo_f, -1.0)
    clamped_hi = min(hi_f, float(limit))
    pts = np.arange(clamped_lo, clamped_hi + 1.0, dtype=float).astype(int)
    pts = pts[(pts >= 0) & (pts < limit)]
    if len(pts) == 0:
        return None
    return int(pts[0]), int(pts[-1]) + 1


def _blend_into_surface_crop(
    surface: Image.Image,
    x_lo: int,
    y_lo: int,
    x_hi: int,
    y_hi: int,
    rows,
    cols,
    r: int,
    g: int,
    b: int,
    aa: np.ndarray,
) -> None:
    """Crop ``surface`` to the line bounding box, alpha-blend, and paste back."""
    crop = surface.crop((x_lo, y_lo, x_hi, y_hi))
    if crop.mode != "RGBA":
        crop = crop.convert("RGBA")
    patch = np.array(crop, dtype=np.uint8)
    sub = patch[rows, cols]
    _blend_slice_rgba(sub, r, g, b, aa)
    patch[rows, cols] = sub
    surface.paste(Image.fromarray(patch, "RGBA"), (x_lo, y_lo))


def drawLineOnPillowImage(
            surface,
            x0,
            y0,
            x1,
            y1,
            color,
            thickness
        ):
    if thickness <= 0:
        return
    if not (math.isfinite(x0) and math.isfinite(y0) and math.isfinite(x1) and math.isfinite(y1)):
        return

    r, g, b, alpha = to_rgba(color)
    if alpha <= 0 or (x0 == x1 and y0 == y1):
        return

    w, h = surface.size
    if w <= 0 or h <= 0:
        return

    buf = getattr(surface, "_kaxe_buf", None)

    if y0 == y1:
        ys, vals = _axis_aligned_profile(y0, thickness, h)
        if len(ys) == 0:
            return
        span = _axis_aligned_span(x0, x1, w)
        if span is None:
            return
        x_lo, x_hi = span
        aa = (alpha * vals).astype(np.uint16)[:, None]
        if buf is not None:
            patch = buf[ys, x_lo:x_hi]
            _blend_slice_rgba(patch, r, g, b, aa)
            buf[ys, x_lo:x_hi] = patch
        else:
            y_lo, y_hi = int(ys.min()), int(ys.max()) + 1
            _blend_into_surface_crop(
                surface, x_lo, y_lo, x_hi, y_hi,
                ys - y_lo, slice(None), r, g, b, aa,
            )
        return

    if x0 == x1:
        xs, vals = _axis_aligned_profile(x0, thickness, w)
        if len(xs) == 0:
            return
        span = _axis_aligned_span(y0, y1, h)
        if span is None:
            return
        y_lo, y_hi = span
        aa = (alpha * vals).astype(np.uint16)[None, :]
        if buf is not None:
            patch = buf[y_lo:y_hi, xs]
            _blend_slice_rgba(patch, r, g, b, aa)
            buf[y_lo:y_hi, xs] = patch
        else:
            x_lo, x_hi = int(xs.min()), int(xs.max()) + 1
            _blend_into_surface_crop(
                surface, x_lo, y_lo, x_hi, y_hi,
                slice(None), xs - x_lo, r, g, b, aa,
            )
        return

    a, b_idx, c = weighted_line(x0, y0, x1, y1, float(thickness))
    if len(a) == 0:
        return
    mask = (a >= 0) & (a < w) & (b_idx >= 0) & (b_idx < h)
    a, b_idx, c = a[mask], b_idx[mask], c[mask]
    if len(a) == 0:
        return

    aa = (alpha * c).astype(np.uint16)
    if buf is not None:
        sub = buf[b_idx, a]
        _blend_slice_rgba(sub, r, g, b, aa)
        buf[b_idx, a] = sub
    else:
        x_lo, x_hi = int(a.min()), int(a.max()) + 1
        y_lo, y_hi = int(b_idx.min()), int(b_idx.max()) + 1
        _blend_into_surface_crop(
            surface, x_lo, y_lo, x_hi, y_hi,
            b_idx - y_lo, a - x_lo, r, g, b, aa,
        )