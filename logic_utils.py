def get_range_for_difficulty(difficulty: str):
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: One of "Easy", "Normal", or "Hard". Any other value
            falls back to the Normal range.

    Returns:
        A ``(low, high)`` tuple of ints giving the inclusive bounds of the
        secret number's range.

    Raises:
        NotImplementedError: Always; this function still needs to be
            refactored from app.py into logic_utils.py.
    """
    raise NotImplementedError(
        "Refactor this function from app.py into logic_utils.py"
    )


# FIX: Refactored out of app.py using agent mode so it can be covered by pytest
# (app.py can't be imported directly in tests since it runs Streamlit UI code
# at module load time). Logic is unchanged from the original app.py version.
def parse_guess(raw: str):
    """Parse raw user input into an integer guess.

    Accepts plain integers (e.g. ``"42"``) and decimal strings (e.g.
    ``"42.9"``), truncating decimals toward zero via ``int(float(raw))``.
    Empty or ``None`` input and non-numeric strings are treated as
    invalid input rather than raising an exception.

    Args:
        raw: The raw text the player typed into the guess field.

    Returns:
        A ``(ok, guess_int, error_message)`` tuple where ``ok`` is ``True``
        only if parsing succeeded, ``guess_int`` is the parsed integer (or
        ``None`` on failure), and ``error_message`` is a user-facing string
        describing the problem (or ``None`` on success).
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# FIX: Refactored out of app.py using agent mode. The old version wrapped this
# comparison in a try/except TypeError with a string-based fallback, which is
# what let the high/low bug through silently instead of erroring. Since app.py
# no longer stringifies the secret before calling this, that fallback was dead
# defensive code and was dropped in favor of a plain numeric comparison.
def check_guess(guess, secret):
    """Compare a guess to the secret number and describe the outcome.

    Args:
        guess: The player's parsed guess, as an int.
        secret: The secret number the player is trying to guess, as an int.

    Returns:
        A ``(outcome, message)`` tuple. ``outcome`` is one of ``"Win"``,
        ``"Too High"``, or ``"Too Low"``, and ``message`` is the matching
        user-facing hint string.
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📈 Go HIGHER!"

    return "Too Low", "📉 Go LOWER!"


# FIX: Added for the enhanced-UI stretch feature using agent mode. Pure
# function (no Streamlit dependency) so it stays testable like the other
# logic_utils functions; app.py only uses its return value for display.
def get_temperature(guess: int, secret: int, low: int, high: int) -> str:
    """Return a "Hot/Cold" emoji cue describing how close a guess is.

    The distance between ``guess`` and ``secret`` is expressed as a
    fraction of the difficulty's full range, so "hot" means close
    relative to the range in play, not close in absolute terms.

    Args:
        guess: The player's parsed guess, as an int.
        secret: The secret number the player is trying to guess, as an int.
        low: The inclusive lower bound of the current difficulty's range.
        high: The inclusive upper bound of the current difficulty's range.

    Returns:
        A short emoji-prefixed string such as ``"🔥 Scorching hot!"`` or
        ``"🧊 Freezing"``.
    """
    span = max(high - low, 1)
    distance = abs(guess - secret)
    ratio = distance / span

    if ratio <= 0.05:
        return "🔥 Scorching hot!"
    if ratio <= 0.15:
        return "♨️ Hot"
    if ratio <= 0.30:
        return "🌤️ Warm"
    if ratio <= 0.60:
        return "❄️ Cold"
    return "🧊 Freezing"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update the player's running score based on the latest guess outcome.

    Args:
        current_score: The player's score before this guess.
        outcome: The result of the latest guess, as returned by
            :func:`check_guess` (e.g. ``"Win"``, ``"Too High"``,
            ``"Too Low"``).
        attempt_number: The 1-based number of the attempt just made.

    Returns:
        The player's updated score as an int.

    Raises:
        NotImplementedError: Always; this function still needs to be
            refactored from app.py into logic_utils.py.
    """
    raise NotImplementedError(
        "Refactor this function from app.py into logic_utils.py"
    )
