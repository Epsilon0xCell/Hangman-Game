"""Tests for hangman.py. I drive play() and main() with scripted input
instead of playing by hand, so a full win, a full loss, and the odd
inputs all run the same way every time."""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import hangman


def run_play(word, lives, guesses):
    """Run one game with a fixed list of guesses and capture its output."""
    with patch("builtins.input", side_effect=list(guesses)) as mock_input, \
            redirect_stdout(io.StringIO()) as out:
        result = hangman.play(word, lives)
    return result, out.getvalue(), mock_input


def run_main(argv, inputs):
    with patch("builtins.input", side_effect=list(inputs)), \
            redirect_stdout(io.StringIO()) as out:
        code = hangman.main(argv)
    return code, out.getvalue()


class DisplayTests(unittest.TestCase):
    def test_nothing_guessed(self):
        self.assertEqual(hangman.display("python", set()), "_ _ _ _ _ _")

    def test_one_guess_reveals_every_position(self):
        self.assertEqual(hangman.display("hangman", {"a"}), "_ a _ _ _ a _")

    def test_full_word_revealed(self):
        self.assertEqual(hangman.display("go", {"g", "o"}), "g o")


class LivesValueTests(unittest.TestCase):
    def test_accepts_bounds(self):
        self.assertEqual(hangman.lives_value("1"), 1)
        self.assertEqual(hangman.lives_value("6"), 6)

    def test_rejects_out_of_range_and_non_number(self):
        for bad in ("0", "7", "x"):
            with self.assertRaises(Exception):
                hangman.lives_value(bad)


class PlayTests(unittest.TestCase):
    def test_win_by_letters(self):
        result, out, _ = run_play("python", 6, ["p", "y", "t", "h", "o", "n"])
        self.assertIs(result, True)
        self.assertIn("You win!", out)

    def test_win_by_whole_word(self):
        result, out, _ = run_play("python", 6, ["python"])
        self.assertIs(result, True)
        self.assertIn("You win!", out)

    def test_loss_after_lives_run_out(self):
        result, out, _ = run_play("python", 2, ["z", "q"])
        self.assertIs(result, False)
        self.assertIn("Out of lives!", out)
        self.assertIn("'python'", out)

    def test_repeated_letter_is_free(self):
        # One wrong letter, the same letter again, then the winning letters.
        # With 2 lives this only wins if the repeat cost nothing.
        result, out, _ = run_play("go", 2, ["z", "z", "g", "o"])
        self.assertIs(result, True)
        self.assertIn("Already guessed.", out)

    def test_repeated_wrong_whole_word_is_free(self):
        # Regression test: before this fix the same wrong word cost a life
        # every time, so two tries at 2 lives ended the game. Now the
        # second try is free and the player can still win by letters.
        result, out, _ = run_play(
            "python", 2, ["zzzzzz", "zzzzzz", "p", "y", "t", "h", "o", "n"])
        self.assertIs(result, True)
        self.assertIn("Wrong word!", out)
        self.assertIn("Already guessed.", out)

    def test_one_letter_word_uses_letter_path(self):
        # Regression test: a wrong guess at a one letter word used to print
        # Wrong word and was never recorded. Now it is a normal letter
        # guess: it costs once, a repeat is free, and the right letter wins.
        result, out, _ = run_play("a", 2, ["b", "b", "a"])
        self.assertIs(result, True)
        self.assertIn("No 'b'.", out)
        self.assertIn("Already guessed.", out)
        self.assertNotIn("Wrong word!", out)

    def test_empty_and_non_letter_guesses_cost_nothing(self):
        result, out, _ = run_play(
            "go", 1, ["", "1", "!!", "g", "o"])
        self.assertIs(result, True)
        self.assertIn("Please enter a single letter.", out)

    def test_multi_letter_entry_that_is_not_the_word_costs_nothing(self):
        result, out, _ = run_play("python", 1, ["py", "python"])
        self.assertIs(result, True)
        self.assertIn("Please enter a single letter.", out)

    def test_eof_abandons_game(self):
        with patch("builtins.input", side_effect=EOFError), \
                redirect_stdout(io.StringIO()) as out:
            result = hangman.play("python", 6)
        self.assertIsNone(result)
        self.assertNotIn("Out of lives!", out.getvalue())


class MainTests(unittest.TestCase):
    def test_full_session_win_then_decline_replay(self):
        code, out = run_main(["--word", "go"], ["g", "o", "n"])
        self.assertEqual(code, 0)
        self.assertIn("Score: 1 win(s), 0 loss(es)", out)
        self.assertIn("Thanks for playing!", out)

    def test_eof_at_first_guess_exits_clean(self):
        with patch("builtins.input", side_effect=EOFError), \
                redirect_stdout(io.StringIO()) as out:
            code = hangman.main(["--word", "python"])
        self.assertEqual(code, 0)
        self.assertIn("Game abandoned.", out.getvalue())
        self.assertIn("Score: 0 win(s), 0 loss(es)", out.getvalue())

    def test_bad_word_returns_1(self):
        code, _ = run_main(["--word", "abc123"], [])
        self.assertEqual(code, 1)

    def test_replay_with_custom_word_reuses_it(self):
        # Win, say yes to replay, win the same word again, then stop.
        code, out = run_main(["--word", "go"],
                             ["g", "o", "y", "g", "o", "n"])
        self.assertEqual(code, 0)
        self.assertIn("Score: 2 win(s), 0 loss(es)", out)


if __name__ == "__main__":
    unittest.main()
