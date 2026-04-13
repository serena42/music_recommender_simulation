"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.
"""

import textwrap

from src.recommender import load_songs, recommend_songs


# User preference dictionaries representing distinct taste archetypes.

HIGH_ENERGY_POP = {
    "genre": "pop",
    "mood": "happy",
    "genres": ["pop", "funk", "indie pop"],
    "moods": ["happy", "playful", "confident"],
    "energy": 0.80,
    "energy_flexibility": 0.35,
    "acoustic_preference": 0.1,
    "target_danceability": 0.85,
    "target_valence": 0.85,
}

CHILL_LOFI = {
    "genre": "lofi",
    "mood": "chill",
    "genres": ["lofi", "ambient"],
    "moods": ["chill", "focused", "peaceful"],
    "energy": 0.35,
    "energy_flexibility": 0.7,
    "acoustic_preference": 0.9,
    "target_danceability": 0.45,
    "target_valence": 0.55,
}

DEEP_INTENSE_ROCK = {
    "genre": "rock",
    "mood": "intense",
    "genres": ["rock", "metal", "hip hop"],
    "moods": ["intense", "aggressive", "confident"],
    "energy": 0.90,
    "energy_flexibility": 0.2,
    "acoustic_preference": 0.05,
    "target_danceability": 0.55,
    "target_valence": 0.45,
}

# Edge case / adversarial profiles designed to stress-test the scoring logic.

CONFLICTING_VIBE = {
    "genre": "blues",
    "mood": "melancholic",
    "genres": ["blues", "jazz"],
    "moods": ["melancholic", "moody"],
    "energy": 0.90,  # Very high energy but melancholic mood—direct conflict
    "energy_flexibility": 0.85,
    "acoustic_preference": 0.9,
}

ULTRA_CHILL = {
    "genre": "ambient",
    "mood": "peaceful",
    "genres": ["ambient", "classical"],
    "moods": ["peaceful", "relaxed"],
    "energy": 0.10,  # Extremely low energy boundary
    "energy_flexibility": 0.25,
    "acoustic_preference": 0.95,
}

PURE_ADRENALINE = {
    "genre": "edm",
    "mood": "euphoric",
    "genres": ["edm", "metal", "rock"],
    "moods": ["euphoric", "aggressive"],
    "energy": 0.98,  # Extremely high energy boundary
    "energy_flexibility": 0.15,
    "acoustic_preference": 0.0,
    "target_danceability": 0.9,
    "target_valence": 0.9,
}

ACOUSTIC_ROCKER = {
    "genre": "rock",
    "mood": "intense",
    "genres": ["rock", "metal"],
    "moods": ["intense", "aggressive"],
    "energy": 0.85,
    "energy_flexibility": 0.5,
    "acoustic_preference": 0.8,  # Unusual: rock fans rarely want acoustic
}

EVERYTHING_GOES = {
    "genre": "pop",
    "mood": "happy",
    "genres": ["pop", "rock", "lofi", "jazz", "edm", "classical"],  # No clear hierarchy
    "moods": ["happy", "intense", "chill", "moody", "peaceful"],
    "energy": 0.50,  # Middle ground
    "energy_flexibility": 1.0,
    "acoustic_preference": 0.4,
    "target_danceability": 0.6,
    "target_valence": 0.6,
    "diversify": True,
    "artist_repeat_penalty": 0.35,
    "genre_repeat_penalty": 0.15,
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

        rank_w = 4
        title_w = 24
        score_w = 7
        reasons_w = 78

        def border() -> str:
            return (
                "+"
                + "-" * (rank_w + 2)
                + "+"
                + "-" * (title_w + 2)
                + "+"
                + "-" * (score_w + 2)
                + "+"
                + "-" * (reasons_w + 2)
                + "+"
            )

        print(f"\n{profile_name}")
        print(border())
        print(
            f"| {'#':<{rank_w}} | {'Song':<{title_w}} | {'Score':<{score_w}} | {'Reasons':<{reasons_w}} |"
        )
        print(border())

        for i, rec in enumerate(recommendations, start=1):
            song, score, _, reasons = rec
            reason_text = "; ".join(reasons) if reasons else "No strong factors"
            wrapped_reasons = textwrap.wrap(reason_text, width=reasons_w) or [""]

            first_line = wrapped_reasons[0]
            print(
                f"| {i:<{rank_w}} | {song['title']:<{title_w}} | {score:<{score_w}.2f} | {first_line:<{reasons_w}} |"
            )
            for continued in wrapped_reasons[1:]:
                print(
                    f"| {'':<{rank_w}} | {'':<{title_w}} | {'':<{score_w}} | {continued:<{reasons_w}} |"
                )
            print(border())


if __name__ == "__main__":
    main()
