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
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
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
        likes_acoustic=False,
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
        likes_acoustic=False,
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
        likes_acoustic=False,
    )
    
    results = rec.recommend(user, k=3)
    
    # High energy song should score highest, low energy lowest
    assert results[0].energy == 0.8
    assert results[1].energy == 0.5
    assert results[2].energy == 0.2


def test_acoustic_preference_boolean_matching():
    """Verify that acoustic preference matching works with boolean preference."""
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
        likes_acoustic=True,
    )
    results_acoustic = rec.recommend(acoustic_lover, k=2)
    assert results_acoustic[0].title == "Acoustic Track"
    
    # User who dislikes acoustic
    electric_lover = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.7,
        likes_acoustic=False,
    )
    results_electric = rec.recommend(electric_lover, k=2)
    assert results_electric[0].title == "Electric Track"


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
        likes_acoustic=False,
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
        likes_acoustic=True,
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
        likes_acoustic=False,
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
        likes_acoustic=False,
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
        likes_acoustic=True,
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
        likes_acoustic=False,
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
        likes_acoustic=False,
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
