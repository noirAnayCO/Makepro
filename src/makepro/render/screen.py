# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Anay

# src/makepro/render/screen.py

"""
Minimal screen primitives for Makepro.

Responsibilities:

- Enter/exit the terminal's alternate screen buffer
- Clear the screen
- Hide/show and position the cursor

This module writes raw ANSI escape sequences to stdout. It does not
implement diffing, redraw scheduling, or layout - that belongs in
higher-level render modules once the core editor exists.
"""

from __future__ import annotations

import sys
from typing import Optional, TextIO

_ENTER_ALT_SCREEN = "\x1b[?1049h"
_EXIT_ALT_SCREEN = "\x1b[?1049l"
_CLEAR_SCREEN = "\x1b[2J"
_CURSOR_HOME = "\x1b[H"
_HIDE_CURSOR = "\x1b[?25l"
_SHOW_CURSOR = "\x1b[?25h"


def _write(stream: TextIO, text: str) -> None:
    stream.write(text)
    stream.flush()


class AlternateScreen:
    """
    Context manager that switches to the terminal's alternate screen
    buffer on entry and restores the user's original screen on exit.

    The alternate screen is a separate buffer most terminal emulators
    support: entering it hides the shell's scrollback behind a blank
    canvas, and leaving it restores exactly what was there before - so
    a crash mid-redraw doesn't leave garbage in the user's history.

    Independent of RawMode (which governs input). Use both together:

        with RawMode(), AlternateScreen():
            ...
    """

    def __init__(self, stream: Optional[TextIO] = None) -> None:
        self.stream = stream if stream is not None else sys.stdout

    def __enter__(self) -> "AlternateScreen":
        _write(self.stream, _ENTER_ALT_SCREEN)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _write(self.stream, _EXIT_ALT_SCREEN)


class HiddenCursor:
    """
    Context manager that hides the terminal cursor on entry and restores
    it on exit. Reduces flicker during redraws.
    """

    def __init__(self, stream: Optional[TextIO] = None) -> None:
        self.stream = stream if stream is not None else sys.stdout

    def __enter__(self) -> "HiddenCursor":
        _write(self.stream, _HIDE_CURSOR)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _write(self.stream, _SHOW_CURSOR)


def clear_screen(stream: Optional[TextIO] = None) -> None:
    """Clear the visible screen and move the cursor to the top-left."""
    stream = stream if stream is not None else sys.stdout
    _write(stream, _CLEAR_SCREEN + _CURSOR_HOME)


def move_cursor(row: int, col: int, stream: Optional[TextIO] = None) -> None:
    """
    Move the cursor to (row, col), 1-indexed from the top-left corner,
    matching terminal convention.
    """
    if row < 1 or col < 1:
        raise ValueError(
            f"row and col must be >= 1, got row={row}, col={col}"
        )

    stream = stream if stream is not None else sys.stdout
    _write(stream, f"\x1b[{row};{col}H")


def draw_lines(lines: list[str], stream: Optional[TextIO] = None) -> None:
    """
    Clear the screen and draw `lines`, one per terminal row, starting
    at the top-left.

    Lines are written with explicit \r\n. In raw mode, output
    post-processing (OPOST) is disabled, so a bare \n does NOT return
    the cursor to column 0 - without \r every line after the first
    would be staircased.

    The caller is responsible for truncating lines to terminal width;
    this function does not wrap or clip.
    """
    stream = stream if stream is not None else sys.stdout

    clear_screen(stream)

    for line in lines:
        _write(stream, line + "\r\n")