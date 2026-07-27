"""Core loading, scoring, ranking, and explanation logic."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Song:
    """Represent one catalog song and its musical attributes."""

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
    popularity: int = 50
    release_decade: int = 2020
    instrumentalness: float = 0.0
    speechiness: float = 0.0
    liveness: float = 0.0


@dataclass
class UserProfile:
    """Represent the most important preferences for one listener."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


MODE_WEIGHTS = {
    "balanced": {"genre": 2.0, "mood": 1.5, "energy": 2.0, "tempo": 1.0},
    "genre_first": {"genre": 3.5, "mood": 1.0, "energy": 1.0, "tempo": 0.5},
    "energy_focus": {"genre": 1.0, "mood": 1.0, "energy": 4.0, "tempo": 1.5},
}

NUMERIC_FIELDS = {
    "id": int,
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float,
    "popularity": int,
    "release_decade": int,
    "instrumentalness": float,
    "speechiness": float,
    "liveness": float,
}


def load_songs(csv_path: str) -> List[Dict]:
    """Load a song CSV and convert every numeric field to a number."""

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            for field, converter in NUMERIC_FIELDS.items():
                if field in row and row[field] != "":
                    row[field] = converter(row[field])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return a transparent preference-match score and its reasons."""

    mode = user_prefs.get("mode", "balanced")
    if mode not in MODE_WEIGHTS:
        raise ValueError(f"Unknown ranking mode: {mode}")
    weights = MODE_WEIGHTS[mode]
    score = 0.0
    reasons: List[str] = []

    if song["genre"].lower() == user_prefs["genre"].lower():
        score += weights["genre"]
        reasons.append(f"genre match (+{weights['genre']:.1f})")
    if song["mood"].lower() == user_prefs["mood"].lower():
        score += weights["mood"]
        reasons.append(f"mood match (+{weights['mood']:.1f})")

    energy_similarity = max(0.0, 1.0 - abs(song["energy"] - user_prefs["energy"]))
    energy_points = weights["energy"] * energy_similarity
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.2f})")

    if "tempo_bpm" in user_prefs:
        tempo_similarity = max(
            0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs["tempo_bpm"]) / 100.0
        )
        tempo_points = weights["tempo"] * tempo_similarity
        score += tempo_points
        reasons.append(f"tempo similarity (+{tempo_points:.2f})")

    for feature, label in (
        ("valence", "valence"),
        ("danceability", "danceability"),
        ("acousticness", "acousticness"),
        ("instrumentalness", "instrumentalness"),
        ("speechiness", "speechiness"),
        ("liveness", "liveness"),
    ):
        if feature in user_prefs:
            similarity = max(0.0, 1.0 - abs(song[feature] - user_prefs[feature]))
            points = 0.5 * similarity
            score += points
            reasons.append(f"{label} similarity (+{points:.2f})")

    if "release_decade" in user_prefs:
        decade_points = 0.5 if song["release_decade"] == user_prefs["release_decade"] else 0.0
        score += decade_points
        if decade_points:
            reasons.append("release decade match (+0.50)")

    if user_prefs.get("prefer_popular"):
        popularity_points = 0.5 * song["popularity"] / 100.0
        score += popularity_points
        reasons.append(f"popularity (+{popularity_points:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, diversify: bool = True
) -> List[Tuple[Dict, float, str]]:
    """Rank all songs and optionally reduce repeated artists and genres."""

    if k < 0:
        raise ValueError("k must be non-negative")
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))
    scored.sort(key=lambda item: (-item[1], item[0]["title"].lower()))

    if not diversify:
        selected = scored[:k]
    else:
        remaining = list(scored)
        selected = []
        artist_counts: Dict[str, int] = {}
        genre_counts: Dict[str, int] = {}
        while remaining and len(selected) < k:
            reranked = []
            for song, base_score, reasons in remaining:
                penalty = 0.75 * artist_counts.get(song["artist"], 0)
                penalty += 0.25 * genre_counts.get(song["genre"], 0)
                reranked.append((base_score - penalty, song, base_score, reasons, penalty))
            _, song, base_score, reasons, penalty = max(
                reranked, key=lambda item: (item[0], -item[1]["id"])
            )
            if penalty:
                reasons = reasons + [f"diversity penalty (-{penalty:.2f})"]
            selected.append((song, base_score - penalty, reasons))
            remaining = [item for item in remaining if item[0]["id"] != song["id"]]
            artist_counts[song["artist"]] = artist_counts.get(song["artist"], 0) + 1
            genre_counts[song["genre"]] = genre_counts.get(song["genre"], 0) + 1

    return [
        (song, round(score, 4), "; ".join(reasons))
        for song, score, reasons in selected
    ]


class Recommender:
    """Offer an object-oriented interface over the shared scoring rules."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _preferences(user: UserProfile) -> Dict:
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acousticness": 0.9 if user.likes_acoustic else 0.1,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return Song objects ordered by preference match."""

        ranked = [
            (song, score_song(self._preferences(user), vars(song))[0])
            for song in self.songs
        ]
        ranked.sort(key=lambda item: (-item[1], item[0].title.lower()))
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain the exact points awarded to one Song object."""

        _, reasons = score_song(self._preferences(user), vars(song))
        return "; ".join(reasons)
