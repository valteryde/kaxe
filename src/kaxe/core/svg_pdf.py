"""Convert Kaxe SvgDocument trees to vector PDF via ReportLab."""

from __future__ import annotations

import base64
import io
import logging
import math
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Union

from PIL import Image

from .svg import SVG_NS, XLINK_NS, is_file_path

if TYPE_CHECKING:
    from .svg import SvgDocument

_PDF_INSTALL_HINT = "PDF export requires reportlab. Install with: pip install kaxe[pdf]"
_FONDI_FONTS_REGISTERED = False
_OTF_TTF_CACHE: dict[str, bytes] = {}

_TRANSFORM_RE = re.compile(
    r"(translate|rotate|matrix)\s*\(([^)]*)\)"
)
_PATH_CMD_RE = re.compile(r"([MLAZ])\s*([^MLAZ]*)", re.IGNORECASE)


def _require_reportlab():
    try:
        import reportlab  # noqa: F401
    except ImportError as exc:
        raise ImportError(_PDF_INSTALL_HINT) from exc


def _local_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _attr(el: ET.Element, name: str) -> Optional[str]:
    if name in el.attrib:
        return el.attrib[name]
    for key, value in el.attrib.items():
        if key.split("}")[-1] == name:
            return value
    return None


def _parse_float(value: Optional[str], default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def _parse_rgb(value: Optional[str]) -> tuple[float, float, float]:
    if not value or value == "none":
        return 0.0, 0.0, 0.0
    match = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", value)
    if match:
        return float(match.group(1)), float(match.group(2)), float(match.group(3))
    return 0.0, 0.0, 0.0


def _rl_color(value: Optional[str], opacity: Optional[str] = None):
    from reportlab.lib.colors import Color

    r, g, b = _parse_rgb(value)
    alpha = float(opacity) if opacity is not None else 1.0
    return Color(r / 255.0, g / 255.0, b / 255.0, alpha=alpha)


def _require_fonttools():
    try:
        import fontTools  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "PDF font embedding requires fonttools. Install with: pip install kaxe[pdf]"
        ) from exc


def _convert_otf_to_ttf_bytes(otf_path: os.PathLike[str]) -> bytes:
    path = os.fspath(otf_path)
    cached = _OTF_TTF_CACHE.get(path)
    if cached is not None:
        return cached

    _require_fonttools()
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont, newTable

    def _glyphs_to_quadratic(glyphs):
        quad: dict = {}
        for gname in glyphs.keys():
            tt_pen = TTGlyphPen(glyphs)
            cu2qu_pen = Cu2QuPen(tt_pen, 1.0, reverse_direction=True)
            glyphs[gname].draw(cu2qu_pen)
            quad[gname] = tt_pen.glyph()
        return quad

    font = TTFont(path)
    if font.sfntVersion != "OTTO" or "CFF " not in font:
        buf = io.BytesIO()
        font.save(buf)
        data = buf.getvalue()
        _OTF_TTF_CACHE[path] = data
        return data

    glyph_order = font.getGlyphOrder()
    font["loca"] = newTable("loca")
    glyf = newTable("glyf")
    glyf.glyphOrder = glyph_order
    glyf.glyphs = _glyphs_to_quadratic(font.getGlyphSet())
    font["glyf"] = glyf
    del font["CFF "]
    glyf.compile(font)

    hmtx = font["hmtx"]
    for glyph_name, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            hmtx[glyph_name] = (hmtx[glyph_name][0], glyph.xMin)

    maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = max(
        len(g.components if hasattr(g, "components") else [])
        for g in glyf.glyphs.values()
    )
    maxp.compile(font)

    post = font["post"]
    post.formatType = 2.0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order
    try:
        post.compile(font)
    except OverflowError:
        post.formatType = 3

    font.sfntVersion = "\000\001\000\000"
    buf = io.BytesIO()
    font.save(buf)
    data = buf.getvalue()
    _OTF_TTF_CACHE[path] = data
    return data


def _register_fondi_fonts() -> None:
    global _FONDI_FONTS_REGISTERED
    if _FONDI_FONTS_REGISTERED:
        return

    _require_reportlab()
    import fondi
    from pathlib import Path
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    resources = Path(fondi.__file__).parent / "resources"
    regular_otf = resources / "NewCM10-Regular.otf"
    italic_otf = resources / "NewCM10-Italic.otf"
    fallback_ttf = resources / "cmu.serif-roman.ttf"

    def _register(name: str, otf: Path, ttf_fallback: Optional[Path] = None) -> bool:
        for candidate in (otf, ttf_fallback):
            if not candidate or not candidate.is_file():
                continue
            try:
                if candidate.suffix.lower() == ".otf":
                    data = _convert_otf_to_ttf_bytes(candidate)
                else:
                    data = candidate.read_bytes()
                pdfmetrics.registerFont(TTFont(name, io.BytesIO(data)))
                return True
            except Exception as exc:
                logging.warning("Could not register PDF font %s from %s: %s", name, candidate, exc)
        return False

    if not _register("FondiNewCM", regular_otf, fallback_ttf):
        logging.warning("Fondi regular font unavailable; PDF math labels will use Helvetica")
        _FONDI_FONTS_REGISTERED = True
        return

    if _register("FondiNewCM-Italic", italic_otf):
        pdfmetrics.registerFontFamily(
            "FondiNewCM",
            normal="FondiNewCM",
            italic="FondiNewCM-Italic",
        )
    else:
        pdfmetrics.registerFontFamily(
            "FondiNewCM",
            normal="FondiNewCM",
            italic="FondiNewCM",
        )

    _FONDI_FONTS_REGISTERED = True


def _resolve_font_name(family: Optional[str], style: Optional[str]) -> str:
    if family == "FondiNewCM" and style == "italic":
        return "FondiNewCM-Italic"
    if family == "FondiNewCM":
        return "FondiNewCM"
    if family:
        logging.warning("Unknown PDF font family %r; using Helvetica", family)
    return "Helvetica"


@dataclass
class _Matrix:
    a: float = 1.0
    b: float = 0.0
    c: float = 0.0
    d: float = 1.0
    e: float = 0.0
    f: float = 0.0

    def multiply(self, other: "_Matrix") -> "_Matrix":
        return _Matrix(
            a=self.a * other.a + self.c * other.b,
            b=self.b * other.a + self.d * other.b,
            c=self.a * other.c + self.c * other.d,
            d=self.b * other.c + self.d * other.d,
            e=self.a * other.e + self.c * other.f + self.e,
            f=self.b * other.e + self.d * other.f + self.f,
        )

    def map_point(self, x: float, y: float) -> tuple[float, float]:
        return (
            self.a * x + self.c * y + self.e,
            self.b * x + self.d * y + self.f,
        )


def _is_identity(matrix: _Matrix, tol: float = 1e-9) -> bool:
    return (
        abs(matrix.a - 1.0) < tol
        and abs(matrix.d - 1.0) < tol
        and abs(matrix.b) < tol
        and abs(matrix.c) < tol
        and abs(matrix.e) < tol
        and abs(matrix.f) < tol
    )


def _matrix_to_reportlab_transform(matrix: _Matrix, height: int, *, nested: bool) -> list[float]:
    """Map SVG-local y-down coords to ReportLab parent coords via Group.transform."""
    # Conjugate y-down SVG affine with flip-to-y-up: T(height) * M * F, F:(x,y)->(x,-y)
    f = height if not nested else 0.0
    return [
        matrix.a,
        -matrix.b,
        -matrix.c,
        matrix.d,
        matrix.e,
        f + matrix.f,
    ]


def _parse_transform(transform: Optional[str]) -> _Matrix:
    matrix = _Matrix()
    if not transform:
        return matrix

    for match in _TRANSFORM_RE.finditer(transform.strip()):
        name = match.group(1).lower()
        parts = [p.strip() for p in re.split(r"[\s,]+", match.group(2).strip()) if p.strip()]

        if name == "translate":
            tx = float(parts[0]) if parts else 0.0
            ty = float(parts[1]) if len(parts) > 1 else 0.0
            matrix = matrix.multiply(_Matrix(e=tx, f=ty))
        elif name == "rotate":
            angle = math.radians(float(parts[0]))
            cx = float(parts[1]) if len(parts) > 1 else 0.0
            cy = float(parts[2]) if len(parts) > 2 else 0.0
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            rot = _Matrix(a=cos_a, b=sin_a, c=-sin_a, d=cos_a)
            to_origin = _Matrix(e=-cx, f=-cy)
            back = _Matrix(e=cx, f=cy)
            matrix = matrix.multiply(back.multiply(rot.multiply(to_origin)))
        elif name == "matrix" and len(parts) >= 6:
            matrix = matrix.multiply(
                _Matrix(
                    a=float(parts[0]),
                    b=float(parts[1]),
                    c=float(parts[2]),
                    d=float(parts[3]),
                    e=float(parts[4]),
                    f=float(parts[5]),
                )
            )
    return matrix


class _PdfBuilder:
    def __init__(self, width: int, height: int):
        _require_reportlab()
        from reportlab.graphics.shapes import Drawing

        self.height = height
        self.drawing = Drawing(width, height)
        self._shapes: list[Any] = []

    def _to_rl(
        self,
        matrix: _Matrix,
        x: float,
        y: float,
        *,
        local: bool = False,
    ) -> tuple[float, float]:
        if local:
            return x, -y
        sx, sy = matrix.map_point(x, y)
        return sx, self.height - sy

    def _add(self, shape) -> None:
        self._shapes.append(shape)

    def _render_element(
        self,
        el: ET.Element,
        matrix: _Matrix,
        *,
        local: bool = False,
    ) -> None:
        from reportlab.graphics.shapes import (
            Circle,
            Group,
            Image as RlImage,
            Line,
            Path,
            Polygon,
            PolyLine,
            Rect,
            String,
        )
        from reportlab.lib.utils import ImageReader

        tag = _local_tag(el.tag)
        opacity = _attr(el, "opacity")

        if tag == "g":
            local_transform = _parse_transform(_attr(el, "transform"))
            if _is_identity(local_transform):
                for child in el:
                    self._render_element(
                        child,
                        matrix.multiply(local_transform),
                        local=local,
                    )
                return

            combined = matrix.multiply(local_transform)
            group = Group()
            group.transform = _matrix_to_reportlab_transform(
                combined if not local else local_transform,
                self.height,
                nested=local,
            )
            child_shapes: list[Any] = []
            saved = self._shapes
            self._shapes = child_shapes
            for child in el:
                self._render_element(child, _Matrix(), local=True)
            self._shapes = saved
            for shape in child_shapes:
                group.add(shape)
            if child_shapes:
                self._add(group)
            return

        if tag == "rect":
            x = _parse_float(_attr(el, "x"))
            y = _parse_float(_attr(el, "y"))
            w = _parse_float(_attr(el, "width"))
            h = _parse_float(_attr(el, "height"))
            x0, y0 = self._to_rl(matrix, x, y, local=local)
            x1, y1 = self._to_rl(matrix, x + w, y + h, local=local)
            rect = Rect(
                min(x0, x1),
                min(y0, y1),
                abs(x1 - x0),
                abs(y1 - y0),
                fillColor=_rl_color(_attr(el, "fill"), opacity),
                strokeColor=None,
            )
            self._add(rect)
            return

        if tag == "line":
            x1, y1 = self._to_rl(matrix, _parse_float(_attr(el, "x1")), _parse_float(_attr(el, "y1")), local=local)
            x2, y2 = self._to_rl(matrix, _parse_float(_attr(el, "x2")), _parse_float(_attr(el, "y2")), local=local)
            stroke = _rl_color(_attr(el, "stroke"), opacity)
            width = _parse_float(_attr(el, "stroke-width"), 1.0)
            self._add(Line(x1, y1, x2, y2, strokeColor=stroke, strokeWidth=width))
            return

        if tag == "circle":
            cx, cy = self._to_rl(matrix, _parse_float(_attr(el, "cx")), _parse_float(_attr(el, "cy")), local=local)
            radius = _parse_float(_attr(el, "r"))
            fill = _attr(el, "fill")
            if fill and fill != "none":
                self._add(
                    Circle(
                        cx,
                        cy,
                        radius,
                        fillColor=_rl_color(fill, opacity),
                        strokeColor=None,
                    )
                )
            else:
                self._add(
                    Circle(
                        cx,
                        cy,
                        radius,
                        fillColor=None,
                        strokeColor=_rl_color(_attr(el, "stroke"), opacity),
                        strokeWidth=_parse_float(_attr(el, "stroke-width"), 1.0),
                    )
                )
            return

        if tag == "polygon":
            points = self._parse_points(_attr(el, "points"), matrix, local=local)
            self._add(
                Polygon(
                    points,
                    fillColor=_rl_color(_attr(el, "fill"), opacity),
                    strokeColor=None,
                )
            )
            return

        if tag == "polyline":
            points = self._parse_points(_attr(el, "points"), matrix, local=local)
            self._add(
                PolyLine(
                    points,
                    fillColor=None,
                    strokeColor=_rl_color(_attr(el, "stroke"), opacity),
                    strokeWidth=_parse_float(_attr(el, "stroke-width"), 1.0),
                )
            )
            return

        if tag == "path":
            path = self._parse_path(_attr(el, "d"), matrix, local=local)
            if path is not None:
                path.fillColor = _rl_color(_attr(el, "fill"), opacity)
                path.strokeColor = None
                self._add(path)
            return

        if tag == "image":
            href = _attr(el, "href") or _attr(el, f"{{{XLINK_NS}}}href")
            if not href or not href.startswith("data:image"):
                return
            header, encoded = href.split(",", 1)
            raw = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(raw))
            x = _parse_float(_attr(el, "x"))
            y = _parse_float(_attr(el, "y"))
            w = _parse_float(_attr(el, "width"), img.width)
            h = _parse_float(_attr(el, "height"), img.height)
            image_transform = _parse_transform(_attr(el, "transform"))

            def _add_image_shape() -> None:
                x0, y0 = self._to_rl(_Matrix(), x, y, local=True)
                x1, y1 = self._to_rl(_Matrix(), x + w, y + h, local=True)
                rl_img = RlImage(
                    min(x0, x1),
                    min(y0, y1),
                    abs(x1 - x0),
                    abs(y1 - y0),
                    path=ImageReader(io.BytesIO(raw)),
                )
                self._add(rl_img)

            if _is_identity(image_transform):
                if local:
                    _add_image_shape()
                else:
                    x0, y0 = self._to_rl(matrix, x, y, local=False)
                    x1, y1 = self._to_rl(matrix, x + w, y + h, local=False)
                    self._add(
                        RlImage(
                            min(x0, x1),
                            min(y0, y1),
                            abs(x1 - x0),
                            abs(y1 - y0),
                            path=ImageReader(io.BytesIO(raw)),
                        )
                    )
                return

            combined = matrix.multiply(image_transform)
            group = Group()
            group.transform = _matrix_to_reportlab_transform(
                combined if not local else image_transform,
                self.height,
                nested=local,
            )
            child_shapes: list[Any] = []
            saved = self._shapes
            self._shapes = child_shapes
            _add_image_shape()
            self._shapes = saved
            for shape in child_shapes:
                group.add(shape)
            self._add(group)
            return

        if tag == "text":
            x = _parse_float(_attr(el, "x"))
            y = _parse_float(_attr(el, "y"))
            rl_x, rl_y = self._to_rl(matrix, x, y, local=local)
            text = (el.text or "").strip()
            if not text:
                text = "".join(el.itertext())
            font_name = _resolve_font_name(_attr(el, "font-family"), _attr(el, "font-style"))
            font_size = _parse_float(_attr(el, "font-size"), 12.0)
            anchor = _attr(el, "text-anchor") or "start"
            text_anchor = {"middle": "middle", "end": "end"}.get(anchor, "start")
            self._add(
                String(
                    rl_x,
                    rl_y,
                    text,
                    fontName=font_name,
                    fontSize=font_size,
                    fillColor=_rl_color(_attr(el, "fill"), opacity),
                    textAnchor=text_anchor,
                )
            )
            return

    def _parse_points(
        self,
        value: Optional[str],
        matrix: _Matrix,
        *,
        local: bool = False,
    ) -> list[float]:
        if not value:
            return []
        nums = [float(n) for n in re.split(r"[\s,]+", value.strip()) if n]
        points: list[float] = []
        for i in range(0, len(nums) - 1, 2):
            x, y = self._to_rl(matrix, nums[i], nums[i + 1], local=local)
            points.extend([x, y])
        return points

    def _parse_path(self, d: Optional[str], matrix: _Matrix, *, local: bool = False):
        from reportlab.graphics.shapes import Path

        if not d:
            return None

        path = Path()
        current_x = 0.0
        current_y = 0.0
        start_x = 0.0
        start_y = 0.0
        subpath_start_x = 0.0
        subpath_start_y = 0.0

        for match in _PATH_CMD_RE.finditer(d):
            cmd = match.group(1).upper()
            nums = [float(n) for n in re.split(r"[\s,]+", match.group(2).strip()) if n]

            if cmd == "M" and len(nums) >= 2:
                current_x, current_y = nums[0], nums[1]
                start_x, start_y = current_x, current_y
                subpath_start_x, subpath_start_y = current_x, current_y
                x, y = self._to_rl(matrix, current_x, current_y, local=local)
                path.moveTo(x, y)
            elif cmd == "L" and len(nums) >= 2:
                current_x, current_y = nums[0], nums[1]
                x, y = self._to_rl(matrix, current_x, current_y, local=local)
                path.lineTo(x, y)
            elif cmd == "A" and len(nums) >= 7:
                rx, ry, _, large_arc, sweep, end_x, end_y = nums[:7]
                start_x, start_y = current_x, current_y
                self._append_circular_arc(
                    path,
                    matrix,
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                    rx,
                    bool(int(large_arc)),
                    bool(int(sweep)),
                    local=local,
                )
                current_x, current_y = end_x, end_y
            elif cmd == "Z":
                current_x, current_y = subpath_start_x, subpath_start_y
                x, y = self._to_rl(matrix, current_x, current_y, local=local)
                path.lineTo(x, y)
                path.closePath()

        return path

    def _append_circular_arc(
        self,
        path,
        matrix: _Matrix,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        radius: float,
        large_arc: bool,
        sweep: bool,
        *,
        local: bool = False,
    ) -> None:
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0 or radius == 0:
            x, y = self._to_rl(matrix, x2, y2, local=local)
            path.lineTo(x, y)
            return

        dist = min(dist, 2 * radius)
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        chord = dist / 2
        sagitta_sq = max(radius * radius - chord * chord, 0.0)
        sagitta = math.sqrt(sagitta_sq)

        perp_x = -(y2 - y1) / dist
        perp_y = (x2 - x1) / dist

        cx1 = mid_x + perp_x * sagitta
        cy1 = mid_y + perp_y * sagitta
        cx2 = mid_x - perp_x * sagitta
        cy2 = mid_y - perp_y * sagitta

        start1 = math.atan2(y1 - cy1, x1 - cx1)
        end1 = math.atan2(y2 - cy1, x2 - cx1)
        start2 = math.atan2(y1 - cy2, x1 - cx2)
        end2 = math.atan2(y2 - cy2, x2 - cx2)

        def arc_span(start: float, end: float) -> float:
            span = end - start
            if sweep and span < 0:
                span += 2 * math.pi
            if not sweep and span > 0:
                span -= 2 * math.pi
            return abs(span)

        use_first = arc_span(start1, end1) > math.pi
        if large_arc:
            cx, cy, start, end = (
                (cx1, cy1, start1, end1) if use_first else (cx2, cy2, start2, end2)
            )
        else:
            cx, cy, start, end = (
                (cx1, cy1, start1, end1) if not use_first else (cx2, cy2, start2, end2)
            )

        if sweep and end < start:
            end += 2 * math.pi
        if not sweep and end > start:
            end -= 2 * math.pi

        steps = max(8, int(abs(end - start) / (math.pi / 16)))
        for i in range(1, steps + 1):
            t = start + (end - start) * (i / steps)
            px = cx + radius * math.cos(t)
            py = cy + radius * math.sin(t)
            x, y = self._to_rl(matrix, px, py, local=local)
            path.lineTo(x, y)

    def build(self, elements: list[ET.Element]):
        identity = _Matrix()
        for el in elements:
            self._render_element(el, identity)
        for shape in self._shapes:
            self.drawing.add(shape)
        return self.drawing


def document_to_pdf(doc: "SvgDocument") -> bytes:
    _register_fondi_fonts()
    from reportlab.graphics import renderPDF

    builder = _PdfBuilder(doc.width, doc.height)
    drawing = builder.build(doc._elements)
    buf = io.BytesIO()
    renderPDF.drawToFile(drawing, buf)
    return buf.getvalue()


def write_pdf(doc: "SvgDocument", fname: Optional[Union[str, io.BytesIO]] = None) -> bytes:
    pdf_bytes = document_to_pdf(doc)
    if fname is not None:
        if is_file_path(fname):
            with open(os.fspath(fname), "wb") as f:
                f.write(pdf_bytes)
        else:
            fname.write(pdf_bytes)
    return pdf_bytes


def image_to_pdf_page(img: Image.Image, fname: Optional[Union[str, io.BytesIO]] = None) -> bytes:
    """Wrap a raster image in a single-page PDF."""
    _require_reportlab()
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    width, height = img.size
    buf = io.BytesIO()
    if img.mode != "RGB":
        img = img.convert("RGB")
    png_buf = io.BytesIO()
    img.save(png_buf, format="PNG")
    png_buf.seek(0)

    pdf = canvas.Canvas(buf, pagesize=(width, height))
    pdf.drawImage(ImageReader(png_buf), 0, 0, width=width, height=height)
    pdf.save()
    pdf_bytes = buf.getvalue()

    if fname is not None:
        if is_file_path(fname):
            with open(os.fspath(fname), "wb") as f:
                f.write(pdf_bytes)
        else:
            fname.write(pdf_bytes)
    return pdf_bytes
