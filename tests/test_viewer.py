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


