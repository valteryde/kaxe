"""Geometric helpers for 3D plot axis selection."""

import numpy as np

def sign(p, p1, p2):
    """
    Calculate the signed area of a triangle formed by three points.
    
    This function computes twice the signed area of the triangle (p1, p2, p).
    Used in point-in-triangle tests to determine which side of a line a point lies on.
    
    Parameters
    ----------
    p : array-like
        Test point [x, y]
    p1, p2 : array-like
        Line segment endpoints [x, y]
        
    Returns
    -------
    float
        Positive if p is on left side of line p1->p2, negative if on right side
    """
    return (p[0] - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (p[1] - p2[1])


def isPointInTriangle(p, p1, p2, p3, tol=-1):
    """
    Test if a point lies inside a triangle using the sign method.
    
    Uses three signed area calculations to determine if a point is inside
    a triangle. A point is inside if all three signs are the same (all positive
    or all negative), indicating the point is on the same side of all three edges.
    
    Parameters
    ----------
    p : array-like
        Test point coordinates [x, y]
    p1, p2, p3 : array-like
        Triangle vertex coordinates [x, y]
    tol : float, optional
        Tolerance for boundary cases (default: -1, meaning strict inside test)
        
    Returns
    -------
    bool
        True if point is inside triangle, False otherwise
        
    Notes
    -----
    This is a fast, numerically stable algorithm for point-in-triangle testing.
    The tolerance parameter allows for fuzzy boundary detection.
    """
    d1 = sign(p, p1, p2)
    d2 = sign(p, p2, p3)
    d3 = sign(p, p3, p1)
        
    has_neg = (d1 < -tol) or (d2 < -tol) or (d3 < -tol)
    has_pos = (d1 > tol) or (d2 > tol) or (d3 > tol)
    
    return not (has_neg and has_pos)


def distance_point_to_line(px, py, x1, y1, x2, y2):
    """Calculate the perpendicular distance from a point (px, py) to a line segment (x1, y1) - (x2, y2)"""
    line_mag = np.hypot(x2 - x1, y2 - y1)
    if line_mag == 0:
        return np.hypot(px - x1, py - y1)
    
    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
    u = np.clip(u, 0, 1)
    
    closest_x = x1 + u * (x2 - x1)
    closest_y = y1 + u * (y2 - y1)
    
    return np.hypot(px - closest_x, py - closest_y)


