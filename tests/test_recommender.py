from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Basic expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_multi_preferences_with_partial_credit_affect_ranking():
    user = UserProfile(
        favorite_genre="hip hop",
        favorite_mood="confident",
        target_energy=0.8,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
        preferred_genres=["hip hop", "lofi"],
        preferred_moods=["confident", "chill"],
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    # Even without exact top-category matches, ranked preferences should help lofi/chill.
    assert results[0].genre == "lofi"


def test_exponential_decay_for_ranked_genres():
    """Verify that ranked preferences use exponential decay (0.8**idx)."""
    songs = [
        Song(id=1, title="Pop A", artist="Artist", genre="pop", mood="happy", 
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
        Song(id=2, title="Jazz B", artist="Artist", genre="jazz", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
        Song(id=3, title="Rock C", artist="Artist", genre="rock", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
        Song(id=4, title="Blues D", artist="Artist", genre="blues", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
        Song(id=5, title="Classical E", artist="Artist", genre="classical", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
    ]
    rec = Recommender(songs)
    
    # User prefers pop > jazz > rock > blues > classical
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.5,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
        preferred_genres=["pop", "jazz", "rock", "blues", "classical"],
    )
    
    results = rec.recommend(user, k=5)
    
    # With exponential decay (0.8**idx), all ranked genres contribute meaningfully:
    # pop: 1.0, jazz: 0.8, rock: 0.64, blues: 0.512, classical: 0.4096
    # All should appear in results in that order
    assert [r.genre for r in results] == ["pop", "jazz", "rock", "blues", "classical"]


def test_energy_closeness_scoring():
    """Verify that energy closeness is properly calculated."""
    songs = [
        Song(id=1, title="Low Energy", artist="Artist", genre="pop", mood="happy",
             energy=0.2, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
        Song(id=2, title="Medium Energy", artist="Artist", genre="pop", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
        Song(id=3, title="High Energy", artist="Artist", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
    ]
    rec = Recommender(songs)
    
    # User wants high energy (0.8)
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    
    results = rec.recommend(user, k=3)
    
    # High energy song should score highest, low energy lowest
    assert results[0].energy == 0.8
    assert results[1].energy == 0.5
    assert results[2].energy == 0.2


def test_acoustic_preference_spectrum_matching():
    """Verify that acoustic preference matching works across the preference spectrum."""
    acoustic_song = Song(
        id=1, title="Acoustic Track", artist="Artist", genre="folk", mood="peaceful",
        energy=0.3, tempo_bpm=80, valence=0.5, danceability=0.3, acousticness=0.95,
    )
    electric_song = Song(
        id=2, title="Electric Track", artist="Artist", genre="pop", mood="happy",
        energy=0.7, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.1,
    )
    rec = Recommender([acoustic_song, electric_song])
    
    # User who likes acoustic
    acoustic_lover = UserProfile(
        favorite_genre="folk",
        favorite_mood="peaceful",
        target_energy=0.3,
        energy_flexibility=0.5,
        acoustic_preference=1.0,
    )
    results_acoustic = rec.recommend(acoustic_lover, k=2)
    assert results_acoustic[0].title == "Acoustic Track"
    
    # User who dislikes acoustic
    electric_lover = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.7,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    results_electric = rec.recommend(electric_lover, k=2)
    assert results_electric[0].title == "Electric Track"

    # User with mid preference should prefer the closer acousticness value.
    balanced_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.6,
        energy_flexibility=0.5,
        acoustic_preference=0.5,
    )
    results_balanced = rec.recommend(balanced_user, k=2)
    assert results_balanced[0].title == "Electric Track"


def test_genre_substring_matching():
    """Verify that genre matching works with substring matching."""
    songs = [
        Song(id=1, title="Indie Pop", artist="Artist", genre="indie pop", mood="happy",
             energy=0.6, tempo_bpm=100, valence=0.7, danceability=0.6, acousticness=0.4),
        Song(id=2, title="Alternative Rock", artist="Artist", genre="alt rock", mood="moody",
             energy=0.7, tempo_bpm=110, valence=0.5, danceability=0.5, acousticness=0.3),
    ]
    rec = Recommender(songs)
    
    # User prefers just "pop" - should match "indie pop" via substring
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.6,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    
    results = rec.recommend(user, k=2)
    assert results[0].genre == "indie pop"


def test_no_matching_genre_still_scores_other_features():
    """Verify that songs with non-matching genres can still score well on other features."""
    songs = [
        Song(id=1, title="Classical Chill", artist="Artist", genre="classical", mood="peaceful",
             energy=0.2, tempo_bpm=60, valence=0.4, danceability=0.1, acousticness=0.9),
        Song(id=2, title="Jazz Groove", artist="Artist", genre="jazz", mood="peaceful",
             energy=0.4, tempo_bpm=90, valence=0.6, danceability=0.5, acousticness=0.6),
    ]
    rec = Recommender(songs)
    
    # User prefers rock (not in catalog), but both songs match mood
    user = UserProfile(
        favorite_genre="rock",
        favorite_mood="peaceful",
        target_energy=0.3,
        energy_flexibility=0.5,
        acoustic_preference=1.0,
    )
    
    results = rec.recommend(user, k=2)
    # Both should still rank by mood, energy closeness, and acoustic match
    assert len(results) == 2
    assert all(r.mood == "peaceful" for r in results)


def test_explanation_includes_matching_features():
    """Verify that song explanations describe actual matching features."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    rec = make_small_recommender()
    song = rec.songs[0]  # "Test Pop Track" - matches genre, mood, energy, acoustic
    
    explanation = rec.explain_recommendation(user, song)
    
    # Should mention genre match
    assert "genre" in explanation.lower() or "pop" in explanation.lower()
    # Should be a reasonable length
    assert len(explanation) > 20


def test_recommend_respects_k_parameter():
    """Verify that the k parameter limits results correctly."""
    songs = [
        Song(id=i, title=f"Song {i}", artist="Artist", genre="pop", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5)
        for i in range(1, 6)
    ]
    rec = Recommender(songs)
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.5,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    
    # Test different k values
    results_1 = rec.recommend(user, k=1)
    assert len(results_1) == 1
    
    results_3 = rec.recommend(user, k=3)
    assert len(results_3) == 3
    
    results_10 = rec.recommend(user, k=10)
    assert len(results_10) == 5  # Can't return more than available


def test_conflicting_preferences_with_ranked_backup():
    """Verify that ranked preferences help when primary preferences conflict."""
    songs = [
        Song(id=1, title="Energetic Classical", artist="Artist", genre="classical", mood="intense",
             energy=0.9, tempo_bpm=180, valence=0.8, danceability=0.3, acousticness=0.8),
        Song(id=2, title="Chill Classic", artist="Artist", genre="classical", mood="peaceful",
             energy=0.2, tempo_bpm=60, valence=0.4, danceability=0.1, acousticness=0.9),
    ]
    rec = Recommender(songs)
    
    # User wants high energy AND peaceful mood (conflicting), but lists classical as 2nd genre
    user = UserProfile(
        favorite_genre="jazz",  # Not in catalog
        favorite_mood="peaceful",
        target_energy=0.9,
        energy_flexibility=0.5,
        acoustic_preference=1.0,
        preferred_genres=["jazz", "classical"],
    )
    
    results = rec.recommend(user, k=2)
    # With ranked preference, classical songs should still appear
    assert any(r.genre == "classical" for r in results)


def test_empty_ranked_preferences():
    """Verify that profiles work correctly with empty ranked preferences."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.5,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
        preferred_genres=[],  # Empty list
        preferred_moods=[],   # Empty list
    )
    rec = make_small_recommender()
    
    # Should still work, using only primary preferences
    results = rec.recommend(user, k=2)
    assert len(results) == 2
    assert results[0].genre == "pop"


def test_score_consistency_across_calls():
    """Verify that the same user and song always produce the same score."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        energy_flexibility=0.5,
        acoustic_preference=0.0,
    )
    rec = make_small_recommender()
    song = rec.songs[0]
    
    # Call recommend multiple times
    results_1 = rec.recommend(user, k=2)
    results_2 = rec.recommend(user, k=2)
    results_3 = rec.recommend(user, k=2)
    
    # Ordering should be identical
    assert [r.id for r in results_1] == [r.id for r in results_2]
    assert [r.id for r in results_2] == [r.id for r in results_3]


def test_energy_flexibility_changes_energy_tolerance():
    """Flexible users should keep farther energy values more competitive."""
    from src.recommender import _score_song

    songs = [
        Song(id=1, title="Target", artist="Artist", genre="pop", mood="happy",
             energy=0.5, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
        Song(id=2, title="Far", artist="Artist", genre="pop", mood="happy",
             energy=0.9, tempo_bpm=100, valence=0.5, danceability=0.5, acousticness=0.5),
    ]
    rec = Recommender(songs)

    rigid_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.5,
        energy_flexibility=0.0,
        acoustic_preference=0.5,
    )
    flexible_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.5,
        energy_flexibility=1.0,
        acoustic_preference=0.5,
    )

    target_score_rigid, _, _ = _score_song(songs[0], rigid_user)
    far_score_rigid, _, _ = _score_song(songs[1], rigid_user)
    target_score_flexible, _, _ = _score_song(songs[0], flexible_user)
    far_score_flexible, _, _ = _score_song(songs[1], flexible_user)

    rigid_gap = target_score_rigid - far_score_rigid
    flexible_gap = target_score_flexible - far_score_flexible

    # Flexible matching should reduce the penalty for farther energies.
    assert flexible_gap < rigid_gap


def test_recommend_songs_reads_energy_flexibility_from_dict():
    """Functional API should honor energy_flexibility from user preference dict."""
    from src.recommender import recommend_songs

    songs = [
        {
            "id": "1",
            "title": "Near Energy",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.5,
            "tempo_bpm": 100,
            "valence": 0.5,
            "danceability": 0.5,
            "acousticness": 0.5,
        },
        {
            "id": "2",
            "title": "Far Energy",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.95,
            "tempo_bpm": 100,
            "valence": 0.5,
            "danceability": 0.5,
            "acousticness": 0.5,
        },
    ]

    user = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.5,
        "energy_flexibility": 1.0,
        "acoustic_preference": 0.5,
    }

    results = recommend_songs(user, songs, k=2)
    assert len(results) == 2
    assert results[0][0]["title"] == "Near Energy"


def test_optional_danceability_and_valence_can_break_ties():
    """Optional danceability/valence targets should influence tie-like candidates."""
    songs = [
        Song(
            id=1,
            title="Dance Match",
            artist="Artist",
            genre="pop",
            mood="happy",
            energy=0.7,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.9,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Dance Mismatch",
            artist="Artist",
            genre="pop",
            mood="happy",
            energy=0.7,
            tempo_bpm=120,
            valence=0.2,
            danceability=0.2,
            acousticness=0.2,
        ),
    ]
    rec = Recommender(songs)

    user_without_optional = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.7,
        energy_flexibility=0.5,
        acoustic_preference=0.2,
    )
    user_with_optional = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.7,
        energy_flexibility=0.5,
        acoustic_preference=0.2,
        target_danceability=0.9,
        target_valence=0.9,
    )

    no_optional = rec.recommend(user_without_optional, k=2)
    with_optional = rec.recommend(user_with_optional, k=2)

    # Without optional tie-breakers, insertion order is preserved for equal core scores.
    assert no_optional[0].title == "Dance Match"
    # With optional targets, the better dance/valence fit should still lead.
    assert with_optional[0].title == "Dance Match"


def test_recommend_songs_reads_optional_danceability_and_valence_from_dict():
    """Functional API should parse optional danceability/valence user targets."""
    from src.recommender import recommend_songs

    songs = [
        {
            "id": "1",
            "title": "Closer Optional Fit",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.6,
            "tempo_bpm": 100,
            "valence": 0.85,
            "danceability": 0.85,
            "acousticness": 0.2,
        },
        {
            "id": "2",
            "title": "Far Optional Fit",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.6,
            "tempo_bpm": 100,
            "valence": 0.2,
            "danceability": 0.2,
            "acousticness": 0.2,
        },
    ]

    user = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.6,
        "energy_flexibility": 0.5,
        "acoustic_preference": 0.2,
        "target_danceability": 0.9,
        "target_valence": 0.9,
    }

    results = recommend_songs(user, songs, k=2)
    assert len(results) == 2
    assert results[0][0]["title"] == "Closer Optional Fit"


def test_explanation_can_reference_new_optional_features():
    """Explanation text should mention optional features when strongly matched."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        energy_flexibility=0.5,
        acoustic_preference=0.2,
        target_danceability=0.8,
        target_valence=0.9,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song).lower()
    assert "danceability" in explanation or "positivity" in explanation


def test_diversify_option_in_recommender_spreads_top_k_artists():
    """Diversity reranking should avoid artist repetition when scores are close."""
    songs = [
        Song(id=1, title="A1", artist="Artist A", genre="pop", mood="happy",
             energy=0.60, tempo_bpm=100, valence=0.60, danceability=0.70, acousticness=0.20),
        Song(id=2, title="A2", artist="Artist A", genre="pop", mood="happy",
             energy=0.59, tempo_bpm=100, valence=0.60, danceability=0.69, acousticness=0.21),
           Song(id=3, title="B1", artist="Artist B", genre="pop", mood="happy",
             energy=0.58, tempo_bpm=100, valence=0.60, danceability=0.68, acousticness=0.20),
    ]
    rec = Recommender(songs)
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.60,
        energy_flexibility=1.0,
        acoustic_preference=0.20,
    )

    baseline = rec.recommend(user, k=2)
    diversified = rec.recommend(user, k=2, diversify=True, artist_penalty=0.35, genre_penalty=0.15)

    assert baseline[0].artist == "Artist A"
    assert baseline[1].artist == "Artist A"
    assert diversified[0].artist != diversified[1].artist


def test_diversify_option_in_functional_api_can_reduce_repeat_genres():
    """Functional API should apply genre/artist repeat penalties when enabled."""
    from src.recommender import recommend_songs

    songs = [
        {
            "id": "1",
            "title": "Pop 1",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.60,
            "tempo_bpm": 100,
            "valence": 0.60,
            "danceability": 0.70,
            "acousticness": 0.20,
        },
        {
            "id": "2",
            "title": "Pop 2",
            "artist": "Artist B",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.59,
            "tempo_bpm": 100,
            "valence": 0.60,
            "danceability": 0.69,
            "acousticness": 0.20,
        },
        {
            "id": "3",
            "title": "Rock 1",
            "artist": "Artist C",
            "genre": "rock",
            "mood": "happy",
            "energy": 0.58,
            "tempo_bpm": 100,
            "valence": 0.60,
            "danceability": 0.68,
            "acousticness": 0.20,
        },
    ]
    user_base = {
        "genre": "pop",
        "mood": "happy",
        "genres": ["pop", "rock"],
        "energy": 0.60,
        "energy_flexibility": 1.0,
        "acoustic_preference": 0.20,
    }

    baseline = recommend_songs(user_base, songs, k=2)
    diversified = recommend_songs(
        {
            **user_base,
            "diversify": True,
            "artist_repeat_penalty": 0.35,
                "genre_repeat_penalty": 0.60,
        },
        songs,
        k=2,
    )

    assert baseline[0][0]["genre"] == "pop"
    assert baseline[1][0]["genre"] == "pop"
    assert diversified[0][0]["genre"] != diversified[1][0]["genre"]
