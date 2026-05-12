#!/usr/bin/env python3
"""Terminal Pong game using curses.

Controls:
  Left paddle: W/S
  Right paddle: Up/Down
  P: pause/resume
  Q: quit
"""

from __future__ import annotations

import curses
import random
import time

TICK_RATE = 0.03
PADDLE_SIZE = 5
WIN_SCORE = 10


class Paddle:
    def __init__(self, x: int, y: int, size: int, min_y: int, max_y: int) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.min_y = min_y
        self.max_y = max_y

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + self.size - 1

    def move(self, dy: int) -> None:
        self.y = max(self.min_y, min(self.max_y - self.size + 1, self.y + dy))


class Ball:
    def __init__(self, y: float, x: float, vy: float, vx: float) -> None:
        self.y = y
        self.x = x
        self.vy = vy
        self.vx = vx

    def reset(self, y: float, x: float, direction: int) -> None:
        self.y = y
        self.x = x
        self.vx = 0.8 * direction
        self.vy = random.uniform(-0.45, 0.45)


def draw(stdscr: curses.window, left: Paddle, right: Paddle, ball: Ball, score_l: int, score_r: int, paused: bool) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    stdscr.border()

    title = f" Pong | {score_l} : {score_r} | W/S vs ↑/↓ | P pause | Q quit "
    stdscr.addnstr(0, 2, title, max(0, w - 4))

    for y in range(1, h - 1):
        if y % 2 == 0:
            stdscr.addch(y, w // 2, "|")

    for y in range(left.top, left.bottom + 1):
        stdscr.addch(y, left.x, "█")
    for y in range(right.top, right.bottom + 1):
        stdscr.addch(y, right.x, "█")

    stdscr.addch(int(round(ball.y)), int(round(ball.x)), "●")

    if paused:
        msg = " PAUSED "
        stdscr.addstr(h // 2, max(1, (w - len(msg)) // 2), msg)

    stdscr.refresh()


def update_ball(ball: Ball, left: Paddle, right: Paddle, h: int, w: int) -> int:
    """Move ball and return scoring side: -1 none, 0 left scored, 1 right scored."""
    next_y = ball.y + ball.vy
    next_x = ball.x + ball.vx

    if next_y <= 1:
        next_y = 1
        ball.vy *= -1
    elif next_y >= h - 2:
        next_y = h - 2
        ball.vy *= -1

    # Left paddle collision
    if int(round(next_x)) <= left.x + 1 and left.top <= int(round(next_y)) <= left.bottom:
        next_x = left.x + 2
        ball.vx = abs(ball.vx) * 1.04
        offset = (next_y - (left.top + left.size / 2)) / (left.size / 2)
        ball.vy += offset * 0.18

    # Right paddle collision
    if int(round(next_x)) >= right.x - 1 and right.top <= int(round(next_y)) <= right.bottom:
        next_x = right.x - 2
        ball.vx = -abs(ball.vx) * 1.04
        offset = (next_y - (right.top + right.size / 2)) / (right.size / 2)
        ball.vy += offset * 0.18

    ball.vy = max(-1.2, min(1.2, ball.vy))

    if next_x <= 0:
        return 1
    if next_x >= w - 1:
        return 0

    ball.x = next_x
    ball.y = next_y
    return -1


def winner_screen(stdscr: curses.window, score_l: int, score_r: int) -> bool:
    h, w = stdscr.getmaxyx()
    stdscr.nodelay(False)
    stdscr.erase()
    winner = "Left Player Wins!" if score_l > score_r else "Right Player Wins!"
    lines = [winner, f"Final score: {score_l} - {score_r}", "Press R to replay or Q to quit"]
    for i, line in enumerate(lines):
        stdscr.addstr(h // 2 - 1 + i, max(1, (w - len(line)) // 2), line)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in (ord("r"), ord("R")):
            return True
        if key in (ord("q"), ord("Q")):
            return False


def run_match(stdscr: curses.window) -> bool:
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.nodelay(True)
    stdscr.keypad(True)

    h, w = stdscr.getmaxyx()
    if h < 18 or w < 60:
        stdscr.nodelay(False)
        stdscr.erase()
        stdscr.addstr(0, 0, f"Terminal too small ({w}x{h}); need at least 60x18.")
        stdscr.addstr(2, 0, "Resize your terminal, then run again. Press any key to exit.")
        stdscr.refresh()
        stdscr.getch()
        return False

    left = Paddle(3, h // 2 - PADDLE_SIZE // 2, PADDLE_SIZE, 1, h - 2)
    right = Paddle(w - 4, h // 2 - PADDLE_SIZE // 2, PADDLE_SIZE, 1, h - 2)

    ball = Ball(h / 2, w / 2, random.uniform(-0.3, 0.3), random.choice([-0.8, 0.8]))
    score_l = 0
    score_r = 0
    paused = False

    last_tick = time.monotonic()
    while True:
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            return False
        if key in (ord("p"), ord("P")):
            paused = not paused

        if key in (ord("w"), ord("W")):
            left.move(-1)
        elif key in (ord("s"), ord("S")):
            left.move(1)

        if key == curses.KEY_UP:
            right.move(-1)
        elif key == curses.KEY_DOWN:
            right.move(1)

        now = time.monotonic()
        if not paused and now - last_tick >= TICK_RATE:
            last_tick = now
            scored = update_ball(ball, left, right, h, w)
            if scored == 0:
                score_l += 1
                ball.reset(h / 2, w / 2, direction=1)
            elif scored == 1:
                score_r += 1
                ball.reset(h / 2, w / 2, direction=-1)

            if score_l >= WIN_SCORE or score_r >= WIN_SCORE:
                return winner_screen(stdscr, score_l, score_r)

        draw(stdscr, left, right, ball, score_l, score_r, paused)
        time.sleep(0.005)


def main() -> None:
    def _wrapped(stdscr: curses.window) -> None:
        while run_match(stdscr):
            pass

    curses.wrapper(_wrapped)


if __name__ == "__main__":
    main()
