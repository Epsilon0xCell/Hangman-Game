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

# I keep the word list in this file on purpose. I did not want a game this
# small to fail at startup because a data file was missing or in the wrong
# folder. Every entry is lowercase and letters only, which matters below:
# main() only checks a word once, and the random picks never get rechecked.
WORDS = [
    "python", "hangman", "keyboard", "function", "variable", "terminal",
    "notebook", "algorithm", "compiler", "debugging", "security", "network",
    "database", "interface", "protocol", "encryption", "framework",
    "library", "syntax", "runtime", "cyberpunk", "mainframe", "firewall",
]

# I have seven drawings, not one per life. Index 0 is the empty gallows and
# index 6 is the finished figure, and play() scales the wrong count onto
# this range, so a 2 life game still jumps through the later drawings
# instead of stopping at drawing 2. Each string starts with a blank line
# because print() adds its own ending and I wanted air above the gallows.
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
    # I test membership here instead of tracking positions. That is why one
    # correct guess reveals a letter in every place it occurs, and why
    # play() can keep right and wrong guesses in a single set.
    return " ".join(ch if ch in guessed else "_" for ch in word)


def play(word, lives):
    guessed, wrong = set(), 0
    # I clamp lives to the number of drawings I actually have. main() already
    # limits --lives to 1 through 6 through lives_value(), so this clamp only
    # bites if someone imports play() and calls it directly with a bigger
    # number. Without it a 10 life game would sit on the same drawing for
    # several wrong guesses in a row, because the scale below has only seven
    # drawings to spread those guesses over.
    max_wrong = min(lives, len(STAGES) - 1)
    print("Welcome to Hangman! Guess the word one letter at a time.")
    while wrong < max_wrong:
        # I scale wrong onto the full drawing range. With 6 lives this is
        # just wrong itself. With 2 lives, one wrong guess already lands on
        # drawing 3, and the second wrong guess ends the game before a board
        # with drawing 6 is printed in the loop, so the loss path after the
        # loop prints STAGES[-1] itself instead.
        stage = STAGES[round(wrong * (len(STAGES) - 1) / max_wrong)]
        print(stage)
        print("\nWord:   ", display(word, guessed))
        print("Guessed:", " ".join(sorted(guessed)) or "-")
        print(f"Lives left: {max_wrong - wrong}")
        # I check the win at the top of the loop, after printing the board.
        # That ordering is deliberate: the player sees the completed word on
        # a fresh board before the win line. The cost is one extra board
        # print after the last correct letter, which I accept.
        if all(ch in guessed for ch in word):
            print(f"\nYou win! The word was '{word}'.")
            return True
        try:
            # I strip and lowercase every guess once, here, so the checks
            # below never have to think about spaces or capital letters.
            # A guess of " P " and a guess of "p" are the same guess.
            guess = input("Guess a letter (or the whole word): ").strip().lower()
        except EOFError:
            # I return None here, not False. Closing input, for example the
            # end of a piped file, is not a loss, and main() relies on None
            # to leave both score counters alone and print Game abandoned.
            # The bare print() ends the prompt line the cursor is sitting on.
            print()
            return None
        if not guess:
            # Empty input costs nothing and skips nothing else. I just redraw
            # the board and ask again.
            continue
        # I try the whole word guess before the single letter checks. The
        # order matters for a one letter custom word: a single letter then
        # takes this branch, so a wrong try prints Wrong word and is never
        # added to guessed below.
        if len(guess) == len(word) and guess.isalpha():
            if guess == word:
                print(f"\nYou win! The word was '{word}'.")
                return True
            # A wrong whole word guess costs a life but I do not record it
            # in guessed. That means typing the same wrong word twice costs
            # two lives, unlike a repeated single letter, which is free.
            # I know that gap is there. I left it because the whole word
            # path is a shortcut attempt, not a letter guess.
            wrong += 1
            print("Wrong word!")
            continue
        # Anything that reaches here and is not exactly one letter is
        # rejected with no cost. That includes a multi letter entry shorter
        # or longer than the word, a digit, and punctuation. The message
        # says single letter even for a long entry, which is the prompt the
        # README documents, so I keep the wording matched to the README.
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        if guess in guessed:
            print("Already guessed.")
            continue
        # I add the letter before I test it against the word, so a wrong
        # letter lands in guessed too. That one set then drives the board,
        # the sorted Guessed line, and the Already guessed check above.
        guessed.add(guess)
        if guess not in word:
            wrong += 1
            print(f"No '{guess}'.")
    # The loop only exits here when wrong has reached max_wrong. I print the
    # last drawing directly because the in loop print never got a turn with
    # this wrong count, then I name the word, since hiding it after a loss
    # would leave the player with no answer.
    print(STAGES[-1])
    print(f"\nOut of lives! The word was '{word}'.")
    return False


def lives_value(text):
    # I put the range check in the argparse type instead of in main(). A bad
    # value then fails during parsing, before any game starts, and argparse
    # prints the message and exits with status 2 on its own.
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("lives must be a number")
    # The upper bound is 6 because STAGES has six wrong steps. Letting a
    # player ask for 8 lives would promise drawings I do not have.
    if not 1 <= value <= 6:
        raise argparse.ArgumentTypeError("lives must be between 1 and 6")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description="Terminal hangman game.")
    parser.add_argument("--lives", type=lives_value, default=6,
                        help="wrong guesses allowed (1-6)")
    parser.add_argument("--word", help="specific word to play with")
    args = parser.parse_args(argv)
    # An empty --word string falls back to a random pick here because an
    # empty string is falsy. I check letters only once, before the replay
    # loop: random picks come from WORDS above, and a custom word is reused
    # unchanged on replay, so no later round can introduce a new bad word.
    word = (args.word or random.choice(WORDS)).lower()
    if not word.isalpha():
        print("error: word must contain letters only", file=sys.stderr)
        return 1
    # The score lives outside play() because play() only knows one game.
    # None from an abandoned game matches neither branch below, so an EOF
    # game changes neither counter, which is the behavior I want.
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
            # EOF at this prompt is a normal exit, not an abandoned game.
            # I break instead of returning, so the Thanks line below still
            # prints and main still returns 0.
            break
        if again != "y":
            break
        # I only draw a new word when the player did not supply one. With
        # --word the replay is the same word again on purpose: the word was
        # picked for this session, so replaying means another run at that
        # same word. I do not lowercase or recheck the new random word:
        # every entry in WORDS is already lowercase and letters only.
        if not args.word:
            word = random.choice(WORDS)
    print("Thanks for playing!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
