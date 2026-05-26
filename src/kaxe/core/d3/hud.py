"""Screen-space footer for the interactive 3D viewer."""

from __future__ import annotations

import os
from typing import Iterable, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


Segment = Tuple[str, Tuple[int, int, int, int]]
Color = Tuple[int, int, int, int]

# Restrained studio palette — warm/cool grays with one sand accent.
INK = (17, 18, 21, 112)
HAIRLINE = (255, 255, 255, 14)
SEPARATOR = (82, 85, 92, 70)
STEEL = (156, 164, 176, 148)
TAUPE = (176, 170, 160, 145)
SLATE = (166, 170, 178, 140)
SAND = (192, 184, 164, 158)
GHOST = (102, 106, 112, 82)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    try:
        import PIL

        candidates.append(
            os.path.join(os.path.dirname(PIL.__file__), "Fonts", "DejaVuSans.ttf")
        )
    except ImportError:
        pass

    candidates.extend(
        [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )

    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue

    return ImageFont.load_default()


def _normalize_angle(angle: float) -> int:
    return int(round(angle % 360))


def _fps_color(fps: int) -> Color:
    if fps >= 45:
        return (186, 188, 184, 175)
    if fps >= 20:
        return (180, 174, 158, 175)
    return (172, 164, 158, 175)


def _text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    if not text:
        return 0
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def _text_height(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[3] - box[1]


def _segments_width(
    draw: ImageDraw.ImageDraw,
    segments: Iterable[Segment],
    font,
    sep: str,
    sep_w: int,
    sep_gap: int,
) -> int:
    width = 0
    count = 0
    for text, _ in segments:
        if not text:
            continue
        width += _text_width(draw, text, font)
        count += 1
    if count > 1:
        width += (sep_w + sep_gap * 2) * (count - 1)
    return width


def _draw_segments(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    segments: Iterable[Segment],
    font,
    sep: str,
    sep_w: int,
    sep_gap: int,
) -> int:
    items = [(text, color) for text, color in segments if text]
    for idx, (text, color) in enumerate(items):
        draw.text((x, y), text, font=font, fill=color)
        x += _text_width(draw, text, font)
        if idx < len(items) - 1:
            x += sep_gap
            draw.text((x, y), sep, font=font, fill=SEPARATOR)
            x += sep_w + sep_gap
    return x


class ViewportHud:
    """Builds a quiet footer bar for the 3D GUI."""

    def __init__(self):
        self.fps = 0
        self.memory_mb = 0.0
        self._image: Optional[Image.Image] = None
        self._cache_key = None

    def update_stats(self, fps: int, memory_mb: float) -> None:
        self.fps = fps
        self.memory_mb = memory_mb
        self._cache_key = None

    def build(
        self,
        rotation: Tuple[float, float],
        auto_rotate: bool,
        gui_width: int,
        gui_height: int,
    ) -> np.ndarray:
        scale = max(gui_height / 750.0, 0.75)
        font_size = max(int(11 * scale), 10)
        footer_h = max(int(24 * scale), 22)
        pad_x = max(int(16 * scale), 12)
        sep_gap = max(int(5 * scale), 4)

        cache_key = (
            self.fps,
            round(self.memory_mb, 1),
            _normalize_angle(rotation[0]),
            _normalize_angle(rotation[1]),
            auto_rotate,
            gui_width,
            footer_h,
            font_size,
        )
        if cache_key == self._cache_key and self._image is not None:
            return np.asarray(self._image)

        font = _load_font(font_size)
        sep = "·"

        azimuth = _normalize_angle(rotation[0])
        elevation = _normalize_angle(rotation[1])

        left: list[Segment] = [
            (f"{self.fps} fps", _fps_color(self.fps)),
            (f"{self.memory_mb:.0f} mb", STEEL),
            (f"{azimuth}°", TAUPE),
            (f"{elevation}°", SLATE),
        ]
        if auto_rotate:
            left.append(("spin", SAND))

        right: list[Segment] = [
            ("drag", GHOST),
            ("space", GHOST),
            ("esc", GHOST),
        ]

        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        text_h = _text_height(probe, "Ag", font)
        sep_w = _text_width(probe, sep, font)
        left_w = _segments_width(probe, left, font, sep, sep_w, sep_gap)
        right_w = _segments_width(probe, right, font, sep, sep_w, sep_gap)

        footer = Image.new("RGBA", (gui_width, footer_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(footer)
        draw.rectangle((0, 0, gui_width, footer_h), fill=INK)
        draw.line((0, 0, gui_width, 0), fill=HAIRLINE, width=1)

        y = (footer_h - text_h) // 2 - 1
        _draw_segments(draw, pad_x, y, left, font, sep, sep_w, sep_gap)

        right_x = gui_width - pad_x - right_w
        if right_x > pad_x + left_w + pad_x:
            _draw_segments(draw, right_x, y, right, font, sep, sep_w, sep_gap)

        self._image = footer
        self._cache_key = cache_key
        return np.asarray(footer)
