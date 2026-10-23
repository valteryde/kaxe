"""Interactive Pyglet window for Kaxe Viewer.

Provides 60 FPS hardware-accelerated OpenGL pan, cursor-anchored zoom,
session plot history navigation, and quick clipboard/file export.
"""

from io import BytesIO
import os
import queue
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional

from .._require_viewer import require_viewer

require_viewer()

import pyglet
from pyglet.window import key, mouse


def _copy_image_to_clipboard(png_bytes: bytes) -> bool:
    """Copy PNG image bytes to system clipboard using native OS tools."""
    try:
        if sys.platform == "darwin":
            # On macOS, use osascript with a temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(png_bytes)
                tmp_path = tmp.name

            script = f'set the clipboard to (read (POSIX file "{tmp_path}") as «class PNGf»)'
            res = subprocess.run(["osascript", "-e", script], capture_output=True)
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return res.returncode == 0
        elif sys.platform.startswith("linux"):
            # Try wl-copy or xclip
            for cmd in (["wl-copy", "-t", "image/png"], ["xclip", "-selection", "clipboard", "-t", "image/png"]):
                try:
                    p = subprocess.run(cmd, input=png_bytes, capture_output=True)
                    if p.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
        elif sys.platform in ("win32", "cygwin"):
            # On Windows, try PowerShell script to set clipboard
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(png_bytes)
                tmp_path = tmp.name
            ps_cmd = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$img = [System.Drawing.Image]::FromFile('{tmp_path}'); "
                f"[System.Windows.Forms.Clipboard]::SetImage($img);"
            )
            res = subprocess.run(["powershell", "-command", ps_cmd], capture_output=True)
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return res.returncode == 0
    except Exception:
        pass
    return False


class KaxeViewerWindow(pyglet.window.Window):
    """Pyglet OpenGL window that renders and inspects streamed Kaxe plots."""

    def __init__(
        self,
        plot_queue: queue.Queue,
        width: int = 1100,
        height: int = 750,
        caption: str = "Kaxe Viewer",
    ):
        super().__init__(width=width, height=height, caption=caption, resizable=True)

        self.plot_queue = plot_queue
        self.history: List[Dict[str, Any]] = []
        self.history_index: int = -1

        # Pan and Zoom transform state
        self.zoom: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

        self.current_sprite: Optional[pyglet.sprite.Sprite] = None
        self.show_hud: bool = True

        # Notification message banner (e.g. "Copied to clipboard!")
        self.notification_text: str = ""
        self.notification_expiry: float = 0.0

        # Pyglet text labels
        self.welcome_label = pyglet.text.Label(
            "Kaxe Viewer Ready\nWaiting for plots... (Call .show() in any script)",
            font_size=16,
            x=self.width // 2,
            y=self.height // 2,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=self.width - 40,
            align="center",
            color=(180, 185, 195, 255),
        )

        self.hud_left = pyglet.text.Label(
            "",
            font_size=11,
            x=15,
            y=15,
            anchor_x="left",
            anchor_y="bottom",
            color=(210, 215, 225, 220),
        )

        self.hud_right = pyglet.text.Label(
            "[R/Space] Fit  [1] 100%  [←/→] History  [C] Copy  [S] Save  [H] Toggle HUD",
            font_size=11,
            x=self.width - 15,
            y=15,
            anchor_x="right",
            anchor_y="bottom",
            color=(150, 155, 165, 220),
        )

        self.notification_label = pyglet.text.Label(
            "",
            font_size=13,
            weight="bold",
            x=self.width // 2,
            y=self.height - 30,
            anchor_x="center",
            anchor_y="top",
            color=(80, 220, 120, 255),
        )

        # Set sleek dark background color
        pyglet.gl.glClearColor(0.11, 0.11, 0.13, 1.0)

        # Schedule queue polling at 60 FPS
        pyglet.clock.schedule_interval(self.poll_queue, 1.0 / 60.0)

    def set_notification(self, text: str, duration: float = 2.0):
        self.notification_text = text
        self.notification_expiry = time.time() + duration

    def poll_queue(self, dt: float):
        """Check for incoming plots sent from user scripts."""
        updated = False
        while not self.plot_queue.empty():
            item = self.plot_queue.get_nowait()
            data = item["data"]
            title = item.get("title", "")

            try:
                py_image = pyglet.image.load("plot.png", file=BytesIO(data))
                entry = {
                    "image": py_image,
                    "data": data,
                    "title": title,
                    "width": py_image.width,
                    "height": py_image.height,
                }
                self.history.append(entry)
                self.history_index = len(self.history) - 1
                self._load_current_plot(first_load=len(self.history) == 1)
                updated = True
            except Exception as e:
                print(f"[Kaxe Viewer] Error loading incoming plot: {e}")

        if updated:
            self.set_notification("New plot received", duration=1.5)

    def _load_current_plot(self, first_load: bool = False):
        if not (0 <= self.history_index < len(self.history)):
            return

        entry = self.history[self.history_index]
        self.current_sprite = pyglet.sprite.Sprite(entry["image"])

        title = entry.get("title") or "Plot"
        self.set_caption(f"Kaxe Viewer - {title} (#{self.history_index + 1})")

        if first_load or len(self.history) <= 1:
            self.fit_to_window()

    def fit_to_window(self):
        """Scale and center the current plot to fit the window cleanly."""
        if not self.current_sprite or not self.history:
            return

        entry = self.history[self.history_index]
        img_w, img_h = entry["width"], entry["height"]

        # Reserve padding for HUD and borders
        padding_x = 40
        padding_y = 60
        avail_w = max(50, self.width - padding_x * 2)
        avail_h = max(50, self.height - padding_y * 2)

        scale_x = avail_w / img_w
        scale_y = avail_h / img_h
        self.zoom = min(scale_x, scale_y)

        # Center on canvas
        self.offset_x = (self.width - img_w * self.zoom) / 2.0
        self.offset_y = (self.height - img_h * self.zoom) / 2.0

    def set_scale_100(self):
        """Set zoom scale to exactly 100% (1:1 native pixels) and center."""
        if not self.current_sprite or not self.history:
            return

        entry = self.history[self.history_index]
        img_w, img_h = entry["width"], entry["height"]

        self.zoom = 1.0
        self.offset_x = (self.width - img_w) / 2.0
        self.offset_y = (self.height - img_h) / 2.0

    def on_mouse_scroll(self, x: int, y: int, scroll_x: float, scroll_y: float):
        """Smooth cursor-anchored zooming."""
        if not self.current_sprite or not self.history:
            return

        zoom_factor = 1.15 ** scroll_y
        new_zoom = max(0.02, min(self.zoom * zoom_factor, 50.0))

        # Anchor zoom relative to current mouse position (x, y)
        img_x = (x - self.offset_x) / self.zoom
        img_y = (y - self.offset_y) / self.zoom

        self.offset_x = x - img_x * new_zoom
        self.offset_y = y - img_y * new_zoom
        self.zoom = new_zoom

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        """Pan plot on left mouse drag."""
        if buttons & mouse.LEFT:
            self.offset_x += dx
            self.offset_y += dy

    def on_key_press(self, symbol: int, modifiers: int):
        # Reset / Fit
        if symbol in (key.R, key.SPACE):
            self.fit_to_window()
        # 1:1 scale
        elif symbol in (key._1, key.NUM_1):
            self.set_scale_100()
        # History navigation
        elif symbol == key.LEFT:
            if self.history_index > 0:
                self.history_index -= 1
                self._load_current_plot()
        elif symbol == key.RIGHT:
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self._load_current_plot()
        # Toggle HUD
        elif symbol == key.H:
            self.show_hud = not self.show_hud
        # Copy to clipboard (C or Cmd+C / Ctrl+C)
        elif symbol == key.C:
            self.copy_current_plot()
        # Save to disk
        elif symbol == key.S:
            self.save_current_plot()

    def copy_current_plot(self):
        if not self.history or not (0 <= self.history_index < len(self.history)):
            return

        entry = self.history[self.history_index]
        if _copy_image_to_clipboard(entry["data"]):
            self.set_notification("Copied to clipboard!")
        else:
            self.set_notification("Failed to copy image to clipboard")

    def save_current_plot(self):
        if not self.history or not (0 <= self.history_index < len(self.history)):
            return

        entry = self.history[self.history_index]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"kaxe_plot_{timestamp}.png"
        try:
            with open(filename, "wb") as f:
                f.write(entry["data"])
            self.set_notification(f"Saved to {filename}!")
        except Exception as e:
            self.set_notification(f"Save failed: {e}")

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.welcome_label.x = width // 2
        self.welcome_label.y = height // 2
        self.welcome_label.width = max(100, width - 40)
        self.hud_right.x = width - 15
        self.notification_label.x = width // 2
        self.notification_label.y = height - 25

    def on_draw(self):
        self.clear()

        if self.current_sprite and self.history:
            # Draw plot sprite with current scale and offset
            self.current_sprite.update(
                x=self.offset_x,
                y=self.offset_y,
                scale_x=self.zoom,
                scale_y=self.zoom,
            )
            self.current_sprite.draw()

            # Render HUD overlay
            if self.show_hud:
                entry = self.history[self.history_index]
                zoom_pct = int(round(self.zoom * 100))
                idx_info = f"Plot {self.history_index + 1}/{len(self.history)}"
                dim_info = f"{entry['width']}×{entry['height']} px"
                title = entry.get("title")
                title_info = f" | {title}" if title else ""

                self.hud_left.text = f"{idx_info}  •  {dim_info}  •  Zoom: {zoom_pct}%{title_info}"
                self.hud_left.draw()
                self.hud_right.draw()
        else:
            self.welcome_label.draw()

        # Render notification banner if active
        if self.notification_text and time.time() < self.notification_expiry:
            self.notification_label.text = self.notification_text
            self.notification_label.draw()
