"""Run the music recommender against several contrasting profiles."""

from __future__ import annotations

from .recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Happy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.9,
        "tempo_bpm": 128, "danceability": 0.9, "mode": "balanced",
    },
    "Chill Acoustic Lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.3,
        "tempo_bpm": 75, "acousticness": 0.9, "mode": "genre_first",
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.95,
        "tempo_bpm": 150, "liveness": 0.7, "mode": "energy_focus",
    },
    "Adversarial Sad Workout": {
        "genre": "edm", "mood": "sad", "energy": 0.95,
        "tempo_bpm": 145, "valence": 0.15, "mode": "balanced",
    },
}


def print_table(recommendations: list) -> None:
    """Print recommendations in a dependency-free ASCII table."""

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        rows.append((str(rank), song["title"], song["artist"], f"{score:.2f}", explanation))
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(("Rank", "Title", "Artist", "Score", "Reasons"))
    ]
    divider = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(divider)
    print("| " + " | ".join(
        header.ljust(widths[index])
        for index, header in enumerate(("Rank", "Title", "Artist", "Score", "Reasons"))
    ) + " |")
    print(divider)
    for row in rows:
        print("| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(row)) + " |")
    print(divider)


def main() -> None:
    """Load the catalog and display five results for every test profile."""

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    for name, preferences in PROFILES.items():
        print(f"\nProfile: {name} (mode={preferences['mode']})")
        print_table(recommend_songs(preferences, songs, k=5))


if __name__ == "__main__":
    main()
