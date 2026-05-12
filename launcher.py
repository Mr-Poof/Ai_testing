#!/usr/bin/env python3
"""Home screen launcher for terminal Python games."""

from __future__ import annotations

import curses
import subprocess
import sys
from pathlib import Path

TITLE = "Python Games for the Terminal"


def draw_home(stdscr: curses.window) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    stdscr.border()

    lines = [
        TITLE,
        "",
        "Press S for Snake",
        "Press P for Pong",
        "Press Q to Quit",
    ]

    start_y = max(1, h // 2 - len(lines) // 2)
    for i, line in enumerate(lines):
        x = max(1, (w - len(line)) // 2)
        stdscr.addnstr(start_y + i, x, line, max(0, w - 2))

    stdscr.refresh()


def run_selected(game_script: str) -> None:
    path = Path(__file__).with_name(game_script)
    if not path.exists():
        print(f"Missing game script: {game_script}")
        input("Press Enter to return to menu...")
        return
    subprocess.run([sys.executable, str(path)], check=False)


def home(stdscr: curses.window) -> None:
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.nodelay(False)
    stdscr.keypad(True)

    while True:
        draw_home(stdscr)
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break
        if key in (ord("s"), ord("S")):
            curses.endwin()
            run_selected("snake.py")
            stdscr.refresh()
        elif key in (ord("p"), ord("P")):
            curses.endwin()
            run_selected("pong.py")
            stdscr.refresh()


def main() -> None:
    curses.wrapper(home)


if __name__ == "__main__":
    main()
