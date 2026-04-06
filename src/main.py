"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 
    print(f"Loaded {len(songs)} songs from the dataset.")

    # Taste profile: a chill/focused lofi listener
    user_prefs = {
        "favorite_genre":     "lofi",
        "favorite_mood":      "chill",
        "target_energy":      0.40,
        "target_tempo":       0.20,   # normalized: (78 - 60) / (152 - 60) ≈ 0.20
        "target_valence":     0.60,
        "target_danceability": 0.58,
        "target_acousticness": 0.75,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 50)
    print("  Top Recommendations")
    print("=" * 50)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  —  {song['artist']}")
        print(f"     Score : {score:.2f}  |  Genre: {song['genre']}  |  Mood: {song['mood']}")
        print("     Why   :")
        for reason in explanation.split("; "):
            print(f"       • {reason}")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
