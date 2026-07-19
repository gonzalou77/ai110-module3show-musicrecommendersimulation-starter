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

### Algorithm recipe (finalized plan)

This is the exact procedure the recommender follows, start to finish:

1. **Load the catalog.** Read `data/songs.csv`, casting `id` to `int` and the
   numeric audio features to `float`.
2. **Take the taste profile.** Read the user's `genre`, `acousticness`,
   `tempo_bpm`, and `valence` targets.
3. **For each song, compute per-feature closeness:**
   - `acousticness`, `valence`: `closeness = 1 − |target − value|`
   - `tempo_bpm`: min-max normalize both target and song to 0–1 over the fixed
     60–180 BPM range, then `1 − |normalized_target − normalized_value|`
   - `genre`: `1.0` on an exact match, else `0.0`
4. **Combine into one score** as a weighted sum with fixed weights that sum to
   1.0 (so a perfect match = 1.0):
   `0.30·acousticness + 0.30·tempo + 0.25·genre + 0.15·valence`
5. **Collect reasons** for any feature whose closeness is strong
   (genre match, or numeric closeness ≥ 0.80) to explain the pick.
6. **Rank and cut.** Sort all songs by score descending and return the top `k`,
   each with its score and explanation.

### Potential biases to expect

Because the scoring is a fixed weighted sum over a small, hand-built catalog,
a few biases are predictable:

- **Genre lock-in.** The 0.25 genre boost is an all-or-nothing bonus, so songs
  in the favorite genre tend to dominate the top ranks even when their numeric
  features are a weaker match. Users get more of the same genre and little
  cross-genre discovery. (Observed directly in the tempo/valence experiment
  below — synthwave tracks held the top 3 under every weighting.)
- **Mood underweighting.** `valence` carries the smallest weight (0.15), so the
  recommender can surface songs whose mood is off from what the user asked for
  if their pace and genre line up. Mood acts only as a tiebreaker.
- **Tempo-range clipping.** Tempos are normalized against a fixed 60–180 BPM
  window and clamped, so any song outside that range collapses to the same
  boundary value and stops being distinguishable by tempo.
- **Popularity/coverage bias.** The catalog is tiny (20 songs) and
  genre-clustered, so results reflect what happens to be in the dataset rather
  than the full space of music — a few artists and genres are over-represented.
- **Ignored signals.** `mood`, `energy`, `danceability`, and lyrics are not
  scored at all, so two songs that "feel" very different can score identically.

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

Running `python src/main.py` from the project root against the 20-song catalog,
using the taste profile `genre=synthwave`, `mood=moody`, `acousticness=0.5`,
`tempo_bpm=150`, `valence=0.85` produces:

```
Loading songs from data/songs.csv...
Loaded 20 songs.

================================================
              TOP RECOMMENDATIONS
================================================

#1  Electric Skyline  -  Voltline
    Score: 5.04
    Why:
      - matches your favorite genre (synthwave)
      - matches your mood (moody)

#2  Night Drive Loop  -  Neon Echo
    Score: 5.03
    Why:
      - matches your favorite genre (synthwave)
      - matches your mood (moody)

#3  Golden Hour Drive  -  Neon Echo
    Score: 5.02
    Why:
      - matches your favorite genre (synthwave)
      - matches your mood (moody)

#4  Rooftop Lights  -  Indigo Parade
    Score: 2.59
    Why:
      - acoustic feel is close to what you like
      - similar mood/positivity

#5  Summer Bloom  -  Neon Echo
    Score: 2.55
    Why:
      - acoustic feel is close to what you like
      - similar mood/positivity

================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Experiment: tempo vs. valence weighting (2:1 vs. 1:1)

I wanted to know how much the mood feature (`valence`) should count relative
to the pace feature (`tempo_bpm`). Both are compared on a normalized 0–1 scale,
so their relative influence comes entirely from their weights.

I ran the same taste profile (`genre=synthwave`, `acousticness=0.5`,
`tempo_bpm=150`, `valence=0.85`) under two settings, holding `acousticness`
(0.30) and `genre` (0.25) fixed and splitting the remaining 0.45:

- **2:1 (shipped):** `tempo_bpm=0.30`, `valence=0.15`
- **1:1:** `tempo_bpm=0.225`, `valence=0.225`

| Rank | 2:1 (tempo-favored) | 1:1 (balanced) |
| --- | --- | --- |
| 1 | Electric Skyline — **0.764** | Electric Skyline — 0.761 |
| 2 | Night Drive Loop — **0.762** | Night Drive Loop — 0.760 |
| 3 | Golden Hour Drive — **0.756** | Golden Hour Drive — 0.757 |
| 4 | Rooftop Lights — 0.634 | Rooftop Lights — **0.647** |
| 5 | Summer Bloom — 0.621 | Summer Bloom — **0.635** |

**What happened:** the top-5 ordering did not change. The genre exact-match
boost (0.25) is large enough that all three synthwave tracks stay on top
regardless of the tempo/valence split.

**The interesting effect is in the scores, not the ranks.** The three
synthwave winners have *low* valence (~0.50, far from the 0.85 target), so
raising the valence weight slightly *lowered* their scores. The indie-pop
runners-up (Rooftop Lights, Summer Bloom) have *high* valence (~0.80), so they
*gained* under 1:1. The gap between #3 and #4 shrank from 0.122 (2:1) to
0.110 (1:1) — i.e. balancing the weights pulls high-mood, wrong-genre songs
closer to breaking into the top ranks.

**Takeaway:** I kept the 2:1 split. Tempo defines the listening context
(driving/workout vs. study/ambient) and should dominate; valence is a
fine-tuner. On this small, genre-clustered catalog the choice barely moves the
results, but 2:1 correctly keeps mood as a tiebreaker rather than letting a
bright-but-off-pace track climb the list.

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



