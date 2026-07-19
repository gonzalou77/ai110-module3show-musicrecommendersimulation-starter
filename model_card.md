# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

### VibeySongMatcher 9000

A simple music recommender that matches songs to a listener's taste profile.

---

## 2. Goal / Task and Intended Use  

**Goal.** VibeySongMatcher 9000 tries to guess which songs a listener will like. It takes a
taste profile and returns the top 5 songs that fit it best. It also gives a short
"Why" line for each pick.

**Who it is for.** This is a classroom project. It is meant for learning and
experiments, not for real users or a real app.

**Assumptions.** It assumes the listener has one favorite genre and one mood. It
also assumes their taste can be described by a few numbers (how acoustic, how
fast, how upbeat).

**Not intended for.** Do not use it to make real recommendations for real people.
Do not use it to judge artists or decide what music gets played. It is too small
and too biased for any real decision. It also cannot help anyone whose taste falls
outside its seven genres.

---

## 3. How the Model Works (Algorithm Summary)  

Think of it like a points game. Each song earns points for how well it fits the
listener.

- If the song's genre matches the listener's favorite genre, it earns 2 points.
- If the song's mood matches, it earns 1 more point.
- Then the song earns up to 1 point each for being close on three things: how
  acoustic it is, how fast it is, and how upbeat it is.
- A perfect song can earn 6 points total.

The closer a song is to what the listener wants, the more partial points it gets.
We then sort every song by its points and show the top 5.

We also fixed a few problems from the starter code. We stopped bad inputs from
making scores go negative. We made genre matching ignore capital letters and extra
spaces. And we made ties break in the same way every time instead of by luck.

---

## 4. Data Used  

- The catalog has **20 songs**.
- Each song has a genre, a mood, and five numbers: energy, tempo, valence
  (upbeat-ness), danceability, and acousticness.
- There are **7 genres** (lofi, pop, rock, synthwave, ambient, jazz, indie pop)
  and **6 moods** (chill, happy, intense, moody, relaxed, focused).
- We did not add or remove songs. We used the starter dataset as is.
- A lot of musical taste is missing. There is no hip-hop, classical, EDM, metal,
  country, or R&B. There are also no sad or low-energy songs, because valence only
  ranges from 0.45 to 0.86.

---

## 5. Strengths  

- It works well for the five built-in personas. Each one gets songs that clearly
  match its taste.
- It is confident and accurate inside a genre. Top matches score near the max (6.0).
- The "Why" lines make sense and are easy to read.
- It is fast, simple, and easy to understand.
- The picks matched our intuition: a "Gym Beast" gets loud rock, a "Study Session"
  gets calm lofi.

---

## 6. Observed Behavior / Biases  

Where the system struggles or behaves unfairly.

The biggest pattern is a **filter bubble**. Each profile gets locked into one
genre and never leaves it. A "Study Session" profile just returns all five lofi
songs and nothing else.

Our experiments surfaced a strong filter-bubble tendency: because each genre in
the dataset is tied to an almost fixed mood (e.g. rock is always "intense," jazz
always "relaxed"), the genre (2 pts) and mood (1 pt) points effectively measure
the same thing, so half of a song's score comes from one underlying attribute and
the numeric preferences barely matter. As a result the top-k recommendations
collapse onto a single genre cluster — a "Study Session" profile simply returns
all five lofi tracks — with no diversity, novelty, or exploration because the
recommender just sorts by score and slices the top results. The catalog also bakes
in a positivity bias: valence only ranges from 0.45 to 0.86, so a user who wants
genuinely sad or low-energy music can never be served well, and several common
genres (hip-hop, classical, EDM, and others) are missing entirely, leaving those
listeners with zero genre credit on every song. Finally, when a profile is empty
or partial the defaults land near the dataset averages, quietly steering
low-information users toward the same mainstream pop tracks.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

### Profiles tested

We evaluated the five built-in listener personas: **Night Driver** (synthwave /
moody), **Study Session** (lofi / focused), **Gym Beast** (rock / intense),
**Jazz Cafe** (jazz / relaxed), and **Ambient Dreamer** (ambient / chill). For
each we looked at the top-k recommendations, the numeric score, and the "Why"
explanation to check whether the picks matched the persona's stated taste. The
most interesting finding was how *cleanly* each profile locked onto its own genre:
scores for the top matches clustered tightly near the 6.0 maximum (5.6–6.0), and
then dropped sharply for anything outside the target genre. That gap confirmed the
filter-bubble effect we saw elsewhere — the recommender is confident and accurate
within a genre, but essentially never crosses genre lines.

### Pairwise comparisons

<!-- Night Driver vs. Study Session: Night Driver returns all synthwave/moody
tracks (Electric Skyline, Night Drive Loop) while Study Session returns lofi/
focused tracks (Focus Flow, Quiet Deadlines). The lists are completely disjoint.
This makes sense: the genre point (2) plus the tightly-coupled mood point (1)
anchor each profile to its own cluster, and the numeric features only reorder
within that cluster. -->

<!-- Study Session vs. Ambient Dreamer: both are low-energy, high-acousticness,
slow-tempo profiles, so numerically they are close — yet the outputs barely
overlap because genre is exact-match. Study Session tops out on lofi (5.99) and
Ambient Dreamer on ambient (5.98), and each only reaches into the other's genre
far down the list at a much lower score. This shows genre dominates even when the
underlying audio features are very similar. -->

<!-- Gym Beast vs. the rest: Gym Beast's top scores (5.64–5.68) are the lowest
"best matches" of any profile. This makes sense because its target tempo (152 BPM)
and near-zero acousticness sit at the extreme edge of the catalog, so even the
best rock tracks lose a little partial credit on the numeric terms — the ceiling
is lower when your taste lives at the boundary of the data. -->

<!-- Jazz Cafe vs. Ambient Dreamer: both are calm, acoustic-leaning profiles and
both return an in-genre pair near 5.98, but their #3 pick diverges sharply
(Jazz Cafe -> Library Rain at 2.73; Ambient Dreamer -> Library Rain at 3.81).
The same fallback song scores differently because acousticness/valence closeness
to each profile differs, illustrating that once a genre runs out of songs, the
numeric features quietly decide the overflow ranking. -->

<!-- Night Driver vs. Gym Beast: both are higher-energy profiles, but Night Driver
matches into a 3-song synthwave pocket with very high scores (5.92–5.98) while Gym
Beast matches rock at lower scores. The difference is data density and feature
extremity: synthwave targets sit near the middle of the tempo/acoustic range where
matches are easy, rock targets sit at the edge where they are penalized. -->

<!-- Night Driver vs. Jazz Cafe: opposite ends of the mood/energy spectrum
(moody + mid-tempo vs. relaxed + acoustic), and the outputs share no songs. Both
top out near 5.9x within their own genre, but Jazz Cafe falls off a cliff after
just two jazz songs (#3 is Library Rain at 2.73) because jazz only has two tracks,
whereas synthwave has three, so Night Driver stays in-genre longer. -->

<!-- Night Driver vs. Ambient Dreamer: both lean calm/atmospheric, yet they never
overlap in the top picks. Ambient Dreamer even produces a tie at 5.98 (Spacewalk
Thoughts and Starlit Fields) because its two ambient songs are near-identical on
every feature; Night Driver's synthwave picks are more spread out. This shows how
a tiny, homogeneous genre pocket collapses into near-identical scores. -->

<!-- Study Session vs. Gym Beast: the starkest contrast — low energy/slow/acoustic
vs. high energy/fast/non-acoustic. Completely disjoint lists, and Study Session's
best score (5.99) beats Gym Beast's best (5.68). That gap exists because Study
Session's targets sit near catalog-typical lofi values while Gym Beast's live at
the tempo/acousticness extremes, costing it partial credit even on ideal songs. -->

<!-- Study Session vs. Jazz Cafe: both are calm, acoustic-leaning, slow profiles,
so numerically they are neighbors, but genre exact-match keeps them apart — lofi
for one, jazz for the other. Tellingly, each surfaces the *other's* type of song
only as a low-scoring fallback (Jazz Cafe's #3 is a lofi track at 2.73), proving
genre, not audio similarity, is drawing the boundary. -->

<!-- Gym Beast vs. Jazz Cafe: near-mirror images (intense/fast/energetic vs.
relaxed/slow/acoustic) with zero shared songs. Jazz Cafe scores higher at the top
(5.98 vs. 5.68) despite jazz having fewer songs, because jazz targets sit in a
denser, more central feature region while Gym Beast's extreme targets are always
slightly penalized. Genre size did not help Gym Beast; feature position hurt it. -->

<!-- Gym Beast vs. Ambient Dreamer: the widest energy gap of any pair (intense vs.
chill), and again fully disjoint. Ambient Dreamer reaches a near-perfect 5.98 tie
while Gym Beast caps at 5.68 — same story as elsewhere: profiles whose targets sit
in the middle of the data hit higher ceilings than profiles at the edges,
regardless of how well the genre itself is represented. -->

---

## 8. Ideas for Improvement  

If we kept working on this, we would:

1. **Add diversity to the results.** Right now every pick is the same genre. We
   would mix in a few songs from nearby genres so the list is not a bubble.
2. **Give partial credit for similar genres.** "pop" and "indie pop" should count
   as close, not as total strangers. A genre similarity map would fix this.
3. **Grow the dataset.** More songs, more genres, and some sad or low-energy tracks
   so every kind of listener gets served.

---

## 9. Personal Reflection  

I learned that a recommender is only as good as its data and its rules. Small
choices, like giving genre 2 points, can quietly control the whole result. The
most surprising part was how easily the system fell into a filter bubble, even
though the code looked fair. It made me realize that real music apps have to work
hard to add variety on purpose, or they would just play the same kind of song over
and over.

---

## System Evaluation

To stress-test the scoring logic, I ran a set of adversarial and edge-case
listener profiles through `recommend_songs` and captured the raw output below.

```text
Loading songs from data/songs.csv...
=== Out-of-range acousticness=5.0 ===
    1.46  Library Rain           genre=lofi       mood=chill
    1.43  Paper Boats            genre=lofi       mood=chill
    1.32  Midnight Coding        genre=lofi       mood=chill
=== Negative valence=-3 ===
    2.50  Thunder Alley          genre=rock       mood=intense
    2.50  Storm Runner           genre=rock       mood=intense
    2.44  Adrenaline Peak        genre=rock       mood=intense
=== Genre Rock (capital) ===
    3.96  Storm Runner           genre=rock       mood=intense
    3.94  Thunder Alley          genre=rock       mood=intense
    3.84  Adrenaline Peak        genre=rock       mood=intense
=== Empty profile {} ===
    2.61  Summer Bloom           genre=indie pop  mood=happy
    2.61  Rooftop Lights         genre=indie pop  mood=happy
    2.54  Electric Skyline       genre=synthwave  mood=moody
=== Genre+mood match, absurd numerics ===
  -191.15  Coffee Shop Stories    genre=jazz       mood=relaxed
  -191.23  Velvet Morning         genre=jazz       mood=relaxed
  -194.31  Rooftop Lights         genre=indie pop  mood=happy
=== Nonexistent genre polka ===
    3.95  Summer Bloom           genre=indie pop  mood=happy
    3.91  Rooftop Lights         genre=indie pop  mood=happy
    3.82  Sunrise City           genre=pop        mood=happy
```

### What the results show

Each test above targets a different weakness in the point-based scoring system
(`score_song`, max intended score = 6.0):

- **Out-of-range acousticness (5.0):** The closeness formula `1 − |target − value|`
  is never clamped, so an impossible acousticness of 5.0 pushes the acousticness
  term deeply negative. Scores drop to ~1.4 instead of erroring. The ranking still
  "works" relative to itself, but the numbers are no longer meaningful.

- **Negative valence (−3):** Same unclamped-math problem. It also produced a
  **tie at 2.50** between Thunder Alley and Storm Runner. Ties are broken silently
  by CSV row order, giving earlier songs an invisible, unearned advantage.

- **Genre "Rock" (capital R):** Genre matching is case-sensitive and exact, so
  `"Rock"` matches nothing and scores 0 genre points — yet rock songs still ranked
  on top (3.96) because mood and numeric proximity carried them. The genre match
  **failed silently**: the user believes genre filtering worked when it did not.

- **Empty profile `{}`:** A completely malformed profile does not crash. It falls
  back to default numeric targets (0.5 / 120 / 0.6) and confidently ranks songs
  (~2.6). A broken input is indistinguishable from a real user.

- **Genre + mood match with absurd numerics:** Even with acousticness/tempo/valence
  set to nonsense, the correct genre (jazz) still floated to the top because the
  categorical genre (2 pts) + mood (1 pt) bonus dominates. Scores hit **−191**,
  confirming both the unclamped-math bug and that numeric taste is easily overridden.

- **Nonexistent genre "polka":** An unknown genre is not validated or rejected.
  The system silently ignores it and ranks purely on mood + numerics, returning
  happy pop songs as if nothing was wrong.

**Takeaways:** (1) numeric closeness needs to be clamped to [0, 1]; (2) categorical
matches should be normalized (case/whitespace) and validated against the catalog
instead of failing silently; (3) genre+mood weighting can drown out numeric
preferences; and (4) tie-breaking should be explicit and deterministic. These are
the fixes to prioritize in the next iteration.

### Update: fixes applied

The evaluation above drove concrete fixes to the scoring logic, each now locked
in by a regression test in `tests/test_adversarial.py`:

- **Clamped numeric closeness.** `_closeness` now clamps to [0, 1], so
  out-of-range inputs can no longer contribute negative points. The "absurd
  numerics" case that previously scored **−191** now scores **3.25**, safely
  inside the intended [0, 6] range.
- **Case- and whitespace-insensitive categorical matching.** Genre and mood are
  normalized before comparison. The `"Rock"` (capital R) case that previously
  scored a **silent 0** on genre now correctly earns the genre match (**5.96**).
- **Deterministic tie-breaking.** Ties are now broken by title, then id, so
  rankings no longer depend on the order songs appear in the CSV.

Two items are intentionally left as follow-ups: unknown genres (e.g. "polka")
and empty profiles still score silently rather than warning or being rejected.
Input validation against the known catalog is the next candidate improvement.
