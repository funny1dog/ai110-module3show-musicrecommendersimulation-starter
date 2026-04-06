"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs, SCORING_MODES


USERS = {
    "Chill Lofi": {
        "favorite_genre":          "lofi",
        "favorite_mood":           "chill",
        "target_energy":           0.40,
        "target_tempo":            0.20,   # (78 bpm - 60) / 92 ≈ 0.20
        "target_valence":          0.60,
        "target_danceability":     0.58,
        "target_acousticness":     0.75,
        "target_popularity":       0.40,   # prefers underground / niche
        "favorite_decade":         "2020s",
        "target_liveness":         0.10,   # prefers studio-polished
        "target_instrumentalness": 0.80,   # mostly instrumental
        "target_loudness":         0.40,   # quiet
    },
    "High-Energy Pop": {
        "favorite_genre":          "pop",
        "favorite_mood":           "happy",
        "target_energy":           0.85,
        "target_tempo":            0.63,   # (118 bpm - 60) / 92 ≈ 0.63
        "target_valence":          0.88,
        "target_danceability":     0.80,
        "target_acousticness":     0.15,
        "target_popularity":       0.80,   # prefers mainstream hits
        "favorite_decade":         "2020s",
        "target_liveness":         0.10,   # studio polished
        "target_instrumentalness": 0.05,   # wants vocals
        "target_loudness":         0.85,   # loud and punchy
    },
    "Deep Intense Rock": {
        "favorite_genre":          "rock",
        "favorite_mood":           "intense",
        "target_energy":           0.92,
        "target_tempo":            1.00,   # (152 bpm - 60) / 92 = 1.00
        "target_valence":          0.40,
        "target_danceability":     0.60,
        "target_acousticness":     0.10,
        "target_popularity":       0.55,   # mid-tier popularity
        "favorite_decade":         "2010s",
        "target_liveness":         0.20,   # slight live energy is fine
        "target_instrumentalness": 0.10,   # prefers vocals / lyrics
        "target_loudness":         0.90,   # very loud
    },

    # --- Adversarial / edge-case profiles ---

    # Conflicting signal: numeric features push toward high-energy rock,
    # but mood targets the opposite end of the spectrum.
    "Conflicting Energy + Mood": {
        "favorite_genre":          "rock",
        "favorite_mood":           "chill",
        "target_energy":           0.90,
        "target_tempo":            0.90,
        "target_valence":          0.20,
        "target_danceability":     0.65,
        "target_acousticness":     0.10,
        "target_popularity":       0.50,
        "favorite_decade":         "2010s",
        "target_liveness":         0.15,
        "target_instrumentalness": 0.10,
        "target_loudness":         0.85,
    },

    # All numeric targets at the midpoint.
    "All Midpoint": {
        "favorite_genre":          "pop",
        "favorite_mood":           "happy",
        "target_energy":           0.50,
        "target_tempo":            0.50,
        "target_valence":          0.50,
        "target_danceability":     0.50,
        "target_acousticness":     0.50,
        "target_popularity":       0.50,
        "favorite_decade":         "2010s",
        "target_liveness":         0.50,
        "target_instrumentalness": 0.50,
        "target_loudness":         0.50,
    },

    # Genre and mood absent from catalog; falls back on numeric features.
    "Unknown Genre and Mood": {
        "favorite_genre":          "classical",
        "favorite_mood":           "peaceful",
        "target_energy":           0.30,
        "target_tempo":            0.15,
        "target_valence":          0.70,
        "target_danceability":     0.40,
        "target_acousticness":     0.80,
        "target_popularity":       0.25,   # obscure / niche
        "favorite_decade":         "2000s",
        "target_liveness":         0.35,
        "target_instrumentalness": 0.85,
        "target_loudness":         0.20,
    },

    # Every target at 0.0
    "All Zeros": {
        "favorite_genre":          "ambient",
        "favorite_mood":           "chill",
        "target_energy":           0.0,
        "target_tempo":            0.0,
        "target_valence":          0.0,
        "target_danceability":     0.0,
        "target_acousticness":     0.0,
        "target_popularity":       0.0,
        "favorite_decade":         "1980s",
        "target_liveness":         0.0,
        "target_instrumentalness": 0.0,
        "target_loudness":         0.0,
    },

    # Every target at 1.0
    "All Ones": {
        "favorite_genre":          "rock",
        "favorite_mood":           "intense",
        "target_energy":           1.0,
        "target_tempo":            1.0,
        "target_valence":          1.0,
        "target_danceability":     1.0,
        "target_acousticness":     1.0,
        "target_popularity":       1.0,
        "favorite_decade":         "2020s",
        "target_liveness":         1.0,
        "target_instrumentalness": 1.0,
        "target_loudness":         1.0,
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

    # --- Standard profiles across all scoring modes ---
    for label, user_prefs in USERS.items():
        for mode in SCORING_MODES:
            recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)
            print_recommendations(f"{label}  [{mode}]", recommendations)


if __name__ == "__main__":
    main()
