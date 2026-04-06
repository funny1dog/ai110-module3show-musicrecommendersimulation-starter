# How Streaming Platforms Predict What You'll Love

## The Core Problem

Platforms like Spotify, YouTube, and Apple Music have libraries of 100M+ tracks. The goal is to surface the ~20 songs a user will actually enjoy at any given moment.

---

## Two Foundational Approaches

### 1. Collaborative Filtering — "People like you also liked..."

**Core idea:** Ignore what a song *sounds like*. Instead, infer taste from the collective behavior of millions of users.

**How it works:**

- Build a giant matrix: rows = users, columns = songs, values = plays/likes/skips
- Find users with similar listening histories ("neighbors")
- Recommend songs those neighbors loved that you haven't heard yet

**Two variants:**

- **User-based CF:** Find users similar to you, borrow their taste
- **Item-based CF:** Find songs similar to songs you've played (based on who else played them), not on audio features

**Matrix Factorization (modern version):**

Spotify and Netflix popularized this. Instead of raw similarity, decompose the matrix into latent factors (hidden dimensions that might loosely correspond to "mood", "energy", "decade") using techniques like **Alternating Least Squares (ALS)** or **SVD**.

**Strengths:**

- Discovers non-obvious connections (e.g., jazz fans who also like certain electronic artists)
- No domain knowledge about music required

**Weaknesses:**

- **Cold start problem:** New songs or new users have no history → nothing to recommend
- Popularity bias: obscure tracks rarely get recommended

---

### 2. Content-Based Filtering — "Because you liked X which sounds like Y..."

**Core idea:** Analyze the *actual attributes* of songs and match them to your taste profile.

**Audio features used (Spotify's known feature set):**

| Feature | Description |
| --- | --- |
| `acousticness` | 0–1 confidence it's acoustic |
| `danceability` | Rhythm regularity, beat strength |
| `energy` | Perceptual intensity and activity |
| `valence` | Musical positiveness (happy vs. sad) |
| `tempo` | BPM |
| `speechiness` | Presence of spoken words |
| `key` / `mode` | Musical key and major/minor |

These are extracted via **audio signal processing** (MFCCs, chroma features, spectral analysis).

**How it works:**

1. Build a feature vector for each song
2. Build a user taste profile = weighted average of feature vectors from their history
3. Recommend songs whose vectors are closest (cosine similarity, KNN)

**Strengths:**

- No cold start for new songs — just analyze the audio
- Explainable ("recommended because it's high-energy and acoustic")
- Doesn't depend on other users

**Weaknesses:**

- "Filter bubble": keeps recommending similar-sounding music, hard to discover genuinely new styles
- Misses cultural/contextual meaning (a cover and original may have similar audio but very different audiences)

---

## What Platforms Actually Do: Hybrid Systems

No major platform uses just one method.

### Spotify's Approach (documented via research papers)

1. **Collaborative filtering** via matrix factorization on play/skip/save events
2. **NLP on text** — scrapes blogs, reviews, playlist names; uses word2vec-style embeddings on song co-occurrence in playlists (this is how obscure tracks get surfaced)
3. **Audio CNNs** — deep learning on raw audio spectrograms for cold-start new tracks
4. **Contextual signals** — time of day, device, recently played, search history

Spotify's **Discover Weekly** specifically uses a two-stage pipeline: CF generates candidates → audio/NLP models re-rank them.

### YouTube's Approach

Uses **deep neural networks** with two towers:

- **Candidate generation:** Wide recall using watch history embeddings
- **Ranking:** Narrow scoring using dense features (video age, user's watch time on similar content, CTR prediction)

Optimizes for **watch time**, not just clicks — which has known side effects (engagement optimization).

---

## Key Tradeoff Summary

| | Collaborative Filtering | Content-Based |
| --- | --- | --- |
| Data needed | User behavior | Song attributes |
| Cold start | Problem | Handled |
| Discovery | High (serendipitous) | Low (filter bubble) |
| Explainability | Low | High |
| Scalability | Expensive (large matrix) | Cheaper |

---

## Relevance to This Project

If this music recommender simulation uses song attributes and user profiles, it's likely implementing a **content-based** approach. Collaborative filtering requires a large user base to be meaningful, making content-based the natural fit for a simulation or starter project.

---

## Main Data Types in Recommendation Systems

### User Behavior Data (Implicit & Explicit Signals)

| Data Type | Kind | Description |
| --- | --- | --- |
| **Like / thumbs up** | Explicit | Direct positive signal; high confidence |
| **Dislike / thumbs down** | Explicit | Direct negative signal; strong filter |
| **Skip** | Implicit | User lost interest; partial play treated as weak negative |
| **Play count** | Implicit | Repeated listens = strong positive signal |
| **Play completion %** | Implicit | 90% completion ≠ same as 20% completion |
| **Save / add to library** | Explicit | Stronger than a like; intent to revisit |
| **Playlist add** | Explicit | Contextual signal (e.g., added to "workout" playlist) |
| **Share** | Explicit | Strongest endorsement; user is broadcasting taste |
| **Search query** | Implicit | Reveals intent and mood in the moment |
| **Session context** | Implicit | Time of day, device type, active vs. passive listening |

---

### Song / Track Attributes (Audio Features)

| Data Type | Value Type | Description |
| --- | --- | --- |
| **Tempo** | Float (BPM) | Speed of the track; e.g., 120 BPM |
| **Energy** | Float 0–1 | Intensity and activity level |
| **Danceability** | Float 0–1 | How suitable for dancing (rhythm, beat stability) |
| **Valence** | Float 0–1 | Emotional positivity; 1 = happy, 0 = sad/tense |
| **Acousticness** | Float 0–1 | Confidence the track is acoustic (not electronic) |
| **Instrumentalness** | Float 0–1 | Probability of no vocals |
| **Speechiness** | Float 0–1 | Presence of spoken words (podcasts score high) |
| **Loudness** | Float (dB) | Average loudness; typically −60 to 0 dB |
| **Key** | Integer 0–11 | Pitch class (0 = C, 1 = C#, etc.) |
| **Mode** | Binary 0/1 | 0 = minor, 1 = major |
| **Duration** | Integer (ms) | Track length |
| **Mood** | Categorical/Float | Derived label: calm, energetic, melancholic, happy, etc. |

---

### Metadata & Taxonomy

| Data Type | Description |
| --- | --- |
| **Genre** | Hierarchical label (e.g., Rock > Alternative > Indie) |
| **Subgenre / microgenre** | Spotify has 6,000+ microgenres (e.g., "vapor twitch") |
| **Artist** | Entity with its own genre tags, follower graph, and similarity scores |
| **Album** | Groups tracks; era and style context |
| **Release year** | Signals era; users often have decade-based nostalgia patterns |
| **Language** | Affects audience segmentation globally |
| **Lyrics** | NLP source for theme, sentiment, and topic modeling |
| **Tags / crowd labels** | User-generated or editorially applied descriptors |

---

### Playlist & Collection Data

| Data Type | Description |
| --- | --- |
| **Playlist** | Ordered or unordered set of tracks; reveals thematic intent |
| **Playlist name** | NLP signal — "focus", "gym", "rainy day" carry strong context |
| **Track co-occurrence** | Two songs in the same playlist = weak similarity signal |
| **Listening queue** | What the user chose to play next; strong sequential signal |
| **Radio seeds** | Song or artist used to start a radio session |

---

### User Profile Data

| Data Type | Description |
| --- | --- |
| **Taste vector** | Weighted average of audio features across listening history |
| **Preferred genres** | Aggregated from play history and explicit follows |
| **Followed artists** | Direct interest graph |
| **Listening history** | Time-stamped sequence of tracks; enables temporal modeling |
| **Demographic / location** | Optional; used for regional trend boosting |
| **Social graph** | Friends' listening activity (used lightly by Spotify) |

---

### How These Data Types Map to Filtering Methods

| Data Type Category | Used In |
| --- | --- |
| Likes, skips, play counts | Collaborative Filtering |
| Playlists, co-occurrence | Collaborative Filtering (item-based) |
| Tempo, energy, mood, key | Content-Based Filtering |
| Genre, tags, lyrics | Content-Based Filtering |
| Session context, time of day | Contextual / Hybrid models |
| User taste vector | Both |
