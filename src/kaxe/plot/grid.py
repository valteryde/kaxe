
from io import BytesIO
from typing import Optional, Union
from ..core.styles import AttrObject, AttrMap
from ..core.window import *
from ..core.legend import LegendBox
from ..core.svg import (
    SvgDocument,
    infer_format,
    is_file_path,
    parse_svg_root,
    extract_svg_children,
    embed_svg_children,
    merge_fondi_css,
)
from PIL import Image
from .constants import XYZPLOT


def _cell_supports_svg(plot) -> bool:
    if plot == XYZPLOT or isinstance(plot, str):
        return False
    return getattr(plot, "supports_vector_export", False)


def _grid_has_3d_cells(grid) -> bool:
    for row in grid:
        for plot in row:
            if plot == XYZPLOT or getattr(plot, "identity", None) == XYZPLOT:
                return True
    return False


class Grid(AttrObject):
    """
    Assemble multiple plots in one image.
    
    Examples
    --------
    >>> grid = kaxe.Grid()
    >>> grid.style(width=500, height=500)
    >>> grid.addRow(plt1, plt2)
    >>> grid.addColumn(plt3, plt4)
    >>> grid.show()
    >>> grid.save('fname.png')
    >>> grid.save('fname.svg')  # 2D vector; 3D cells embed as raster
    >>> grid.save('fname.pdf')  # 2D vector PDF; requires kaxe[pdf]

    """

    name = "Grid"

    def __init__(self):
        super().__init__()

        self.grid = []
        self.gridGap = [20, 20]

        # styles
        self.attrmap = AttrMap()
        self.attrmap.default(attr='width', value=2500)
        self.attrmap.default(attr='height', value=2000)
        self.attrmap.default(attr='backgroundColor', value=(255,255,255,255))
        self.attrmap.default(attr='outerPadding', value=[10,10,10,10])
        self.attrmap.default(attr='fontSize', value=50)
        self.attrmap.default(attr='color', value=(0,0,0,255))
        self.setAttrMap(self.attrmap)
        self.attrmap.submit(LegendBox)

        self.style = self.attrmap.style # for backwards compatibility

        self.__legends = []
        self.padding = [0,0,0,0]

        self.__bakedImage__ = False
        self.__bakedSvg__ = None
        self.__bakedPdf__ = None
        self.laterDraws = []


    def help(self):
        print('Please also see the style docstring or style for each plotting window')
        print(self.style.__doc__)


    def legends(self, *legends):
        """
        Set the legends for the grid. All information must be provided for a legend.
        
        Parameters
        ----------
        *legends : list[tuple]
            Diffrent legends consisting of a label, color and symboltype
        
        Examples
        --------
        >>> grid.legends(
            ("A legend", kaxe.Symbol.CROSS, color1),
            ...
            ("N legend", kaxe.Symbol.CIRCLE, colorn),
        )
        """
        
        self.__legends = legends


    def theme(self, theme):
        """Apply a theme dict (e.g. :data:`kaxe.Themes.A4Medium`) to the grid."""
        self.style(**theme)


    def adjust(self, procentWidth, documentFontSize=0.25, documentMarginProcent=1.5, documentWidth=11.8, imageSlimRatio=1):
        """
        Adjust grid size and typography for LaTeX page fractions (same API as :meth:`kaxe.Plot.adjust`).

        Sets width, height, fontSize, outerPadding, and per-cell xNumbers / yNumbers from cell size.
        zNumbers is set when the grid contains 3D plots.

        See :meth:`kaxe.core.window.Window.adjust` for parameter details.
        """
        styles = compute_adjust_styles(
            procentWidth,
            documentFontSize=documentFontSize,
            documentMarginProcent=documentMarginProcent,
            documentWidth=documentWidth,
            imageSlimRatio=imageSlimRatio,
        )
        cols = max((len(row) for row in self.grid), default=1) or 1
        rows = len(self.grid) or 1
        cell_w = styles["width"] // cols
        cell_h = styles["height"] // rows
        x_numbers, y_numbers = compute_axis_numbers(
            cell_w, cell_h, styles["fontSize"]
        )
        axis_kwargs = {
            "xNumbers": x_numbers,
            "yNumbers": y_numbers,
        }
        if _grid_has_3d_cells(self.grid):
            z_extent = min(cell_w, cell_h)
            axis_kwargs["zNumbers"] = compute_axis_numbers(
                z_extent, z_extent, styles["fontSize"]
            )[0]
        self.style(**styles, **axis_kwargs)


    def _axis_style_kwargs(self):
        kwargs = {}
        for attr in ("xNumbers", "yNumbers", "zNumbers"):
            value = self.getAttr(attr)
            if value is not None:
                kwargs[attr] = value
        return kwargs


    def _reset_cell_bake_state(self, plot):
        if plot == XYZPLOT or isinstance(plot, str):
            return
        plot.padding = [0, 0, 0, 0]
        plot.resetAllPushed()
        plot.shapes = []
        plot.__included__ = []
        plot.__baked__ = False
        plot.__bakedImage__ = False


    def _apply_cell_styles(self, plot, cellWidth, cellHeight):
        self._reset_cell_bake_state(plot)
        plot.style(
            width=cellWidth,
            height=cellHeight,
            outerPadding=self.outerPadding,
            fontSize=self.getAttr('fontSize'),
            color=self.getAttr('color'),
            **self._axis_style_kwargs(),
        )


    def _prepare_cells(self, vector: bool = False):
        """Style cells, export to memory, and compute composite layout."""
        grid = self.grid
        gridSize = ((max([len(i) for i in grid])), len(grid))
        self.width, self.height = self.getAttr('width'), self.getAttr('height')
        self.outerPadding = self.getAttr('outerPadding')

        cellWidth, cellHeight = self.width // gridSize[0], self.height // gridSize[1]

        leftpadding = 0
        rightpadding = 0
        toppadding = 0
        bottompadding = 0
        gapcol = 0

        for row in grid:
            for colNum, plot in enumerate(row):
                self._apply_cell_styles(plot, cellWidth, cellHeight)

                memfile = BytesIO()
                plot.showProgressBar = False
                plot.printDebugInfo = False

                if plot == XYZPLOT:
                    plot.forceWidthHeight = True

                if vector and _cell_supports_svg(plot):
                    plot.save(memfile, format="svg")
                else:
                    plot.save(memfile)

                plot.__ioBytes = memfile
                memfile.seek(0)

                if colNum == 0:
                    leftpadding = max(leftpadding, plot.padding[0])
                    bottompadding = max(bottompadding, plot.padding[1])
                else:
                    gapcol = max(gapcol, plot.padding[0] + row[colNum - 1].padding[2])

                if colNum == len(row) - 1:
                    rightpadding = max(rightpadding, plot.padding[2])
                    toppadding = max(toppadding, plot.padding[3])

        gapcol = max(gapcol, self.gridGap[0])

        gaprows = []
        for row_idx in range(len(grid) - 1):
            boundary_gap = 0
            row_above = grid[row_idx]
            row_below = grid[row_idx + 1]
            for col_idx in range(max(len(row_above), len(row_below))):
                if col_idx < len(row_above) and col_idx < len(row_below):
                    above = row_above[col_idx]
                    below = row_below[col_idx]
                    boundary_gap = max(
                        boundary_gap,
                        above.padding[1] + below.padding[3],
                    )
            gaprows.append(max(boundary_gap, self.gridGap[1]))

        num_rows = len(grid)
        largetsRowNumber = max(len(i) for i in grid)
        width = (
            gapcol * (largetsRowNumber - 1)
            + largetsRowNumber * cellWidth
            + leftpadding
            + rightpadding
        )
        height = (
            num_rows * cellHeight
            + sum(gaprows)
            + toppadding
            + bottompadding
        )

        size = (
            width + self.outerPadding[0] + self.outerPadding[2],
            height + self.outerPadding[1] + self.outerPadding[3],
        )

        legend_image = None
        legend_doc = None
        legend_top_margin = 0

        if self.__legends:
            self.legendbox = LegendBox()
            for d in self.__legends:
                self.legendbox.add(*d)

            if vector:
                legend_doc = self.legendbox.finalize_svg_sneaky(self)
                legend_h = legend_doc.height
                legend_top_margin = self.legendbox.getAttr('topMargin')
            else:
                legend_image = self.legendbox.finalize(self, sneaky=True)
                legend_h = legend_image.height
                legend_top_margin = self.legendbox.getAttr('topMargin')

            size = (size[0], size[1] + legend_h + legend_top_margin)

        return {
            "grid": grid,
            "cellWidth": cellWidth,
            "cellHeight": cellHeight,
            "gapcol": gapcol,
            "gaprows": gaprows,
            "size": size,
            "leftpadding": leftpadding,
            "toppadding": toppadding,
            "bottompadding": bottompadding,
            "legend_image": legend_image,
            "legend_doc": legend_doc,
            "legend_top_margin": legend_top_margin,
        }


    def _composite_png(self, layout: dict) -> Image.Image:
        grid = layout["grid"]
        size = layout["size"]
        cellWidth = layout["cellWidth"]
        cellHeight = layout["cellHeight"]
        gapcol = layout["gapcol"]
        gaprows = layout["gaprows"]
        leftpadding = layout["leftpadding"]
        toppadding = layout["toppadding"]

        image = Image.new('RGBA', size, self.getAttr('backgroundColor'))

        legend_image = layout["legend_image"]
        if legend_image is not None:
            image.alpha_composite(
                legend_image,
                (
                    image.width // 2 - legend_image.width // 2,
                    image.height - legend_image.height - self.outerPadding[3],
                ),
            )

        y = toppadding + self.outerPadding[1]

        for row_idx, row in enumerate(grid):
            x = leftpadding + self.outerPadding[0]

            for plot in row:
                img = Image.open(plot.__ioBytes)
                plot.__ioBytes.seek(0)
                image.paste(img, (x - plot.padding[0], y - plot.padding[3]))
                x += cellWidth + gapcol

            if row_idx < len(grid) - 1:
                y += cellHeight + gaprows[row_idx]

        return image


    def _composite_doc(self, layout: dict) -> SvgDocument:
        size = layout["size"]
        grid = layout["grid"]
        cellWidth = layout["cellWidth"]
        cellHeight = layout["cellHeight"]
        gapcol = layout["gapcol"]
        gaprows = layout["gaprows"]
        leftpadding = layout["leftpadding"]
        toppadding = layout["toppadding"]

        doc = SvgDocument(size)
        bg = self.getAttr('backgroundColor')
        if bg[3] != 0:
            doc.add_rect(0, 0, size[0], size[1], bg)

        legend_doc = layout["legend_doc"]
        if legend_doc is not None:
            lx = size[0] // 2 - legend_doc.width // 2
            ly = size[1] - legend_doc.height - self.outerPadding[3]
            embed_svg_children(doc, list(legend_doc._elements), lx, ly)
            merge_fondi_css(doc, legend_doc._fondi_font_css)

        y = toppadding + self.outerPadding[1]

        for row_idx, row in enumerate(grid):
            x = leftpadding + self.outerPadding[0]

            for plot in row:
                px = x - plot.padding[0]
                py = y - plot.padding[3]

                if _cell_supports_svg(plot):
                    plot.__ioBytes.seek(0)
                    xml = plot.__ioBytes.read().decode("utf-8")
                    root = parse_svg_root(xml)
                    children, fondi_css = extract_svg_children(root)
                    embed_svg_children(doc, children, px, py)
                    merge_fondi_css(doc, fondi_css)
                else:
                    plot.__ioBytes.seek(0)
                    img = Image.open(plot.__ioBytes)
                    doc.add_image(img, px, py, y_coord="top")

                x += cellWidth + gapcol

            if row_idx < len(grid) - 1:
                y += cellHeight + gaprows[row_idx]

        return doc

    def _composite_svg(self, layout: dict) -> str:
        return self._composite_doc(layout).serialize()


    def __bake__(self):
        layout = self._prepare_cells(vector=False)
        image = self._composite_png(layout)
        self.__bakedImage__ = image
        return image


    def __bake_svg__(self) -> str:
        layout = self._prepare_cells(vector=True)
        xml = self._composite_svg(layout)
        self.__bakedSvg__ = xml
        return xml

    def __bake_pdf__(self) -> bytes:
        layout = self._prepare_cells(vector=True)
        pdf_bytes = self._composite_doc(layout).to_pdf()
        self.__bakedPdf__ = pdf_bytes
        return pdf_bytes

    
    def addRow(self, *row:list):
        """
        Adds a row of plots to the grid.

        Parameters
        ----------
        row : list
            A list of plots to be added as a row in the grid.

        """

        self.grid.append(row)


    def addColumn(self, *column:list):
        """
        Adds a column of plots to the grid.

        Parameters
        ----------
        column : list
            A list of plots to be added as a column in the grid.
        """

        for i, plot in enumerate(column):
            
            if i >= len(self.grid):
                self.grid.append([])

            self.grid[i].append(plot)

    
    def save(self, fname: Union[str, BytesIO], format: Optional[str] = None):
        fmt = infer_format(fname, format)

        if fmt == "svg":
            if self.__bakedSvg__ is not None:
                xml = self.__bakedSvg__
            else:
                xml = self.__bake_svg__()

            if fname is not None:
                if is_file_path(fname):
                    with open(fname, 'w', encoding='utf-8') as f:
                        f.write(xml)
                else:
                    fname.write(xml.encode('utf-8'))
            return

        if fmt == "pdf":
            if self.__bakedPdf__ is not None:
                pdf_bytes = self.__bakedPdf__
            else:
                pdf_bytes = self.__bake_pdf__()

            if fname is not None:
                if is_file_path(fname):
                    with open(fname, 'wb') as f:
                        f.write(pdf_bytes)
                else:
                    fname.write(pdf_bytes)
            return

        if self.__bakedImage__:
            if is_file_path(fname):
                self.__bakedImage__.save(fname)
            else:
                self.__bakedImage__.save(fname, format="png")
            return

        img = self.__bake__()

        if isinstance(fname, str):
            img.save(fname)
        else:
            img.save(fname, format="png")


    def show(self):
        """
        Show the current image using `Pillow.Image.Show`
        
        If a cached image is available, it will be used to save the file.
        Otherwise, the image will be generated and then saved.

        Examples
        --------
        >>> plt.show( )
        """

        fname = 'plot{}.png'.format(''.join([str(randint(0,9)) for i in range(10)]))

        if terminaltype != "terminal":
            self.save(fname)
            i = display.Image(filename=fname, width=800, unconfined=True)
            display.display(i)
            os.remove(fname)

        else:
            
            self.save(fname)
            pilImage = Image.open(fname)
            pilImage.show()
            os.remove(fname)

        return fname


    def getSize(self):
        if self.__bakedImage__:
            return self.__bakedImage__.size
        layout = self._prepare_cells(vector=False)
        return layout["size"]
