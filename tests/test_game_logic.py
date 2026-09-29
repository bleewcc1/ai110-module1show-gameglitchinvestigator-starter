from logic_utils import check_guess, parse_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

def test_guess_too_high_lexicographic_edge_case():
    # Regression test for the fixed bug: app.py used to stringify the secret
    # on even-numbered attempts, so check_guess compared guess vs. secret as
    # strings instead of numbers. 80 vs 9 is the classic case where that goes
    # wrong: numerically 80 > 9 ("Too High"), but as strings "80" < "9"
    # lexicographically (since "8" < "9"), which used to produce "Too Low".
    outcome, _ = check_guess(80, 9)
    assert outcome == "Too High"

# --- Challenge 1: Advanced edge-case testing for parse_guess ---

def test_parse_guess_negative_number():
    # A negative guess is outside the valid range but must still parse
    # cleanly instead of crashing, so check_guess can grade it as "Too Low"
    ok, guess_int, err = parse_guess("-5")
    assert ok is True
    assert guess_int == -5
    assert err is None

def test_parse_guess_decimal_input():
    # Users may type a decimal (e.g. "50.7"); parse_guess should truncate
    # toward zero via int(float(raw)) rather than rejecting or rounding
    ok, guess_int, err = parse_guess("50.7")
    assert ok is True
    assert guess_int == 50
    assert err is None

def test_parse_guess_extremely_large_number():
    # Python ints are arbitrary precision, so an absurdly large guess should
    # still parse without raising OverflowError/ValueError
    ok, guess_int, err = parse_guess("99999999999999999999999999")
    assert ok is True
    assert guess_int == 99999999999999999999999999
    assert err is None
