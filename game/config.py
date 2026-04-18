from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DifficultyConfig:
    name: str
    round_time_seconds: float
    base_points: int


@dataclass(slots=True)
class GameConfig:
    """Zentrale Konfiguration, um magische Zahlen zu vermeiden."""

    max_lives: int = 6
    min_syllable_length: int = 2
    max_syllable_length: int = 3
    min_word_length: int = 3
    max_syllable_candidates: int = 300
    use_ai_correction: bool = False
    ai_model_name: str = "oliverguhr/spelling-correction-german-base"
    allow_fallback_wordlist: bool = True
    dictionaries_dir: Path = Path("dictionaries")
    fallback_wordlist_path: Path = Path("data/wordlist_de_fallback.txt")
    highscore_path: Path = Path("data/highscores.json")
    difficulties: dict[str, DifficultyConfig] = field(
        default_factory=lambda: {
            "leicht": DifficultyConfig("leicht", round_time_seconds=10.0, base_points=10),
            "normal": DifficultyConfig("normal", round_time_seconds=8.0, base_points=12),
            "schwer": DifficultyConfig("schwer", round_time_seconds=7.0, base_points=15),
        }
    )

    @property
    def default_difficulty(self) -> DifficultyConfig:
        return self.difficulties["normal"]
