from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int
    release_decade: str
    liveness: float
    instrumentalness: float
    loudness_norm: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str           # exact match against song genre
    favorite_mood: str            # partial match via _MOOD_PROXIMITY table
    target_energy: float          # 0.0–1.0 proximity target
    target_tempo: float           # normalized 0.0–1.0, i.e. (bpm - 60) / (152 - 60)
    target_valence: float         # 0.0–1.0 proximity target
    target_danceability: float    # 0.0–1.0 proximity target
    target_acousticness: float    # 0.0–1.0 proximity target
    target_popularity: float      # 0.0–1.0 (popularity / 100)
    favorite_decade: str          # partial match via _DECADE_PROXIMITY table
    target_liveness: float        # 0.0–1.0 proximity target
    target_instrumentalness: float  # 0.0–1.0 proximity target
    target_loudness: float        # 0.0–1.0 proximity target

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the song catalog for later scoring and ranking."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs best matching the user's taste profile."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Describe why a specific song was recommended to this user."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return each row as a typed dictionary."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "popularity":       int(row["popularity"]),
                "release_decade":   row["release_decade"],
                "liveness":         float(row["liveness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "loudness_norm":    float(row["loudness_norm"]),
            })
    return songs

# ---------------------------------------------------------------------------
# Scoring modes — each is a complete weight dict that sums to 1.0.
# Pass the mode name to score_song() / recommend_songs() to switch strategy.
# ---------------------------------------------------------------------------
SCORING_MODES: Dict[str, Dict[str, float]] = {

    # All 11 features weighted proportionally. Good general-purpose default.
    "balanced": {
        "target_energy":           0.20,
        "favorite_mood":           0.15,
        "target_tempo":            0.12,
        "target_valence":          0.10,
        "target_acousticness":     0.08,
        "favorite_genre":          0.08,
        "target_popularity":       0.08,
        "favorite_decade":         0.07,
        "target_liveness":         0.06,
        "target_instrumentalness": 0.04,
        "target_loudness":         0.02,
    },

    # Genre and era dominate. Finds songs that fit the user's preferred
    # stylistic box first, then breaks ties with audio features.
    "genre_first": {
        "favorite_genre":          0.30,
        "favorite_decade":         0.15,
        "favorite_mood":           0.15,
        "target_energy":           0.10,
        "target_tempo":            0.08,
        "target_valence":          0.07,
        "target_acousticness":     0.05,
        "target_popularity":       0.04,
        "target_liveness":         0.03,
        "target_instrumentalness": 0.02,
        "target_loudness":         0.01,
    },

    # Mood carries more than a third of the total score. Surfaces songs
    # that match the user's emotional state even across genres.
    "mood_first": {
        "favorite_mood":           0.35,
        "target_energy":           0.15,
        "target_valence":          0.12,
        "favorite_genre":          0.10,
        "target_tempo":            0.08,
        "target_acousticness":     0.07,
        "target_popularity":       0.05,
        "favorite_decade":         0.04,
        "target_liveness":         0.02,
        "target_instrumentalness": 0.01,
        "target_loudness":         0.01,
    },

    # Energy and tempo together hold 65% of the score. Loudness adds another
    # 10%. Best for activity-based contexts like workouts or study sessions.
    "energy_focused": {
        "target_energy":           0.40,
        "target_tempo":            0.25,
        "target_loudness":         0.10,
        "favorite_mood":           0.08,
        "target_valence":          0.05,
        "target_acousticness":     0.04,
        "favorite_genre":          0.03,
        "target_popularity":       0.02,
        "favorite_decade":         0.01,
        "target_liveness":         0.01,
        "target_instrumentalness": 0.01,
    },
}

# Partial mood-similarity table (symmetric). Missing pairs default to 0.0.
# Exact match returns 1.0, handled separately in _mood_score.
_MOOD_PROXIMITY: Dict[Tuple[str, str], float] = {
    ("chill",     "relaxed"):   0.7,
    ("chill",     "focused"):   0.5,
    ("chill",     "peaceful"):  0.6,
    ("chill",     "moody"):     0.3,
    ("chill",     "happy"):     0.2,
    ("chill",     "intense"):   0.0,
    ("relaxed",   "focused"):   0.6,
    ("relaxed",   "peaceful"):  0.8,
    ("relaxed",   "moody"):     0.4,
    ("relaxed",   "happy"):     0.3,
    ("relaxed",   "nostalgic"): 0.5,
    ("relaxed",   "romantic"):  0.6,
    ("focused",   "moody"):     0.3,
    ("happy",     "euphoric"):  0.7,
    ("happy",     "uplifting"): 0.8,
    ("happy",     "groovy"):    0.6,
    ("happy",     "romantic"):  0.4,
    ("happy",     "dreamy"):    0.3,
    ("intense",   "aggressive"):0.7,
    ("intense",   "energetic"): 0.6,
    ("intense",   "groovy"):    0.3,
    ("peaceful",  "nostalgic"): 0.5,
    ("peaceful",  "dreamy"):    0.6,
    ("peaceful",  "romantic"):  0.5,
    ("moody",     "melancholic"):0.7,
    ("moody",     "nostalgic"): 0.5,
    ("moody",     "dreamy"):    0.4,
    ("soulful",   "nostalgic"): 0.6,
    ("soulful",   "melancholic"):0.5,
    ("soulful",   "romantic"):  0.4,
    ("dreamy",    "romantic"):  0.5,
    ("euphoric",  "uplifting"): 0.7,
    ("euphoric",  "groovy"):    0.5,
    ("uplifting", "groovy"):    0.6,
}

# Decade proximity: adjacent decades score 0.8, two apart 0.5, etc.
_DECADE_PROXIMITY: Dict[Tuple[str, str], float] = {
    ("2020s", "2010s"): 0.8,
    ("2020s", "2000s"): 0.5,
    ("2020s", "1990s"): 0.3,
    ("2020s", "1980s"): 0.1,
    ("2010s", "2000s"): 0.8,
    ("2010s", "1990s"): 0.5,
    ("2010s", "1980s"): 0.3,
    ("2000s", "1990s"): 0.8,
    ("2000s", "1980s"): 0.5,
    ("1990s", "1980s"): 0.8,
}

def _mood_score(user_mood: str, song_mood: str) -> float:
    """Return a [0, 1] similarity between two mood labels."""
    if user_mood == song_mood:
        return 1.0
    pair = (user_mood, song_mood)
    rev  = (song_mood, user_mood)
    return _MOOD_PROXIMITY.get(pair, _MOOD_PROXIMITY.get(rev, 0.0))

def _decade_score(user_decade: str, song_decade: str) -> float:
    """Return a [0, 1] similarity between two release decades."""
    if user_decade == song_decade:
        return 1.0
    pair = (user_decade, song_decade)
    rev  = (song_decade, user_decade)
    return _DECADE_PROXIMITY.get(pair, _DECADE_PROXIMITY.get(rev, 0.0))

def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, str]:
    """Return a weighted similarity score and human-readable explanation for one song."""
    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {list(SCORING_MODES)}")
    weights = SCORING_MODES[mode]

    reasons = []
    score = 0.0

    # --- Numeric proximity features ---
    # tempo_bpm normalized to [0, 1] before scoring
    tempo_norm = (song["tempo_bpm"] - 60) / (152 - 60)
    pop_norm   = song["popularity"] / 100.0

    numeric = {
        "target_energy":           (song["energy"],           user_prefs["target_energy"]),
        "target_tempo":            (tempo_norm,               user_prefs["target_tempo"]),
        "target_valence":          (song["valence"],          user_prefs["target_valence"]),
        "target_acousticness":     (song["acousticness"],     user_prefs["target_acousticness"]),
        "target_popularity":       (pop_norm,                 user_prefs["target_popularity"]),
        "target_liveness":         (song["liveness"],         user_prefs["target_liveness"]),
        "target_instrumentalness": (song["instrumentalness"], user_prefs["target_instrumentalness"]),
        "target_loudness":         (song["loudness_norm"],    user_prefs["target_loudness"]),
    }

    for feature, (song_val, user_val) in numeric.items():
        diff = abs(song_val - user_val)
        score += weights[feature] * (1 - diff)
        label = feature.replace("target_", "")
        if diff <= 0.1:
            reasons.append(f"{label} closely matches (diff={diff:.2f})")
        elif diff >= 0.4:
            reasons.append(f"{label} is far off (diff={diff:.2f})")

    # --- Mood (partial match) ---
    mood_sim = _mood_score(user_prefs["favorite_mood"], song["mood"])
    score += weights["favorite_mood"] * mood_sim
    if mood_sim == 1.0:
        reasons.append(f"mood is an exact match ({song['mood']})")
    elif mood_sim > 0.0:
        reasons.append(f"mood is a partial match ({song['mood']} ~ {user_prefs['favorite_mood']}, sim={mood_sim})")
    else:
        reasons.append(f"mood does not match ({song['mood']} vs {user_prefs['favorite_mood']})")

    # --- Genre (exact match) ---
    if song["genre"] == user_prefs["favorite_genre"]:
        score += weights["favorite_genre"]
        reasons.append(f"genre matches ({song['genre']})")
    else:
        reasons.append(f"genre does not match ({song['genre']} vs {user_prefs['favorite_genre']})")

    # --- Decade (partial match) ---
    decade_sim = _decade_score(user_prefs["favorite_decade"], song["release_decade"])
    score += weights["favorite_decade"] * decade_sim
    if decade_sim == 1.0:
        reasons.append(f"decade matches ({song['release_decade']})")
    elif decade_sim > 0.0:
        reasons.append(f"decade is close ({song['release_decade']} ~ {user_prefs['favorite_decade']}, sim={decade_sim})")
    else:
        reasons.append(f"decade is far off ({song['release_decade']} vs {user_prefs['favorite_decade']})")

    return score, "; ".join(reasons)

def rerank_with_diversity(
    scored: List[Tuple[Dict, float, str]],
    k: int = 5,
    artist_penalty: float = 0.5,
    genre_penalty: float = 0.7,
) -> List[Tuple[Dict, float, str]]:
    """Greedily pick k songs, penalising candidates that repeat an artist or genre.

    Already-selected artists incur artist_penalty (multiplier < 1.0) on a
    candidate's effective score.  Already-selected genres incur genre_penalty.
    Both penalties stack multiplicatively when a song matches on both dimensions.
    The original score stored in the returned tuple is unchanged — only the
    selection order is affected by the penalties.
    """
    selected: List[Tuple[Dict, float, str]] = []
    remaining = list(scored)

    while len(selected) < k and remaining:
        seen_artists = {s["artist"] for s, _, _ in selected}
        seen_genres  = {s["genre"]  for s, _, _ in selected}

        best_idx, best_effective = 0, -1.0
        for i, (song, score, explanation) in enumerate(remaining):
            effective = score
            if song["artist"] in seen_artists:
                effective *= artist_penalty
            if song["genre"] in seen_genres:
                effective *= genre_penalty
            if effective > best_effective:
                best_effective, best_idx = effective, i

        selected.append(remaining.pop(best_idx))

    return selected


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversity: bool = False,
    artist_penalty: float = 0.5,
    genre_penalty: float = 0.7,
) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return the top-k as (song, score, explanation) tuples.

    Set diversity=True to apply a re-ranking pass that penalises repeated
    artists (artist_penalty) and genres (genre_penalty) in the final list.
    """
    scored = sorted(
        ((song, *score_song(user_prefs, song, mode)) for song in songs),
        key=lambda item: item[1],
        reverse=True,
    )
    if diversity:
        return rerank_with_diversity(scored, k, artist_penalty, genre_penalty)
    return [(song, score, explanation) for song, score, explanation in scored[:k]]
