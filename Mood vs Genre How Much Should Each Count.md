# Mood vs Genre: How Much Should Each Count?

## First, Look at What the Data Actually Tells You

**Mood distribution** — 16 distinct values across 20 songs, nearly all unique:

```text
chill ×3, happy ×2, intense ×2 — all others appear exactly once
```

**Genre distribution** — 16 distinct values across 20 songs, also mostly unique:

```text
lofi ×2, pop ×2 — all others appear exactly once
```

This matters enormously. With 20 songs and 16 unique moods, an exact mood match will hit at most 2–3 songs. An exact genre match behaves the same way. **Both features are sparse at this catalog size** — binary exact-match on either will frequently return 0, starving the recommender of signal.

---

## The Core Question: What Does Each Feature Actually Represent?

| | Mood | Genre |
| --- | --- | --- |
| What it captures | Emotional feel in the moment | Stylistic and cultural category |
| How listener-centric it is | High — mood is about the user's state | Medium — genre is about the song's tradition |
| Cross-genre overlap? | Yes — `chill` spans lofi, ambient, jazz | No — `lofi` doesn't overlap with `metal` |
| Granularity in this dataset | Fine (16 values, 20 songs) | Fine (16 values, 20 songs) |

**Mood is more listener-centric.** A user who wants `chill` doesn't care whether it's lofi, jazz, or ambient — they care how it feels. Genre is more about catalog style, which is a weaker proxy for what a user actually wants right now.

---

## Recommended Weighting

```python
weights = {
    "favorite_mood":       0.20,   # stronger — cross-genre, listener-state signal
    "favorite_genre":      0.10,   # weaker — tiebreaker, not a veto
    "target_energy":       0.25,   # highest — most predictive numeric feature
    "target_tempo":        0.20,   # strong activity-level signal
    "target_valence":      0.15,   # emotional tone
    "target_acousticness": 0.10,   # secondary texture signal
}
# sum = 1.0
```

**Mood gets 2× the weight of genre** (0.20 vs 0.10).

---

## Why Not Equal Weight?

Consider this pair from the dataset:

| Song | Genre | Mood | Energy | Acousticness |
| --- | --- | --- | --- | --- |
| *Spacewalk Thoughts* | ambient | chill | 0.28 | 0.92 |
| *Focus Flow* | lofi | focused | 0.40 | 0.78 |

For a user with `favorite_genre=lofi, favorite_mood=chill`:

- **Equal weights (0.15 each):** *Focus Flow* wins on genre match, *Spacewalk Thoughts* wins on mood match — they cancel out and the numeric features decide
- **Mood-weighted (0.20 vs 0.10):** *Spacewalk Thoughts* pulls ahead slightly — which is the **more correct behavior**, since its audio profile (low energy, high acousticness) is a closer match to a chill listener than a focused-mood lofi track

---

## Why Not Make Mood Dominant (e.g. 0.40)?

With only 20 songs and 16 unique moods, an exact match on mood will hit 1–2 songs at most. If mood carries 0.40 of the total weight, the remaining 0.60 is spread across 5 numeric features — and the 18 songs with non-matching moods are immediately playing catch-up from 0, making the recommender feel rigid.

**The fix is partial mood matching** so adjacent moods (`chill`/`relaxed`/`peaceful`) score 0.5–0.7 instead of 0.0. That lets you raise mood's weight safely without starving the rest of the catalog:

```python
mood_proximity = {
    ("chill", "relaxed"):    0.7,
    ("chill", "focused"):    0.5,
    ("chill", "peaceful"):   0.6,
    ("chill", "moody"):      0.3,
    ("chill", "happy"):      0.2,
    ("chill", "intense"):    0.0,
    ("chill", "aggressive"): 0.0,
    ("chill", "euphoric"):   0.0,
}
```

With partial matching in place, `mood=0.20` is well-calibrated and `genre=0.10` acts as the tiebreaker it should be — not a decisive filter.
