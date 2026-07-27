"""Tests for loading, scoring, ranking, explanations, modes, and diversity."""

import pytest

from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    load_songs,
    recommend_songs,
    score_song,
)


def make_song(song_id=1, title="Test Pop", artist="Artist A", genre="pop",
              mood="happy", energy=0.8):
    return Song(song_id, title, artist, genre, mood, energy, 120, 0.8, 0.8, 0.2)


def test_catalog_loads_with_typed_values():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 20
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["popularity"], int)


def test_exact_preferences_score_above_mismatch():
    user = {"genre": "pop", "mood": "happy", "energy": 0.8}
    exact = vars(make_song())
    mismatch = vars(make_song(2, "Mismatch", genre="metal", mood="sad", energy=0.1))
    assert score_song(user, exact)[0] > score_song(user, mismatch)[0]


def test_score_returns_numeric_value_and_accurate_reasons():
    score, reasons = score_song(
        {"genre": "pop", "mood": "happy", "energy": 0.8}, vars(make_song())
    )
    assert isinstance(score, float)
    assert "genre match (+2.0)" in reasons
    assert "mood match (+1.5)" in reasons
    assert any(reason.startswith("energy similarity") for reason in reasons)


def test_recommendations_are_sorted_and_limited():
    songs = load_songs("data/songs.csv")
    results = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=3,
        diversify=False,
    )
    assert len(results) == 3
    assert [item[1] for item in results] == sorted(
        [item[1] for item in results], reverse=True
    )


def test_different_modes_change_scores():
    song = vars(make_song())
    genre_score = score_song(
        {"genre": "pop", "mood": "sad", "energy": 0.1, "mode": "genre_first"}, song
    )[0]
    energy_score = score_song(
        {"genre": "pop", "mood": "sad", "energy": 0.1, "mode": "energy_focus"}, song
    )[0]
    assert genre_score > energy_score


def test_diversity_penalty_discourages_repeated_artist():
    songs = [
        vars(make_song(1, "One", "Same Artist")),
        vars(make_song(2, "Two", "Same Artist")),
        vars(make_song(3, "Three", "Other Artist", genre="rock", mood="happy", energy=0.8)),
    ]
    results = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=3
    )
    repeated = next(item for item in results if item[0]["title"] == "Two")
    assert "diversity penalty" in repeated[2]


def test_oop_interface_ranks_and_explains():
    recommender = Recommender([
        make_song(),
        make_song(2, "Chill Loop", genre="lofi", mood="chill", energy=0.3),
    ])
    user = UserProfile("pop", "happy", 0.8, False)
    assert recommender.recommend(user, 2)[0].genre == "pop"
    assert "genre match" in recommender.explain_recommendation(user, recommender.songs[0])


def test_invalid_mode_and_negative_k_are_rejected():
    song = vars(make_song())
    with pytest.raises(ValueError):
        score_song({"genre": "pop", "mood": "happy", "energy": 0.8, "mode": "bad"}, song)
    with pytest.raises(ValueError):
        recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, [song], -1)
