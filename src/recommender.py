import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Content-based scoring configuration
#
# Features used: acousticness, tempo_bpm, valence, genre
# Weights favor acousticness and tempo, with lighter emphasis on valence.
# Weights sum to 1.0 so the maximum possible score is 1.0 (perfect match).
# ---------------------------------------------------------------------------
WEIGHTS = {
    "acousticness": 0.30,  # favored: widest spread, most discriminative
    "tempo_bpm": 0.30,     # favored: normalized before comparison
    "genre": 0.25,         # categorical exact-match boost
    "valence": 0.15,       # light emphasis, per design
}

# Tempo range used to normalize BPM onto a 0-1 scale so it does not
# dominate the distance math against the other 0-1 features.
TEMPO_MIN = 60.0
TEMPO_MAX = 180.0


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_acousticness: float
    target_tempo_bpm: float
    target_valence: float


# ---------------------------------------------------------------------------
# Core scoring helpers
# ---------------------------------------------------------------------------
def _clamp01(x: float) -> float:
    """Clamp a value into the [0, 1] range."""
    return max(0.0, min(1.0, x))


def _normalize_tempo(bpm: float) -> float:
    """Map a BPM value onto a 0-1 scale using the configured tempo range."""
    return _clamp01((bpm - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN))


def _closeness(a: float, b: float) -> float:
    """
    Convert a distance between two 0-1 values into a closeness score.
    Returns 1.0 when identical, approaching 0.0 as they diverge.
    """
    return 1.0 - abs(a - b)


def _weighted_score(
    target_genre: str,
    target_acousticness: float,
    target_tempo_bpm: float,
    target_valence: float,
    song_genre: str,
    song_acousticness: float,
    song_tempo_bpm: float,
    song_valence: float,
) -> Tuple[float, List[str]]:
    """
    Shared content-based scoring used by both the functional and OOP APIs.

    Rewards songs whose features are close to the user's preferences.
    Returns (score, reasons) where score is in [0, 1].
    """
    acoustic_c = _closeness(target_acousticness, song_acousticness)
    tempo_c = _closeness(_normalize_tempo(target_tempo_bpm),
                         _normalize_tempo(song_tempo_bpm))
    valence_c = _closeness(target_valence, song_valence)
    genre_c = 1.0 if target_genre and target_genre == song_genre else 0.0

    score = (
        WEIGHTS["acousticness"] * acoustic_c
        + WEIGHTS["tempo_bpm"] * tempo_c
        + WEIGHTS["genre"] * genre_c
        + WEIGHTS["valence"] * valence_c
    )

    # Build human-readable reasons for the strongest contributors.
    reasons: List[str] = []
    if genre_c == 1.0:
        reasons.append(f"matches your favorite genre ({song_genre})")
    if acoustic_c >= 0.8:
        reasons.append("acoustic feel is close to what you like")
    if tempo_c >= 0.8:
        reasons.append("tempo is a good match")
    if valence_c >= 0.8:
        reasons.append("similar mood/positivity")
    if not reasons:
        reasons.append("partial match on your preferences")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        return _weighted_score(
            target_genre=user.favorite_genre,
            target_acousticness=user.target_acousticness,
            target_tempo_bpm=user.target_tempo_bpm,
            target_valence=user.target_valence,
            song_genre=song.genre,
            song_acousticness=song.acousticness,
            song_tempo_bpm=song.tempo_bpm,
            song_valence=song.valence,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(
            self.songs,
            key=lambda s: self._score(user, s)[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = self._score(user, song)
        return f"Score {score:.2f}: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file, converting numeric fields to floats.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    numeric_fields = {
        "energy", "tempo_bpm", "valence", "danceability", "acousticness",
    }
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song: Dict = {}
            for key, value in row.items():
                if key == "id":
                    song[key] = int(value)
                elif key in numeric_fields:
                    song[key] = float(value)
                else:
                    song[key] = value
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.

    user_prefs may contain: genre, acousticness, tempo_bpm, valence.
    Missing keys fall back to neutral defaults.
    Returns (score, reasons).
    """
    return _weighted_score(
        target_genre=user_prefs.get("genre", ""),
        target_acousticness=user_prefs.get("acousticness", 0.5),
        target_tempo_bpm=user_prefs.get("tempo_bpm", 120.0),
        target_valence=user_prefs.get("valence", 0.6),
        song_genre=song["genre"],
        song_acousticness=song["acousticness"],
        song_tempo_bpm=song["tempo_bpm"],
        song_valence=song["valence"],
    )


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Returns a list of (song_dict, score, explanation) sorted by score desc.
    Required by src/main.py
    """
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
