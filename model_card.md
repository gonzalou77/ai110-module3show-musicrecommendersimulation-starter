# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

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
