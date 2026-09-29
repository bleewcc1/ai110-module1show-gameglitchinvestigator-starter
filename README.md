# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- **Purpose:** A Streamlit number-guessing game. The app picks a secret number in a range set by the chosen difficulty (Easy 1-20, Normal 1-100, Hard 1-50), and the player has a limited number of attempts to guess it, getting a "Too High"/"Too Low" hint after each wrong guess and a score based on how efficiently they win.
- **Bugs found:**
  1. **Wrong high/low hints.** On every even-numbered attempt, `app.py` converted the secret to a string (`secret = str(st.session_state.secret)`) before comparing it to the guess. `check_guess` then hit a `try/except TypeError` fallback that compared the two values as strings instead of numbers, so a guess like `80` against a secret of `9` was reported as "Too Low" instead of "Too High" (since `"80" < "9"` lexicographically, even though `80 > 9`).
  2. **Logic duplicated instead of refactored.** `check_guess`, `parse_guess`, `get_range_for_difficulty`, and `update_score` were fully implemented in `app.py`, while `logic_utils.py` only had `NotImplementedError` stubs — so `tests/test_game_logic.py` (which imports from `logic_utils`) couldn't run at all.
  3. **Broken test assertions.** The existing tests compared `check_guess`'s return value directly to a bare string (e.g. `assert result == "Win"`), even though the function returns a `(outcome, message)` tuple — so the tests would fail even once `logic_utils` was implemented correctly.
- **Fixes applied:**
  1. Removed the even-attempt string conversion in `app.py` and moved `check_guess` into `logic_utils.py` with a plain numeric comparison (no more string fallback).
  2. Added a regression test, `test_guess_too_high_lexicographic_edge_case`, using `check_guess(80, 9)` — the pair most likely to expose the bug again if the string-comparison fallback were ever reintroduced.
  3. Fixed the existing tests to unpack the `(outcome, message)` tuple instead of comparing it to a bare string.
  4. Added a `pytest.ini` with `pythonpath = .` so `pytest` (not just `python -m pytest`) can find `logic_utils.py` from the project root.
  5. Moved `parse_guess` into `logic_utils.py` as well (unchanged logic) so its input-parsing behavior — negative numbers, decimals, extremely large values — could be covered directly by pytest (see Challenge 1 below).

## 📸 Demo Walkthrough

1. Game starts on Normal difficulty (secret number between 1 and 100), 8 attempts allowed.
2. User enters a guess of `40` and clicks "Submit Guess 🚀" — the game shows "📉 Go LOWER!" ("Too Low"), meaning the secret is below 40.
3. User enters a guess of `20` — the game shows "📈 Go HIGHER!" ("Too High"), meaning the secret is above 20, narrowing the range to 21–39.
4. Score updates after each guess: a "Too Low" guess subtracts 5 points, alternating "Too High" guesses add or subtract 5 depending on the attempt number, all visible live in the "Developer Debug Info" expander.
5. User enters a guess of `30`, which matches the secret — the game shows "🎉 Correct!", displays balloons, reports the final score, and marks the game as "won" so further guesses are blocked until "New Game 🔁" is clicked.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
============================= test session starts ==============================
platform darwin -- Python 3.11.6, pytest-9.1.1, pluggy-1.6.0
rootdir: ai110-module1show-gameglitchinvestigator-starter
configfile: pytest.ini
collecting ... collected 7 items

tests/test_game_logic.py::test_winning_guess PASSED                      [ 14%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 28%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 42%]
tests/test_game_logic.py::test_guess_too_high_lexicographic_edge_case PASSED [ 57%]
tests/test_game_logic.py::test_parse_guess_negative_number PASSED        [ 71%]
tests/test_game_logic.py::test_parse_guess_decimal_input PASSED          [ 85%]
tests/test_game_logic.py::test_parse_guess_extremely_large_number PASSED [100%]

============================== 7 passed in 0.03s ===============================
```

### Challenge 1: Advanced Edge-Case Testing

Three edge-case inputs to `parse_guess` were identified and covered:

- **Negative number** (`"-5"`) — outside the valid guess range, but must still parse cleanly to `-5` instead of crashing, so `check_guess` can grade it as "Too Low."
- **Decimal input** (`"50.7"`) — a user might type a decimal by habit or mistake; `parse_guess` truncates toward zero (`int(float(raw))`) rather than rejecting or rounding it.
- **Extremely large value** (`"99999999999999999999999999"`) — Python integers are arbitrary precision, so an absurdly large guess should parse without raising `OverflowError`/`ValueError`.

See [ai_interactions.md](ai_interactions.md) for the prompts used to generate these tests.

## 🚀 Stretch Features

### Challenge 4: Enhanced UI

Four structured, user-friendly output changes were added to `app.py`, without changing `check_guess`, `parse_guess`, or `update_score`'s core logic:

- **Structured metrics row.** The old single `st.info(...)` text banner ("Guess a number between 1 and 100. Attempts left: ...") was replaced with a `st.metric` row for Score / Attempts Left / Range, right after the `st.subheader("Make a guess")` line.
- **Color-coded, Hot/Cold hints.** In the `if submit:` block, the hint is now `st.error` (red) for "Too High" and `st.info` (blue) for "Too Low", instead of a single `st.warning` for every outcome. Each hint is also paired with a Hot/Cold emoji cue from the new `get_temperature(guess, secret, low, high)` function in `logic_utils.py`, which buckets how close the guess was (as a fraction of the difficulty's range) into `🔥 Scorching hot!` → `♨️ Hot` → `🌤️ Warm` → `❄️ Cold` → `🧊 Freezing`. A win shows `🎯 Bullseye!` instead.
- **Session summary table.** `st.session_state.history` now stores a structured dict per attempt (`Attempt`, `Guess`, `Result`, `Hint`) instead of a bare guess value, and a `📊 Session Summary` table (`st.table`) renders below the guess form whenever there's at least one attempt. The table is cleared in the `if new_game:` block so it doesn't mix guesses from a previous game.
- **Verification:** ran the app locally with `streamlit run app.py` and drove it with a headless Playwright browser — confirmed the metrics row, red/blue hint coloring, Hot/Cold emoji cues, and the growing session summary table all render correctly across a losing guess, a winning guess, and a fresh "Too High" guess, with no console errors. The existing pytest suite (7 tests) still passes unchanged, since none of the tested functions' logic was touched.
