from __future__ import annotations

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# Additive point values — scores are NOT normalized to [0, 1].
# Design rationale:
#   Genre is a hard long-term preference (2.0 pts); mood is contextual and
#   situational, so it counts half as much (1.0 pt).  Energy and acousticness
#   are continuous signals scored by closeness, giving songs that nail the
#   numeric feel a meaningful boost without overriding categorical matches.
#   Max possible score: 2.0 + 1.0 + 1.0 + 0.5 = 4.5
FEATURE_WEIGHTS = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 1.0,
    "acousticness": 0.5,
}


def _closeness(target: float, value: float, max_range: float = 1.0) -> float:
    """Returns a normalized similarity in [0, 1]."""
    distance = abs(target - value)
    return max(0.0, 1.0 - (distance / max_range))


def _ranked_match(value: str, ordered_preferences: List[str]) -> float:
    """Returns partial credit based on preference rank for categorical values."""
    for idx, pref in enumerate(ordered_preferences):
        if value == pref:
            # First preference gets full credit, then gently decays.
            return max(0.4, 1.0 - (0.2 * idx))
    return 0.0


def _genre_preferences(user: UserProfile) -> List[str]:
    prefs = user.preferred_genres if user.preferred_genres else [user.favorite_genre]
    return [p for p in prefs if p]


def _mood_preferences(user: UserProfile) -> List[str]:
    prefs = user.preferred_moods if user.preferred_moods else [user.favorite_mood]
    return [p for p in prefs if p]


def _score_song(song: Song, user: UserProfile) -> Tuple[float, Dict[str, float]]:
    """Scores a song and returns both total score and per-feature contributions."""
    contributions: Dict[str, float] = {}

    genre_match = _ranked_match(song.genre, _genre_preferences(user))
    mood_match = _ranked_match(song.mood, _mood_preferences(user))
    acoustic_target = 1.0 if user.likes_acoustic else 0.0

    contributions["genre"] = FEATURE_WEIGHTS["genre"] * genre_match
    contributions["mood"] = FEATURE_WEIGHTS["mood"] * mood_match
    contributions["energy"] = FEATURE_WEIGHTS["energy"] * _closeness(user.target_energy, song.energy)
    contributions["acousticness"] = FEATURE_WEIGHTS["acousticness"] * _closeness(acoustic_target, song.acousticness)

    total_score = sum(contributions.values())
    return total_score, contributions


def _build_explanation(song: Song, user: UserProfile, contributions: Dict[str, float]) -> str:
    """Builds a short explanation grounded in top positive factors."""
    reasons = []

    if _ranked_match(song.genre, _genre_preferences(user)) > 0:
        reasons.append(f"matches your favorite genre ({song.genre})")
    if _ranked_match(song.mood, _mood_preferences(user)) > 0:
        reasons.append(f"fits your preferred mood ({song.mood})")
    if _closeness(user.target_energy, song.energy) >= 0.8:
        reasons.append("has an energy level close to your target")

    acoustic_target = 1.0 if user.likes_acoustic else 0.0
    if _closeness(acoustic_target, song.acousticness) >= 0.8:
        if user.likes_acoustic:
            reasons.append("leans acoustic, which matches your preference")
        else:
            reasons.append("is less acoustic, which matches your preference")

    if not reasons:
        top_factor = max(contributions, key=contributions.get)
        pretty = top_factor.replace("_", " ")
        reasons.append(f"is a strong fit based on {pretty}")

    return "; ".join(reasons)

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
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_genres: Optional[List[str]] = None
    preferred_moods: Optional[List[str]] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored: List[Tuple[Song, float]] = []
        for song in self.songs:
            score, _ = _score_song(song, user)
            scored.append((song, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, contributions = _score_song(song, user)
        return _build_explanation(song, user, contributions)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    user = UserProfile(
        favorite_genre=user_prefs.get("genre", ""),
        favorite_mood=user_prefs.get("mood", ""),
        target_energy=float(user_prefs.get("energy", 0.5)),
        likes_acoustic=bool(user_prefs.get("likes_acoustic", False)),
        preferred_genres=user_prefs.get("genres"),
        preferred_moods=user_prefs.get("moods"),
    )

    scored: List[Tuple[Dict, float, str]] = []
    for song_dict in songs:
        song = Song(
            id=int(song_dict["id"]),
            title=song_dict["title"],
            artist=song_dict["artist"],
            genre=song_dict["genre"],
            mood=song_dict["mood"],
            energy=float(song_dict["energy"]),
            tempo_bpm=float(song_dict["tempo_bpm"]),
            valence=float(song_dict["valence"]),
            danceability=float(song_dict["danceability"]),
            acousticness=float(song_dict["acousticness"]),
        )

        score, contributions = _score_song(song, user)
        explanation = _build_explanation(song, user, contributions)
        scored.append((song_dict, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
