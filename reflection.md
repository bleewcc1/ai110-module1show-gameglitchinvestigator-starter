# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The game itself launched fine and looked normal — Streamlit rendered the title, sidebar, difficulty picker, and guess box without errors. The problems only showed up once I actually played: the "Too High"/"Too Low" hints were unreliable, flipping to the wrong direction on some attempts but not others, which made the game unwinnable by logic alone. Separately, the test suite couldn't even run: `logic_utils.py` only contained `NotImplementedError` stubs, so anything that depended on it (including `tests/test_game_logic.py`, which imports `check_guess` from there) failed immediately instead of giving real pass/fail feedback.

**Bug Reproduction Log**

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Difficulty: Normal. Attempt #2 (even), guess `80`, secret `9` | "Too High" (📈 Go HIGHER!) | "Too Low" (📉 Go LOWER!) — wrong direction | No error printed; the hint was just silently wrong because `app.py` stringified the secret on even attempts, pushing `check_guess` into a string-comparison fallback |
| Run `pytest` from a fresh checkout | Tests execute and report pass/fail for `check_guess` | Collection/test failure | `NotImplementedError: Refactor this function from app.py into logic_utils.py`, raised the moment a test called into the stubbed-out `logic_utils.check_guess` |
| Difficulty: Easy (range 1–20), click "New Game 🔁" | New secret drawn from the Easy range shown in the sidebar (1–20) | New secret drawn from a hardcoded `random.randint(1, 100)` in the "New Game" handler, ignoring the selected difficulty | No error; sidebar still said "Range: 1 to 20" while the real secret could be any number 1–100 (noticed but not part of the fixes applied — see Section 2) |

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

I'd tell a friend that a Streamlit app isn't really a running program with a memory the way they'd expect — every time you click a button, type into a box, or change a dropdown, Streamlit throws away the whole in-memory state and reruns your entire script from top to bottom, like restarting the file. If that were the whole story, every variable would reset to its initial value on every click (the secret number would re-roll itself constantly), which is exactly the kind of "impossible to win" bug this project's setup mentions. `st.session_state` is the escape hatch: it's a dictionary-like object that survives across those reruns for a given browser session, so code like `if "secret" not in st.session_state: st.session_state.secret = random.randint(...)` only picks a new secret the very first time, and every rerun after that just reads the same value back out instead of generating a new one. In this codebase, `secret`, `attempts`, `score`, `status`, and `history` are all stored this way, which is why the score and attempt count kept climbing correctly across guesses instead of resetting to zero every time I clicked "Submit."

---

## 5. Looking ahead: your developer habits

The habit I want to keep is writing a regression test around the *specific* input that exposes a bug, rather than just re-testing the happy path — `check_guess(80, 9)` only means something as a test because it's exactly the pair where string comparison and integer comparison disagree, not because it's "another number." I also want to keep the pattern of asking my AI assistant to explain *why* a bug happens before accepting a fix, since that's what let me catch that its first fix left dead defensive code (the `try/except TypeError` fallback) sitting in `check_guess` for a case that could no longer occur.

One thing I'd do differently: I'd run `pytest` myself, in the actual terminal I intended to use day-to-day, earlier in the process. I only discovered the `pytest` vs. `python -m pytest` sys.path difference after I'd already told my AI assistant "tests pass" based on `python -m pytest`, which meant I had to backtrack once bare `pytest` failed with a `ModuleNotFoundError` — that's a step I skipped and shouldn't have.

This project changed how I think about AI-generated code mainly around trust calibration: the AI's explanations of *why* a fix worked were consistently clear and easy to follow, but I only actually believed a fix was correct once I'd seen a concrete before/after comparison (the old buggy logic really producing "Too Low" for 80-vs-9, and the new logic really producing "Too High") — a plausible-sounding explanation and a verified fact turned out to be two different things, and it's on me to check for the second one every time.
