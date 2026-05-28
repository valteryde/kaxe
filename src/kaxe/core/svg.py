"""SVG document builder for Kaxe vector export."""

from __future__ import annotations

import base64
import copy
import io
import math
import os
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Any, Optional, Union

from PIL import Image

from .color import to_rgba

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)


def flip_y(y: float, height: int) -> float:
    """Convert kaxe y-up coordinate to SVG y-down."""
    return height - y


def rgba_to_svg(color: tuple) -> tuple[str, Optional[float]]:
    """Return (fill/stroke color string, opacity or None)."""
    r, g, b, a = to_rgba(color)
    alpha = a / 255.0
    opacity = None if alpha >= 1.0 else round(alpha, 4)
    return f"rgb({r},{g},{b})", opacity


def _apply_color(attribs: dict[str, str], color: tuple, *, stroke: bool = False) -> None:
    value, opacity = rgba_to_svg(color)
    key = "stroke" if stroke else "fill"
    attribs[key] = value
    if opacity is not None:
        attribs["opacity"] = str(opacity)


def pil_to_data_uri(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


class SvgDocument:
    """Collects SVG elements and serializes to XML."""

    def __init__(self, size: tuple[int, int]):
        self._width, self._height = int(size[0]), int(size[1])
        self._elements: list[ET.Element] = []
        self._fondi_font_css: Optional[str] = None
        self._clip_defs: list[ET.Element] = []
        self._clip_counter = 0
        self._active_group: Optional[ET.Element] = None

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    def flip_y(self, y: float) -> float:
        return flip_y(y, self._height)

    def _register_clip_rect(self, x: float, y: float, width: float, height: float) -> str:
        clip_id = f"kaxe-clip-{self._clip_counter}"
        self._clip_counter += 1
        clip_path = ET.Element(
            f"{{{SVG_NS}}}clipPath",
            {"id": clip_id},
        )
        ET.SubElement(
            clip_path,
            f"{{{SVG_NS}}}rect",
            {
                "x": str(round(x, 3)),
                "y": str(round(y, 3)),
                "width": str(round(width, 3)),
                "height": str(round(height, 3)),
            },
        )
        self._clip_defs.append(clip_path)
        return clip_id

    def push_clip_layer(self, x: float, y: float, width: float, height: float) -> None:
        """Clip subsequent elements to a rectangle in SVG top-down coordinates."""
        clip_id = self._register_clip_rect(x, y, width, height)
        group = ET.Element(
            f"{{{SVG_NS}}}g",
            {"clip-path": f"url(#{clip_id})"},
        )
        self._elements.append(group)
        self._active_group = group

    def pop_clip_layer(self) -> None:
        self._active_group = None

    def add_element(self, tag: str, attribs: dict[str, Any]) -> ET.Element:
        el = ET.Element(
            f"{{{SVG_NS}}}{tag}",
            {k: str(v) for k, v in attribs.items() if v is not None},
        )
        if self._active_group is not None:
            self._active_group.append(el)
        else:
            self._elements.append(el)
        return el

    def add_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        color: tuple,
        *,
        outline_width: int = 0,
        outline_color: tuple = (0, 0, 0, 255),
    ) -> None:
        svg_y = self.flip_y(y) - height
        if outline_width:
            outer = {
                "x": str(x),
                "y": str(svg_y),
                "width": str(width),
                "height": str(height),
            }
            _apply_color(outer, outline_color)
            self.add_element("rect", outer)
            inset = outline_width
            if 2 * inset < width and 2 * inset < height:
                inner = {
                    "x": str(x + inset),
                    "y": str(svg_y + inset),
                    "width": str(width - 2 * inset),
                    "height": str(height - 2 * inset),
                }
                _apply_color(inner, color)
                self.add_element("rect", inner)
        else:
            attribs = {
                "x": str(x),
                "y": str(svg_y),
                "width": str(width),
                "height": str(height),
            }
            _apply_color(attribs, color)
            self.add_element("rect", attribs)

    def add_line(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        color: tuple,
        width: float = 1,
    ) -> None:
        if width <= 0:
            return
        attribs = {
            "x1": str(x0),
            "y1": str(self.flip_y(y0)),
            "x2": str(x1),
            "y2": str(self.flip_y(y1)),
            "stroke-width": str(width),
            "stroke-linecap": "round",
        }
        _apply_color(attribs, color, stroke=True)
        attribs["fill"] = "none"
        self.add_element("line", attribs)

    def add_circle(
        self,
        cx: float,
        cy: float,
        radius: float,
        color: tuple,
        *,
        fill: bool = True,
        stroke_width: float = 5,
    ) -> None:
        attribs = {
            "cx": str(cx),
            "cy": str(self.flip_y(cy)),
            "r": str(radius),
        }
        if fill:
            _apply_color(attribs, color)
        else:
            attribs["fill"] = "none"
            _apply_color(attribs, color, stroke=True)
            attribs["stroke-width"] = str(stroke_width)
        self.add_element("circle", attribs)

    def add_polygon(self, points: list[tuple[float, float]], color: tuple) -> None:
        if len(points) < 3:
            return
        parts = []
        for x, y in points:
            parts.append(f"{x},{self.flip_y(y)}")
        attribs = {"points": " ".join(parts)}
        _apply_color(attribs, color)
        self.add_element("polygon", attribs)

    def add_polyline(
        self,
        points: list[tuple[float, float]],
        color: tuple,
        width: float = 1,
        *,
        dotted: bool = False,
        dotted_dist: float = 30,
        dashed: bool = False,
        dashed_dist: float = 30,
    ) -> None:
        if len(points) < 2:
            return

        if dotted:
            self._add_dotted_polyline(points, color, width, dotted_dist)
            return

        svg_points = [(x, self.flip_y(y)) for x, y in points]

        if dashed:
            self._add_dashed_polyline(points, color, width, dashed_dist)
            return

        parts = [f"{x},{y}" for x, y in svg_points]
        attribs = {
            "points": " ".join(parts),
            "fill": "none",
            "stroke-width": str(width),
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        }
        _apply_color(attribs, color, stroke=True)
        self.add_element("polyline", attribs)

    def _add_dotted_polyline(
        self,
        points: list[tuple[float, float]],
        color: tuple,
        width: float,
        dot_dist: float,
    ) -> None:
        last = points[0]
        for point in points[1:]:
            dist = math.hypot(point[0] - last[0], point[1] - last[1])
            if dist > dot_dist:
                last = point
                self.add_circle(last[0], last[1], width, color, fill=True)

    def _add_dashed_polyline(
        self,
        points: list[tuple[float, float]],
        color: tuple,
        width: float,
        dash_dist: float,
    ) -> None:
        drew = False
        last = points[0]
        for point in points[1:]:
            dist = math.hypot(point[0] - last[0], point[1] - last[1])
            if dist > dash_dist:
                if not drew:
                    self.add_line(last[0], last[1], point[0], point[1], color, width)
                    drew = True
                else:
                    drew = False
                last = point

    def add_arc_wedge(
        self,
        cx: float,
        cy: float,
        radius: float,
        start_deg: float,
        end_deg: float,
        color: tuple,
    ) -> None:
        """Filled pie wedge; angles follow PIL pieslice convention (0=3 o'clock, CCW)."""
        svg_cy = self.flip_y(cy)
        start_rad = math.radians(start_deg)
        end_rad = math.radians(end_deg)

        x0 = cx + radius * math.cos(start_rad)
        y0 = svg_cy - radius * math.sin(start_rad)
        x1 = cx + radius * math.cos(end_rad)
        y1 = svg_cy - radius * math.sin(end_rad)

        delta = (end_deg - start_deg) % 360
        large_arc = 1 if delta > 180 else 0
        sweep = 1 if delta > 0 else 0

        fill, opacity = rgba_to_svg(color)
        d = (
            f"M {cx},{svg_cy} L {x0},{y0} "
            f"A {radius},{radius} 0 {large_arc},{sweep} {x1},{y1} Z"
        )
        attribs: dict[str, str] = {"d": d, "fill": fill}
        if opacity is not None:
            attribs["opacity"] = str(opacity)
        self.add_element("path", attribs)

    def add_image(
        self,
        img: Image.Image,
        x: float,
        y: float,
        *,
        y_coord: str = "bottom",
        rotate: float = 0,
        rotate_center: Optional[tuple[float, float]] = None,
    ) -> None:
        """Place an image; y is in kaxe coords (y-up) unless y_coord='svg_top'."""
        href = pil_to_data_uri(img)
        if y_coord == "svg_top":
            svg_top = y
        elif y_coord == "top":
            svg_top = self.flip_y(y)
        else:
            svg_top = self.flip_y(y) - img.height
        attribs = {
            "x": str(x),
            "y": str(svg_top),
            "width": str(img.width),
            "height": str(img.height),
            "href": href,
            f"{{{XLINK_NS}}}href": href,
        }
        if rotate:
            cx, cy = rotate_center or (x + img.width / 2, svg_top + img.height / 2)
            attribs["transform"] = f"rotate({-rotate},{cx},{cy})"
        self.add_element("image", attribs)

    def _ensure_fondi_fonts(self) -> None:
        if self._fondi_font_css is not None:
            return
        from fondi.backends.svg import _font_face_css

        self._fondi_font_css = _font_face_css(embed_fonts=True, font_url_prefix="")

    def add_fondi_scene(
        self,
        scene,
        svg_left: float,
        svg_top: float,
        *,
        rotate: float = 0,
        rotate_center: Optional[tuple[float, float]] = None,
    ) -> None:
        """Embed a fondi scene (vector math text) at SVG top-left coordinates."""
        from fondi.backends import render_svg

        self._ensure_fondi_fonts()
        h = max(scene.height, 0)

        mini = render_svg(scene, embed_fonts=False)
        if mini.startswith("<?"):
            mini = mini.split("\n", 1)[1]
        root = ET.fromstring(mini)
        inner = root.find(f"{{{SVG_NS}}}g") or root.find("g")
        if inner is None:
            return

        transform = f"translate({round(svg_left, 3)},{round(svg_top, 3)})"
        if rotate:
            cx, cy = rotate_center or (svg_left + scene.width / 2, svg_top + h / 2)
            transform = (
                f"translate({round(cx, 3)},{round(cy, 3)}) "
                f"rotate({-rotate}) "
                f"translate({round(-cx, 3)},{round(-cy, 3)}) "
                f"{transform}"
            )

        group = ET.Element(f"{{{SVG_NS}}}g", {"transform": transform})
        for child in list(inner):
            group.append(copy.deepcopy(child))
        if self._active_group is not None:
            self._active_group.append(group)
        else:
            self._elements.append(group)

    def serialize(self) -> str:
        root = ET.Element(
            f"{{{SVG_NS}}}svg",
            {
                "version": "1.1",
                "width": str(self._width),
                "height": str(self._height),
                "viewBox": f"0 0 {self._width} {self._height}",
            },
        )
        if self._fondi_font_css is not None or self._clip_defs:
            defs = ET.SubElement(root, f"{{{SVG_NS}}}defs")
            if self._fondi_font_css is not None:
                style = ET.SubElement(defs, f"{{{SVG_NS}}}style")
                style.text = self._fondi_font_css
            for clip_el in self._clip_defs:
                defs.append(clip_el)
        for el in self._elements:
            root.append(el)
        body = ET.tostring(root, encoding="unicode")
        try:
            from fondi.backends.svg import _ascii_safe_svg_markup

            body = _ascii_safe_svg_markup(body)
        except ImportError:
            pass
        return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + body

    def to_pdf(self, fname: Optional[Union[str, BytesIO]] = None) -> bytes:
        """Render this document to PDF bytes via ReportLab."""
        from .svg_pdf import write_pdf

        return write_pdf(self, fname)


def parse_svg_root(xml: str) -> ET.Element:
    """Parse SVG XML and return the root element."""
    if xml.startswith("<?"):
        xml = xml.split("\n", 1)[1]
    root = ET.fromstring(xml)
    if not (root.tag.endswith("svg") or root.tag == "svg"):
        raise ValueError("Expected SVG root element")
    return root


def extract_svg_children(root: ET.Element) -> tuple[list[ET.Element], Optional[str]]:
    """Return drawable children (excluding defs) and optional fondi style text."""
    fondi_css: Optional[str] = None
    children: list[ET.Element] = []
    for child in root:
        local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if local == "defs":
            for sub in child:
                sub_local = sub.tag.split("}")[-1] if "}" in sub.tag else sub.tag
                if sub_local == "style" and sub.text:
                    fondi_css = sub.text
            continue
        children.append(child)
    return children, fondi_css


def embed_svg_children(
    doc: SvgDocument,
    children: list[ET.Element],
    tx: float,
    ty: float,
    *,
    clip_rect: Optional[tuple[float, float, float, float]] = None,
) -> None:
    """Embed copied SVG children at top-left offset (SVG y-down coordinates).

    clip_rect is optional (x, y, width, height) in the embedded cell's local SVG space.
    """
    if not children:
        return
    attribs: dict[str, str] = {
        "transform": f"translate({round(tx, 3)},{round(ty, 3)})",
    }
    if clip_rect is not None:
        cx, cy, cw, ch = clip_rect
        clip_id = doc._register_clip_rect(cx, cy, cw, ch)
        attribs["clip-path"] = f"url(#{clip_id})"
    group = ET.Element(f"{{{SVG_NS}}}g", attribs)
    for child in children:
        group.append(copy.deepcopy(child))
    doc._elements.append(group)


def merge_fondi_css(doc: SvgDocument, *style_texts: Optional[str]) -> None:
    """Set fondi font CSS on doc once (skip duplicates and empty)."""
    if doc._fondi_font_css is not None:
        return
    for text in style_texts:
        if text:
            doc._fondi_font_css = text
            return


def is_file_path(fname: Any) -> bool:
    """Return True when fname is a filesystem path (str or os.PathLike)."""
    return isinstance(fname, (str, os.PathLike))


def infer_format(fname: Union[str, os.PathLike, Any], format: Optional[str] = None) -> str:
    """Infer save format from explicit format, file extension, or default to png."""
    if format is not None:
        fmt = format.lower().lstrip(".")
        if fmt in ("svg", "png", "pdf"):
            return fmt
        raise ValueError(f"Unsupported format: {format}")

    if is_file_path(fname):
        lower = os.fspath(fname).lower()
        if lower.endswith(".svg"):
            return "svg"
        if lower.endswith(".png"):
            return "png"
        if lower.endswith(".pdf"):
            return "pdf"

    return "png"
