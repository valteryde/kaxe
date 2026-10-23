import queue
import time
from unittest.mock import patch
import pytest

from kaxe._require_viewer import require_viewer
from kaxe.viewer.client import (
    DEFAULT_PORT,
    get_viewer_port,
    is_viewer_active,
    send_to_viewer,
    try_show_in_viewer,
)
from kaxe.viewer.server import start_server_thread


def test_require_viewer_succeeds_when_installed():
    # Should not raise when pyglet is present
    require_viewer()


def test_require_viewer_raises_informative_error(monkeypatch):
    import sys

    # Simulate pyglet missing
    with patch.dict(sys.modules, {"pyglet": None}):
        with pytest.raises(ImportError) as excinfo:
            require_viewer()
        assert "pip install kaxe[viewer]" in str(excinfo.value)


def test_is_viewer_active_returns_false_for_unused_port():
    # A port unlikely to be open
    assert not is_viewer_active(port=59999, timeout=0.02)


def test_server_and_client_roundtrip():
    plot_queue = queue.Queue()
    test_port = 58492

    server, thread = start_server_thread(test_port, plot_queue)
    try:
        # Give server a moment to start
        time.sleep(0.05)

        # 1. Probe should report active
        assert is_viewer_active(port=test_port)

        # 2. Send image payload
        dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRtest"
        success = send_to_viewer(dummy_png, title="Test Plot", port=test_port)
        assert success is True

        # 3. Server should have received item in queue
        assert not plot_queue.empty()
        item = plot_queue.get(timeout=1.0)
        assert item["data"] == dummy_png
        assert item["title"] == "Test Plot"

    finally:
        server.shutdown()
        server.server_close()


def test_try_show_in_viewer_inactive(monkeypatch):
    monkeypatch.setenv("KAXE_VIEWER_PORT", "59998")
    dummy_png = b"\x89PNGdummy"
    # When port is closed, returns False immediately without error
    assert try_show_in_viewer(dummy_png) is False


def test_plot_show_routes_to_viewer_when_active(monkeypatch):
    import kaxe
    from PIL import Image

    plot_queue = queue.Queue()
    test_port = 58493
    monkeypatch.setenv("KAXE_VIEWER_PORT", str(test_port))

    server, thread = start_server_thread(test_port, plot_queue)
    try:
        time.sleep(0.05)
        plt = kaxe.Plot()
        plt.add(kaxe.Points([1, 2], [3, 4]))

        with patch.object(Image.Image, "show") as mock_pil_show:
            plt.show()
            # PIL Image.show should NOT have been called
            mock_pil_show.assert_not_called()

        assert not plot_queue.empty()
        item = plot_queue.get(timeout=1.0)
        assert len(item["data"]) > 0  # Received actual rendered PNG bytes!
    finally:
        server.shutdown()
        server.server_close()


def test_plot_show_falls_back_to_pil_when_viewer_inactive(monkeypatch):
    import kaxe
    from PIL import Image

    # Point to closed port
    monkeypatch.setenv("KAXE_VIEWER_PORT", "59997")

    plt = kaxe.Plot()
    plt.add(kaxe.Points([1, 2], [3, 4]))

    with patch.object(Image.Image, "show") as mock_pil_show:
        plt.show()
        # PIL Image.show should have been called as fallback
        mock_pil_show.assert_called_once()


def test_grid_show_routes_to_viewer_when_active(monkeypatch):
    import kaxe
    from PIL import Image

    plot_queue = queue.Queue()
    test_port = 58494
    monkeypatch.setenv("KAXE_VIEWER_PORT", str(test_port))

    server, thread = start_server_thread(test_port, plot_queue)
    try:
        time.sleep(0.05)
        grid = kaxe.Grid()
        grid.addRow(kaxe.Plot())

        with patch.object(Image.Image, "show") as mock_pil_show:
            grid.show()
            mock_pil_show.assert_not_called()

        assert not plot_queue.empty()
        item = plot_queue.get(timeout=1.0)
        assert len(item["data"]) > 0
    finally:
        server.shutdown()
        server.server_close()


def test_plot_open_streams_and_prints_message(capsys, monkeypatch):
    import kaxe
    from PIL import Image

    plot_queue = queue.Queue()
    test_port = 58495
    monkeypatch.setenv("KAXE_VIEWER_PORT", str(test_port))

    server, thread = start_server_thread(test_port, plot_queue)
    try:
        time.sleep(0.05)
        plt = kaxe.Plot()
        plt.add(kaxe.Points([1, 2], [3, 4]))

        with patch.object(Image.Image, "show") as mock_pil_show:
            plt.open()
            mock_pil_show.assert_not_called()

        captured = capsys.readouterr()
        assert "streamed" in captured.out.lower()
        assert "[Kaxe] Plot streamed to viewer" in captured.out
    finally:
        server.shutdown()
        server.server_close()


def test_grid_open_streams_and_prints_message(capsys, monkeypatch):
    import kaxe
    from PIL import Image

    plot_queue = queue.Queue()
    test_port = 58496
    monkeypatch.setenv("KAXE_VIEWER_PORT", str(test_port))

    server, thread = start_server_thread(test_port, plot_queue)
    try:
        time.sleep(0.05)
        grid = kaxe.Grid()
        grid.addRow(kaxe.Plot())

        with patch.object(Image.Image, "show") as mock_pil_show:
            grid.open()
            mock_pil_show.assert_not_called()

        captured = capsys.readouterr()
        assert "streamed" in captured.out.lower()
        assert "[Kaxe] Plot streamed to viewer" in captured.out
    finally:
        server.shutdown()
        server.server_close()


def test_viewer_zoom_reversed_and_less_sensitive():
    from unittest.mock import MagicMock
    from kaxe.viewer.window import KaxeViewerWindow

    # Create uninitialized instance to test logic without opening GUI window
    window = object.__new__(KaxeViewerWindow)
    window.current_sprite = MagicMock()
    window.history = [{"width": 800, "height": 600}]
    window.zoom = 1.0
    window.offset_x = 0.0
    window.offset_y = 0.0

    # 1. Positive scroll_y (scroll up) must zoom OUT (reverse of previous behavior)
    window.on_mouse_scroll(x=400, y=300, scroll_x=0.0, scroll_y=1.0)
    expected_factor = 1.05 ** (-1.0)
    assert window.zoom < 1.0
    assert abs(window.zoom - expected_factor) < 1e-6

    # 2. Negative scroll_y (scroll down) must zoom IN
    window.zoom = 1.0
    window.offset_x = 0.0
    window.offset_y = 0.0
    window.on_mouse_scroll(x=400, y=300, scroll_x=0.0, scroll_y=-1.0)
    expected_in_factor = 1.05 ** 1.0
    assert window.zoom > 1.0
    assert abs(window.zoom - expected_in_factor) < 1e-6
    # Sensitivity check: 1.05 per unit (much less sensitive than old 1.15)
    assert abs(window.zoom - 1.05) < 1e-6


def test_scroll_pans_side_to_side_without_zoom_modifier():
    from unittest.mock import MagicMock
    from kaxe.viewer.window import KaxeViewerWindow
    from pyglet.window import key

    window = object.__new__(KaxeViewerWindow)
    window.keys = {key.LCOMMAND: False, key.RCOMMAND: False, key.LCTRL: False, key.RCTRL: False, key.LSHIFT: False, key.RSHIFT: False}
    window.current_modifiers = 0
    window.camera_x = 0.0
    window.camera_y = 0.0
    window.zoom = 1.0

    # Horizontal scroll without Cmd/Ctrl -> pans horizontally, zoom stays unchanged!
    window.on_mouse_scroll(x=400, y=300, scroll_x=2.0, scroll_y=0.0)
    assert window.zoom == 1.0
    assert window.camera_x < 0.0  # Camera moved left

    # Vertical scroll without Cmd/Ctrl -> pans vertically, zoom stays unchanged!
    orig_cam_x = window.camera_x
    window.on_mouse_scroll(x=400, y=300, scroll_x=0.0, scroll_y=3.0)
    assert window.zoom == 1.0
    assert window.camera_x == orig_cam_x
    assert window.camera_y > 0.0

    # With Cmd key pressed -> zooms!
    window.keys[key.LCOMMAND] = True
    window.on_mouse_scroll(x=400, y=300, scroll_x=0.0, scroll_y=-1.0)
    assert window.zoom > 1.0


def test_plot_id_chaining_and_streaming(monkeypatch):
    import kaxe

    plot_queue = queue.Queue()
    test_port = 58497
    monkeypatch.setenv("KAXE_VIEWER_PORT", str(test_port))

    server, thread = start_server_thread(test_port, plot_queue)
    try:
        time.sleep(0.05)
        plt1 = kaxe.Plot().id("my_custom_plot")
        plt1.show()

        assert not plot_queue.empty()
        item1 = plot_queue.get(timeout=1.0)
        assert item1["plot_id"] == "my_custom_plot"

        plt2 = kaxe.Plot()
        plt2.show(id="plot_from_show_arg")

        assert not plot_queue.empty()
        item2 = plot_queue.get(timeout=1.0)
        assert item2["plot_id"] == "plot_from_show_arg"
    finally:
        server.shutdown()
        server.server_close()


def test_canvas_multi_card_and_versioning():
    from io import BytesIO
    from PIL import Image
    from kaxe.viewer.window import KaxeViewerWindow

    q = queue.Queue()
    window = KaxeViewerWindow(q, width=800, height=600)

    # 1. First plot arrives -> creates card "graph_1"
    img = Image.new("RGB", (100, 80), color=(100, 150, 200))
    buf = BytesIO()
    img.save(buf, format="PNG")
    raw_png = buf.getvalue()

    q.put({"data": raw_png, "title": "Loss", "plot_id": "graph_1"})
    window.poll_queue(0.016)
    assert len(window.cards) == 1
    assert window.cards[0].card_id == "graph_1"
    assert len(window.cards[0].versions) == 1

    # 2. Re-running with same ID -> increments version on existing card (stays 1 card!)
    q.put({"data": raw_png, "title": "Loss v2", "plot_id": "graph_1"})
    window.poll_queue(0.016)
    assert len(window.cards) == 1
    assert len(window.cards[0].versions) == 2
    assert window.cards[0].active_version_idx == 1

    # 3. New plot with distinct ID -> creates second card on the canvas
    q.put({"data": raw_png, "title": "Accuracy", "plot_id": "graph_2"})
    window.poll_queue(0.016)
    assert len(window.cards) == 2
    assert window.cards[0].card_id == "graph_1"
    assert window.cards[1].card_id == "graph_2"

    # 4. Moving card changes its coordinates via press and drag
    card = window.cards[1]
    sx, sy = window.world_to_screen(card.world_x + 20, card.world_y + 20)
    window.on_mouse_press(int(sx), int(sy), button=1, modifiers=0)
    orig_x = card.world_x
    window.on_mouse_drag(int(sx + 50), int(sy + 20), dx=50, dy=20, buttons=1, modifiers=0)
    assert card.world_x > orig_x

    window.close()




