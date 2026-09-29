import random
import streamlit as st

# FIX: check_guess and parse_guess moved to logic_utils.py using agent mode
# (check_guess was duplicated here with a buggy string-comparison fallback;
# parse_guess moved so pytest can cover it with edge-case tests)
from logic_utils import check_guess, get_temperature, parse_guess

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

# UI ENHANCEMENT: structured metrics row (score / attempts left / range) in
# place of a single plain-text info banner, using agent mode
metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Score", st.session_state.score)
metric_col2.metric(
    "Attempts Left", max(attempt_limit - st.session_state.attempts, 0)
)
metric_col3.metric("Range", f"{low}–{high}")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    # UI ENHANCEMENT: clear the session summary table so it doesn't mix
    # guesses from a previous game in with the new one
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        # UI ENHANCEMENT: session summary rows are now structured dicts
        # instead of raw guess values, so they can be rendered as a table
        st.session_state.history.append({
            "Attempt": st.session_state.attempts,
            "Guess": raw_guess,
            "Result": "⚠️ Invalid input",
            "Hint": err,
        })
        st.error(err)
    else:
        # FIX: removed the "if attempts % 2 == 0: secret = str(secret)"
        # block that used to sit here — that was the actual glitch,
        # silently flipping high/low hints
        outcome, message = check_guess(guess_int, st.session_state.secret)

        # UI ENHANCEMENT: Hot/Cold emoji cue based on how close the guess was
        temperature = (
            "\U0001f3af Bullseye!"
            if outcome == "Win"
            else get_temperature(guess_int, st.session_state.secret, low, high)
        )

        st.session_state.history.append({
            "Attempt": st.session_state.attempts,
            "Guess": guess_int,
            "Result": outcome,
            "Hint": f"{message} {temperature}",
        })

        # UI ENHANCEMENT: color-coded hint by outcome (red = too high, blue =
        # too low) instead of a single st.warning for every outcome; the win
        # case is skipped here since the success banner below covers it
        if show_hint and outcome != "Win":
            if outcome == "Too High":
                st.error(f"{message}  {temperature}")
            else:
                st.info(f"{message}  {temperature}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"{temperature} You won! The secret was "
                f"{st.session_state.secret}. Final score: "
                f"{st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# UI ENHANCEMENT: session summary table of every guess made this game
if st.session_state.history:
    st.subheader("\U0001f4ca Session Summary")
    st.table(st.session_state.history)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
