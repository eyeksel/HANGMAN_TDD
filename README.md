# HANGMAN_TDD

OVERVIEW

This project is a Hangman game in Python, developed using Test-Driven Development (TDD).
The game has two modes:
Beginner: random word
Intermediate: random phrase
Players have 15 seconds per guess. Wrong guesses or timeouts deduct lives.

FEATURES

Beginner and Intermediate difficulty
Random word/phrase selection
Countdown timer with life deduction on timeout
Replay option after each game
Code quality checked with flake8 and pylint

How to Run:
# Run the game
python hangman.py
----------------------------------
# Run tests
pytest -q
----------------------------------
# Run linting
flake8 .
pylint hangman.py test_hangman.py

Project Files

hangman.py – main game program
test_hangman.py – pytest unit tests
Software Unit Testing Report_FINAL – assignment report
README.md – project overview
