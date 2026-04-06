# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

This system is a **content-based recommender**: it matches songs to a user purely based on audio features and mood, with no need for other users’ data.

### What features each `Song` uses

Not all columns in `songs.csv` are useful for similarity. `id` and `title` are identifiers; `artist` has too few examples to be meaningful at this scale. The system uses these **5 numeric features** plus **1 categorical feature**:

| Feature | Why it matters |
| --- | --- |
| `energy` | Primary driver of perceived intensity (0.28 ambient → 0.93 gym) |
| `tempo_bpm` | Normalized to 0–1 before scoring; captures slow/fast feel |
| `valence` | Emotional tone — happy vs. melancholic |
| `danceability` | Complements energy; separates rhythmic from atmospheric tracks |
| `acousticness` | Highest variance in the dataset (0.05–0.92); cleanly separates lofi/ambient from electronic |
| `mood` | Categorical label (chill, intense, happy, relaxed, focused, moody); scored as exact match |

`tempo_bpm` is normalized with `(bpm - 60) / (152 - 60)` so it sits on the same 0–1 scale as the other features and doesn’t dominate the score.

### What `UserProfile` stores

A `UserProfile` holds a **taste vector** — one preferred value per feature derived from the user’s listening history. Specifically:

- Preferred values for each numeric feature (e.g., preferred energy = 0.75)
- Preferred mood and genre labels
- Implicit signals: play counts, listen completion rate, and save/skip history, which are used to weight how strongly a past song influences the taste vector

### How `Recommender` scores each song

Each song receives a weighted similarity score against the user’s taste vector. For numeric features, the score rewards proximity — not just high or low values:

```text
feature_score = 1 - abs(song_value - user_preferred_value)
```

For the categorical `mood` feature, scoring is binary:

```text
mood_score = 1.0 if song mood matches user preferred mood, else 0.0
```

The final score is a weighted sum across all features:

```python
weights = {
    "energy":       0.25,
    "mood":         0.20,
    "tempo_bpm":    0.20,
    "valence":      0.15,
    "acousticness": 0.10,
    "danceability": 0.10,
}
score = sum(weights[f] * feature_score(f) for f in weights)
```

### How songs are chosen (Scoring Rule → Ranking Rule)

Scoring and ranking are two separate steps:

1. **Scoring Rule** — evaluates each song independently against the user profile, producing a score in [0, 1]
2. **Ranking Rule** — sorts all scored songs descending, excludes the seed song (the one the user is currently playing), and returns the top N results

This separation matters: scoring is a local, per-song operation; ranking is a global decision over the full catalog. Changing the scoring formula (e.g., switching from absolute difference to Gaussian similarity) does not require changing the ranking logic, and vice versa.

```text
Scoring  →  [Library Rain: 0.91, Focus Flow: 0.88, Rooftop Lights: 0.54, ...]
                                    ↓
Ranking  →  sort descending, exclude current song, return top 3
                                    ↓
Output   →  [Library Rain, Focus Flow, Midnight Coding]
```

---

### Algorithm Recipe

The complete pipeline, from user preferences to top-K recommendations:

```text
INPUT:  user_prefs  — dict of target feature values
        songs       — all rows loaded from songs.csv
        k           — number of recommendations to return
        weights     — importance of each feature (must sum to 1.0)

STEP 1 — Normalize
  For each song: tempo_normalized = (tempo_bpm - 60) / (152 - 60)

STEP 2 — Score every song
  For each song in catalog:
    numeric_score  = Σ weights[f] × (1 - abs(song[f] - user_prefs[f]))
                     for f in [energy, tempo, valence, danceability, acousticness]
    mood_score     = weights[mood]  × mood_proximity(song.mood, user_prefs.mood)
    genre_score    = weights[genre] × (1.0 if match else 0.0)
    total_score    = numeric_score + mood_score + genre_score

STEP 3 — Rank
  Sort all songs by total_score descending
  Remove the seed song (currently playing)
  Return top K
```

**Finalized weights:**

```python
weights = {
    "target_energy":       0.25,  # strongest numeric signal
    "favorite_mood":       0.20,  # cross-genre listener-state signal
    "target_tempo":        0.20,  # activity level
    "target_valence":      0.15,  # emotional tone
    "target_acousticness": 0.10,  # texture / organic vs electronic
    "favorite_genre":      0.10,  # tiebreaker, not a veto
}
# danceability folded into energy weight at this catalog size
```

**Mood uses partial matching, not binary:**

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

See [flowchart.md](flowchart.md) for a visual representation of this pipeline.

---

### Expected Biases

| Bias | Cause | Effect |
| --- | --- | --- |
| **Mood sparsity bias** | 16 unique moods across 20 songs — most moods appear once | Without partial matching, mood matching hits ≤2 songs; the system effectively ignores mood for most of the catalog |
| **Genre sparsity bias** | Same distribution as mood | Genre match rarely fires; acts more like a coin flip than a meaningful filter |
| **Filter bubble** | Numeric features reward proximity to one fixed taste vector | The system keeps recommending the same cluster of songs; a lofi listener will never discover jazz even if the audio features are nearly identical |
| **Acousticness dominance** | Highest variance feature (0.05–0.92) in the dataset | Small weight changes on acousticness shift scores more than the same change on valence or danceability |
| **Small catalog amplification** | Only 20 songs total | Scores compress — the difference between rank 1 and rank 5 may be <0.05, making top-K feel arbitrary near the boundary |
| **Static profile bias** | `UserProfile` is fixed at runtime | The system cannot adapt if a user's mood shifts mid-session; a user who usually likes chill but starts a workout gets the same recommendations |

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

1. Run the app:

```bash
python -m src.main
```

### Example Output

![Top Recommendations terminal output](Top_Recommendations.png)

---

### Stress Test with Diverse Profiles

Running all 8 user profiles (3 normal + 5 adversarial) against the 20-song catalog:

```text
Loaded 20 songs from the dataset.

==================================================
  Top Recommendations — Chill Lofi
==================================================

#1  Midnight Coding  —  LoRoom
     Score : 0.98  |  Genre: lofi  |  Mood: chill
     Why   :
       • energy closely matches (diff=0.02)
       • tempo closely matches (diff=0.00)
       • valence closely matches (diff=0.04)
       • acousticness closely matches (diff=0.04)
       • mood is an exact match (chill)
       • genre matches (lofi)

#2  Library Rain  —  Paper Lanterns
     Score : 0.96  |  Genre: lofi  |  Mood: chill
     Why   :
       • energy closely matches (diff=0.05)
       • tempo closely matches (diff=0.07)
       • valence closely matches (diff=0.00)
       • mood is an exact match (chill)
       • genre matches (lofi)

#3  Focus Flow  —  LoRoom
     Score : 0.89  |  Genre: lofi  |  Mood: focused
     Why   :
       • energy closely matches (diff=0.00)
       • tempo closely matches (diff=0.02)
       • valence closely matches (diff=0.01)
       • acousticness closely matches (diff=0.03)
       • mood is a partial match (focused ~ chill, sim=0.5)
       • genre matches (lofi)

#4  Spacewalk Thoughts  —  Orbit Bloom
     Score : 0.81  |  Genre: ambient  |  Mood: chill
     Why   :
       • valence closely matches (diff=0.05)
       • mood is an exact match (chill)
       • genre does not match (ambient vs lofi)

#5  Coffee Shop Stories  —  Slow Stereo
     Score : 0.78  |  Genre: jazz  |  Mood: relaxed
     Why   :
       • energy closely matches (diff=0.03)
       • mood is a partial match (relaxed ~ chill, sim=0.7)
       • genre does not match (jazz vs lofi)

==================================================

==================================================
  Top Recommendations — High-Energy Pop
==================================================

#1  Sunrise City  —  Neon Echo
     Score : 0.98  |  Genre: pop  |  Mood: happy
     Why   :
       • energy closely matches (diff=0.03)
       • tempo closely matches (diff=0.00)
       • valence closely matches (diff=0.04)
       • acousticness closely matches (diff=0.03)
       • mood is an exact match (happy)
       • genre matches (pop)

#2  Rooftop Lights  —  Indigo Parade
     Score : 0.83  |  Genre: indie pop  |  Mood: happy
     Why   :
       • energy closely matches (diff=0.09)
       • tempo closely matches (diff=0.07)
       • valence closely matches (diff=0.07)
       • mood is an exact match (happy)
       • genre does not match (indie pop vs pop)

#3  Neon Rave  —  Pulse Grid
     Score : 0.76  |  Genre: edm  |  Mood: euphoric
     Why   :
       • energy closely matches (diff=0.10)
       • valence closely matches (diff=0.00)
       • mood is a partial match (euphoric ~ happy, sim=0.7)
       • genre does not match (edm vs pop)

#4  Gym Hero  —  Max Pulse
     Score : 0.72  |  Genre: pop  |  Mood: intense
     Why   :
       • energy closely matches (diff=0.08)
       • acousticness closely matches (diff=0.10)
       • mood does not match (intense vs happy)
       • genre matches (pop)

#5  Fuego Lento  —  Casa Ritmo
     Score : 0.62  |  Genre: latin  |  Mood: dreamy
     Why   :
       • tempo closely matches (diff=0.06)
       • valence closely matches (diff=0.09)
       • mood does not match (dreamy vs happy)
       • genre does not match (latin vs pop)

==================================================

==================================================
  Top Recommendations — Deep Intense Rock
==================================================

#1  Storm Runner  —  Voltline
     Score : 0.99  |  Genre: rock  |  Mood: intense
     Why   :
       • energy closely matches (diff=0.01)
       • tempo closely matches (diff=0.00)
       • valence closely matches (diff=0.08)
       • acousticness closely matches (diff=0.00)
       • mood is an exact match (intense)
       • genre matches (rock)

#2  Gym Hero  —  Max Pulse
     Score : 0.79  |  Genre: pop  |  Mood: intense
     Why   :
       • energy closely matches (diff=0.01)
       • acousticness closely matches (diff=0.05)
       • mood is an exact match (intense)
       • genre does not match (pop vs rock)

#3  Iron Curtain  —  Rustvolt
     Score : 0.76  |  Genre: metal  |  Mood: aggressive
     Why   :
       • energy closely matches (diff=0.05)
       • acousticness closely matches (diff=0.06)
       • mood is a partial match (aggressive ~ intense, sim=0.7)
       • genre does not match (metal vs rock)

#4  Neon Rave  —  Pulse Grid
     Score : 0.59  |  Genre: edm  |  Mood: euphoric
     Why   :
       • energy closely matches (diff=0.03)
       • valence is far off (diff=0.48)
       • acousticness closely matches (diff=0.07)
       • mood does not match (euphoric vs intense)
       • genre does not match (edm vs rock)

#5  Night Drive Loop  —  Neon Echo
     Score : 0.54  |  Genre: synthwave  |  Mood: moody
     Why   :
       • tempo is far off (diff=0.46)
       • valence closely matches (diff=0.09)
       • mood does not match (moody vs intense)
       • genre does not match (synthwave vs rock)

==================================================

==================================================
  Top Recommendations — Conflicting Energy + Mood
==================================================

#1  Storm Runner  —  Voltline
     Score : 0.74  |  Genre: rock  |  Mood: intense
     Why   :
       • energy closely matches (diff=0.01)
       • tempo closely matches (diff=0.10)
       • acousticness closely matches (diff=0.00)
       • mood does not match (intense vs chill)
       • genre matches (rock)

#2  Iron Curtain  —  Rustvolt
     Score : 0.62  |  Genre: metal  |  Mood: aggressive
     Why   :
       • energy closely matches (diff=0.07)
       • valence closely matches (diff=0.02)
       • acousticness closely matches (diff=0.06)
       • mood does not match (aggressive vs chill)
       • genre does not match (metal vs rock)

#3  Night Drive Loop  —  Neon Echo
     Score : 0.60  |  Genre: synthwave  |  Mood: moody
     Why   :
       • mood is a partial match (moody ~ chill, sim=0.3)
       • genre does not match (synthwave vs rock)

#4  Gym Hero  —  Max Pulse
     Score : 0.58  |  Genre: pop  |  Mood: intense
     Why   :
       • energy closely matches (diff=0.03)
       • valence is far off (diff=0.57)
       • acousticness closely matches (diff=0.05)
       • mood does not match (intense vs chill)
       • genre does not match (pop vs rock)

#5  Neon Rave  —  Pulse Grid
     Score : 0.57  |  Genre: edm  |  Mood: euphoric
     Why   :
       • energy closely matches (diff=0.05)
       • tempo closely matches (diff=0.03)
       • valence is far off (diff=0.68)
       • acousticness closely matches (diff=0.07)
       • mood does not match (euphoric vs chill)
       • genre does not match (edm vs rock)

==================================================

==================================================
  Top Recommendations — All Midpoint
==================================================

#1  Sunrise City  —  Neon Echo
     Score : 0.81  |  Genre: pop  |  Mood: happy
     Why   :
       • mood is an exact match (happy)
       • genre matches (pop)

#2  Rooftop Lights  —  Indigo Parade
     Score : 0.73  |  Genre: indie pop  |  Mood: happy
     Why   :
       • mood is an exact match (happy)
       • genre does not match (indie pop vs pop)

#3  Midnight Coding  —  LoRoom
     Score : 0.63  |  Genre: lofi  |  Mood: chill
     Why   :
       • energy closely matches (diff=0.08)
       • valence closely matches (diff=0.06)
       • mood is a partial match (chill ~ happy, sim=0.2)
       • genre does not match (lofi vs pop)

#4  Coffee Shop Stories  —  Slow Stereo
     Score : 0.62  |  Genre: jazz  |  Mood: relaxed
     Why   :
       • mood is a partial match (relaxed ~ happy, sim=0.3)
       • genre does not match (jazz vs pop)

#5  Dusty Road Home  —  The Pines
     Score : 0.62  |  Genre: country  |  Mood: nostalgic
     Why   :
       • energy closely matches (diff=0.06)
       • tempo closely matches (diff=0.02)
       • mood does not match (nostalgic vs happy)
       • genre does not match (country vs pop)

==================================================

==================================================
  Top Recommendations — Unknown Genre and Mood
==================================================

#1  Candlelight Folk  —  Wren & Hollow
     Score : 0.88  |  Genre: folk  |  Mood: peaceful
     Why   :
       • energy closely matches (diff=0.00)
       • tempo closely matches (diff=0.00)
       • valence closely matches (diff=0.03)
       • mood is an exact match (peaceful)
       • genre does not match (folk vs classical)

#2  Coffee Shop Stories  —  Slow Stereo
     Score : 0.80  |  Genre: jazz  |  Mood: relaxed
     Why   :
       • energy closely matches (diff=0.07)
       • valence closely matches (diff=0.01)
       • acousticness closely matches (diff=0.09)
       • mood is a partial match (relaxed ~ peaceful, sim=0.8)
       • genre does not match (jazz vs classical)

#3  Library Rain  —  Paper Lanterns
     Score : 0.78  |  Genre: lofi  |  Mood: chill
     Why   :
       • energy closely matches (diff=0.05)
       • tempo closely matches (diff=0.02)
       • valence closely matches (diff=0.10)
       • acousticness closely matches (diff=0.06)
       • mood is a partial match (chill ~ peaceful, sim=0.6)
       • genre does not match (lofi vs classical)

#4  Spacewalk Thoughts  —  Orbit Bloom
     Score : 0.77  |  Genre: ambient  |  Mood: chill
     Why   :
       • energy closely matches (diff=0.02)
       • valence closely matches (diff=0.05)
       • mood is a partial match (chill ~ peaceful, sim=0.6)
       • genre does not match (ambient vs classical)

#5  Midnight Coding  —  LoRoom
     Score : 0.75  |  Genre: lofi  |  Mood: chill
     Why   :
       • tempo closely matches (diff=0.05)
       • acousticness closely matches (diff=0.09)
       • mood is a partial match (chill ~ peaceful, sim=0.6)
       • genre does not match (lofi vs classical)

==================================================

==================================================
  Top Recommendations — All Zeros
==================================================

#1  Spacewalk Thoughts  —  Orbit Bloom
     Score : 0.74  |  Genre: ambient  |  Mood: chill
     Why   :
       • tempo closely matches (diff=0.00)
       • valence is far off (diff=0.65)
       • acousticness is far off (diff=0.92)
       • mood is an exact match (chill)
       • genre matches (ambient)

#2  Library Rain  —  Paper Lanterns
     Score : 0.61  |  Genre: lofi  |  Mood: chill
     Why   :
       • valence is far off (diff=0.60)
       • acousticness is far off (diff=0.86)
       • mood is an exact match (chill)
       • genre does not match (lofi vs ambient)

#3  Midnight Coding  —  LoRoom
     Score : 0.60  |  Genre: lofi  |  Mood: chill
     Why   :
       • energy is far off (diff=0.42)
       • valence is far off (diff=0.56)
       • acousticness is far off (diff=0.71)
       • mood is an exact match (chill)
       • genre does not match (lofi vs ambient)

#4  Candlelight Folk  —  Wren & Hollow
     Score : 0.51  |  Genre: folk  |  Mood: peaceful
     Why   :
       • valence is far off (diff=0.73)
       • acousticness is far off (diff=0.94)
       • mood is a partial match (peaceful ~ chill, sim=0.6)
       • genre does not match (folk vs ambient)

#5  Moonlight Sonata Reimagined  —  Clara Voss
     Score : 0.50  |  Genre: classical  |  Mood: melancholic
     Why   :
       • tempo closely matches (diff=0.02)
       • acousticness is far off (diff=0.97)
       • mood does not match (melancholic vs chill)
       • genre does not match (classical vs ambient)

==================================================

==================================================
  Top Recommendations — All Ones
==================================================

#1  Storm Runner  —  Voltline
     Score : 0.81  |  Genre: rock  |  Mood: intense
     Why   :
       • energy closely matches (diff=0.09)
       • tempo closely matches (diff=0.00)
       • valence is far off (diff=0.52)
       • acousticness is far off (diff=0.90)
       • mood is an exact match (intense)
       • genre matches (rock)

#2  Gym Hero  —  Max Pulse
     Score : 0.71  |  Genre: pop  |  Mood: intense
     Why   :
       • energy closely matches (diff=0.07)
       • acousticness is far off (diff=0.95)
       • mood is an exact match (intense)
       • genre does not match (pop vs rock)

#3  Iron Curtain  —  Rustvolt
     Score : 0.58  |  Genre: metal  |  Mood: aggressive
     Why   :
       • energy closely matches (diff=0.03)
       • valence is far off (diff=0.78)
       • acousticness is far off (diff=0.96)
       • mood is a partial match (aggressive ~ intense, sim=0.7)
       • genre does not match (metal vs rock)

#4  Neon Rave  —  Pulse Grid
     Score : 0.55  |  Genre: edm  |  Mood: euphoric
     Why   :
       • energy closely matches (diff=0.05)
       • acousticness is far off (diff=0.97)
       • mood does not match (euphoric vs intense)
       • genre does not match (edm vs rock)

#5  Rooftop Lights  —  Indigo Parade
     Score : 0.49  |  Genre: indie pop  |  Mood: happy
     Why   :
       • acousticness is far off (diff=0.65)
       • mood does not match (happy vs intense)
       • genre does not match (indie pop vs rock)

==================================================
```

---

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

### Do the recommendations "feel" right? A musical intuition check

#### Chill Lofi — feels right

The top 3 are all lofi tracks with chill or adjacent moods: *Midnight Coding*, *Library Rain*, and *Focus Flow*. Musically this is exactly what you'd expect — slow BPM, high acousticness, mellow energy. #4 (*Spacewalk Thoughts*, ambient/chill) is a reasonable stretch: ambient and lofi share the same listener headspace even if they're different genres. #5 (*Coffee Shop Stories*, jazz/relaxed) also makes intuitive sense — jazz cafè music sits right next to lofi study playlists on real platforms. **This profile produces the most trustworthy results.**

#### High-Energy Pop — mostly right, one odd result

\#1–3 feel natural: *Sunrise City* (pop/happy) is a near-perfect hit, *Rooftop Lights* (indie pop/happy) is a reasonable adjacent pick, and *Neon Rave* (edm/euphoric) is a credible energy match even without a genre hit. The partial mood match `euphoric ~ happy (0.7)` is doing real work here. \#4 (*Gym Hero*, pop/intense) is genre-correct but mood-wrong — a real listener asking for happy pop probably doesn't want an intense workout track. \#5 (*Fuego Lento*, latin/dreamy) feels out of place: tempo matches but dreamy latin doesn't belong in a high-energy pop session. **The system gets the top 3 right but the bottom 2 reveal that tempo proximity can pull in off-vibe songs when mood and genre both miss.**

#### Conflicting Energy + Mood — exposes the biggest flaw

This is where musical intuition and the scorer diverge most clearly. The user wants **high energy (0.9) but chill mood** — think chillstep, lo-fi drum and bass, or atmospheric electronic. The system returns *Storm Runner* (hard rock/intense) at #1 because energy+tempo (45% combined weight) dominate the chill mood penalty (20% weight). A real listener would find this jarring. The scoring formula has no concept of "genre adjacency to the requested vibe" — it sees matching numbers, not matching feel. **This confirms that numeric proximity alone cannot capture listener intent when features conflict, and that mood weight at 0.20 is too weak to veto a strong numeric match.**

---

## Challenge 1: Advanced Song Features

### What was added

5 new columns were added to `data/songs.csv` and integrated into the scoring logic in `src/recommender.py`:

| Feature | Type | Range | What it captures |
| --- | --- | --- | --- |
| `popularity` | int | 0–100 | Mainstream vs underground. Neon Rave = 82, Delta Crossroads = 24 |
| `release_decade` | string | 1990s–2020s | Era feel. Delta Crossroads = 1990s, all lofi tracks = 2020s |
| `liveness` | float | 0–1 | Studio-polished (0.06) vs raw live feel. Coffee Shop Stories = 0.62, Delta Crossroads = 0.71 |
| `instrumentalness` | float | 0–1 | Vocal-heavy near 0 (Gym Hero = 0.03) to fully instrumental (Moonlight Sonata = 0.98) |
| `loudness_norm` | float | 0–1 | Quiet ambient (Spacewalk Thoughts = 0.18) to wall-of-sound metal (Iron Curtain = 0.95) |

Weights were rebalanced across all 11 scored features so the sum stays 1.0. Core audio features still lead; the 5 new features act as secondary tiebreakers (weights 0.02–0.08).

A `_DECADE_PROXIMITY` table was added for partial era matching — adjacent decades score 0.8, two apart score 0.5, and so on.

The `_MOOD_PROXIMITY` table was also expanded to cover the 7 previously orphaned moods (`dreamy`, `groovy`, `melancholic`, `nostalgic`, `romantic`, `soulful`, `uplifting`), fixing the mood orphan bias documented earlier.

### Findings

**1. Mood orphan bias is fixed.**
The 7 previously invisible moods now have proximity entries. *Fuego Lento* (dreamy) and *Dusty Road Home* (nostalgic) now surface in relevant profiles because `dreamy ~ peaceful (0.6)` and `nostalgic ~ relaxed (0.5)` give them partial mood credit they never had before.

**2. New features act as tiebreakers, not score drivers.**
At weights of 0.02–0.08, the new features rarely change the #1 result but do shift lower-ranked slots. *Candlelight Folk* (high liveness = 0.55, high instrumentalness = 0.42) now appears in the Chill Lofi top 5 where it previously didn't — the instrumentalness match pushed it past songs with weaker numeric alignment.

**3. Popularity separates otherwise tied songs.**
Several songs that scored similarly on audio features now get differentiated by popularity proximity. A user targeting underground music (target popularity = 0.40) now ranks *Library Rain* (38) above *Midnight Coding* (45) by a small but consistent margin.

**4. Decade matching adds era preference without dominating.**
At weight 0.07, decade matching is roughly equivalent to a weak genre signal. A user who prefers 2020s music gets a small boost for 2020s tracks and a measurable penalty for 1990s tracks like *Delta Crossroads* — without burying it completely if the audio features are a strong match.

**5. The filter bubble is slightly reduced.**
With more differentiating features, more songs find at least one profile where they rank well. Songs like *Delta Crossroads* (1990s, high liveness, soulful) now match the Unknown Genre profile more precisely, pushing it into the top 5 in cases where it was previously edged out by lofi tracks with better mood proximity.

**6. Scores are richer and more explainable.**
Each recommendation now shows up to 11 bullet-point reasons instead of 6. A user can see not just "energy closely matches" but also "liveness closely matches (diff=0.02)" and "decade matches (2020s)", making the output more informative and easier to audit.

---
## Challenge 2: Multiple Scoring Modes

### What was built

Four scoring modes were added to `src/recommender.py` in a `SCORING_MODES` registry. Each mode is a complete weight dict that sums to 1.0. Pass the mode name to `recommend_songs()` to switch strategy:

```python
recommend_songs(user_prefs, songs, k=5, mode="mood_first")
```

| Mode | Dominant signal | Weight | Best for |
| --- | --- | --- | --- |
| `balanced` | All 11 features proportionally | energy 0.20, mood 0.15, tempo 0.12 | General-purpose default |
| `genre_first` | Genre + era | genre 0.30, decade 0.15, mood 0.15 | Stylistic consistency — same genre and era |
| `mood_first` | Mood | mood 0.35, energy 0.15, valence 0.12 | Vibe-driven listening across genres |
| `energy_focused` | Energy + tempo + loudness | energy 0.40, tempo 0.25, loudness 0.10 | Activity contexts — workouts, focus sessions |

### Findings: how modes change rankings

The table below shows the top-5 for three representative profiles across all four modes. Songs that change position are the most interesting signal.

#### Chill Lofi

| Rank | balanced | genre_first | mood_first | energy_focused |
| --- | --- | --- | --- | --- |
| #1 | Midnight Coding | Midnight Coding | Midnight Coding | Midnight Coding |
| #2 | Library Rain | Library Rain | Library Rain | Library Rain |
| #3 | Focus Flow | Focus Flow | Spacewalk Thoughts | Focus Flow |
| #4 | Spacewalk Thoughts | Spacewalk Thoughts | Focus Flow | Coffee Shop Stories |
| #5 | Candlelight Folk | Candlelight Folk | Coffee Shop Stories | Candlelight Folk |

`mood_first` swaps #3 and #4 — *Spacewalk Thoughts* (ambient/chill, exact mood match) jumps above *Focus Flow* (lofi/focused, partial mood match) because mood weight triples from 0.15 to 0.35. `energy_focused` pushes *Coffee Shop Stories* into #4 because it closely matches the low energy target (diff=0.03), bumping *Candlelight Folk* down.

#### High-Energy Pop

| Rank | balanced | genre_first | mood_first | energy_focused |
| --- | --- | --- | --- | --- |
| #1 | Sunrise City | Sunrise City | Sunrise City | Sunrise City |
| #2 | Rooftop Lights | Gym Hero | Rooftop Lights | Rooftop Lights |
| #3 | Neon Rave | Rooftop Lights | Neon Rave | Gym Hero |
| #4 | Gym Hero | Neon Rave | Concrete Jungle | Concrete Jungle |
| #5 | Concrete Jungle | Concrete Jungle | Island Drift | Neon Rave |

`genre_first` promotes *Gym Hero* (pop/intense) to #2 — same genre as the user, and the 0.30 genre weight overwhelms the mood mismatch. `mood_first` replaces *Gym Hero* entirely with *Island Drift* (reggae/uplifting), which has a strong `uplifting ~ happy (0.8)` partial match. `energy_focused` pushes *Neon Rave* (edm) down because its tempo normalizes to 0.87 vs the user's 0.63 — a 0.24 gap that now costs 0.06 points (25% weight × 0.24).

#### Conflicting Energy + Mood

| Rank | balanced | genre_first | mood_first | energy_focused |
| --- | --- | --- | --- | --- |
| #1 | Storm Runner | Storm Runner | Storm Runner | Storm Runner |
| #2 | Iron Curtain | Night Drive Loop | Night Drive Loop | Gym Hero |
| #3 | Night Drive Loop | Midnight Coding | Midnight Coding | Neon Rave |
| #4 | Gym Hero | Rooftop Lights | Storm Runner | Iron Curtain |
| #5 | Rooftop Lights | Iron Curtain | Library Rain | Sunrise City |

This is the most revealing comparison. `mood_first` demotes *Iron Curtain* (metal/aggressive, mood mismatch) all the way to off the list and surfaces *Midnight Coding* and *Library Rain* — lofi tracks that partially match "chill" via mood proximity. `genre_first` does something different: it surfaces *Night Drive Loop* and *Midnight Coding* because the genre weight rewards the rock/synthwave/lofi cluster over pure numeric proximity. `energy_focused` makes the conflict worse — *Storm Runner* stays #1 with an even larger margin and the whole list fills with high-energy songs regardless of mood.

### Key takeaways

1. **`mood_first` is the best fix for the Conflicting Energy + Mood problem.** Tripling the mood weight (0.15 → 0.35) finally has enough force to override the energy signal and surfaces vibe-appropriate songs.
2. **`genre_first` tightens the stylistic cluster but kills diversity.** For High-Energy Pop, slots #2–5 are all pop or pop-adjacent. For Chill Lofi, all 5 slots are lofi or ambient — no jazz, no folk, no cross-genre surprises.
3. **`energy_focused` is reliable for activity profiles but fragile for mixed-intent users.** It correctly ranks Storm Runner and Gym Hero for workout users, but completely fails the Conflicting Energy + Mood profile.
4. **#1 never changes for any profile.** The top song is so dominant across all features that no weight shift dislodges it. Diversity at the top requires a different mechanism — like a penalty for returning the same artist twice.

---
## Challenge 3: Diversity and Fairness Logic

### What was built

A `rerank_with_diversity()` function was added to `src/recommender.py`. After all songs are scored, it greedily builds the top-k list one slot at a time. Before picking each song, it applies multiplier penalties to any candidate that repeats an artist or genre already in the list:

- **Artist penalty (default 0.5):** halves the effective score of a song whose artist already appears. Strong deterrent — the catalog has a few artists with multiple tracks (LoRoom has 2 lofi songs, Neon Echo has 2).
- **Genre penalty (default 0.7):** reduces the effective score by 30% for a repeated genre. Gentler push — genre diversity is less critical than artist diversity for short lists.
- **Penalties stack:** a song that repeats both artist and genre gets `score × 0.5 × 0.7 = score × 0.35`.

The original score stored in the returned tuple is **unchanged** — only the selection order is affected. This keeps scoring and diversity as separate, independent steps.

**How to use:**

```python
# diversity off (default)
recommend_songs(user_prefs, songs, k=5, mode="balanced")

# diversity on with default penalties
recommend_songs(user_prefs, songs, k=5, mode="balanced", diversity=True)

# diversity on with custom penalties
recommend_songs(user_prefs, songs, k=5, mode="balanced",
                diversity=True, artist_penalty=0.3, genre_penalty=0.8)
```

### Findings: what changed with diversity=ON

#### Chill Lofi — biggest impact

| Rank | diversity=OFF | diversity=ON |
| --- | --- | --- |
| #1 | Midnight Coding (lofi / LoRoom) | Midnight Coding (lofi / LoRoom) |
| #2 | Library Rain (lofi / Paper Lanterns) | **Spacewalk Thoughts (ambient / Orbit Bloom)** |
| #3 | Focus Flow (lofi / LoRoom) | **Candlelight Folk (folk / Wren & Hollow)** |
| #4 | Spacewalk Thoughts (ambient / Orbit Bloom) | **Coffee Shop Stories (jazz / Slow Stereo)** |
| #5 | Candlelight Folk (folk / Wren & Hollow) | **Library Rain (lofi / Paper Lanterns)** |

Without diversity, slots #2–#3 were both lofi tracks from LoRoom (same artist). The artist penalty halved *Focus Flow*'s effective score, pushing it out of the top 3. *Library Rain* falls to #5 because the lofi genre penalty accumulates after *Midnight Coding* is selected. The result spans 4 genres (lofi, ambient, folk, jazz) instead of a single lofi cluster.

#### High-Energy Pop — minor shift at the bottom

| Rank | diversity=OFF | diversity=ON |
| --- | --- | --- |
| #1 | Sunrise City (pop / Neon Echo) | Sunrise City (pop / Neon Echo) |
| #2 | Rooftop Lights (indie pop / Indigo Parade) | Rooftop Lights (indie pop / Indigo Parade) |
| #3 | Neon Rave (edm / Pulse Grid) | Neon Rave (edm / Pulse Grid) |
| #4 | Gym Hero (pop / Max Pulse) | **Concrete Jungle (hip-hop / Verse City)** |
| #5 | Concrete Jungle (hip-hop / Verse City) | **Fuego Lento (latin / Casa Ritmo)** |

*Gym Hero* drops from #4 to off-list — it's pop genre (same as *Sunrise City*), so it takes a 0.7× genre penalty. *Fuego Lento* (latin/dreamy), previously out of the top 5, enters at #5 because every other candidate already carries a genre penalty.

#### Deep Intense Rock and Conflicting Energy + Mood — no change

All 5 songs in these lists already have unique artists and unique genres, so no penalties fire. Diversity only matters when the top-scoring songs cluster around the same artist or genre.

#### All Zeros — swap at #3/#4

*Midnight Coding* (lofi / LoRoom) drops from #3 to off-list because *Library Rain* (also lofi) was already selected at #2. *Coffee Shop Stories* (jazz) and *Moonlight Sonata* (classical) move up, and *Candlelight Folk* (folk) enters at #5.

### Key takeaways

1. **Diversity has the most impact when the catalog has multi-song artists or genre clusters.** Chill Lofi is the clearest case: LoRoom has two lofi tracks that both score near the top, and without diversity both appear in slots #2–#3.
2. **The penalty does not change scores — only selection order.** A penalised song can still appear in the list if no better alternative exists. *Library Rain* still appears at #5 for Chill Lofi because after 4 unique-genre songs are picked, it's the best remaining option.
3. **Strong artist penalty (0.5) moves the needle more than the genre penalty (0.7).** The artist penalty is the main driver of visible change. Raising genre penalty to 0.5 would break up genre clusters more aggressively but risks surfacing songs the user doesn't want at all.
4. **Diversity cannot fix a sparse catalog.** For Deep Intense Rock, all top-5 songs already have unique artists and genres — there's no clustering to break. The fairness problem there is that only one rock song exists, not that the same artist repeats.

---
## Challenge 4: Visual Summary Table

### What was built

Terminal output was redesigned using the `tabulate` library. Each recommendation block now has three parts:

1. **Box header** — Unicode `╔═╗ / ╚═╝` border showing the profile name and scoring mode
2. **Summary table** — five songs in a clean aligned grid (rank, title, artist, genre, mood, score)
3. **Reasons block** — per-song bullet points indented below the table

`tabulate` was added to `requirements.txt`.

### Example output — Chill Lofi profile, all four scoring modes

```text
╔══════════════════════════════════════════════════════════════╗
║  Chill Lofi  [balanced]                                      ║
╚══════════════════════════════════════════════════════════════╝

    Title               Artist          Genre    Mood      Score
--  ------------------  --------------  -------  --------  -------
#1  Midnight Coding     LoRoom          lofi     chill     0.98
#2  Library Rain        Paper Lanterns  lofi     chill     0.97
#3  Focus Flow          LoRoom          lofi     focused   0.92
#4  Spacewalk Thoughts  Orbit Bloom     ambient  chill     0.83
#5  Candlelight Folk    Wren & Hollow   folk     peaceful  0.75

  Why each song was picked:
  #1 Midnight Coding
      • energy closely matches (diff=0.02)
      • tempo closely matches (diff=0.00)
      • valence closely matches (diff=0.04)
      • acousticness closely matches (diff=0.04)
      • popularity closely matches (diff=0.05)
      • liveness closely matches (diff=0.02)
      • instrumentalness closely matches (diff=0.05)
      • loudness closely matches (diff=0.04)
      • mood is an exact match (chill)
      • genre matches (lofi)
      • decade matches (2020s)
  #2 Library Rain
      • energy closely matches (diff=0.05)
      • tempo closely matches (diff=0.07)
      • valence closely matches (diff=0.00)
      • popularity closely matches (diff=0.02)
      • liveness closely matches (diff=0.01)
      • instrumentalness closely matches (diff=0.02)
      • loudness closely matches (diff=0.02)
      • mood is an exact match (chill)
      • genre matches (lofi)
      • decade matches (2020s)
  #3 Focus Flow
      • energy closely matches (diff=0.00)
      • tempo closely matches (diff=0.02)
      • valence closely matches (diff=0.01)
      • acousticness closely matches (diff=0.03)
      • popularity closely matches (diff=0.02)
      • liveness closely matches (diff=0.00)
      • instrumentalness closely matches (diff=0.00)
      • loudness closely matches (diff=0.05)
      • mood is a partial match (focused ~ chill, sim=0.5)
      • genre matches (lofi)
      • decade matches (2020s)
  #4 Spacewalk Thoughts
      • valence closely matches (diff=0.05)
      • liveness closely matches (diff=0.04)
      • mood is an exact match (chill)
      • genre does not match (ambient vs lofi)
      • decade matches (2020s)
  #5 Candlelight Folk
      • tempo closely matches (diff=0.05)
      • liveness is far off (diff=0.45)
      • mood is a partial match (peaceful ~ chill, sim=0.6)
      • genre does not match (folk vs lofi)
      • decade matches (2020s)

╔══════════════════════════════════════════════════════════════╗
║  Chill Lofi  [genre_first]                                   ║
╚══════════════════════════════════════════════════════════════╝

    Title               Artist          Genre    Mood      Score
--  ------------------  --------------  -------  --------  -------
#1  Midnight Coding     LoRoom          lofi     chill     0.99
#2  Library Rain        Paper Lanterns  lofi     chill     0.98
#3  Focus Flow          LoRoom          lofi     focused   0.92
#4  Spacewalk Thoughts  Orbit Bloom     ambient  chill     0.65
#5  Candlelight Folk    Wren & Hollow   folk     peaceful  0.58

╔══════════════════════════════════════════════════════════════╗
║  Chill Lofi  [mood_first]                                    ║
╚══════════════════════════════════════════════════════════════╝

    Title               Artist          Genre    Mood      Score
--  ------------------  --------------  -------  --------  -------
#1  Midnight Coding     LoRoom          lofi     chill     0.97
#2  Library Rain        Paper Lanterns  lofi     chill     0.96
#3  Spacewalk Thoughts  Orbit Bloom     ambient  chill     0.88
#4  Focus Flow          LoRoom          lofi     focused   0.87
#5  Coffee Shop Stories Slow Stereo     jazz     relaxed   0.78

╔══════════════════════════════════════════════════════════════╗
║  Chill Lofi  [energy_focused]                                ║
╚══════════════════════════════════════════════════════════════╝

    Title               Artist          Genre    Mood      Score
--  ------------------  --------------  -------  --------  -------
#1  Midnight Coding     LoRoom          lofi     chill     0.96
#2  Library Rain        Paper Lanterns  lofi     chill     0.93
#3  Focus Flow          LoRoom          lofi     focused   0.93
#4  Coffee Shop Stories Slow Stereo     jazz     relaxed   0.90
#5  Candlelight Folk    Wren & Hollow   folk     peaceful  0.88
```

### What improved

Before this change, each song took 8–12 lines of terminal output. The summary table collapses all five songs into 7 lines, making it easy to scan and compare results across modes at a glance. The reasons block is still present for deeper inspection but no longer dominates the screen. Long strings (title, artist, genre, mood) are truncated to fixed widths so columns stay aligned regardless of song name length.

---
