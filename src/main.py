"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.")

    # Taste profile: the target values the recommender compares songs against.
    # Features used for scoring: genre, acousticness, tempo_bpm, valence.
    user_prefs = {
        "genre": "synthwave",   # favored genre (2-point match)
        "mood": "moody",        # favored mood (1-point match)
        "acousticness": 0.5,    # balanced acoustic/electronic
        "tempo_bpm": 150,       # fast, driving pace
        "valence": 0.85,        # bright, upbeat mood
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 48
    print()
    print("=" * width)
    print(f"{'TOP RECOMMENDATIONS':^{width}}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print()
        print(f"#{rank}  {song['title']}  -  {song['artist']}")
        print(f"    Score: {score:.2f}")
        print("    Why:")
        for reason in explanation.split(", "):
            print(f"      - {reason}")

    print()
    print("=" * width)


if __name__ == "__main__":
    main()
