# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| | | | |
| | | | |
| | | | |

---

## 2. How did you use AI as a teammate?

I used Claude Code (Claude Sonnet 5) in agent mode as my main assistant for this project — it could read the files, run pytest, and edit code directly instead of me copy-pasting snippets back and forth.

**Correct suggestion:** I asked it to find where the high/low hint logic was breaking. It traced the bug to `app.py`, where every even-numbered attempt ran `secret = str(st.session_state.secret)` before calling `check_guess`. Because `check_guess` had a `try/except TypeError` fallback that compared the guess and secret as strings, a guess like `80` against a secret of `9` came back as "Too Low" instead of "Too High" (since `"80" < "9"` lexicographically, even though `80 > 9` numerically). I verified this was correct by manually running the old buggy code path against `(80, 9)` in a Python shell and confirming it really did produce "Too Low," then confirming the fixed code produces "Too High" for the same inputs.

**Suggestion I changed:** When it first fixed the bug, its instinct was to just delete the `secret = str(...)` conversion in `app.py` but leave `check_guess`'s `try/except TypeError` string-fallback in place "as defensive code," since it wasn't explicitly asked to touch that part. I didn't think that was the right call once I asked it to also move `check_guess` into `logic_utils.py` — that fallback existed only to paper over the exact type mismatch we had just removed, so keeping it would leave dead, confusing code and a stray behavior path with no way to reach it. I had it rewrite `check_guess` with a plain numeric comparison instead. I verified this version was still correct by adding a regression test (`check_guess(80, 9)` should be `"Too High"`) and running the full pytest suite to confirm all four tests passed.

---

## 3. Debugging and testing your fixes

I considered a bug "really fixed" only once I had a concrete before/after comparison, not just a code change that looked reasonable. For the high/low bug, I first re-created the old buggy comparison logic in a throwaway Python snippet and ran it against `guess=80, secret=str(9)` — it printed `("Too Low", "Go LOWER")`, confirming the bug was real and not just a hunch. Then I ran the same inputs (as plain ints) through the fixed `check_guess` in `logic_utils.py` and got `("Too High", "📈 Go HIGHER!")`, which is the numerically correct answer.

To lock that in, I added `test_guess_too_high_lexicographic_edge_case` to `tests/test_game_logic.py`, asserting `check_guess(80, 9)` returns `"Too High"` — this specific input was chosen because `"80"` and `"9"` compare in the opposite order as strings versus as integers, so it's the input most likely to catch a regression if the string-fallback bug were ever reintroduced. Running `pytest -v` showed all 4 tests passing (`test_winning_guess`, `test_guess_too_high`, `test_guess_too_low`, and the new regression test). I also had to fix a separate, unrelated pytest problem along the way: running bare `pytest` failed with `ModuleNotFoundError: No module named 'logic_utils'` because pytest only adds the `tests/` folder to `sys.path`, not the project root — I added a `pytest.ini` with `pythonpath = .` so the tests can always find `logic_utils.py` regardless of how pytest is invoked.

AI helped design the regression test by picking `80` vs `9` specifically because it's the smallest, clearest example where string comparison and integer comparison disagree — I would not have picked that number pair as quickly on my own, and it made the test meaningfully target the bug instead of just re-testing normal cases.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
