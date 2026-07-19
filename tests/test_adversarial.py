"""
Adversarial and edge-case tests for the point-based scoring logic.

Each test asserts the DESIRED behavior of `score_song` / `recommend_songs`.
These cases originally exposed real bugs (unclamped numeric closeness,
case/whitespace-sensitive genre matching, and order-dependent tie-breaking);
they now serve as regression guards that keep those fixes in place.

See the "System Evaluation" section of model_card.md for the raw output that
motivated these cases.
"""

from src.recommender import score_song, recommend_songs

# Maximum intended score: genre(2) + mood(1) + acousticness(1) + tempo(1) + valence(1)
MAX_SCORE = 6.0


def make_song(**overrides) -> dict:
    """Build a valid song dict, overriding individual fields as needed."""
    song = {
        "id": 1,
        "title": "Test Track",
        "artist": "Test Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120.0,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    song.update(overrides)
    return song


# ---------------------------------------------------------------------------
# 1. Unclamped numeric closeness -> scores escape the [0, MAX_SCORE] range.
# ---------------------------------------------------------------------------
def test_out_of_range_acousticness_stays_in_bounds():
    # No genre/mood match, so the out-of-range numeric term is not cushioned
    # by the +3 categorical bonus and drives the total negative.
    prefs = {"genre": "no-match", "mood": "no-match", "acousticness": 5.0,
             "tempo_bpm": 120, "valence": 0.9}
    score, _ = score_song(prefs, make_song(tempo_bpm=120, valence=0.9))
    assert 0.0 <= score <= MAX_SCORE


def test_absurd_numerics_do_not_produce_huge_negative_scores():
    prefs = {"genre": "jazz", "mood": "relaxed", "acousticness": 99,
             "tempo_bpm": 9999, "valence": 99}
    score, _ = score_song(prefs, make_song(genre="jazz", mood="relaxed"))
    assert 0.0 <= score <= MAX_SCORE


def test_negative_valence_stays_in_bounds():
    # Uncushioned again: no categorical match, so the negative valence term
    # is free to push the total below 0.
    prefs = {"genre": "no-match", "mood": "no-match", "acousticness": 0.2,
             "tempo_bpm": 120, "valence": -3}
    score, _ = score_song(prefs, make_song(acousticness=0.2, tempo_bpm=120))
    assert 0.0 <= score <= MAX_SCORE


# ---------------------------------------------------------------------------
# 2. Categorical matching should be case/whitespace insensitive.
# ---------------------------------------------------------------------------
def test_genre_match_is_case_insensitive():
    prefs = {"genre": "Rock", "mood": "intense", "acousticness": 0.1,
             "tempo_bpm": 150, "valence": 0.5}
    score, reasons = score_song(prefs, make_song(genre="rock", mood="intense"))
    assert any("favorite genre" in r for r in reasons)


def test_genre_match_ignores_surrounding_whitespace():
    prefs = {"genre": "lofi ", "mood": "chill", "acousticness": 0.8,
             "tempo_bpm": 80, "valence": 0.6}
    score, reasons = score_song(prefs, make_song(genre="lofi", mood="chill"))
    assert any("favorite genre" in r for r in reasons)


# ---------------------------------------------------------------------------
# 3. Tie-breaking should be deterministic and independent of catalog order.
# ---------------------------------------------------------------------------
def test_tie_break_is_deterministic_regardless_of_input_order():
    prefs = {"genre": "rock", "mood": "intense", "acousticness": 0.1,
             "tempo_bpm": 150, "valence": 0.5}
    a = make_song(id=1, title="Alpha", genre="rock", mood="intense")
    b = make_song(id=2, title="Bravo", genre="rock", mood="intense")

    top_ab = recommend_songs(prefs, [a, b], k=1)[0][0]["title"]
    top_ba = recommend_songs(prefs, [b, a], k=1)[0][0]["title"]
    # Same tied inputs should yield the same winner regardless of ordering.
    assert top_ab == top_ba


# ---------------------------------------------------------------------------
# 4. tempo is already clamped -> this one should PASS today (regression guard).
# ---------------------------------------------------------------------------
def test_extreme_tempo_is_clamped_and_bounded():
    prefs = {"genre": "pop", "mood": "happy", "acousticness": 0.2,
             "tempo_bpm": 100000, "valence": 0.9}
    score, _ = score_song(prefs, make_song(tempo_bpm=120))
    # tempo term is normalized+clamped, so score stays within the intended range.
    assert 0.0 <= score <= MAX_SCORE


# ---------------------------------------------------------------------------
# 5. Empty / malformed profile should not silently rank as a real user.
#    Documents current behavior: it does NOT raise (this test passes today).
# ---------------------------------------------------------------------------
def test_empty_profile_currently_does_not_raise():
    score, reasons = score_song({}, make_song())
    assert isinstance(score, float)
    assert isinstance(reasons, list) and len(reasons) > 0
