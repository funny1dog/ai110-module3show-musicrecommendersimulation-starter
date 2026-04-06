# Data Analysis: songs.csv

## Dataset Overview

**10 songs, 10 columns:**

`id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`

---

## Feature Assessment

| Feature | Type | Usable for Similarity? | Notes |
| --- | --- | --- | --- |
| `energy` | Float 0–1 | **Yes — top pick** | Wide range (0.28–0.93), continuous, numerically comparable |
| `tempo_bpm` | Float (BPM) | **Yes — top pick** | Range 60–152, strong proxy for activity level; normalize before use |
| `valence` | Float 0–1 | **Yes — top pick** | Captures happy vs. sad; range 0.48–0.84, good spread |
| `danceability` | Float 0–1 | **Yes** | Range 0.41–0.88, complements energy well |
| `acousticness` | Float 0–1 | **Yes** | High variance (0.05–0.92), strongly differentiates lofi/ambient from synthwave/rock |
| `mood` | Categorical | **Yes — but encode first** | 5 values: happy, chill, intense, relaxed, focused, moody — one-hot encode |
| `genre` | Categorical | **Secondary** | 6 genres; useful but coarser than audio features |
| `artist` | Categorical | **Skip for now** | Only 10 songs — artist similarity not meaningful at this scale |
| `title` | Text | **Skip** | No NLP infrastructure warranted for 10 songs |
| `id` | Integer | **Skip** | Identifier only |

---

## Recommended Feature Set

For a simple content-based recommender on this dataset, use these **5 features**:

```text
energy, tempo_bpm (normalized), valence, danceability, acousticness
```

They are all continuous floats on comparable scales (after normalizing `tempo_bpm` to 0–1), so you can compute **cosine similarity** or **Euclidean distance** directly on the feature vector without encoding overhead.

**Optionally add** `mood` as a one-hot encoded vector — it gives a strong categorical signal that separates *focused* (lofi study) from *intense* (gym/rock) even when audio features partially overlap.

---

## Observable Clusters in the Data

Even by eye, the features cleanly separate the songs into natural groups:

| Group | Songs | Key signal |
| --- | --- | --- |
| High-energy / gym | Gym Hero, Storm Runner | energy > 0.9, tempo > 130 |
| Lofi / chill | Midnight Coding, Library Rain, Focus Flow | energy < 0.45, acousticness > 0.7 |
| Ambient | Spacewalk Thoughts | lowest energy (0.28), lowest tempo (60) |
| Upbeat pop / indie | Sunrise City, Rooftop Lights | high valence > 0.8, high danceability |
| Synthwave / moody | Night Drive Loop | mid-energy, low acousticness, low valence |
| Jazz / relaxed | Coffee Shop Stories | high acousticness, mid-low energy |

A recommender using the 5 core features would correctly return lofi songs when a user likes "Midnight Coding", and gym tracks when they like "Gym Hero" — without needing any user history.
