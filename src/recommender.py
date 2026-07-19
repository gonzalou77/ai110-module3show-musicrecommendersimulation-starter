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
    """Represents a song and its attributes."""
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
    """Represents a user's taste preferences."""
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
    """Return a closeness score for two 0-1 values (1.0 identical, toward 0.0 as they diverge).

    Clamped to [0, 1] so out-of-range inputs cannot produce negative
    contributions that escape the intended score range.
    """
    return _clamp01(1.0 - abs(a - b))


def _norm_category(value) -> str:
    """Normalize a categorical value for comparison (case- and whitespace-insensitive)."""
    return str(value).strip().lower() if value else ""


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
    """Score a song's features against user targets, returning (score in [0, 1], reasons)."""
    acoustic_c = _closeness(target_acousticness, song_acousticness)
    tempo_c = _closeness(_normalize_tempo(target_tempo_bpm),
                         _normalize_tempo(song_tempo_bpm))
    valence_c = _closeness(target_valence, song_valence)
    genre_c = 1.0 if target_genre and _norm_category(target_genre) == _norm_category(song_genre) else 0.0

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
    """OOP implementation of the recommendation logic."""
    def __init__(self, songs: List[Song]):
        """Store the catalog of songs to recommend from."""
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one song against a user profile, returning (score, reasons)."""
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
        """Return the top-k songs ranked by score, highest first."""
        # Deterministic tie-break by title then id, independent of list order.
        ranked = sorted(self.songs, key=lambda s: (s.title, s.id))
        ranked.sort(key=lambda s: self._score(user, s)[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string of a song's score and reasons."""
        score, reasons = self._score(user, song)
        return f"Score {score:.2f}: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file as a list of dicts, converting numeric fields to floats."""
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


# ---------------------------------------------------------------------------
# Point-based scoring (used by score_song)
#
# Categorical features are all-or-nothing; numeric features earn partial
# credit scaled by closeness so near-misses still count.
#   genre match ....... 2 points  (strongest signal)
#   mood match ........ 1 point
#   acousticness ...... up to 1 point  (1 x closeness)
#   tempo_bpm ......... up to 1 point  (normalized, then 1 x closeness)
#   valence ........... up to 1 point  (1 x closeness)
# Maximum possible score = 6.0 (perfect match on everything).
# ---------------------------------------------------------------------------
POINTS = {
    "genre": 2.0,
    "mood": 1.0,
    "acousticness": 1.0,
    "tempo_bpm": 1.0,
    "valence": 1.0,
}


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences with a point system, returning (score in [0, 6], reasons)."""
    reasons: List[str] = []
    score = 0.0

    # Categorical features: all-or-nothing points (case/whitespace insensitive).
    if user_prefs.get("genre") and _norm_category(user_prefs["genre"]) == _norm_category(song["genre"]):
        score += POINTS["genre"]
        reasons.append(f"matches your favorite genre ({song['genre']})")
    if user_prefs.get("mood") and _norm_category(user_prefs["mood"]) == _norm_category(song["mood"]):
        score += POINTS["mood"]
        reasons.append(f"matches your mood ({song['mood']})")

    # Numeric features: partial credit scaled by closeness (1 - |target - value|).
    acoustic_c = _closeness(user_prefs.get("acousticness", 0.5),
                            song["acousticness"])
    tempo_c = _closeness(_normalize_tempo(user_prefs.get("tempo_bpm", 120.0)),
                         _normalize_tempo(song["tempo_bpm"]))
    valence_c = _closeness(user_prefs.get("valence", 0.6), song["valence"])

    score += POINTS["acousticness"] * acoustic_c
    score += POINTS["tempo_bpm"] * tempo_c
    score += POINTS["valence"] * valence_c

    if acoustic_c >= 0.8:
        reasons.append("acoustic feel is close to what you like")
    if tempo_c >= 0.8:
        reasons.append("tempo is a good match")
    if valence_c >= 0.8:
        reasons.append("similar mood/positivity")
    if not reasons:
        reasons.append("partial match on your preferences")

    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Return the top-k (song, score, explanation) tuples sorted by score descending."""
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    # Sort by score descending; break ties deterministically by title then id
    # so results do not depend on catalog/CSV row order.
    scored.sort(key=lambda item: (item[0].get("title", ""), item[0].get("id", 0)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
