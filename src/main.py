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
    "acoustic_preference": 0.1,
}

CHILL_LOFI = {
    "genre": "lofi",
    "mood": "chill",
    "genres": ["lofi", "ambient"],
    "moods": ["chill", "focused", "peaceful"],
    "energy": 0.35,
    "acoustic_preference": 0.9,
}

DEEP_INTENSE_ROCK = {
    "genre": "rock",
    "mood": "intense",
    "genres": ["rock", "metal", "hip hop"],
    "moods": ["intense", "aggressive", "confident"],
    "energy": 0.90,
    "acoustic_preference": 0.05,
}

# Edge case / adversarial profiles designed to stress-test the scoring logic.

CONFLICTING_VIBE = {
    "genre": "blues",
    "mood": "melancholic",
    "genres": ["blues", "jazz"],
    "moods": ["melancholic", "moody"],
    "energy": 0.90,  # Very high energy but melancholic mood—direct conflict
    "acoustic_preference": 0.9,
}

ULTRA_CHILL = {
    "genre": "ambient",
    "mood": "peaceful",
    "genres": ["ambient", "classical"],
    "moods": ["peaceful", "relaxed"],
    "energy": 0.10,  # Extremely low energy boundary
    "acoustic_preference": 0.95,
}

PURE_ADRENALINE = {
    "genre": "edm",
    "mood": "euphoric",
    "genres": ["edm", "metal", "rock"],
    "moods": ["euphoric", "aggressive"],
    "energy": 0.98,  # Extremely high energy boundary
    "acoustic_preference": 0.0,
}

ACOUSTIC_ROCKER = {
    "genre": "rock",
    "mood": "intense",
    "genres": ["rock", "metal"],
    "moods": ["intense", "aggressive"],
    "energy": 0.85,
    "acoustic_preference": 0.8,  # Unusual: rock fans rarely want acoustic
}

EVERYTHING_GOES = {
    "genre": "pop",
    "mood": "happy",
    "genres": ["pop", "rock", "lofi", "jazz", "edm", "classical"],  # No clear hierarchy
    "moods": ["happy", "intense", "chill", "moody", "peaceful"],
    "energy": 0.50,  # Middle ground
    "acoustic_preference": 0.4,
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
