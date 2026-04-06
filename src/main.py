"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


USERS = {
    "Chill Lofi": {
        "favorite_genre":      "lofi",
        "favorite_mood":       "chill",
        "target_energy":       0.40,
        "target_tempo":        0.20,   # (78 bpm - 60) / 92 ≈ 0.20
        "target_valence":      0.60,
        "target_danceability": 0.58,
        "target_acousticness": 0.75,
    },
    "High-Energy Pop": {
        "favorite_genre":      "pop",
        "favorite_mood":       "happy",
        "target_energy":       0.85,
        "target_tempo":        0.63,   # (118 bpm - 60) / 92 ≈ 0.63
        "target_valence":      0.88,
        "target_danceability": 0.80,
        "target_acousticness": 0.15,
    },
    "Deep Intense Rock": {
        "favorite_genre":      "rock",
        "favorite_mood":       "intense",
        "target_energy":       0.92,
        "target_tempo":        1.00,   # (152 bpm - 60) / 92 = 1.00
        "target_valence":      0.40,
        "target_danceability": 0.60,
        "target_acousticness": 0.10,
    },

    # --- Adversarial / edge-case profiles ---

    # Conflicting signal: numeric features push toward high-energy rock,
    # but mood targets the opposite end of the spectrum.
    # Exposes whether the 0.20 mood weight can override numeric proximity.
    "Conflicting Energy + Mood": {
        "favorite_genre":      "rock",
        "favorite_mood":       "chill",
        "target_energy":       0.90,
        "target_tempo":        0.90,
        "target_valence":      0.20,
        "target_danceability": 0.65,
        "target_acousticness": 0.10,
    },

    # All numeric targets at the midpoint.
    # Every song is roughly equidistant; scores compress and top-k
    # is decided almost entirely by mood/genre exact matches.
    "All Midpoint": {
        "favorite_genre":      "pop",
        "favorite_mood":       "happy",
        "target_energy":       0.50,
        "target_tempo":        0.50,
        "target_valence":      0.50,
        "target_danceability": 0.50,
        "target_acousticness": 0.50,
    },

    # Genre and mood that don't exist in the catalog.
    # The 0.30 combined weight for mood + genre always scores 0;
    # ranking falls back entirely on numeric proximity.
    "Unknown Genre and Mood": {
        "favorite_genre":      "classical",
        "favorite_mood":       "peaceful",
        "target_energy":       0.30,
        "target_tempo":        0.15,
        "target_valence":      0.70,
        "target_danceability": 0.40,
        "target_acousticness": 0.80,
    },

    # Every target at 0.0 — checks whether any song is artificially
    # rewarded just for having uniformly low feature values.
    "All Zeros": {
        "favorite_genre":      "ambient",
        "favorite_mood":       "chill",
        "target_energy":       0.0,
        "target_tempo":        0.0,
        "target_valence":      0.0,
        "target_danceability": 0.0,
        "target_acousticness": 0.0,
    },

    # Every target at 1.0 — symmetric opposite of All Zeros;
    # verifies high-feature songs don't unfairly dominate.
    "All Ones": {
        "favorite_genre":      "rock",
        "favorite_mood":       "intense",
        "target_energy":       1.0,
        "target_tempo":        1.0,
        "target_valence":      1.0,
        "target_danceability": 1.0,
        "target_acousticness": 1.0,
    },
}


def print_recommendations(label: str, recommendations: list) -> None:
    """Print a labeled recommendation block to the terminal."""
    print("\n" + "=" * 50)
    print(f"  {label}")
    print("=" * 50)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  —  {song['artist']}")
        print(f"     Score : {score:.2f}  |  Genre: {song['genre']}  |  Mood: {song['mood']}")
        print("     Why   :")
        for reason in explanation.split("; "):
            print(f"       • {reason}")
    print("\n" + "=" * 50)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs from the dataset.")

    for label, user_prefs in USERS.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(f"Top Recommendations — {label}", recommendations)


if __name__ == "__main__":
    main()
