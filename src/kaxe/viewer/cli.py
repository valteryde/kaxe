"""Command line interface for launching Kaxe Viewer."""

import argparse
import queue
import sys

from .client import get_viewer_port, is_viewer_active
from .server import start_server_thread


def run_viewer(port: int = 41783):
    """Launch the Kaxe Viewer Pyglet window and HTTP server."""
    # Ensure optional dependency is installed
    from .._require_viewer import require_viewer

    try:
        require_viewer()
    except ImportError as e:
        print(f"\n[Kaxe] {e}\n", file=sys.stderr)
        sys.exit(1)

    import pyglet
    from .window import KaxeViewerWindow

    # Check if a viewer is already running on this port
    if is_viewer_active(port):
        print(f"\n[Kaxe Viewer] Port {port} is already in use.", file=sys.stderr)
        print("A Kaxe Viewer instance is likely already open.\n", file=sys.stderr)
        sys.exit(1)

    plot_queue = queue.Queue()

    # Start HTTP server on background thread
    server, thread = start_server_thread(port, plot_queue)

    print("=" * 64)
    print(f"  Kaxe Viewer running on http://127.0.0.1:{port}")
    print("  Keep this terminal open while working.")
    print("  In another terminal, run your scripts calling .show()!")
    print()
    print("  Controls:")
    print("    • Mouse Wheel     : Zoom (centered at cursor)")
    print("    • Left Click Drag : Pan image")
    print("    • [R] or [Space]  : Fit plot to window")
    print("    • [1]             : 100% native resolution")
    print("    • [←] / [→]       : Cycle through previous plots")
    print("    • [C]             : Copy image to clipboard")
    print("    • [S]             : Save image to file")
    print("    • [H]             : Toggle HUD overlay")
    print("=" * 64)

    # Create Pyglet window and run Cocoa / OpenGL event loop on main thread
    window = KaxeViewerWindow(plot_queue)
    pyglet.app.run()


def main(argv=None):
    """Entrypoint for the `kaxe` CLI command."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="kaxe",
        description="Kaxe graphing & plotting toolkit CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # `kaxe viewer` command
    viewer_parser = subparsers.add_parser(
        "viewer",
        help="Start the standalone Kaxe interactive plot viewer",
    )
    viewer_parser.add_argument(
        "--port",
        type=int,
        default=get_viewer_port(),
        help=f"Port to listen on (default: {get_viewer_port()})",
    )

    args = parser.parse_args(argv)

    if args.subcommand == "viewer":
        run_viewer(port=args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
