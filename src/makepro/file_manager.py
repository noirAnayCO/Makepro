# src/makepro/file_manager.py
"""
Filesystem utilities for Makepro.

Responsibilities:
- Validate paths (readable / writable)
- Read file contents (with clear exceptions)
- Write files atomically (safe write + optional backup)
- Keep filesystem logic isolated from CLI/UI/editor

This module raises standard Python exceptions for the caller to handle:
- FileNotFoundError
- PermissionError
- ValueError
- OSError (for other IO issues)

NOTE : No instances shall be initialised! 
"""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("makepro.file_manager")


# -----------------------
# Validation / helpers
# -----------------------

@staticmethod
def validate_readable(path: str) -> Path:
    """
    Validate that the given path exists, is a file, and is readable.

    Raises:
        FileNotFoundError: if path does not exist
        ValueError: if path exists but is not a regular file
        PermissionError: if path is not readable
    Returns:
        resolved Path
    """
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not p.is_file():
        raise ValueError(f"Not a file: {path}")

    if not os.access(p, os.R_OK):
        raise PermissionError(f"Permission denied (not readable): {path}")

    return p.resolve()

@staticmethod
def validate_writable(path: str, create: bool = False) -> Path:
    """
    Validate that the given path is writable.

    If `create` is False:
        - The path must exist and be a regular file, and be writable.
    If `create` is True:
        - The parent directory must exist and be writable (so we can create the file).
        - If the file exists, it must be writable.

    Raises:
        FileNotFoundError: if path (or parent) doesn't exist in cases where it should
        ValueError: if path exists but is not a regular file
        PermissionError: if not writable
    Returns:
        resolved Path
    """
    p = Path(path)

    if p.exists():
        # If exists, ensure it's a file
        if not p.is_file():
            raise ValueError(f"Not a file: {path}")

        # Ensure writable
        if not os.access(p, os.W_OK):
            raise PermissionError(f"Permission denied (not writable): {path}")

        return p.resolve()

    # If file does not exist
    parent = p.parent
    if not parent.exists():
        raise FileNotFoundError(f"Parent directory does not exist: {parent}")

    if not parent.is_dir():
        raise ValueError(f"Parent is not a directory: {parent}")

    # Ensure we can create files in parent
    if not os.access(parent, os.W_OK):
        raise PermissionError(f"Permission denied (cannot create file in): {parent}")

    return p.resolve()


# -----------------------
# Read / Write operations
# -----------------------

@staticmethod
def read_file(path: Path, encoding: str = "utf-8") -> str:
    """
    Read and return file contents as text.

    This function assumes the caller already validated the path (or will catch exceptions).
    It will surface:
      - FileNotFoundError
      - PermissionError
      - OSError for other IO issues
    """
    logger.debug("Reading file: %s", path)
    try:
        with path.open("r", encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        logger.error("File not found during open: %s", path)
        raise
    except PermissionError:
        logger.error("Permission denied reading file: %s", path)
        raise
    except OSError as e:
        logger.exception("I/O error reading file %s: %s", path, e)
        raise


@staticmethod
def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write content to `path` atomically using a temporary file in the same directory,
    then rename (os.replace) into place. Ensures data is flushed and fsynced.

    Raises:
      - PermissionError
      - OSError
    """
    logger.debug("Atomic write to: %s", path)
    dirpath = path.parent

    # Ensure the directory exists
    if not dirpath.exists():
        raise FileNotFoundError(f"Directory does not exist: {dirpath}")

    # Use NamedTemporaryFile in the same dir so os.replace is atomic on POSIX
    fd = None
    tmp_path = None
    try:
        # mkstemp gives us a file descriptor and a path, safer for fsync usage
        fd, tmp = tempfile.mkstemp(prefix=".makepro_tmp_", dir=str(dirpath))
        tmp_path = Path(tmp)
        logger.debug("Writing to temp file %s", tmp_path)

        # Open file descriptor and write
        with os.fdopen(fd, "w", encoding=encoding) as tf:
            tf.write(content)
            tf.flush()
            os.fsync(tf.fileno())

        # Atomically replace target
        os.replace(str(tmp_path), str(path))
        logger.debug("Replaced %s with %s", path, tmp_path)

    except PermissionError:
        logger.exception("Permission denied during atomic write to %s", path)
        # attempt to clean up tmp file if it exists
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                logger.debug("Failed to remove temp file %s after PermissionError", tmp_path)
        raise
    except OSError as e:
        logger.exception("OS error during atomic write to %s: %s", path, e)
        # cleanup
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                logger.debug("Failed to remove temp file %s after OSError", tmp_path)
        raise


@staticmethod
def write_file(path: Path, content: str, *, create: bool = False, backup: bool = False, encoding: str = "utf-8") -> None:
    """
    Safely write `content` to `path`.

    Parameters:
      - create: if True, allow creating the file (if it doesn't exist). If False, FileNotFoundError is raised.
      - backup: if True and the target exists, create a backup copy alongside the original (filename.bak)
      - encoding: text encoding to use

    Raises:
      - FileNotFoundError
      - PermissionError
      - ValueError
      - OSError
    """
    logger.debug("write_file(path=%s, create=%s, backup=%s)", path, create, backup)
    p = Path(path)

    if p.exists():
        if not p.is_file():
            raise ValueError(f"Not a file: {p}")

        # If file exists but not writable
        if not os.access(p, os.W_OK):
            raise PermissionError(f"Permission denied (not writable): {p}")

        # Optionally back up
        if backup:
            bak = p.with_name(p.name + ".bak")
            logger.debug("Creating backup: %s", bak)
            shutil.copy2(p, bak)

    else:
        if not create:
            raise FileNotFoundError(f"File does not exist: {p}")

        # Ensure parent exists and is writable
        parent = p.parent
        if not parent.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {parent}")
        if not os.access(parent, os.W_OK):
            raise PermissionError(f"Permission denied (cannot create file in): {parent}")

    # Perform atomic write (this will replace the file if it exists)
    atomic_write(p, content, encoding=encoding)


# -----------------------
# Convenience high-level API
# -----------------------

@staticmethod
def open_for_read(path_str: Optional[str]) -> Optional[str]:
    """
    Convenience: given a path string or None, validate then read and return text.
    Returns None if path_str is None.
    Caller should catch and handle exceptions.
    """
    if path_str is None:
        return None

    p = validate_readable(path_str)  # may raise
    return read_file(p)

@staticmethod
def open_for_write(path_str: str, content: str, *, create: bool = False, backup: bool = False) -> None:
    """
    Convenience wrapper: validate path for write then write content.
    Caller should catch and handle exceptions.
    """
    p = validate_writable(path_str, create=create)
    write_file(p, content, create=create, backup=backup)