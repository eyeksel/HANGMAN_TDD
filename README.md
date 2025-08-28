# HANGMAN_TDD

OVERVIEW

This project is a Hangman game written in Python and developed using Test-Driven Development (TDD). The game has two difficulty levels. In Beginner mode, the program randomly selects a single word, while in Intermediate mode, it randomly selects a phrase. Players have fifteen seconds to make each guess, and a life is deducted if the guess is wrong or if the timer runs out. The game ends when the player correctly guesses the word or phrase, when the player runs out of lives, or when the player chooses to quit.

FEATURES

The program allows the user to choose between Beginner and Intermediate modes. It generates random words and phrases, displays underscores for hidden letters, and reveals correct guesses in their correct positions. A countdown timer ensures that each guess must be made within fifteen seconds, and a life is deducted on timeout. The player may replay the game after it finishes. Code quality and readability were validated using flake8 and pylint.

HOW TO RUN

To run the program, execute python hangman.py from the command line. Unit tests can be run using the command pytest -q. Code style checks can be performed with the commands flake8 . and pylint hangman.py test_hangman.py.

PROJECT FILES

This repository contains the main game implementation in hangman.py, the unit tests in test_hangman.py, the written assignment report in Software Unit Testing Report_FINAL (word document), and this README file.
