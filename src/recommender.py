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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str       # categorical — exact or partial match against song genre
    favorite_mood: str        # categorical — exact or partial match against song mood
    target_energy: float      # 0.0–1.0 proximity target
    target_tempo: float       # normalized 0.0–1.0, i.e. (bpm - 60) / (152 - 60)
    target_valence: float     # 0.0–1.0 proximity target
    target_danceability: float  # 0.0–1.0 proximity target
    target_acousticness: float  # 0.0–1.0 proximity target

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
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

# Weight shift experiment: energy doubled (0.25→0.50), genre halved (0.10→0.05).
# Remaining four weights scaled proportionally so sum stays 1.0.
# Original → New: mood 0.20→0.14, tempo 0.20→0.14, valence 0.15→0.10, acousticness 0.10→0.07
_WEIGHTS = {
    "target_energy":       0.50,   # was 0.25
    "favorite_mood":       0.14,   # was 0.20
    "target_tempo":        0.14,   # was 0.20
    "target_valence":      0.10,   # was 0.15
    "target_acousticness": 0.07,   # was 0.10
    "favorite_genre":      0.05,   # was 0.10
}

# Partial mood-similarity table (symmetric).  Missing pairs default to 0.0
# (exact match returns 1.0, handled separately).
_MOOD_PROXIMITY: Dict[Tuple[str, str], float] = {
    ("chill",    "relaxed"):  0.7,
    ("chill",    "focused"):  0.5,
    ("chill",    "peaceful"): 0.6,
    ("chill",    "moody"):    0.3,
    ("chill",    "happy"):    0.2,
    ("chill",    "intense"):  0.0,
    ("relaxed",  "focused"):  0.6,
    ("relaxed",  "peaceful"): 0.8,
    ("relaxed",  "moody"):    0.4,
    ("relaxed",  "happy"):    0.3,
    ("focused",  "moody"):    0.3,
    ("happy",    "euphoric"): 0.7,
    ("happy",    "energetic"):0.5,
    ("intense",  "aggressive"):0.7,
    ("intense",  "energetic"):0.6,
}

def _mood_score(user_mood: str, song_mood: str) -> float:
    """Return a [0, 1] similarity between two mood labels."""
    if user_mood == song_mood:
        return 1.0
    pair = (user_mood, song_mood)
    rev  = (song_mood, user_mood)
    return _MOOD_PROXIMITY.get(pair, _MOOD_PROXIMITY.get(rev, 0.0))

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """Return a weighted similarity score and human-readable explanation for one song."""
    reasons = []

    # STEP 1 — normalize tempo
    tempo_norm = (song["tempo_bpm"] - 60) / (152 - 60)

    # STEP 2 — numeric feature scores
    numeric = {
        "target_energy":       abs(song["energy"]      - user_prefs["target_energy"]),
        "target_tempo":        abs(tempo_norm           - user_prefs["target_tempo"]),
        "target_valence":      abs(song["valence"]      - user_prefs["target_valence"]),
        "target_acousticness": abs(song["acousticness"] - user_prefs["target_acousticness"]),
    }
    score = 0.0
    for feature, diff in numeric.items():
        feature_score = 1 - diff
        score += _WEIGHTS[feature] * feature_score
        label = feature.replace("target_", "")
        if diff <= 0.1:
            reasons.append(f"{label} closely matches (diff={diff:.2f})")
        elif diff >= 0.4:
            reasons.append(f"{label} is far off (diff={diff:.2f})")

    # STEP 3 — mood (partial match)
    mood_sim = _mood_score(user_prefs["favorite_mood"], song["mood"])
    score += _WEIGHTS["favorite_mood"] * mood_sim
    if mood_sim == 1.0:
        reasons.append(f"mood is an exact match ({song['mood']})")
    elif mood_sim > 0.0:
        reasons.append(f"mood is a partial match ({song['mood']} ~ {user_prefs['favorite_mood']}, sim={mood_sim})")
    else:
        reasons.append(f"mood does not match ({song['mood']} vs {user_prefs['favorite_mood']})")

    # STEP 4 — genre (exact match)
    if song["genre"] == user_prefs["favorite_genre"]:
        score += _WEIGHTS["favorite_genre"]
        reasons.append(f"genre matches ({song['genre']})")
    else:
        reasons.append(f"genre does not match ({song['genre']} vs {user_prefs['favorite_genre']})")

    explanation = "; ".join(reasons)
    return score, explanation

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return the top-k as (song, score, explanation) tuples."""
    scored = sorted(
        ((song, *score_song(user_prefs, song)) for song in songs),
        key=lambda item: item[1],
        reverse=True,
    )
    return [(song, score, explanation) for song, score, explanation in scored[:k]]
