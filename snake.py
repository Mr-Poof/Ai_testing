#!/usr/bin/env python3
"""Terminal Snake game using curses.

Controls:
  Arrow keys or WASD to move
  P to pause/resume
  Q to quit
"""

from __future__ import annotations

import curses
import random
import time
from collections import deque


TICK_RATE = 0.10  # seconds per game tick


DIRECTIONS = {
    curses.KEY_UP: (-1, 0),
    curses.KEY_DOWN: (1, 0),
    curses.KEY_LEFT: (0, -1),
    curses.KEY_RIGHT: (0, 1),
    ord("w"): (-1, 0),
    ord("s"): (1, 0),
    ord("a"): (0, -1),
    ord("d"): (0, 1),
}


def make_food(height: int, width: int, snake: deque[tuple[int, int]]) -> tuple[int, int]:
    """Return a random empty cell inside the border."""
    snake_cells = set(snake)
    available = [
        (r, c)
        for r in range(1, height - 1)
        for c in range(1, width - 1)
        if (r, c) not in snake_cells
    ]
    return random.choice(available) if available else (-1, -1)


def draw_frame(
    stdscr: curses.window,
    snake: deque[tuple[int, int]],
    food: tuple[int, int],
    score: int,
    paused: bool,
) -> None:
    """Render game state to the terminal."""
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    # Border
    stdscr.border()

    # HUD
    status = f" Score: {score} | Move: arrows/WASD | P: pause | Q: quit "
    stdscr.addnstr(0, 2, status, max(0, width - 4))

    if paused:
        text = " PAUSED "
        stdscr.addstr(height // 2, max(1, (width - len(text)) // 2), text)

    # Food
    fr, fc = food
    if fr != -1:
        stdscr.addch(fr, fc, "*")

    # Snake
    head = snake[0]
    stdscr.addch(head[0], head[1], "@")
    for r, c in list(snake)[1:]:
        stdscr.addch(r, c, "o")

    stdscr.refresh()


def game_over_screen(stdscr: curses.window, score: int) -> None:
    """Show game over message and wait for keypress."""
    stdscr.nodelay(False)
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    lines = [
        "GAME OVER",
        f"Final score: {score}",
        "Press R to play again or Q to quit",
    ]
    for i, line in enumerate(lines):
        stdscr.addstr(h // 2 - 1 + i, max(1, (w - len(line)) // 2), line)
    stdscr.refresh()



def run_game(stdscr: curses.window) -> bool:
    """Run one game. Returns True if user wants restart."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()
    min_h, min_w = 10, 30
    if height < min_h or width < min_w:
        stdscr.erase()
        msg = f"Terminal too small ({width}x{height}). Need at least {min_w}x{min_h}."
        stdscr.addstr(0, 0, msg)
        stdscr.addstr(2, 0, "Resize terminal and run again. Press any key to exit.")
        stdscr.nodelay(False)
        stdscr.getch()
        return False

    center_r, center_c = height // 2, width // 2
    snake = deque([(center_r, center_c + i) for i in range(3)])
    direction = (0, -1)
    pending_direction = direction
    score = 0
    paused = False
    food = make_food(height, width, snake)

    last_tick = time.monotonic()

    while True:
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            return False
        if key in (ord("p"), ord("P")):
            paused = not paused

        if key in DIRECTIONS:
            nd = DIRECTIONS[key]
            # Prevent instant 180-degree turns.
            if not (nd[0] == -direction[0] and nd[1] == -direction[1]):
                pending_direction = nd

        now = time.monotonic()
        if not paused and now - last_tick >= TICK_RATE:
            last_tick = now
            direction = pending_direction
            dr, dc = direction
            hr, hc = snake[0]
            new_head = (hr + dr, hc + dc)

            # Collision with wall
            if (
                new_head[0] <= 0
                or new_head[0] >= height - 1
                or new_head[1] <= 0
                or new_head[1] >= width - 1
            ):
                break

            # Collision with self
            if new_head in snake:
                break

            snake.appendleft(new_head)

            if new_head == food:
                score += 1
                food = make_food(height, width, snake)
                if food == (-1, -1):
                    # Player filled board.
                    break
            else:
                snake.pop()

        draw_frame(stdscr, snake, food, score, paused)
        time.sleep(0.01)

    game_over_screen(stdscr, score)
    while True:
        k = stdscr.getch()
        if k in (ord("r"), ord("R")):
            return True
        if k in (ord("q"), ord("Q")):
            return False



def main() -> None:
    """Entry point."""

    def _wrapped(stdscr: curses.window) -> None:
        while run_game(stdscr):
            pass

    curses.wrapper(_wrapped)


if __name__ == "__main__":
    main()
