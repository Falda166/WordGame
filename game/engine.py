from __future__ import annotations

from dataclasses import dataclass

from .config import DifficultyConfig, GameConfig
from .dictionary import DictionaryFactory, FallbackWordListProvider
from .hf_correction import HFCorrector
from .models import GameState, ValidationResult
from .scoring import calculate_points
from .syllables import SyllablePool
from .validator import WordValidator


@dataclass(slots=True)
class RoundResolution:
    result: ValidationResult | None
    lost_life: bool
    gained_points: int
    reaction_time: float


class GameEngine:
    def __init__(self, config: GameConfig, difficulty: DifficultyConfig | None = None) -> None:
        self.config = config
        self.difficulty = difficulty or config.default_difficulty
        self.dictionary = DictionaryFactory.create(
            dictionaries_dir=config.dictionaries_dir,
            fallback_wordlist_path=config.fallback_wordlist_path,
            allow_fallback=config.allow_fallback_wordlist,
        )
        self.validator = WordValidator(
            dictionary=self.dictionary,
            ai_corrector=HFCorrector(config.ai_model_name, enabled=config.use_ai_correction),
            allow_ai_fallback_validation=isinstance(self.dictionary, FallbackWordListProvider),
            min_word_length=config.min_word_length,
        )
        self.syllable_pool = SyllablePool.from_words(
            self.dictionary.iter_words(),
            min_len=config.min_syllable_length,
            max_len=config.max_syllable_length,
            max_candidates=config.max_syllable_candidates,
        )
        self.state = GameState(lives=config.max_lives)

    def reset(self, difficulty: DifficultyConfig | None = None) -> None:
        if difficulty:
            self.difficulty = difficulty
        self.state = GameState(lives=self.config.max_lives)

    def next_round(self) -> str:
        syllable = self.syllable_pool.choose_random()
        self.state.current_syllable = syllable
        self.state.stats.rounds_played += 1
        return syllable

    def resolve_timeout(self) -> RoundResolution:
        self.state.lives -= 1
        self.state.stats.invalid_words += 1
        return RoundResolution(result=None, lost_life=True, gained_points=0, reaction_time=self.difficulty.round_time_seconds)

    def submit_word(self, user_input: str, reaction_time: float) -> RoundResolution:
        result = self.validator.validate(user_input, self.state.current_syllable, self.state.used_words)

        if result.is_valid:
            final_word = result.corrected_word or result.normalized_word or ""
            self.state.used_words.add(final_word)
            gained_points = calculate_points(
                base_points=self.difficulty.base_points,
                word=final_word,
                remaining_seconds=max(0.0, self.difficulty.round_time_seconds - reaction_time),
                used_ai_correction=result.used_ai_correction,
            )
            self.state.score += gained_points
            self.state.stats.valid_words += 1
            self.state.stats.total_reaction_time += reaction_time
            if result.used_ai_correction:
                self.state.stats.ai_corrections_used += 1
            return RoundResolution(result=result, lost_life=False, gained_points=gained_points, reaction_time=reaction_time)

        self.state.lives -= 1
        self.state.stats.invalid_words += 1
        return RoundResolution(result=result, lost_life=True, gained_points=0, reaction_time=reaction_time)

    @property
    def is_game_over(self) -> bool:
        return self.state.lives <= 0
