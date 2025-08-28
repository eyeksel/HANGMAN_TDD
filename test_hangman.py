"""Unit tests for the Hangman game."""

import time
import random

import pytest

from hangman import TurnTimer, HangmanGame


def test_initial_mask_shows_underscores_only_for_letters():
    """Letters should be hidden as underscores on start."""
    game = HangmanGame(answer="banana", max_lives=6)
    assert game.masked == "______"


def test_correct_guess_reveals_all_positions():
    """A correct guess reveals all matching positions."""
    game = HangmanGame(answer="banana", max_lives=6)
    was_correct, occurrences = game.guess("a")
    assert was_correct is True
    assert occurrences == 3
    assert game.masked == "_a_a_a"


def test_wrong_guess_deducts_life():
    """A wrong guess deducts one life."""
    game = HangmanGame(answer="banana", max_lives=6)
    was_correct, occurrences = game.guess("z")
    assert was_correct is False
    assert occurrences == 0
    assert game.lives == 5


def test_phrase_keeps_spaces_and_punctuation():
    """Spaces and punctuation remain visible for phrases."""
    game = HangmanGame(answer="hello world!", max_lives=6)
    assert game.masked == "_____ _____!"
    was_correct, occurrences = game.guess("o")
    assert was_correct is True
    assert occurrences == 2
    assert game.masked == "____o _o___!"


def test_random_word_provider_returns_string():
    """Random word provider returns an item from the list."""
    words = ["apple", "banana", "cherry"]
    random.seed(0)
    word = HangmanGame.get_random_word(words)
    assert isinstance(word, str)
    assert word in words


def test_random_phrase_provider_returns_string():
    """Random phrase provider returns an item from the list."""
    phrases = ["hello world", "open ai rocks", "unit testing"]
    random.seed(1)
    phrase = HangmanGame.get_random_phrase(phrases)
    assert isinstance(phrase, str)
    assert phrase in phrases


def test_timer_counts_down_and_expires(monkeypatch):
    """Timer should count down and expire at zero seconds."""
    t = [0.0]
    monkeypatch.setattr(time, "monotonic", lambda: t[0])

    timer = TurnTimer(15)
    timer.start()
    assert timer.is_expired() is False
    assert timer.remaining() == pytest.approx(15.0, abs=0.001)

    t[0] = 10.0
    assert timer.is_expired() is False
    assert timer.remaining() == pytest.approx(5.0, abs=0.001)

    t[0] = 16.0
    assert timer.is_expired() is True
    assert timer.remaining() == pytest.approx(0.0, abs=0.001)


def test_timeout_deducts_single_life(monkeypatch):
    """Timeout deducts one life and does not double-deduct."""
    t = [0.0]
    monkeypatch.setattr(time, "monotonic", lambda: t[0])

    game = HangmanGame(answer="banana", max_lives=6)
    game.start_turn(15)
    assert game.lives == 6

    t[0] = 16.0
    game.handle_timeout()
    assert game.lives == 5

    # Calling again should not deduct twice
    game.handle_timeout()
    assert game.lives == 5
