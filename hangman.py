#!/usr/bin/env python3
"""Hangman - a custom Python hangman game for the terminal.

Usage:
    python3 hangman.py                 # random word, 6 lives
    python3 hangman.py --lives 8       # custom lives
    python3 hangman.py --word python   # play with a specific word (2-player)
"""
import argparse
import random
import sys

WORDS = [
    "python", "hangman", "keyboard", "function", "variable", "terminal",
    "notebook", "algorithm", "compiler", "debugging", "security", "network",
    "database", "interface", "protocol", "encryption", "framework",
    "library", "syntax", "runtime", "cyberpunk", "mainframe", "firewall",
]

STAGES = [
    "\n  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========",
    "\n  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========",
    "\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========",
    "\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========",
    "\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========",
    "\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========",
    "\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========",
]


def display(word, guessed):
    return " ".join(ch if ch in guessed else "_" for ch in word)


def play(word, lives):
    guessed, wrong = set(), 0
    max_wrong = min(lives, len(STAGES) - 1)
    print("Welcome to Hangman! Guess the word one letter at a time.")
    while wrong < max_wrong:
        stage = STAGES[round(wrong * (len(STAGES) - 1) / max_wrong)]
        print(stage)
        print("\nWord:   ", display(word, guessed))
        print("Guessed:", " ".join(sorted(guessed)) or "-")
        print(f"Lives left: {max_wrong - wrong}")
        if all(ch in guessed for ch in word):
            print(f"\nYou win! The word was '{word}'.")
            return True
        try:
            guess = input("Guess a letter (or the whole word): ").strip().lower()
        except EOFError:
            print()
            return None
        if not guess:
            continue
        if len(guess) == len(word) and guess.isalpha():
            if guess == word:
                print(f"\nYou win! The word was '{word}'.")
                return True
            wrong += 1
            print("Wrong word!")
            continue
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        if guess in guessed:
            print("Already guessed.")
            continue
        guessed.add(guess)
        if guess not in word:
            wrong += 1
            print(f"No '{guess}'.")
    print(STAGES[-1])
    print(f"\nOut of lives! The word was '{word}'.")
    return False


def lives_value(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("lives must be a number")
    if not 1 <= value <= 6:
        raise argparse.ArgumentTypeError("lives must be between 1 and 6")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description="Terminal hangman game.")
    parser.add_argument("--lives", type=lives_value, default=6,
                        help="wrong guesses allowed (1-6)")
    parser.add_argument("--word", help="specific word to play with")
    args = parser.parse_args(argv)
    word = (args.word or random.choice(WORDS)).lower()
    if not word.isalpha():
        print("error: word must contain letters only", file=sys.stderr)
        return 1
    wins = losses = 0
    while True:
        result = play(word, args.lives)
        if result is True:
            wins += 1
        elif result is False:
            losses += 1
        else:
            print("Game abandoned.")
        print(f"Score: {wins} win(s), {losses} loss(es)")
        try:
            again = input("Play again? [y/N] ").strip().lower()
        except EOFError:
            break
        if again != "y":
            break
        if not args.word:
            word = random.choice(WORDS)
    print("Thanks for playing!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
