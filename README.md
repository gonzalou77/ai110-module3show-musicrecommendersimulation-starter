# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version implements a **content-based** music recommender that matches songs to a
user's stated taste on four features.

- **Represent songs and a user "taste profile" as data.** Each song is a `Song`
  dataclass loaded from `data/songs.csv` (genre, mood, energy, tempo, valence,
  danceability, acousticness). A user's taste is a `UserProfile` holding a
  `favorite_genre` plus numeric targets for `target_acousticness`,
  `target_tempo_bpm`, and `target_valence`.
- **Design a scoring rule that turns that data into recommendations.** Each song
  gets a score in `[0, 1]` from a weighted sum of per-feature *closeness*
  (`1 − distance`), so songs nearer the user's preferences rank higher. Weights
  favor acousticness (0.30) and tempo (0.30), with genre as an exact-match boost
  (0.25) and lighter emphasis on valence (0.15). Tempo is min-max normalized to a
  0–1 scale first so it doesn't dominate the other features. The recommender sorts
  all songs by score and returns the top *k*, each with a plain-language
  explanation of why it matched.
- **Evaluate what the system gets right and wrong.** It reliably surfaces songs
  that share the user's genre and sit close on acoustic feel and tempo, and the
  generated reasons make each pick easy to sanity-check. It is weaker when
  preferences fall between the features it tracks, and it ignores features like
  mood, energy, and danceability that could refine the ranking.
- **Reflect on how this mirrors real-world AI recommenders.** This is a small
  version of the content-based filtering big platforms use ("recommend items
  similar to what you already like"), including the same real-world concerns:
  the cold-start problem, filter bubbles from over-favoring one genre, and the
  need to normalize features so no single one dominates the math.

---

## How The System Works

The system is a **content-based recommender**: it compares the features of each
song against a user's stated preferences and ranks songs by how closely they match.

### What features does each `Song` use

A `Song` is loaded from `data/songs.csv` with these fields: `id`, `title`,
`artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and
`acousticness`. Of these, the scoring uses **four**:

- `genre` — categorical (exact-match)
- `acousticness` — numeric, 0–1
- `tempo_bpm` — numeric, normalized to 0–1
- `valence` — numeric, 0–1

The remaining fields (`mood`, `energy`, `danceability`, `artist`, `title`) are
stored and displayed but do not currently factor into the score.

### What information does the `UserProfile` store

The `UserProfile` holds the user's taste targets:

- `favorite_genre` — the genre to match against
- `target_acousticness` — desired acoustic feel (0–1)
- `target_tempo_bpm` — desired tempo
- `target_valence` — desired mood/positivity (0–1)
- (`favorite_mood` and `target_energy` are also stored for future use)

### How the `Recommender` computes a score

For each song, the recommender computes a **closeness** value per feature and
combines them into a single weighted score in `[0, 1]`:

1. **Per-feature closeness** — for the numeric features, `closeness = 1 − |target − song_value|`, so an exact match scores 1.0 and drifts toward 0 as they diverge. For genre, closeness is 1.0 on an exact match and 0.0 otherwise.
2. **Tempo normalization** — `tempo_bpm` is min-max scaled to 0–1 (using a fixed 60–180 BPM range) *before* comparison, so it stays on the same scale as the other features and can't dominate the math.
3. **Weighted sum** — the closeness values are combined using weights that favor acousticness and tempo:

   | Feature | Weight |
   | --- | --- |
   | `acousticness` | 0.30 |
   | `tempo_bpm` | 0.30 |
   | `genre` | 0.25 |
   | `valence` | 0.15 |

   Weights sum to 1.0, so a perfect match scores 1.0.

Alongside the score, the recommender collects **reasons** (e.g. "matches your
favorite genre", "tempo is a good match") to explain each recommendation.

### How songs are chosen

All songs are scored, sorted by score in descending order, and the **top `k`**
are returned — each paired with its score and a plain-language explanation.

### Flow at a glance

```
songs.csv ──> load_songs() ──> [Song data]
                                     │
UserProfile (taste targets) ─────────┤
                                     ▼
                        score each song (weighted closeness)
                                     ▼
                      sort by score, take top k
                                     ▼
                 recommendations + explanations
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



