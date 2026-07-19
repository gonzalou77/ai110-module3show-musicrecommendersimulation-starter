"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse
import random

from recommender import load_songs, recommend_songs


# Distinct listener personas the simulation can choose from. Each is a coherent
# taste profile: a favored genre (2-point match), mood (1-point match), and
# target values for the numeric features (acousticness, tempo_bpm, valence).
USER_PROFILES = {
    "Night Driver": {
        "genre": "synthwave",
        "mood": "moody",
        "acousticness": 0.2,
        "tempo_bpm": 115,
        "valence": 0.5,
    },
    "Study Session": {
        "genre": "lofi",
        "mood": "focused",
        "acousticness": 0.78,
        "tempo_bpm": 80,
        "valence": 0.58,
    },
    "Gym Beast": {
        "genre": "rock",
        "mood": "intense",
        "acousticness": 0.05,
        "tempo_bpm": 152,
        "valence": 0.75,
    },
    "Jazz Cafe": {
        "genre": "jazz",
        "mood": "relaxed",
        "acousticness": 0.88,
        "tempo_bpm": 90,
        "valence": 0.7,
    },
    "Ambient Dreamer": {
        "genre": "ambient",
        "mood": "chill",
        "acousticness": 0.92,
        "tempo_bpm": 60,
        "valence": 0.63,
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Music Recommender Simulation (CLI)."
    )
    parser.add_argument(
        "-p", "--profile",
        choices=list(USER_PROFILES),
        help="listener profile to use (default: a random one)",
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.")

    # Use the chosen profile, or randomly pick one for this run.
    profile_name = args.profile or random.choice(list(USER_PROFILES))
    user_prefs = USER_PROFILES[profile_name]
    print(f"Listener profile: {profile_name} "
          f"(genre={user_prefs['genre']}, mood={user_prefs['mood']})")

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
