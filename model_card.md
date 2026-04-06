# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

VibeFinder 1.0

---

## 2. Intended Use

This system suggests 5 songs from a small catalog based on a user's preferred genre, mood, and audio features like energy and tempo.

It is built for classroom exploration, not real users. It assumes every user can be described by a single fixed taste profile. It does not learn or update over time.

---

## 3. How the Model Works

Each song gets a score between 0 and 1. Higher score means better match.

The score is based on six features: energy, tempo, valence (happy vs. sad tone), acousticness, mood, and genre. For numeric features, the score rewards closeness — a song with energy 0.42 scores higher for a user who wants 0.40 than a song with energy 0.80. For mood, the system uses a partial-match table — "relaxed" is treated as close to "chill" but not identical. For genre, it is a simple yes or no match.

Each feature has a weight that controls how much it matters. Energy carries the most weight (0.25), followed by mood and tempo (0.20 each). Genre has the least weight (0.10). The final score is the weighted sum of all six feature scores.

Songs are then sorted from highest to lowest score, and the top 5 are returned.

---

## 4. Data

The catalog has 20 songs stored in `data/songs.csv`. Each song has a title, artist, genre, mood, and five numeric audio features: energy, tempo, valence, danceability, and acousticness.

17 different genres are represented, including lofi, pop, rock, jazz, EDM, hip-hop, folk, and classical. 16 different moods are represented, including chill, happy, intense, relaxed, focused, and melancholic.

No songs were removed. The catalog is small and skewed: lofi has 3 songs, pop has 2, and every other genre has exactly 1. High-energy songs (above 0.7) make up 8 of the 20 tracks, so the dataset leans energetic.

Parts of musical taste that are missing: no lyrics, no era or decade, no language, no tempo ranges for genres like jazz or classical that vary widely. The catalog also has no collaborative data — there are no play counts, skips, or listener history.

---

## 5. Strengths

The system works best when the user's preferences match a well-represented part of the catalog.

For a Chill Lofi listener, the top 3 results were all lofi tracks with matching or adjacent moods. The scores were high (0.89–0.98) and the picks felt natural. For a High-Energy Pop listener, the top result (*Sunrise City*) was a near-perfect match with an exact genre and mood hit. For a Deep Intense Rock listener, *Storm Runner* scored 0.99 — all six features aligned closely.

The partial mood matching also works well in some cases. A user who prefers "chill" still receives credit for songs tagged "relaxed" or "focused," which widens the result set in a reasonable way.

The system is also easy to understand. Every recommendation comes with a plain-language reason for each feature, so users can see exactly why a song was or was not recommended.

---

## 6. Limitations and Bias

**Mood orphan bias: 7 out of 16 catalog moods are permanently shut out of partial credit.**

The scoring formula uses a hand-built mood proximity table to give partial scores when a song's mood is adjacent to the user's preferred mood — for example, "relaxed" scores 0.7 against a "chill" preference instead of a hard zero. However, 7 moods present in the catalog — `dreamy`, `groovy`, `melancholic`, `nostalgic`, `romantic`, `soulful`, and `uplifting` — have no entries in that table at all. Any song carrying one of these moods scores exactly 0 on the mood feature for every user except the one who asks for that exact mood, creating a structural deficit of up to 0.20 points that numeric features alone cannot overcome. In testing, songs like *Fuego Lento* (dreamy) and *Dusty Road Home* (nostalgic) almost never appeared in any top-5 list regardless of how well they matched the user's energy or tempo targets. This means the system quietly ignores an entire emotional dimension of the catalog — a user who enjoys melancholic or romantic music will see it surface only when they state it exactly, and even then competing songs with "chill" or "happy" moods benefit from partial-match pathways that these moods do not. A fairer system would either extend the proximity table to cover all catalog moods, or replace the static table with a continuous embedding that captures mood similarity automatically.

Other known limitations:

- **Energy dominates.** Energy and tempo together make up 45% of the score. A song that matches energy and tempo well will rank high even if the mood and genre are wrong.
- **Genre is almost a tiebreaker.** At 0.10 weight, genre rarely decides the outcome. Only lofi and pop have more than one song, so genre matching is partly luck of catalog coverage.
- **Filter bubble.** Only 16 of 20 songs ever appeared in any top-5 list across all profiles. Three songs appeared 4 times each. The system keeps recommending the same cluster of catalog songs.
- **Static profile.** The user's taste is fixed at runtime. If a user's mood shifts mid-session, the recommendations do not change.

---

## 7. Evaluation

The system was evaluated by running 8 user profiles against the full 20-song catalog and inspecting the top-5 results for each, then repeating the experiment after a weight shift (energy doubled from 0.25 → 0.50, genre halved from 0.10 → 0.05).

### Profiles tested

Three normal profiles covered the expected use cases: *Chill Lofi* (lofi/chill, low energy), *High-Energy Pop* (pop/happy, high energy), and *Deep Intense Rock* (rock/intense, maximum energy and tempo). Five adversarial profiles were designed to stress-test specific failure modes: *Conflicting Energy + Mood* (high energy but chill mood), *All Midpoint* (every numeric target at 0.5), *Unknown Genre and Mood* (genre and mood absent from the catalog), *All Zeros* (all targets at minimum), and *All Ones* (all targets at maximum).

### What was checked

For each profile, the top-5 results were compared against musical intuition — would a real listener find these recommendations appropriate? Song frequency across all profiles was also counted to detect overrepresentation. The weight-shift experiment compared rankings before and after to measure how sensitive the system is to a single parameter change.

### What the results showed

The three normal profiles produced intuitively correct results: *Midnight Coding* and *Library Rain* dominated the Chill Lofi list; *Sunrise City* led High-Energy Pop with a near-perfect score of 0.98; *Storm Runner* scored 0.99 for Deep Intense Rock. However, a repeat-appearance count revealed that only 16 of 20 songs ever appeared in any top-5 list, and three songs — *Neon Rave*, *Gym Hero*, and *Midnight Coding* — each appeared 4 times across 8 profiles, indicating a filter bubble concentrated around catalog songs near the mean feature values.

### What surprised us

The Conflicting Energy + Mood profile was the most revealing. A user requesting high energy (0.9) but a chill mood received *Storm Runner* (hard rock, intense) as the top result — the opposite of what a real listener would want. The mood weight at 0.20 was not strong enough to override the 0.45 combined energy+tempo signal. This conflict became worse after the weight shift, with Storm Runner's lead growing from 0.74 to 0.81. The weight-shift experiment also showed that the top-2 results were identical across all 8 profiles before and after the change, confirming that the songs closest to multiple feature targets are entrenched at the top regardless of weight tuning.

---

## 8. Future Work

- **Fix the mood table.** Add proximity entries for the 7 orphaned moods so every song can earn partial mood credit.
- **Add diversity.** Right now the top 5 can be nearly identical songs. A diversity rule that penalizes showing two songs with the same genre back-to-back would help.
- **Use listening history.** The current system ignores what the user has already heard. A real recommender would avoid repeating recent songs.
- **Try Gaussian similarity instead of absolute difference.** The current formula penalizes a 0.3 gap the same whether the song is close or far. A smoother curve would be more forgiving of near-matches.
- **Grow the catalog.** With only 20 songs, many genres have just one representative. A larger and more balanced dataset would reduce the filter bubble significantly.
- **Support session context.** Let the user's mood shift over time. A user who starts with chill and switches to intense should get different recommendations mid-session.

---

## 9. Personal Reflection

Building this made it clear that a recommender is only as good as what it measures. The formula looks mathematical and precise, but it reflects choices — which features to include, how much each one matters, and which moods count as "similar." Those choices have real effects on which songs get surfaced and which ones disappear.

The most surprising result was the Conflicting Energy + Mood test. It showed that the system does not really understand listener intent — it just finds numeric proximity. A real person who wants high-energy but chill music is describing a vibe, not a math problem. The formula cannot tell the difference.

This changed how I think about apps like Spotify. When a recommendation feels slightly off — technically close but wrong in feel — it is probably the same issue at a much larger scale. The model found the right numbers but missed the point. Fixing that gap between "close in features" and "right for the moment" is probably one of the hardest problems in real recommender systems.
