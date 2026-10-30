![Hangman Game banner](banner.png)

# Hangman-Game

A custom Python Hangman game for the terminal.

Requirements: Python 3, standard library only.

## Run

```bash
python3 hangman.py                  # random word from the built-in list
python3 hangman.py --lives 4        # allow only 4 wrong guesses
python3 hangman.py --word secret    # two-player: play with a specific word
```

## How to play

- The word is shown as one underscore per letter, with a gallows drawing
  that advances as wrong guesses are used up.
- Guess one letter at a time. A correct letter is revealed everywhere it
  occurs. A wrong letter costs one life.
- Typing the whole word at the prompt also wins if it matches exactly;
  a wrong whole-word guess costs one life.
- Empty input is ignored. A multi-letter entry that is not the whole word,
  a digit, or any other non-letter prints `Please enter a single letter.`
  Guessing a letter you already tried prints `Already guessed.` Neither
  costs a life.
- You win by revealing every letter or guessing the whole word before your
  lives run out. You lose when the lives reach zero, and the word is then
  revealed.

## Options

- `--lives N` - wrong guesses allowed, from 1 to 6 (default 6). Values
  outside that range, and non-numeric values, are rejected by argparse
  with exit status 2.
- `--word WORD` - the word to guess, lowercased before play. A word with
  anything other than letters is rejected with an error and exit status 1.

After each game the running score (wins and losses) is printed and you can
play again with `y`. With `--word`, playing again reuses the same word.
Without `--word`, each new game picks a new random word. Closing input
(EOF) during a game abandons that game: it is not counted as a win or a
loss. Exit status is 0 for a completed session.

## Files

- `hangman.py` - the whole game, including the built-in word list
- `logo.png`, `banner.png` - project branding
- `LICENSE` - MIT license

## License

MIT (see LICENSE).
