# src/makepro/terminal/raw_mode.py
# SPDX-License-Identifier: MIT

# Copyright (c) 2026 Anay

# src/makepro/terminal/raw_mode.py

"""
Raw terminal I/O for Makepro.

Responsibilities:

- Enter/exit raw terminal mode (no echo, no line buffering, no signal munging)
- Report terminal size
- Read single keypresses, decoding escape sequences and control bytes into
  a single KeyEvent type

POSIX-only (termios/tty/select). No external dependencies.
"""

from __future__ import annotations

import codecs
import os
import select
import sys
import termios
import tty
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class Key(Enum):
    """Named special keys. Anything not listed here arrives as a plain char."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    HOME = auto()
    END = auto()
    PAGE_UP = auto()
    PAGE_DOWN = auto()
    DELETE = auto()
    BACKSPACE = auto()
    ENTER = auto()
    TAB = auto()
    ESC = auto()

    # Ctrl-H, Ctrl-I, Ctrl-J, Ctrl-M are intentionally absent:
    # those bytes are claimed by BACKSPACE/TAB/ENTER.
    CTRL_A = auto()
    CTRL_B = auto()
    CTRL_C = auto()
    CTRL_D = auto()
    CTRL_E = auto()
    CTRL_F = auto()
    CTRL_G = auto()
    CTRL_K = auto()
    CTRL_L = auto()
    CTRL_N = auto()
    CTRL_O = auto()
    CTRL_P = auto()
    CTRL_Q = auto()
    CTRL_R = auto()
    CTRL_S = auto()
    CTRL_T = auto()
    CTRL_U = auto()
    CTRL_V = auto()
    CTRL_W = auto()
    CTRL_X = auto()
    CTRL_Y = auto()
    CTRL_Z = auto()


@dataclass(frozen=True)
class KeyEvent:
    """
    A single decoded input event.

    KeyEvent(key=Key.UP)   -> special key
    KeyEvent(char="a")     -> printable character
    """

    key: Optional[Key] = None
    char: Optional[str] = None

    def __post_init__(self) -> None:
        if (self.key is None) == (self.char is None):
            raise ValueError(
                "KeyEvent requires exactly one of `key` or `char`"
            )

    @property
    def is_special(self) -> bool:
        return self.key is not None

    @property
    def is_printable(self) -> bool:
        return self.char is not None


# Escape sequences matched after the leading ESC byte.
_ESCAPE_SEQUENCES: dict[str, Key] = {
    "[A": Key.UP,
    "[B": Key.DOWN,
    "[C": Key.RIGHT,
    "[D": Key.LEFT,
    "[H": Key.HOME,
    "[F": Key.END,
    "[1~": Key.HOME,
    "[4~": Key.END,
    "[3~": Key.DELETE,
    "[5~": Key.PAGE_UP,
    "[6~": Key.PAGE_DOWN,
    "OH": Key.HOME,
    "OF": Key.END,
}


# Dedicated control-byte mappings.
_CONTROL_KEYS: dict[str, Key] = {
    "\r": Key.ENTER,
    "\n": Key.ENTER,
    "\t": Key.TAB,
    "\x7f": Key.BACKSPACE,
    "\x08": Key.BACKSPACE,
}


# Fill in Ctrl-A .. Ctrl-Z except for bytes already claimed above.
for _byte in range(1, 27):
    _ch = chr(_byte)

    if _ch in _CONTROL_KEYS:
        continue

    _letter = chr(_byte + 0x60).upper()
    _CONTROL_KEYS[_ch] = Key[f"CTRL_{_letter}"]


class RawMode:
    """
    Context manager that puts the terminal into raw mode and restores
    the previous settings on exit.

    Raw mode disables canonical input, echo, and signal generation.
    Ctrl-C will NOT raise KeyboardInterrupt while active; instead it
    arrives as KeyEvent(key=Key.CTRL_C).
    """

    def __init__(self, fd: Optional[int] = None) -> None:
        self.fd = fd if fd is not None else sys.stdin.fileno()
        self._saved_attrs: Optional[list] = None

    def __enter__(self) -> "RawMode":
        self._saved_attrs = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._saved_attrs is not None:
            try:
                termios.tcsetattr(
                    self.fd,
                    termios.TCSADRAIN,
                    self._saved_attrs,
                )
            finally:
                self._saved_attrs = None


@dataclass(frozen=True)
class TerminalSize:
    columns: int
    rows: int


def get_terminal_size(fd: Optional[int] = None) -> TerminalSize:
    """Return the current terminal size, falling back to 80x24."""

    if fd is None:
        try:
            target_fd = sys.stdout.fileno()
        except OSError:
            return TerminalSize(columns=80, rows=24)
    else:
        target_fd = fd

    try:
        size = os.get_terminal_size(target_fd)
        return TerminalSize(
            columns=size.columns,
            rows=size.lines,
        )
    except OSError:
        return TerminalSize(columns=80, rows=24)


_utf8_decoder = codecs.getincrementaldecoder("utf-8")()


def _read_char(fd: int) -> str:
    """
    Read and decode a single Unicode character.

    Raises:
        EOFError: stdin was closed.
    """

    while True:
        data = os.read(fd, 1)

        if not data:
            raise EOFError("stdin closed")

        text = _utf8_decoder.decode(data)

        if text:
            return text


def _byte_ready(fd: int, timeout: float) -> bool:
    """Return True if input is available within timeout seconds."""

    ready, _, _ = select.select([fd], [], [], timeout)
    return bool(ready)


def read_event(
    fd: Optional[int] = None,
    escape_timeout: float = 0.01,
) -> KeyEvent:
    """
    Block until input arrives and return a KeyEvent.

    Escape sequences (arrows, Home/End, etc.) are decoded by reading
    everything available shortly after an ESC byte.

    Ctrl+<letter> combinations are returned as their corresponding
    Key.CTRL_<LETTER> values.
    """

    fd = fd if fd is not None else sys.stdin.fileno()

    ch = _read_char(fd) # type: ignore

    if ch == "\x1b":
        seq = ""

        while _byte_ready(fd, escape_timeout): # pyright: ignore[reportArgumentType]
            seq += _read_char(fd) # pyright: ignore[reportArgumentType]

        return KeyEvent(
            key=_ESCAPE_SEQUENCES.get(seq, Key.ESC)
        )

    if ch in _CONTROL_KEYS:
        return KeyEvent(key=_CONTROL_KEYS[ch])

    return KeyEvent(char=ch)