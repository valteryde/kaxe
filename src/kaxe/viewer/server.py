"""Lightweight HTTP server embedded inside Kaxe Viewer.

Uses Python standard library `http.server.ThreadingHTTPServer` to receive
plot images and metadata from client scripts without external web frameworks.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import queue
import threading
import urllib.parse
from typing import Any, Dict


class PlotRequestHandler(BaseHTTPRequestHandler):
    """Handles incoming /show POST requests and /ping health checks."""

    # Reference to the shared Queue injected by start_server
    plot_queue: queue.Queue = queue.Queue()

    def do_GET(self):
        if self.path in ("/ping", "/health"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/show":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Empty body")
                return

            img_bytes = self.rfile.read(content_length)
            raw_title = self.headers.get("X-Kaxe-Title", "")
            title = urllib.parse.unquote(raw_title) if raw_title else ""

            item: Dict[str, Any] = {
                "data": img_bytes,
                "title": title,
            }
            self.plot_queue.put(item)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args):
        # Format messages cleanly in terminal
        first_arg = args[0] if args else ""
        if "POST /show" in str(first_arg):
            print(f"[Kaxe Viewer] New plot received ({format % args})")
        # Suppress noisy health checks in console


def start_server_thread(
    port: int,
    plot_queue: queue.Queue,
    host: str = "127.0.0.1",
) -> tuple[ThreadingHTTPServer, threading.Thread]:
    """Start the HTTP server on a daemon background thread."""
    PlotRequestHandler.plot_queue = plot_queue
    server = ThreadingHTTPServer((host, port), PlotRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread
