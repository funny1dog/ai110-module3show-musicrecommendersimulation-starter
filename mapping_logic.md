# Mapping Logic: Scoring & Ranking Songs

## Scoring Numerical Features: Proximity, Not Direction

The key insight: you don't want "higher energy = better." You want "closer to the user's preferred energy = better."

### Absolute Difference (simplest)

```python
score = 1 - abs(song_energy - user_pref_energy)
# user likes 0.8 energy, song has 0.75 → score = 1 - 0.05 = 0.95
# user likes 0.8 energy, song has 0.30 → score = 1 - 0.50 = 0.50
```

Returns a value in [0, 1]. Works well when all features are already normalized to [0, 1].

### Gaussian Similarity (smoother, more forgiving)

```python
import math
score = math.exp(-((song_val - user_pref) ** 2) / (2 * sigma ** 2))
```

- `sigma` controls the tolerance window (e.g., `0.15` = tight match required, `0.4` = loose)
- Score = 1.0 at perfect match, decays smoothly toward 0 as distance grows
- Better than raw difference because small gaps don't get penalized as harshly as large ones

For most starters, **absolute difference is sufficient** and easy to reason about.

---

## Handling Categorical Features

### Option 1: Exact Match (binary)

```python
score = 1.0 if song_genre == user_pref_genre else 0.0
```

Simple. All-or-nothing. Works fine when categories are meaningfully distinct (genre, mood).

### Option 2: Weighted Partial Match

Define a similarity matrix between categories:

```python
mood_similarity = {
    ("chill", "chill"):    1.0,
    ("chill", "relaxed"):  0.7,   # close enough
    ("chill", "focused"):  0.5,
    ("chill", "happy"):    0.2,
    ("chill", "intense"):  0.0,
}
score = mood_similarity.get((user_mood, song_mood), 0.0)
```

More expressive — "chill" and "relaxed" are adjacent, but "chill" and "intense" are opposites.

### Option 3: One-Hot + Cosine Similarity

Encode each category as a binary vector, then compute cosine similarity across all category dimensions at once. Overkill for 10 songs, but scales well.

For this project: **exact match for mood, optional partial match for genre** is the right level of complexity.

---

## The Full Algorithm Recipe

```text
INPUT:  user_preferences (dict of feature → preferred value)
        songs (list of song feature vectors)
        weights (dict of feature → importance, must sum to 1.0)

FOR each song:
    total_score = 0

    # --- Numerical features ---
    FOR each numerical feature (energy, tempo_bpm, valence, danceability, acousticness):
        feature_score = 1 - abs(song[feature] - user_pref[feature])
        total_score  += weights[feature] * feature_score

    # --- Categorical features ---
    FOR each categorical feature (mood, genre):
        feature_score = 1.0 if song[feature] == user_pref[feature] else 0.0
        total_score  += weights[feature] * feature_score

    song.score = total_score

SORT songs by score descending
RETURN top-N songs (excluding the seed song itself)
```

### Example Weight Distribution

```python
weights = {
    "energy":       0.25,   # strongest driver of "feel"
    "mood":         0.20,   # categorical, high signal
    "tempo_bpm":    0.20,   # activity level
    "valence":      0.15,   # emotional tone
    "acousticness": 0.10,
    "danceability": 0.10,
}
# sum = 1.0
```

---

## Critical Pre-Processing Step

`tempo_bpm` lives on a different scale (60–152) than everything else (0–1). **Normalize it first** or it will dominate the distance calculation:

```python
tempo_normalized = (tempo_bpm - 60) / (152 - 60)
# 60 BPM → 0.0,  152 BPM → 1.0
```

---

## Why This Works on the Dataset

Given the clusters in `data/songs.csv`:

- A user who likes *Midnight Coding* (energy=0.42, mood=chill) will score *Library Rain* and *Focus Flow* highly — same mood, similar energy
- A user who likes *Gym Hero* (energy=0.93, mood=intense) will score *Storm Runner* highly and *Spacewalk Thoughts* near zero
- The weights let you tune whether mood or audio features drive the ranking

---

## Why You Need Both a Scoring Rule and a Ranking Rule

### The distinction

A **Scoring Rule** is a *local* operation — it takes a single song and a user profile and returns one number: "how well does this song match this user?"

A **Ranking Rule** is a *global* operation — it takes the full list of scored songs and decides which ones to surface and in what order.

### Why scoring alone is not enough

Scoring tells you each song's match quality in isolation, but it cannot answer questions like:

- "Which 3 songs should I show out of 10?"
- "Should I show the top 3 by score, or avoid showing two nearly identical songs back-to-back?"
- "Should I exclude the song the user is currently playing?"

These are list-level decisions. Scoring has no awareness of the other songs — it only knows about one at a time.

### Why ranking alone is not enough

Ranking needs numbers to sort. Without a scoring rule, you have no meaningful signal to order songs by. Sorting by play count or release date is not personalization — it's just a list.

### They solve different problems

| | Scoring Rule | Ranking Rule |
| --- | --- | --- |
| Operates on | One song at a time | The full scored list |
| Answers | "How good is this song for this user?" | "Which songs should be shown, and in what order?" |
| Runs | Per song (parallelizable) | Once, after all songs are scored |
| Can be changed independently | Yes — swap distance formula | Yes — swap sort strategy or add filters |

### Concrete example

```text
Scoring Rule  →  [Song A: 0.91, Song B: 0.88, Song C: 0.87, Song D: 0.86, ...]
                                        ↓
Ranking Rule  →  sort descending, exclude current song, return top 3
                                        ↓
Output        →  [Song A, Song B, Song C]
```

If you only had scoring, you'd have a dictionary of floats with no presentation logic.
If you only had ranking, you'd have a sort with nothing meaningful to sort by.

Together, they form the complete pipeline: **score every candidate → rank the scored list → return top-N.**
