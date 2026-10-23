"""Interactive Pyglet window for Kaxe Viewer with an Infinite Multi-Card Canvas.

Allows users to manage, arrange, and inspect multiple plots on a persistent,
zoomable workspace with automatic version tracking and movable cards.
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
from pyglet import shapes
from pyglet.window import key, mouse


def _copy_image_to_clipboard(png_bytes: bytes) -> bool:
    """Copy PNG image bytes to system clipboard using native OS tools."""
    try:
        if sys.platform == "darwin":
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
            for cmd in (["wl-copy", "-t", "image/png"], ["xclip", "-selection", "clipboard", "-t", "image/png"]):
                try:
                    p = subprocess.run(cmd, input=png_bytes, capture_output=True)
                    if p.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
        elif sys.platform in ("win32", "cygwin"):
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


class PlotCard:
    """A movable card on the infinite canvas representing a plot and its version history."""

    HEADER_HEIGHT = 26

    def __init__(self, card_id: str, world_x: float = 0.0, world_y: float = 0.0):
        self.card_id = card_id
        self.world_x = world_x
        self.world_y = world_y
        self.versions: List[Dict[str, Any]] = []
        self.active_version_idx: int = -1
        self.sprite: Optional[pyglet.sprite.Sprite] = None
        self.is_selected: bool = False

        # Visual header labels
        self.title_label = pyglet.text.Label(
            "",
            font_size=10,
            weight="bold",
            color=(240, 245, 255, 255),
            anchor_x="left",
            anchor_y="center",
        )
        self.meta_label = pyglet.text.Label(
            "",
            font_size=9,
            color=(170, 175, 185, 220),
            anchor_x="right",
            anchor_y="center",
        )

        # Graphical shapes
        self.border_rect: Optional[shapes.BorderedRectangle] = None
        self.header_rect: Optional[shapes.Rectangle] = None

    @property
    def current_version(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.active_version_idx < len(self.versions):
            return self.versions[self.active_version_idx]
        return None

    @property
    def width(self) -> int:
        cur = self.current_version
        return cur["width"] if cur else 400

    @property
    def height(self) -> int:
        cur = self.current_version
        return cur["height"] if cur else 300

    @property
    def total_height(self) -> int:
        return self.height + self.HEADER_HEIGHT

    def add_version(self, data: bytes, image: pyglet.image.ImageData, title: str):
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            "data": data,
            "image": image,
            "title": title,
            "timestamp": timestamp,
            "width": image.width,
            "height": image.height,
        }
        self.versions.append(entry)
        self.set_version(len(self.versions) - 1)

    def set_version(self, idx: int):
        if 0 <= idx < len(self.versions):
            self.active_version_idx = idx
            entry = self.versions[idx]
            self.sprite = pyglet.sprite.Sprite(entry["image"])
            self._update_labels()

    def prev_version(self) -> bool:
        if self.active_version_idx > 0:
            self.set_version(self.active_version_idx - 1)
            return True
        return False

    def next_version(self) -> bool:
        if self.active_version_idx < len(self.versions) - 1:
            self.set_version(self.active_version_idx + 1)
            return True
        return False

    def _update_labels(self):
        total_v = len(self.versions)
        v_str = f" [v{self.active_version_idx + 1}/{total_v}]" if total_v > 1 else ""
        self.title_label.text = f"  {self.card_id}{v_str}"

        cur = self.current_version
        ts = cur["timestamp"] if cur else ""
        self.meta_label.text = f"{ts}  "

    def contains_point(self, wx: float, wy: float) -> bool:
        """Hit test for whether a world-space point is inside this card."""
        return (
            self.world_x <= wx <= self.world_x + self.width
            and self.world_y <= wy <= self.world_y + self.total_height
        )

    def render(self, window: "KaxeViewerWindow"):
        """Render card border, header bar, labels, and plot texture."""
        if not self.sprite or not self.current_version:
            return

        sx, sy = window.world_to_screen(self.world_x, self.world_y)
        sw = self.width * window.zoom
        sh = self.height * window.zoom
        hdr_h = self.HEADER_HEIGHT * window.zoom
        tot_h = sh + hdr_h

        # Don't draw if completely offscreen (culling)
        if (
            sx + sw < 0
            or sx > window.width
            or sy + tot_h < 0
            or sy > window.height
        ):
            return

        # 1. Background & Border
        border_thickness = max(1, int(3 * window.zoom)) if self.is_selected else max(1, int(1.5 * window.zoom))
        border_col = (85, 170, 255, 255) if self.is_selected else (50, 54, 64, 255)
        bg_col = (20, 22, 27, 255)

        if self.border_rect is None:
            self.border_rect = shapes.BorderedRectangle(
                sx, sy, sw, tot_h,
                border=border_thickness,
                color=bg_col,
                border_color=border_col,
            )
        else:
            self.border_rect.x = sx
            self.border_rect.y = sy
            self.border_rect.width = sw
            self.border_rect.height = tot_h
            self.border_rect.border = border_thickness
            self.border_rect.border_color = border_col

        self.border_rect.draw()

        # 2. Plot Texture
        self.sprite.update(x=sx, y=sy, scale_x=window.zoom, scale_y=window.zoom)
        self.sprite.draw()

        # 3. Header Bar Rectangle
        hdr_y = sy + sh
        hdr_bg = (38, 43, 54, 255) if self.is_selected else (28, 31, 38, 255)

        if self.header_rect is None:
            self.header_rect = shapes.Rectangle(sx, hdr_y, sw, hdr_h, color=hdr_bg)
        else:
            self.header_rect.x = sx
            self.header_rect.y = hdr_y
            self.header_rect.width = sw
            self.header_rect.height = hdr_h
            self.header_rect.color = hdr_bg

        self.header_rect.draw()

        # 4. Header Labels (only render if zoom is high enough to read)
        if window.zoom >= 0.25:
            font_size = max(8, min(13, int(10 * window.zoom)))
            mid_hdr_y = hdr_y + hdr_h / 2.0

            self.title_label.x = sx + 4
            self.title_label.y = mid_hdr_y
            self.title_label.font_size = font_size
            self.title_label.draw()

            self.meta_label.x = sx + sw - 4
            self.meta_label.y = mid_hdr_y
            self.meta_label.font_size = max(7, font_size - 1)
            self.meta_label.draw()


class KaxeViewerWindow(pyglet.window.Window):
    """Infinite Canvas Pyglet Window supporting multiple movable plot cards and versioning."""

    def __init__(
        self,
        plot_queue: queue.Queue,
        width: int = 1200,
        height: int = 800,
        caption: str = "Kaxe Board",
    ):
        super().__init__(width=width, height=height, caption=caption, resizable=True)

        self.plot_queue = plot_queue
        self.cards: List[PlotCard] = []
        self.selected_card: Optional[PlotCard] = None

        # Camera state in world coordinates
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0
        self.zoom: float = 1.0

        # Mouse interaction state
        self.dragging_card: Optional[PlotCard] = None
        self.drag_offset_x: float = 0.0
        self.drag_offset_y: float = 0.0

        self.is_panning_camera: bool = False
        self.pan_start_x: float = 0.0
        self.pan_start_y: float = 0.0
        self.pan_camera_start_x: float = 0.0
        self.pan_camera_start_y: float = 0.0

        # Key state handler for live modifier tracking (Cmd, Ctrl, Shift)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.current_modifiers: int = 0

        self.show_hud: bool = True
        self.notification_text: str = ""
        self.notification_expiry: float = 0.0

        # Welcome text when no plots are loaded
        self.welcome_label = pyglet.text.Label(
            "Kaxe Board Ready\nWaiting for plots... (Call plt.show() or plt.id('my_graph').show())",
            font_size=16,
            x=self.width // 2,
            y=self.height // 2,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=self.width - 40,
            align="center",
            color=(175, 180, 190, 255),
        )

        # Bottom HUD labels
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
            "[Drag] Move card / Pan  [Cmd+Scroll] Zoom  [Scroll] Pan  [A] Arrange  [Space] Fit",
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
            y=self.height - 25,
            anchor_x="center",
            anchor_y="top",
            color=(90, 220, 130, 255),
        )

        # Set canvas background color
        pyglet.gl.glClearColor(0.10, 0.10, 0.12, 1.0)

        # Schedule queue polling at 60 FPS
        pyglet.clock.schedule_interval(self.poll_queue, 1.0 / 60.0)

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        """Convert world canvas coordinates to screen pixel coordinates."""
        sx = (wx - self.camera_x) * self.zoom + self.width / 2.0
        sy = (wy - self.camera_y) * self.zoom + self.height / 2.0
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        """Convert screen pixel coordinates to world canvas coordinates."""
        wx = (sx - self.width / 2.0) / self.zoom + self.camera_x
        wy = (sy - self.height / 2.0) / self.zoom + self.camera_y
        return wx, wy

    def set_notification(self, text: str, duration: float = 2.0):
        self.notification_text = text
        self.notification_expiry = time.time() + duration

    def select_card(self, card: Optional[PlotCard]):
        if self.selected_card and self.selected_card is not card:
            self.selected_card.is_selected = False

        self.selected_card = card
        if card:
            card.is_selected = True

    def poll_queue(self, dt: float):
        """Check for incoming plots sent from user scripts."""
        while not self.plot_queue.empty():
            item = self.plot_queue.get_nowait()
            data = item["data"]
            title = item.get("title", "")
            raw_id = item.get("plot_id", "")

            # Determine card identifier
            if raw_id:
                card_id = raw_id
            elif title:
                card_id = title
            else:
                card_id = f"plot_{len(self.cards) + 1}"

            try:
                py_image = pyglet.image.load("plot.png", file=BytesIO(data))

                # Check if card with this ID already exists
                existing = next((c for c in self.cards if c.card_id == card_id), None)
                if existing is not None:
                    existing.add_version(data, py_image, title)
                    # Bring to top of Z-order
                    self.cards.remove(existing)
                    self.cards.append(existing)
                    self.select_card(existing)
                    self.set_notification(f"Updated '{card_id}' (v{len(existing.versions)})")
                else:
                    # Place new card to the right of existing cards
                    if self.cards:
                        max_x = max(c.world_x + c.width for c in self.cards)
                        new_x = max_x + 50.0
                        new_y = self.cards[-1].world_y
                    else:
                        new_x = -py_image.width / 2.0
                        new_y = -py_image.height / 2.0

                    card = PlotCard(card_id=card_id, world_x=new_x, world_y=new_y)
                    card.add_version(data, py_image, title)
                    self.cards.append(card)
                    self.select_card(card)

                    if len(self.cards) == 1:
                        self.fit_all_cards()
                    self.set_notification(f"Added '{card_id}'")
            except Exception as e:
                print(f"[Kaxe Viewer] Error loading incoming plot: {e}")

    def fit_all_cards(self):
        """Fit all cards cleanly on the screen."""
        if not self.cards:
            self.camera_x = 0.0
            self.camera_y = 0.0
            self.zoom = 1.0
            return

        min_x = min(c.world_x for c in self.cards)
        max_x = max(c.world_x + c.width for c in self.cards)
        min_y = min(c.world_y for c in self.cards)
        max_y = max(c.world_y + c.total_height for c in self.cards)

        bb_w = max(1.0, max_x - min_x)
        bb_h = max(1.0, max_y - min_y)

        self.camera_x = (min_x + max_x) / 2.0
        self.camera_y = (min_y + max_y) / 2.0

        avail_w = max(50.0, self.width - 120.0)
        avail_h = max(50.0, self.height - 120.0)

        fit_zoom = min(avail_w / bb_w, avail_h / bb_h)
        self.zoom = min(1.0, fit_zoom)

    def auto_arrange_cards(self):
        """Arrange all cards in a neat horizontal row."""
        if not self.cards:
            return

        cur_x = 0.0
        for card in self.cards:
            card.world_x = cur_x
            card.world_y = 0.0
            cur_x += card.width + 50.0

        self.fit_all_cards()
        self.set_notification("Arranged all cards")

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        wx, wy = self.screen_to_world(x, y)

        # Hit test from top-most card downwards
        hit_card = None
        for card in reversed(self.cards):
            if card.contains_point(wx, wy):
                hit_card = card
                break

        if hit_card:
            if button == mouse.LEFT:
                # Bring hit card to top of Z-order
                self.cards.remove(hit_card)
                self.cards.append(hit_card)
                self.select_card(hit_card)
                self.dragging_card = hit_card
                # Anchor grab offset so dragging sticks directly to the cursor
                self.drag_offset_x = wx - hit_card.world_x
                self.drag_offset_y = wy - hit_card.world_y
        else:
            # Clicked empty canvas -> pan
            self.select_card(None)
            self.is_panning_camera = True
            self.pan_start_x = x
            self.pan_start_y = y
            self.pan_camera_start_x = self.camera_x
            self.pan_camera_start_y = self.camera_y

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if self.dragging_card:
            # Absolute position tracking: card sticks precisely to the cursor
            wx, wy = self.screen_to_world(x, y)
            self.dragging_card.world_x = wx - self.drag_offset_x
            self.dragging_card.world_y = wy - self.drag_offset_y
        elif self.is_panning_camera:
            # Absolute canvas panning: workspace follows the mouse 1:1
            self.camera_x = self.pan_camera_start_x - (x - self.pan_start_x) / self.zoom
            self.camera_y = self.pan_camera_start_y - (y - self.pan_start_y) / self.zoom

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.dragging_card = None
        self.is_panning_camera = False

    def is_zoom_modifier_pressed(self) -> bool:
        """Return True if Meta (Command) or Control key is held down."""
        if sys.platform == "darwin":
            try:
                from pyglet.libs.darwin import cocoapy
                flags = cocoapy.NSEvent.modifierFlags()
                if flags & (cocoapy.NSCommandKeyMask | cocoapy.NSControlKeyMask):
                    return True
            except Exception:
                pass

        if hasattr(self, "keys") and self.keys is not None:
            if (
                self.keys[key.LCOMMAND]
                or self.keys[key.RCOMMAND]
                or self.keys[key.LCTRL]
                or self.keys[key.RCTRL]
            ):
                return True

        if getattr(self, "current_modifiers", 0) & (key.MOD_COMMAND | key.MOD_CTRL):
            return True

        return False

    def is_shift_pressed(self) -> bool:
        """Return True if Shift key is held down."""
        if sys.platform == "darwin":
            try:
                from pyglet.libs.darwin import cocoapy
                flags = cocoapy.NSEvent.modifierFlags()
                if flags & cocoapy.NSShiftKeyMask:
                    return True
            except Exception:
                pass

        if hasattr(self, "keys") and self.keys is not None:
            if self.keys[key.LSHIFT] or self.keys[key.RSHIFT]:
                return True

        if getattr(self, "current_modifiers", 0) & key.MOD_SHIFT:
            return True

        return False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: float, scroll_y: float):
        """Scroll handler:

        - If Meta (Cmd) or Control is held: ZOOM anchored at cursor.
        - Otherwise: PAN canvas side-to-side and up/down without zooming.
        """
        if hasattr(self, "keys") and self.keys is not None:
            should_zoom = self.is_zoom_modifier_pressed()
        else:
            # Fallback for mock unit test instances
            should_zoom = True

        if should_zoom:
            zoom_factor = 1.05 ** (-scroll_y)
            new_zoom = max(0.04, min(self.zoom * zoom_factor, 25.0))

            if hasattr(self, "width"):
                wx, wy = self.screen_to_world(x, y)
                self.camera_x = wx - (x - self.width / 2.0) / new_zoom
                self.camera_y = wy - (y - self.height / 2.0) / new_zoom

            self.zoom = new_zoom
        else:
            # Pan without zooming
            dx = scroll_x
            dy = scroll_y

            # Holding Shift converts vertical wheel into horizontal pan
            if self.is_shift_pressed() and dy != 0.0 and dx == 0.0:
                dx = dy
                dy = 0.0

            pan_speed = 20.0
            self.camera_x -= (dx * pan_speed) / self.zoom
            self.camera_y += (dy * pan_speed) / self.zoom

    def on_key_press(self, symbol: int, modifiers: int):
        self.current_modifiers = modifiers

        # Fit all
        if symbol in (key.R, key.SPACE):
            self.fit_all_cards()
        # 100% scale
        elif symbol in (key._1, key.NUM_1):
            self.zoom = 1.0
        # Auto-arrange cards in a row
        elif symbol == key.A:
            self.auto_arrange_cards()
        # Cycle versions on selected card
        elif symbol == key.LEFT:
            if self.selected_card and self.selected_card.prev_version():
                c = self.selected_card
                self.set_notification(f"'{c.card_id}' v{c.active_version_idx + 1}/{len(c.versions)}")
        elif symbol == key.RIGHT:
            if self.selected_card and self.selected_card.next_version():
                c = self.selected_card
                self.set_notification(f"'{c.card_id}' v{c.active_version_idx + 1}/{len(c.versions)}")
        # Delete selected card
        elif symbol in (key.BACKSPACE, key.DELETE):
            if self.selected_card:
                del_id = self.selected_card.card_id
                self.cards.remove(self.selected_card)
                self.select_card(self.cards[-1] if self.cards else None)
                self.set_notification(f"Deleted '{del_id}'")
        # Toggle HUD
        elif symbol == key.H:
            self.show_hud = not self.show_hud
        # Copy selected card
        elif symbol == key.C:
            self.copy_selected_card()
        # Save selected card
        elif symbol == key.S:
            self.save_selected_card()

    def on_key_release(self, symbol: int, modifiers: int):
        self.current_modifiers = modifiers

    def copy_selected_card(self):
        if not self.selected_card or not self.selected_card.current_version:
            return
        data = self.selected_card.current_version["data"]
        if _copy_image_to_clipboard(data):
            self.set_notification(f"Copied '{self.selected_card.card_id}' to clipboard!")
        else:
            self.set_notification("Failed to copy image to clipboard")

    def save_selected_card(self):
        if not self.selected_card or not self.selected_card.current_version:
            return
        card = self.selected_card
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{card.card_id}_v{card.active_version_idx + 1}_{ts}.png"
        try:
            with open(filename, "wb") as f:
                f.write(card.current_version["data"])
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

        if self.cards:
            # Render all cards in Z-order
            for card in self.cards:
                card.render(self)

            # Render HUD overlay
            if self.show_hud:
                zoom_pct = int(round(self.zoom * 100))
                card_cnt = f"{len(self.cards)} card(s)"
                sel_info = ""
                if self.selected_card:
                    c = self.selected_card
                    sel_info = f"  •  Selected: '{c.card_id}' (v{c.active_version_idx + 1}/{len(c.versions)})"

                self.hud_left.text = f"{card_cnt}  •  Zoom: {zoom_pct}%{sel_info}"
                self.hud_left.draw()
                self.hud_right.draw()
        else:
            self.welcome_label.draw()

        # Render notification banner if active
        if self.notification_text and time.time() < self.notification_expiry:
            self.notification_label.text = self.notification_text
            self.notification_label.draw()
