# hangman.py
from __future__ import annotations

import math
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Optional


# ---------------- Timer ---------------- #
class TurnTimer:
    """Countdown timer based on time.monotonic()."""

    def __init__(self, duration_sec: float = 15.0) -> None:
        self.duration = float(duration_sec)
        self._deadline: Optional[float] = None

    def start(self) -> None:
        self._deadline = time.monotonic() + self.duration

    def is_expired(self) -> bool:
        return self.remaining() <= 0.0

    def remaining(self) -> float:
        if self._deadline is None:
            return self.duration
        return max(0.0, float(self._deadline - time.monotonic()))

    def deadline(self) -> float:
        if self._deadline is None:
            return time.monotonic() + self.duration
        return self._deadline


# ---------------- Core game engine ---------------- #
@dataclass
class HangmanGame:
    """Core Hangman logic."""

    answer: str
    max_lives: int = 6

    lives: int = field(init=False)
    _answer_norm: str = field(init=False, repr=False)
    _masked_chars: list[str] = field(init=False, repr=False)
    guessed_letters: set[str] = field(default_factory=set, init=False)

    _turn_timer: Optional[TurnTimer] = field(
        default=None, init=False, repr=False
    )
    _timeout_penalized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self.lives = self.max_lives
        self._answer_norm = self.answer.lower()
        self._masked_chars = [
            "_" if ch.isalpha() else ch for ch in self.answer
        ]

    @property
    def masked(self) -> str:
        return "".join(self._masked_chars)

    def guess(self, letter: str) -> tuple[bool, int]:
        if not letter or len(letter) != 1 or not letter.isalpha():
            raise ValueError("Guess must be a single alphabetic character.")

        letter = letter.lower()

        if letter in self.guessed_letters:
            return (letter in self._answer_norm, 0)

        self.guessed_letters.add(letter)

        count = 0
        for idx, ch in enumerate(self._answer_norm):
            if ch == letter and self._masked_chars[idx] == "_":
                self._masked_chars[idx] = self.answer[idx]
                count += 1

        if count == 0:
            self.lives -= 1
            return (False, 0)
        return (True, count)

    def is_solved(self) -> bool:
        return "_" not in self._masked_chars

    def is_dead(self) -> bool:
        return self.lives <= 0

    def start_turn(self, duration_sec: float = 15.0) -> None:
        self._turn_timer = TurnTimer(duration_sec)
        self._turn_timer.start()
        self._timeout_penalized = False

    def handle_timeout(self) -> None:
        if (self._turn_timer and
                not self._timeout_penalized and
                self._turn_timer.is_expired()):
            self.lives -= 1
            self._timeout_penalized = True

    def remaining_time(self) -> int:
        if not self._turn_timer:
            return 0
        return int(self._turn_timer.remaining())

    @staticmethod
    def get_random_word(word_list: list[str]) -> str:
        import random
        return random.choice(word_list)

    @staticmethod
    def get_random_phrase(phrase_list: list[str]) -> str:
        import random
        return random.choice(phrase_list)


# ---------------- Platform I/O helpers ---------------- #
CURRENT_GAME: HangmanGame  # used by Windows HUD helper


def _read_line_with_deadline_windows(deadline: float) -> str | None:
    """
    Read a line with Enter on Windows, with a live countdown.
    Returns the line (lowercased) or None if time expired.
    """
    import msvcrt  # type: ignore[attr-defined]

    buf = ""
    last_shown = -1

    while True:
        display_secs = max(0, math.ceil(deadline - time.monotonic()))
        if display_secs != last_shown:
            hud = (
                f"Word: {CURRENT_GAME.masked}   Lives: {CURRENT_GAME.lives}   "
                f"Time: {display_secs:02d}s   "
                f"In: {buf}"
            )
            sys.stdout.write("\r" + hud)
            sys.stdout.flush()
            last_shown = display_secs

        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print()
                return buf.strip().lower()
            if ch == "\b":
                buf = buf[:-1]
            else:
                buf += ch

        if time.monotonic() >= deadline:
            print()
            return None

        time.sleep(0.02)


def _read_line_with_timeout_posix(timeout_sec: float) -> str | None:
    """Read one line with a timeout. Portable fallback (no live countdown)."""
    done = threading.Event()
    box: dict[str, str] = {}

    def _reader() -> None:
        try:
            s = input("Enter a letter: ").strip().lower()
        except EOFError:
            s = ""
        box["s"] = s
        done.set()

    threading.Thread(target=_reader, daemon=True).start()
    if done.wait(timeout_sec):
        return box.get("s", "")
    return None


# ---------------- Game loop and menus ---------------- #
def choose_mode() -> str:
    """Ask user to choose Beginner or Intermediate."""
    while True:
        print("\n=== Hangman Menu ===")
        print("1) Beginner (random word)")
        print("2) Intermediate (random phrase)")
        choice = input("Select difficulty (1/2): ").strip()
        if choice == "1":
            return "basic"
        if choice == "2":
            return "intermediate"
        print("Invalid choice. Please enter 1 or 2.")


def ask_play_again() -> bool:
    """Ask if the player wants to play again."""
    while True:
        ans = input("\nPlay again? (y/n): ").strip().lower()
        if ans in {"y", "yes"}:
            return True
        if ans in {"n", "no"}:
            return False
        print("Please enter y or n.")


def run_single_game(mode: str) -> None:
    """Run one game session in the chosen mode."""
    words = [
        "python", "banana", "hangman", "testing", "quality",
        "module", "package", "function", "variable", "exception",
        "object", "class", "method", "loop", "string",
        "integer", "boolean", "dictionary", "tuple", "syntax",
        "compile", "runtime", "debug", "memory", "process",
        "thread", "queue", "input", "output", "file",
        "system", "network", "socket", "server", "client",
    ]
    phrases = [
        "hello world", "unit testing", "clean code", "open source",
        "time and space", "read the docs", "pep eight", "software design",
        "data structures", "object oriented", "artificial intelligence",
        "machine learning", "deep learning", "version control",
        "continuous integration", "code review", "error handling",
        "garbage collection", "software engineering",
        "application programming",
    ]

    answer = (
        HangmanGame.get_random_word(words)
        if mode == "basic"
        else HangmanGame.get_random_phrase(phrases)
    )
    game = HangmanGame(answer=answer, max_lives=6)

    global CURRENT_GAME
    CURRENT_GAME = game

    print("\n=== Hangman ===")
    print("Type 'quit' to exit this game.\n")

    while not game.is_dead() and not game.is_solved():
        game.start_turn(15)

        if os.name == "nt":
            # Split across lines to satisfy flake8
            user = _read_line_with_deadline_windows(
                game._turn_timer.deadline()
            )
        else:
            print(
                "\n"
                f"Word: {game.masked}   "
                f"Lives: {game.lives}   "
                "Time left: 15s"
            )
            user = _read_line_with_timeout_posix(15.0)

        if user is None:
            game.handle_timeout()
            if getattr(game, "_timeout_penalized", False):
                print("Time's up! Life deducted.")
            continue

        if user == "quit":
            print(
                "\nYou quit the game. The answer was:",
                game.answer,
            )
            return

        if len(user) == 1 and user.isalpha():
            if user in game.guessed_letters:
                print("You already guessed that letter.")
                continue
            correct, count = game.guess(user)
            if correct:
                print(f"Revealed {count} position(s).")
            else:
                print("Wrong guess. Life deducted.")
        else:
            print("Please enter a single letter (a-z).")

    if game.is_solved():
        print("\nYou solved it!")
    else:
        print("\nNo lives left.")
    print("Answer:", game.answer)


def main() -> None:
    """Main loop with menu and play-again prompt."""
    while True:
        mode = choose_mode()
        run_single_game(mode)
        if not ask_play_again():
            print("\nThanks for playing.")
            break


if __name__ == "__main__":
    main()
