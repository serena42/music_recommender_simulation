from __future__ import annotations

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# Additive point values — scores are NOT normalized to [0, 1].
# Design rationale:
#   Genre is a hard long-term preference (2.0 pts); mood is contextual and
#   situational, so it counts half as much (1.0 pt). Energy and acousticness
#   are continuous signals scored by closeness, giving songs that nail the
#   numeric feel a meaningful boost without overriding categorical matches.
#   Max possible score: 2.0 + 1.0 + 1.0 + 1.0 = 5.0
FEATURE_WEIGHTS = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 1.0,
    "acousticness": 1.0,
}


def _closeness(target: float, value: float, max_range: float = 1.0) -> float:
    """Return a similarity score in [0.0, 1.0] based on how close value is to target.

    A perfect match (value == target) returns 1.0. The score decreases linearly
    as the distance grows, reaching 0.0 when the distance equals max_range.

    Args:
        target: The ideal value the user is looking for.
        value: The song's actual value for this feature.
        max_range: The maximum meaningful distance (default 1.0 for 0–1 features).

    Returns:
        A float in [0.0, 1.0] where 1.0 means a perfect match.
    """
    distance = abs(target - value)
    return max(0.0, 1.0 - (distance / max_range))


def _ranked_match(value: str, ordered_preferences: List[str]) -> float:
    """Return a partial-credit score based on where value appears in an ordered preference list.

    Uses exponential decay: 1st preference = 1.0 credit, 2nd = 0.8, 3rd = 0.64, 4th = 0.51, etc.
    This ensures that even lower-ranked preferences still contribute meaningfully, without a hard floor.
    Matching is flexible: an exact match, a substring match in either direction
    (e.g. "pop" matches "indie pop"), all count equally.
    Returns 0.0 if value does not appear in the list at all.

    Args:
        value: The song's categorical value (e.g. its genre or mood).
        ordered_preferences: The user's preferences ranked from most to least preferred.

    Returns:
        A float in [0.0, 1.0] representing how well value matches the user's preferences.
    """
    for idx, pref in enumerate(ordered_preferences):
        if value == pref or pref in value or value in pref:
            # Exponential decay: 0.8 ** idx gives smoother falloff than linear.
            return 0.8 ** idx
    return 0.0


def _genre_preferences(user: UserProfile) -> List[str]:
    """Return the user's ordered genre preferences, falling back to favorite_genre if needed.

    Args:
        user: The UserProfile to read preferences from.

    Returns:
        A non-empty list of genre strings ordered from most to least preferred.
    """
    prefs = user.preferred_genres if user.preferred_genres else [user.favorite_genre]
    return [p for p in prefs if p]


def _mood_preferences(user: UserProfile) -> List[str]:
    """Return the user's ordered mood preferences, falling back to favorite_mood if needed.

    Args:
        user: The UserProfile to read preferences from.

    Returns:
        A non-empty list of mood strings ordered from most to least preferred.
    """
    prefs = user.preferred_moods if user.preferred_moods else [user.favorite_mood]
    return [p for p in prefs if p]


def _score_song(song: Song, user: UserProfile) -> Tuple[float, Dict[str, float], List[str]]:
    """Score a single song against a user profile using the additive point recipe.

    Each feature contributes raw points (not normalized fractions) according to
    FEATURE_WEIGHTS. Categorical features (genre, mood) use _ranked_match for
    partial credit; numeric features (energy, acousticness) use _closeness.
    Only features that score above 0 are included in the reasons list.

    Args:
        song: The Song to evaluate.
        user: The UserProfile containing the user's preferences.

    Returns:
        A tuple of:
        - total_score (float): Sum of all feature contributions, max 5.0.
        - contributions (Dict[str, float]): Points earned per feature.
        - reasons (List[str]): Human-readable strings for each non-zero contribution,
          e.g. ["genre match (+2.00)", "energy closeness (+0.93)"].
    """
    contributions: Dict[str, float] = {}
    reasons: List[str] = []

    genre_match = _ranked_match(song.genre, _genre_preferences(user))
    mood_match = _ranked_match(song.mood, _mood_preferences(user))

    contributions["genre"] = FEATURE_WEIGHTS["genre"] * genre_match
    contributions["mood"] = FEATURE_WEIGHTS["mood"] * mood_match
    contributions["energy"] = FEATURE_WEIGHTS["energy"] * _closeness(user.target_energy, song.energy)
    contributions["acousticness"] = FEATURE_WEIGHTS["acousticness"] * _closeness(
        user.acoustic_preference,
        song.acousticness,
    )

    if contributions["genre"] > 0:
        reasons.append(f"genre match (+{contributions['genre']:.2f})")
    if contributions["mood"] > 0:
        reasons.append(f"mood match (+{contributions['mood']:.2f})")
    if contributions["energy"] > 0:
        reasons.append(f"energy closeness (+{contributions['energy']:.2f})")
    if contributions["acousticness"] > 0:
        reasons.append(f"acousticness closeness (+{contributions['acousticness']:.2f})")

    total_score = sum(contributions.values())
    return total_score, contributions, reasons


def _build_explanation(song: Song, user: UserProfile, contributions: Dict[str, float]) -> str:
    """Build a prose explanation of why a song was recommended.

    Checks each feature in priority order and appends a plain-English phrase
    for each strong match. Falls back to naming the top-scoring feature if no
    individual threshold is met.

    Args:
        song: The recommended Song.
        user: The UserProfile the song was scored against.
        contributions: The per-feature point contributions from _score_song.

    Returns:
        A semicolon-separated string of reasons, e.g.
        "matches your favorite genre (pop); has an energy level close to your target".
    """
    reasons = []

    if _ranked_match(song.genre, _genre_preferences(user)) > 0:
        reasons.append(f"matches your favorite genre ({song.genre})")
    if _ranked_match(song.mood, _mood_preferences(user)) > 0:
        reasons.append(f"fits your preferred mood ({song.mood})")
    if _closeness(user.target_energy, song.energy) >= 0.8:
        reasons.append("has an energy level close to your target")

    if _closeness(user.acoustic_preference, song.acousticness) >= 0.8:
        if user.acoustic_preference >= 0.65:
            reasons.append("leans acoustic, which matches your preference")
        elif user.acoustic_preference <= 0.35:
            reasons.append("is less acoustic, which matches your preference")
        else:
            reasons.append("matches your balanced acoustic preference")

    if not reasons:
        top_factor = max(contributions, key=contributions.get)
        pretty = top_factor.replace("_", " ")
        reasons.append(f"is a strong fit based on {pretty}")

    return "; ".join(reasons)

@dataclass
class Song:
    """A single song and its audio feature attributes loaded from the catalog.

    Attributes:
        id: Unique integer identifier from songs.csv.
        title: Display name of the song.
        artist: Artist or band name.
        genre: Primary genre tag (e.g. "pop", "lofi", "hip hop").
        mood: Emotional character of the track (e.g. "happy", "chill", "intense").
        energy: Perceived intensity and activity level, 0.0 (calm) to 1.0 (energetic).
        tempo_bpm: Beats per minute.
        valence: Musical positivity, 0.0 (negative) to 1.0 (positive).
        danceability: How suitable the track is for dancing, 0.0 to 1.0.
        acousticness: Likelihood the track is acoustic, 0.0 to 1.0.
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
    """A user's stated music taste preferences used to score and rank songs.

    Attributes:
        favorite_genre: The user's top genre preference.
        favorite_mood: The user's top mood preference.
        target_energy: Ideal energy level the user wants, 0.0 to 1.0.
        acoustic_preference: Preferred acousticness from 0.0 to 1.0.
            0.0 means strongly non-acoustic, 1.0 means strongly acoustic.
        preferred_genres: Optional ordered list of genres (most to least preferred).
            Falls back to [favorite_genre] when not provided.
        preferred_moods: Optional ordered list of moods (most to least preferred).
            Falls back to [favorite_mood] when not provided.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    acoustic_preference: float = 0.5
    preferred_genres: Optional[List[str]] = None
    preferred_moods: Optional[List[str]] = None

class Recommender:
    """OOP wrapper around the scoring and ranking logic.

    Holds a catalog of Song objects and exposes methods to generate ranked
    recommendations and plain-English explanations for a given UserProfile.
    """

    def __init__(self, songs: List[Song]):
        """Initialise the recommender with a catalog of songs.

        Args:
            songs: List of Song objects to score and rank against.
        """
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by score for the given user.

        Args:
            user: The UserProfile to score songs against.
            k: Number of results to return (default 5).

        Returns:
            A list of up to k Song objects sorted highest score first.
        """
        scored: List[Tuple[Song, float]] = []
        for song in self.songs:
            score, _, _ = _score_song(song, user)
            scored.append((song, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a prose explanation of why song was recommended for user.

        Args:
            user: The UserProfile the song was scored against.
            song: The Song to explain.

        Returns:
            A semicolon-separated string of plain-English reasons.
        """
        _, contributions, _ = _score_song(song, user)
        return _build_explanation(song, user, contributions)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return them as a list of dictionaries.

    Each row becomes a dict keyed by column name. Numeric fields
    (energy, tempo_bpm, valence, danceability, acousticness) are cast to
    float so arithmetic operations work without further conversion.

    Args:
        csv_path: Path to the CSV file (e.g. "data/songs.csv").

    Returns:
        A list of dicts, one per song, with string and float values.
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
    """Score every song in the catalog and return the top k results.

    Converts raw dicts (from load_songs) into typed Song and UserProfile
    objects, scores each song with _score_song, then returns the highest-
    scoring results sorted from best to worst.

    Args:
        user_prefs: Dict of user preference keys — "genre", "mood", "energy",
            "acoustic_preference" (0.0-1.0), and optionally "genres" and "moods"
            for ranked lists. Legacy "likes_acoustic" is still accepted.
        songs: List of song dicts as returned by load_songs.
        k: Number of recommendations to return (default 5).

    Returns:
        A list of up to k tuples of (song_dict, score, explanation, reasons),
        sorted highest score first.
    """
    legacy_likes_acoustic = bool(user_prefs.get("likes_acoustic", False))
    acoustic_pref = user_prefs.get(
        "acoustic_preference",
        1.0 if legacy_likes_acoustic else 0.0,
    )

    user = UserProfile(
        favorite_genre=user_prefs.get("genre", ""),
        favorite_mood=user_prefs.get("mood", ""),
        target_energy=float(user_prefs.get("energy", 0.5)),
        acoustic_preference=float(acoustic_pref),
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

        score, contributions, reasons = _score_song(song, user)
        explanation = _build_explanation(song, user, contributions)
        scored.append((song_dict, score, explanation, reasons))

    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
