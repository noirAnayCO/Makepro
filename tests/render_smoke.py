# test_render.py - manual smoke test, not part of the package
#
# Run from repo root: PYTHONPATH=src python test_render.py
#
# Verify:
# - your normal shell scrollback is untouched after quitting
# - the cursor is hidden during the loop and visible again after
# - lines render flush-left, no staircasing
# - Ctrl-Q or Ctrl-C exits cleanly

from makepro.terminal.raw_mode import RawMode, read_event, Key, get_terminal_size
from makepro.render.screen import AlternateScreen, HiddenCursor, draw_lines, move_cursor


def main() -> None:
    with RawMode(), AlternateScreen(), HiddenCursor():
        size = get_terminal_size()

        lines = [
            "makepro render smoke test",
            f"terminal size: {size.columns}x{size.rows}",
            "",
            "press any key to see it echoed below",
            "Ctrl-Q or Ctrl-C to quit",
            "",
        ]

        draw_lines(lines)

        while True:
            event = read_event()

            if event.key in (Key.CTRL_C, Key.CTRL_Q):
                break

            label = event.key.name if event.key else repr(event.char)
            draw_lines(lines + [f"last event: {label}"])


if __name__ == "__main__":
    main()