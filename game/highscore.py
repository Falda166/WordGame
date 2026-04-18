from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(slots=True)
class HighscoreEntry:
    score: int
    rounds_played: int
    valid_words: int
    timestamp_utc: str


class HighscoreStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[HighscoreEntry]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        entries = []
        for row in payload:
            entries.append(HighscoreEntry(**row))
        return entries

    def save_entry(self, score: int, rounds_played: int, valid_words: int) -> None:
        entries = self.load()
        entries.append(
            HighscoreEntry(
                score=score,
                rounds_played=rounds_played,
                valid_words=valid_words,
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
            )
        )
        entries.sort(key=lambda item: item.score, reverse=True)
        entries = entries[:10]
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump([asdict(entry) for entry in entries], handle, ensure_ascii=False, indent=2)
