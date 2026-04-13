"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# Specific taste profile used for recommendation comparisons.
TASTE_PROFILE = {
    "genre": "pop",
    "mood": "happy",
    "genres": ["pop"],
    "moods": ["happy"],
    "energy": 0.75,
    "likes_acoustic": False,
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    recommendations = recommend_songs(TASTE_PROFILE, songs, k=5)

    divider = "-" * 45
    print(f"\n{'Top Recommendations':^45}")
    print(divider)
    for i, rec in enumerate(recommendations, start=1):
        song, score, _, reasons = rec
        print(f" #{i}  {song['title']:<30} {score:.2f} / 5.00")
        for reason in reasons:
            print(f"      * {reason}")
        print(divider)


if __name__ == "__main__":
    main()
