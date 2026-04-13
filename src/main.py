"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# User preference dictionaries representing distinct taste archetypes.

HIGH_ENERGY_POP = {
    "genre": "pop",
    "mood": "happy",
    "genres": ["pop", "funk", "indie pop"],
    "moods": ["happy", "playful", "confident"],
    "energy": 0.80,
    "likes_acoustic": False,
}

CHILL_LOFI = {
    "genre": "lofi",
    "mood": "chill",
    "genres": ["lofi", "ambient"],
    "moods": ["chill", "focused", "peaceful"],
    "energy": 0.35,
    "likes_acoustic": True,
}

DEEP_INTENSE_ROCK = {
    "genre": "rock",
    "mood": "intense",
    "genres": ["rock", "metal", "hip hop"],
    "moods": ["intense", "aggressive", "confident"],
    "energy": 0.90,
    "likes_acoustic": False,
}

# Edge case / adversarial profiles designed to stress-test the scoring logic.

CONFLICTING_VIBE = {
    "genre": "blues",
    "mood": "melancholic",
    "genres": ["blues", "jazz"],
    "moods": ["melancholic", "moody"],
    "energy": 0.90,  # Very high energy but melancholic mood—direct conflict
    "likes_acoustic": True,
}

ULTRA_CHILL = {
    "genre": "ambient",
    "mood": "peaceful",
    "genres": ["ambient", "classical"],
    "moods": ["peaceful", "relaxed"],
    "energy": 0.10,  # Extremely low energy boundary
    "likes_acoustic": True,
}

PURE_ADRENALINE = {
    "genre": "edm",
    "mood": "euphoric",
    "genres": ["edm", "metal", "rock"],
    "moods": ["euphoric", "aggressive"],
    "energy": 0.98,  # Extremely high energy boundary
    "likes_acoustic": False,
}

ACOUSTIC_ROCKER = {
    "genre": "rock",
    "mood": "intense",
    "genres": ["rock", "metal"],
    "moods": ["intense", "aggressive"],
    "energy": 0.85,
    "likes_acoustic": True,  # Unusual: rock fans rarely want acoustic
}

EVERYTHING_GOES = {
    "genre": "pop",
    "mood": "happy",
    "genres": ["pop", "rock", "lofi", "jazz", "edm", "classical"],  # No clear hierarchy
    "moods": ["happy", "intense", "chill", "moody", "peaceful"],
    "energy": 0.50,  # Middle ground
    "likes_acoustic": False,
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs from catalog\n")

    for profile_name, profile in [
        ("High-Energy Pop", HIGH_ENERGY_POP),
        ("Chill Lofi", CHILL_LOFI),
        ("Deep Intense Rock", DEEP_INTENSE_ROCK),
        ("Conflicting Vibe (High Energy + Sad)", CONFLICTING_VIBE),
        ("Ultra Chill (Energy: 0.10)", ULTRA_CHILL),
        ("Pure Adrenaline (Energy: 0.98)", PURE_ADRENALINE),
        ("Acoustic Rocker (Unusual Combo)", ACOUSTIC_ROCKER),
        ("Everything Goes (No Clear Hierarchy)", EVERYTHING_GOES),
    ]:
        recommendations = recommend_songs(profile, songs, k=5)

        divider = "-" * 60
        print(f"\n{profile_name:^60}")
        print(divider)
        for i, rec in enumerate(recommendations, start=1):
            song, score, explanation, reasons = rec
            print(f" #{i}  {song['title']:<35} Score: {score:.2f}")
            print(f"      → {explanation}")
            print(divider)


if __name__ == "__main__":
    main()
