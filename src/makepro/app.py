#!/usr/bin/env python3

# src/makepro/app.py

"""
App lifecycle / CLI entry for Makepro.

Responsibilities:
- Parse CLI args
- Configure logging
- Validate startup state
- Delay heavy imports until needed
- Launch the UI with validated flags
- Centralise error handling and exit codes

This file must not contain any UI, editing, or file I/O logic.
"""

from __future__ import annotations

import argparse
import logging
import sys
import traceback
from . import file_manager
from pathlib import Path

VERSION = "0.1.0"


# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------

def setup_logging(debug: bool) -> None:
    """Configure the root logger. Called before any heavy work."""
    level = logging.DEBUG if debug else logging.WARNING
    fmt = "%(asctime)s %(levelname)-8s %(name)s - %(message)s"
    logging.basicConfig(level=level, format=fmt)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """ Build the parser and return argparse.ArgumentParser/parser
    
        Arguments:
            file -         file to open on startup
            --version -    Show version and exit
            --readonly -   Open file in read-only mode (UI will lock editing)
            debug -        Enable debug logging and show full tracebacks on crash
            config -       Path to a config file (optional)
    """
    parser = argparse.ArgumentParser(
        prog="makepro",
        description="Makepro — lightweight terminal IDE",
    )

    #file
    parser.add_argument(
        "file",
        nargs="?",
        help="Optional file to open on startup",
    )

    #--version
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    #read-only
    parser.add_argument(
        "--readonly",
        action="store_true",
        help="Open file in read-only mode (UI will lock editing)",
    )

    #debug
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging and show full tracebacks on crash",
    )

    #config
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        metavar="PATH",
        help="Path to a config file (optional)",
    )

    return parser

def isatty() -> bool:
    """ Returns whether std.out/std.in/std.err is a tty(Text Terminal-Type) or not. """
    return sys.stdin.isatty() and sys.stdout.isatty()

# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main() -> int:
    """
    Returns an integer exit code:

      0    — success
      1    — user error  (bad args, missing file)
      2    — unexpected fatal error
      130  — interrupted by user (Ctrl-C / SIGINT)
      160  — standard stream not a tty
    """
    
    
    parser = build_parser()
    args = parser.parse_args()

    # Fast path: --version (never import UI)
    if args.version:
        print(f"makepro {VERSION}")
        return 0

    setup_logging(args.debug)
    log = logging.getLogger("makepro.app")
    log.debug("Args: %s", args)
    
    if not isatty():
        print("fatal: Standard Stream is not a TTY")
        log.error("Standard Stream is not a TTY(Text Terminal-Type)")
        sys.exit(160)

    try:
        file_path = file_manager.validate_readable(args.file)
        config_path = Path(args.config).resolve() if args.config else None

        # Delayed import — keeps CLI-only operations lightweight
        from .ui import MakeproApp  # type: ignore

        MakeproApp(
            file_path=file_path,
            readonly=args.readonly,
            config_path=config_path,
            debug=args.debug,
        ).run()

        log.info("Exited normally.")
        return 0
    
    except ModuleNotFoundError as e:
        print(f"[makepro] Module Not Found: {e.name}, Try installing it with pip install {e.name}")
        return 2
    

    except FileNotFoundError as e:
        print(f"[makepro] {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"[makepro] {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n[makepro] Interrupted.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"[makepro] Fatal error: {e}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        else:
            print(
                "[makepro] Run with --debug for a full traceback.",
                file=sys.stderr,
            )
        return 2


# Allow direct execution during development:
# python src/makepro/app.py somefile.py
if __name__ == "__main__":
    raise SystemExit(main())
