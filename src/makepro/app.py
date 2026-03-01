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
from pathlib import Path
from typing import Optional

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
    """ Build the parser - argparse.ArgumentParser for parsing the arguments"""
    
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

    parser.add_argument(
        "--readonly",
        action="store_true",
        help="Open file in read-only mode (UI will lock editing)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging and show full tracebacks on crash",
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        metavar="PATH",
        help="Path to a config file (optional)",
    )

    return parser


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------

def validate_file(path: Optional[str]) -> Optional[Path]:
    """
    Validate the given path string and return a resolved Path, or None.

    Raises:
        FileNotFoundError  — path given but does not exist
        ValueError         — path exists but is not a regular file
    """
    if path is None:
        return None

    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not p.is_file():
        raise ValueError(f"Not a file: {path}")

    return p.resolve()


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

    try:
        file_path = validate_file(args.file)
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
