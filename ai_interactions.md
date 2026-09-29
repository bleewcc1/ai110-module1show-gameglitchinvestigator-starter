# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code in agent mode across several prompts to investigate and repair the game glitch end to end:
1. "Add a `# FIXME: Logic breaks here` comment where you believe the issue is located."
2. "Fix the code."
3. "Move the `check_guess` function to `logic_utils.py`, update the logic to fix the high/low bug, and update the import in `app.py`."
4. "Create a pytest case in `tests/test_game_logic.py` that specifically targets the bug you just fixed."
5. Debug a `ModuleNotFoundError: No module named 'logic_utils'` when running bare `pytest`.
6. Add `# FIX:` comments near each fix, fill in `reflection.md`, and generate a commit message.
7. Fill in `README.md`'s Demo Walkthrough, Document Your Experience, and Test Results sections.
8. Complete the remaining `reflection.md` questions (bugs found at start, Streamlit/session-state explanation, developer habits).
9. Move `parse_guess` into `logic_utils.py`, identify three edge-case inputs (negative numbers, decimals, extremely large values), and generate a pytest suite covering them.

**What did the agent do? (files modified)**

- **`app.py`** — traced the high/low hint bug to a block that stringified `st.session_state.secret` on every even-numbered attempt; removed that block, and replaced the local `check_guess`/`parse_guess` definitions with `from logic_utils import check_guess, parse_guess`. Added `# FIX:` comments at the import and call site.
- **`logic_utils.py`** — implemented `check_guess` (plain numeric comparison, no string fallback) and `parse_guess` (moved unchanged from `app.py`), replacing their `NotImplementedError` stubs. Added a `# FIX:` comment explaining why the old `try/except TypeError` string-fallback was dropped instead of kept.
- **`tests/test_game_logic.py`** — fixed the 3 existing tests to unpack `check_guess`'s `(outcome, message)` tuple instead of comparing it to a bare string, and added 4 new tests: a regression test for the high/low bug (`check_guess(80, 9)` → `"Too High"`) and 3 edge-case tests for `parse_guess` (negative number, decimal, extremely large value).
- **`pytest.ini`** (new file) — added `pythonpath = .` so bare `pytest` (not just `python -m pytest`) can resolve `import logic_utils` from the project root.
- **`.gitignore`** — added `._*` to ignore macOS AppleDouble sidecar files.
- **`reflection.md`** and **`README.md`** — filled in with the bug list, fixes applied, a text-based demo walkthrough, and real pytest terminal output (ran `pytest -v` and pasted the actual result, not a fabricated one).
- Ran `pytest -v` after every code change to confirm the suite stayed green (ended at 7 passed), and ran `git add` / `git commit` once I confirmed the fix, using a commit message the agent drafted from the actual diff.

**What did you have to verify or fix manually?**

- The agent's first attempt at "fix the code" removed the buggy string-stringification in `app.py` but left a now-dead `try/except TypeError` string-comparison fallback inside `check_guess`. I did not accept that as written — once `check_guess` was moved into `logic_utils.py`, I had the agent delete the fallback entirely instead of keeping it as "defensive code," since there was no longer any code path that could reach it. See `reflection.md` Section 2 for the full reasoning.
- Earlier in the session, an added `# FIXME` comment silently disappeared between turns (likely a save/sync hiccup on the external drive) — I had to notice it was missing and ask the agent to re-add it.
- The agent once overwrote this same `ai_interactions.md` file wholesale (which already existed as a stretch-feature template) instead of reading it first and editing only the relevant section. It caught its own mistake via `git status`/`git show HEAD` and restored the original template structure before I had to intervene — but it's a good example of why "read before write" matters even for an AI agent.
- I double-checked the agent's claims against real output rather than trusting its explanation alone: I had it manually reproduce the old buggy `check_guess` logic against `(80, 9)` in a Python shell to confirm the bug was real before accepting the fix, and I re-ran `pytest -v` myself after each change rather than taking "tests pass" on faith.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

**Prompt used:**

```
Move parse_guess into logic_utils.py too, identify three edge case inputs
(e.g. negative numbers, decimals, or extremely large values) that might
still break the game, and generate a pytest suite that verifies parse_guess
handles them gracefully.
```

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
| --- | --- | --- | --- | --- |
| Negative number (`"-5"`) | (prompt above) | `test_parse_guess_negative_number`: asserts `parse_guess("-5") == (True, -5, None)` | Yes | A negative guess is outside the valid 1–N range, but `parse_guess` should still parse it cleanly instead of crashing, so `check_guess` can grade it as "Too Low" rather than the app erroring out. |
| Decimal input (`"50.7"`) | (prompt above) | `test_parse_guess_decimal_input`: asserts `parse_guess("50.7") == (True, 50, None)` | Yes | Users may type a decimal by habit or mistake; this locks in that `parse_guess` truncates toward zero (`int(float(raw))`) rather than rounding or rejecting the input. |
| Extremely large value (`"99999999999999999999999999"`) | (prompt above) | `test_parse_guess_extremely_large_number`: asserts the huge string still parses to the equivalent int with `ok=True` | Yes | Python integers are arbitrary precision, but many parsers overflow on huge numeric strings; this confirms `parse_guess` doesn't raise `OverflowError`/`ValueError` on an absurdly large guess. |

Full terminal output for these tests (plus the existing suite, 7 passed total) is in [README.md](README.md#-test-results).

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
Review the code and add professional-grade docstrings to every function in
logic_utils.py. Then, review the code for PEP 8 style compliance and apply
its suggestions to resolve any formatting or naming issues it identifies.
```

**Linting output before (`flake8 logic_utils.py`):**

```
logic_utils.py:3:80: E501 line too long (87 > 79 characters)
logic_utils.py:54:80: E501 line too long (87 > 79 characters)
```

**Linting output after (`flake8 logic_utils.py`):**

```
(no output — exit code 0, no remaining issues)
```

**Changes applied:**

- Added a full docstring (summary, `Args`, `Returns`, and `Raises` where relevant) to all 4 functions in `logic_utils.py`: `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` — including the two that are still `NotImplementedError` stubs, since a docstring documenting the intended contract is still useful even before the body is implemented.
- Naming: all function and parameter names were already `snake_case` and PEP 8-compliant (`get_range_for_difficulty`, `raw`, `guess_int`, etc.), so no renames were needed.
- Formatting: `flake8` flagged the two `raise NotImplementedError("Refactor this function from app.py into logic_utils.py")` lines as `E501 line too long` (87 > 79 characters). Wrapped each onto multiple lines with parentheses instead of shortening the message, so the error text stays identical for anyone depending on it. I applied both of the suggested line-length fixes; there were no naming issues to accept or reject.
- Re-ran `pytest -v` after the changes to confirm the docstring/formatting edits didn't change behavior — all 7 tests still passed.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

Review and fix the Streamlit guessing game's incorrect high/low hints and
pytest import problem. Compare the implementation choices, test coverage, and
the reasoning behind the fix.

| | Model A | Model B |
|-|---------|---------|
| **Model name** | Claude Code (agent mode) | GitHub Copilot |
| **Response summary** | Implemented the fix by removing the even-attempt string conversion, moving `check_guess` and `parse_guess` into `logic_utils.py`, updating the tests, and adding `pytest.ini`. It also added regression and edge-case tests. | Reviewed the history and current implementation, confirmed the string comparison was the root cause, and evaluated the import configuration and refactor boundaries. It also identified that `get_range_for_difficulty` and `update_score` remain duplicated in `app.py` and stubbed in `logic_utils.py`. |
| **More readable / Pythonic fix?** | **Yes for the submitted implementation.** The final numeric comparison in `check_guess` is simple and readable, and removing the dead string fallback avoids hiding type errors. | **Yes as a proposed design, but it was not applied in this review.** The cleaner long-term design is to move all pure game logic into `logic_utils.py`, keep types consistent as integers, and leave `app.py` responsible only for Streamlit state and display. |
| **Clearer explanation of why?** | Explained the specific `80` versus `9` lexicographic failure and why the fallback was no longer needed after the secret stayed numeric. | **Yes.** It connected the symptom to the type conversion, explained why `pytest.ini` fixes the import when run from the project root, and pointed out the remaining incomplete refactor and difficulty-reset inconsistency. |

**Which did you prefer and why?**

I preferred Claude Code for making the immediate code change because it produced a
working, test-backed patch. I preferred GitHub Copilot's explanation of the
design because it separated the root-cause fix from follow-up improvements and
made the tradeoff clear: removing the string fallback fixes the bug, but moving
all game logic into `logic_utils.py` would make the code easier to test and
maintain. Overall, Claude Code produced the more complete submitted fix, while
GitHub Copilot explained the "why" more clearly.
