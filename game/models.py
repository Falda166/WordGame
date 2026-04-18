from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ValidationReason(str, Enum):
    EMPTY_INPUT = "empty_input"
    MISSING_SYLLABLE = "missing_syllable"
    TOO_SHORT = "too_short"
    ALREADY_USED = "already_used"
    NOT_IN_DICTIONARY = "not_in_dictionary"
    VALID = "valid"


@dataclass(slots=True)
class ValidationResult:
    is_valid: bool
    reason: ValidationReason
    normalized_word: str | None = None
    corrected_word: str | None = None
    used_ai_correction: bool = False
    message: str = ""


@dataclass(slots=True)
class GameStats:
    rounds_played: int = 0
    valid_words: int = 0
    invalid_words: int = 0
    ai_corrections_used: int = 0
    total_reaction_time: float = 0.0

    @property
    def average_reaction_time(self) -> float:
        if self.valid_words == 0:
            return 0.0
        return self.total_reaction_time / self.valid_words


@dataclass(slots=True)
class GameState:
    lives: int
    score: int = 0
    used_words: set[str] = field(default_factory=set)
    current_syllable: str = ""
    stats: GameStats = field(default_factory=GameStats)
