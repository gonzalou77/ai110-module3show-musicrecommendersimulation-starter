from src.recommender import Song, UserProfile, Recommender, score_song

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_acousticness=0.2,
        target_tempo_bpm=120,
        target_valence=0.9,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_acousticness=0.2,
        target_tempo_bpm=120,
        target_valence=0.9,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_returns_numeric_score_and_reasons_list():
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "acousticness": 0.2,
        "tempo_bpm": 120,
        "valence": 0.9,
    }
    song = {
        "genre": "pop",
        "mood": "happy",
        "acousticness": 0.2,
        "tempo_bpm": 120,
        "valence": 0.9,
    }

    result = score_song(user_prefs, song)

    # Returns a (score, reasons) tuple.
    assert isinstance(result, tuple)
    assert len(result) == 2

    score, reasons = result

    # First element is a numeric score.
    assert isinstance(score, (int, float))
    assert not isinstance(score, bool)

    # Second element is a non-empty list of reason strings.
    assert isinstance(reasons, list)
    assert len(reasons) > 0
    assert all(isinstance(r, str) for r in reasons)
