"""Client-side probe and transmitter for Kaxe Viewer.

This module intentionally uses ONLY Python standard library modules
(socket, urllib, os) so that calling `plt.show()` never requires
pyglet or any other viewer dependency.
"""

import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

DEFAULT_PORT = 41783


def get_viewer_port() -> int:
    """Return the configured viewer port from environment or the default."""
    env_port = os.getenv("KAXE_VIEWER_PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass
    return DEFAULT_PORT


def is_viewer_active(port: Optional[int] = None, timeout: float = 0.03) -> bool:
    """Check if the Kaxe Viewer is currently listening on localhost.

    Uses a fast socket connection test with a short timeout (~30ms).
    When no viewer is running, the OS kernel rejects the connection
    virtually instantaneously (<1ms).
    """
    if port is None:
        port = get_viewer_port()

    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def send_to_viewer(
    data: bytes,
    title: str = "",
    port: Optional[int] = None,
    timeout: float = 2.0,
) -> bool:
    """Send image PNG bytes to the active Kaxe Viewer over HTTP POST.

    Returns True if successfully received, False otherwise.
    """
    if port is None:
        port = get_viewer_port()

    url = f"http://127.0.0.1:{port}/show"
    safe_title = urllib.parse.quote(title or "")
    headers = {
        "Content-Type": "image/png",
        "X-Kaxe-Title": safe_title,
    }

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError):
        return False


def try_show_in_viewer(data: bytes, title: str = "") -> bool:
    """Convenience helper: probe port and send image if viewer is alive.

    Returns True if sent to viewer, False if fallback is needed.
    """
    port = get_viewer_port()
    if is_viewer_active(port):
        return send_to_viewer(data, title=title, port=port)
    return False
