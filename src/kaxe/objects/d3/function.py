
from ...core.symbol import symbol as symbols # namespace confusison
from ...plot import identities
from .base import Base3DObject

# 3d
from ...core.d3.objects import Triangle, Line3D, Point3D
from ...core.d3.helper import rc
from ...core.color import Colormaps, Colormap

# other
import numpy as np
import math
import numbers
import time



### OPTIMIZING
def getTriangleNormal(p1, p2, p3):

    Ax, Ay, Az = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    Bx, By, Bz = p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]

    Nx = Ay * Bz - Az * By
    Ny = Az * Bx - Ax * Bz
    Nz = Ax * By - Ay * Bx

    return (Nx, Ny, Nz)

def isHorizontalTriangle(dependantVariable, p1, p2, p3):
    normal = getTriangleNormal(p1, p2, p3)

    if dependantVariable == "z":
        return (
            np.isclose(normal[0], 0) and 
            np.isclose(normal[1], 0) and 
            (not np.isclose(normal[2], 0))
        )
    elif dependantVariable == "y":
        return (
            np.isclose(normal[0], 0) and 
            (not np.isclose(normal[1], 0)) and 
            np.isclose(normal[2], 0)
        )
    elif dependantVariable == "x":
        return (
            (not np.isclose(normal[0], 0)) and 
            np.isclose(normal[1], 0) and 
            np.isclose(normal[2], 0)
        )










class Function3D(Base3DObject):
    """
    Create a Function in 3D given .. math:: z=f(x,y)
    
    Parameters
    ----------
    f : callable
        The function to be plotted.
    color : Colormap, optional
        The colormap to be used for plotting. If None, the standard colormap is used.
    numPoints : int, optional
        The number of points to be used for plotting. If None, defaults to 500 if `fill` is True, otherwise 25.
    fill : bool
        Whether to fill the plot. default is True
    drawDiagonalLines: bool
        Whether to draw diagonal lines in triangles when fill is False. default is False
    excludeLight : bool, optional
        Whether to exclude lighting effects. Default is True.
    
    Methods
    -------
    __call__(x)
        Evaluates the function at a given x value.

    """
    
    def __init__(self, 
                 f, 
                 color:Colormap=None, 
                 numPoints:int=None, 
                 fill:bool=True, 
                 drawDiagonalLines:bool=False, 
                 axis="xy", 
                 excludeLight=True,
                 *args, 
                 **kwargs
        ):
        
        super().__init__()

        self.f = f
        self.axis = ''.join(sorted(axis)) #xy, xz, yz
        self.dependantVariable = "xyz".replace(self.axis[0], '').replace(self.axis[1], '')
        self.otherArgs = args
        self.otherKwargs = kwargs
        self.excludeLight = excludeLight

        self.fill = fill
        self.drawDiagonalLines = drawDiagonalLines
        
        self.supports = [identities.XYZPLOT]
        self.legendSymbol = symbols.RECTANGLE
        self.legendColor = rc()

        self.cmap = color
        if color is None:
            self.cmap = Colormaps.standard

        self.numPoints = numPoints
        if numPoints is None and fill:
            self.numPoints = 500
        elif numPoints is None:
            self.numPoints = 25


    

    def __addTriangle__(self, render, p1, p2, p3, color, isRealpoint):
        
        # dont draw vertical vertices
        if isHorizontalTriangle(self.dependantVariable, p1, p2, p3) and not isRealpoint:
            return

        render.add3DObject(
            Triangle(
                p1,
                p2,
                p3,
                color=color,
                ableToUseLight=not self.excludeLight
            )
        )


    def __fill__(self, render, matrix, xn, yn, color, isRealpoint):
        
        if all(i[0] is not None for i in [matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1]]):
            
            self.__addTriangle__(render, matrix[xn][yn], matrix[xn+1][yn], matrix[xn][yn+1], color, isRealpoint)

        if all(i[0] is not None for i in [matrix[xn+1][yn+1], matrix[xn+1][yn], matrix[xn][yn+1]]):
                    
            self.__addTriangle__(render, matrix[xn+1][yn], matrix[xn+1][yn+1], matrix[xn][yn+1], color, isRealpoint)
        

    def __addTriangleOutline__(self, render, p1, p2, p3, color, isRealpoint, xn, yn):
        
        # dont draw vertical vertices
        if isHorizontalTriangle(self.dependantVariable, p1, p2, p3) and not isRealpoint:
            return

        render.add3DObject(Line3D(p1,p2,color=color))
        
        if self.drawDiagonalLines:
            render.add3DObject(Line3D(p1,p3,color=color))
            render.add3DObject(Line3D(p2,p3,color=color))
            return
        
        # Correcting for not drawing diagonals
        # Here the parrallel lines will have an perpendicalur lines at the end at x=len(self.numPoints) and so on
        if xn == self.numPoints-1:
            render.add3DObject(Line3D(p2,p3,color=color))
        
        if yn == 0:
            render.add3DObject(Line3D(p1,p3,color=color))


    def __outline__(self, render, matrix, xn, yn, color, isRealpoint):
        if all(not np.isnan(i[0]) for i in [matrix[xn, yn], matrix[xn + 1, yn], matrix[xn, yn + 1]]):

            self.__addTriangleOutline__(render, matrix[xn, yn], matrix[xn, yn + 1], matrix[xn + 1, yn], color, isRealpoint, -1, yn)
        
        if all(not np.isnan(i[0]) for i in [matrix[xn + 1, yn + 1], matrix[xn + 1, yn], matrix[xn, yn + 1]]):
            
            self.__addTriangleOutline__(render, matrix[xn, yn + 1], matrix[xn + 1, yn + 1], matrix[xn + 1, yn], color, isRealpoint, xn, -1)


    def _color_grid(self, zmap, zmin, zmax):
        steps = np.array(self.cmap.colorGradientSteps, dtype=np.float32)
        values = np.clip(zmap, zmin, zmax)
        if zmax == zmin:
            return np.repeat(steps[:1], zmap.size, axis=0).reshape(zmap.shape + (4,))

        x = ((values - zmin) / (zmax - zmin)) * (len(steps) - 1)
        x0 = np.floor(x).astype(np.int32)
        x1 = np.ceil(x).astype(np.int32)
        frac = (x - x0)[..., np.newaxis]
        return ((1.0 - frac) * steps[x0] + frac * steps[x1]) / 255.0

    def _maybe_tick_loading(self, render, counter, stride=32):
        if counter & (stride - 1) == 0:
            render.tick_loading()

    def _sample_z_dependent_grid(self, render, parent, xs, ys, x_grid, y_grid, z_grid, realpoint, loading):
        z_lo = parent.window[4]
        z_hi = parent.window[5]

        def sample_loop():
            for xn, x in enumerate(xs):
                if loading:
                    self._maybe_tick_loading(render, xn)
                for yn, y in enumerate(ys):
                    try:
                        z = self.f(x, y, *self.otherArgs, **self.otherKwargs)
                    except Exception:
                        continue
                    if not isinstance(z, numbers.Number):
                        continue
                    if z > z_hi:
                        z = z_hi
                        realpoint[xn, yn] = False
                    if z < z_lo:
                        z = z_lo
                        realpoint[xn, yn] = False
                    z_grid[xn, yn] = z

        with render.profiler.measure('finalize_sample'):
            try:
                z_vals = np.asarray(
                    self.f(x_grid, y_grid, *self.otherArgs, **self.otherKwargs),
                    dtype=np.float64,
                )
            except Exception:
                sample_loop()
                return

            if z_vals.shape != x_grid.shape or not np.issubdtype(z_vals.dtype, np.floating):
                sample_loop()
                return

            if loading:
                render.tick_loading()

            z_vals = z_vals.copy()
            over = z_vals > z_hi
            under = z_vals < z_lo
            realpoint[:] = ~(over | under)
            np.clip(z_vals, z_lo, z_hi, out=z_vals)
            z_grid[:] = z_vals

    def _coords_from_grid(self, parent, x_grid, y_grid, z_grid):
        size = parent.size
        offset = parent.offset
        wl = parent.windowAxisLength
        coords = np.stack([
            size[0] * (x_grid - parent.window[0]) / wl[0] + offset[0],
            size[1] * (y_grid - parent.window[2]) / wl[1] + offset[1],
            size[2] * (z_grid - parent.window[4]) / wl[2] + offset[2],
        ], axis=-1)
        coords[np.isnan(z_grid)] = np.nan
        return coords

    def _build_fill_mesh_arrays(self, coords, realpoint, color_grid, n):
        valid = ~np.isnan(coords[:n, :n, 0])
        if not np.any(valid):
            return None

        flat = valid.ravel()
        c00 = coords[:n, :n].reshape(-1, 3)[flat]
        c10 = coords[1:n + 1, :n].reshape(-1, 3)[flat]
        c01 = coords[:n, 1:n + 1].reshape(-1, 3)[flat]
        c11 = coords[1:n + 1, 1:n + 1].reshape(-1, 3)[flat]
        cell_colors = color_grid[:n, :n].reshape(-1, 4)[flat]
        cell_real = realpoint[:n, :n].ravel()[flat]

        p1s = np.concatenate([c00, c10])
        p2s = np.concatenate([c10, c11])
        p3s = np.concatenate([c01, c01])
        colors = np.concatenate([cell_colors, cell_colors])
        realpoint_flags = np.concatenate([cell_real, cell_real])
        return p1s, p2s, p3s, colors, realpoint_flags


    def finalize(self, parent):

        render = parent.render
        n = self.numPoints
        dep_var = {"z": 0, "y": 1, "x": 2}[self.dependantVariable]
        loading = render.loading_screen_active

        xlen = parent.window[1] - parent.window[0]
        ylen = parent.window[3] - parent.window[2]
        zlen = parent.window[5] - parent.window[4]

        coords = np.full((n + 1, n + 1, 3), np.nan, dtype=np.float64)
        zmap = np.full((n + 1, n + 1), -math.inf, dtype=np.float64)
        realpoint = np.ones((n + 1, n + 1), dtype=np.bool_)

        if self.dependantVariable == "z":
            xs = xlen * (np.arange(n + 1) / n) + parent.window[0]
            ys = ylen * (np.arange(n + 1) / n) + parent.window[2]
            x_grid, y_grid = np.meshgrid(xs, ys, indexing="ij")
            z_grid = np.full_like(x_grid, np.nan, dtype=np.float64)
            self._sample_z_dependent_grid(render, parent, xs, ys, x_grid, y_grid, z_grid, realpoint, loading)
            zmap = np.where(np.isnan(z_grid), -math.inf, z_grid)
            coords = self._coords_from_grid(parent, x_grid, y_grid, z_grid)
        elif self.dependantVariable == "y":
            xs = xlen * (np.arange(n + 1) / n) + parent.window[0]
            ys = zlen * (np.arange(n + 1) / n) + parent.window[4]
            for xn, x in enumerate(xs):
                if loading:
                    self._maybe_tick_loading(render, xn)
                for yn, y in enumerate(ys):
                    try:
                        z = self.f(x, y, *self.otherArgs, **self.otherKwargs)
                    except Exception:
                        continue
                    if not isinstance(z, numbers.Number):
                        continue
                    if z > parent.window[3]:
                        z = parent.window[3]
                        realpoint[xn, yn] = False
                    if z < parent.window[2]:
                        z = parent.window[2]
                        realpoint[xn, yn] = False
                    coords[xn, yn] = parent.pixel(x, z, y)
                    zmap[xn, yn] = y
        else:
            z_coords = zlen * (np.arange(n + 1) / n) + parent.window[4]
            y_coords = ylen * (np.arange(n + 1) / n) + parent.window[2]
            for xn, z_coord in enumerate(z_coords):
                if loading:
                    self._maybe_tick_loading(render, xn)
                for yn, y_coord in enumerate(y_coords):
                    try:
                        x_val = self.f(z_coord, y_coord, *self.otherArgs, **self.otherKwargs)
                    except Exception:
                        continue
                    if not isinstance(x_val, numbers.Number):
                        continue
                    if x_val > parent.window[1]:
                        x_val = parent.window[1]
                        realpoint[xn, yn] = False
                    if x_val < parent.window[0]:
                        x_val = parent.window[0]
                        realpoint[xn, yn] = False
                    coords[xn, yn] = parent.pixel(x_val, y_coord, z_coord)
                    zmap[xn, yn] = x_val

        if self.fill:
            zmin = parent.windowAxis[4]
            zmax = parent.windowAxis[5]
            with render.profiler.measure('finalize_color'):
                color_grid = self._color_grid(zmap, zmin, zmax)
            if loading:
                render.tick_loading()
            with render.profiler.measure('finalize_mesh'):
                mesh = self._build_fill_mesh_arrays(coords, realpoint, color_grid, n)
            if mesh is not None:
                if loading:
                    render.tick_loading()
                p1s, p2s, p3s, colors, realpoint_flags = mesh
                with render.profiler.measure('finalize_upload'):
                    render.addMeshTriangles(
                        p1s,
                        p2s,
                        p3s,
                        colors,
                        dep_var,
                        realpoint_flags,
                        use_light=not self.excludeLight,
                    )
            return

        for xn in range(n):
            for yn in range(n):
                if np.isnan(coords[xn, yn, 0]):
                    continue
                color = self.cmap.getColor(zmap[xn, yn], parent.windowAxis[4], parent.windowAxis[5])
                self.__outline__(render, coords, xn, yn, color, realpoint[xn, yn])

    def legend(self, text:str, color=None, symbol=None):
        """
        Adds a legend
        
        Parameters
        ----------
        text : str
            The text to be displayed in the legend.
        symbol : symbols, optional
            The symbol to be used in the legend.
        color : optional
            The color to be used for the legend text. If not provided, the default color will be used.
        
        Returns
        -------
        self : object
            Returns the instance of the arrow object with the updated legend.        
        """
        

        self.legendText = text

        if color:
            self.legendColor = color

        if symbol:
            self.legendSymbol = symbol

        return self


    def __call__(self, x, y):
        return self.f(x, y, *self.otherArgs, **self.otherKwargs)