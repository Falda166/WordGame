from __future__ import annotations

from dataclasses import dataclass
import unicodedata

from .dictionary import DictionaryProvider
from .hf_correction import HFCorrector
from .models import ValidationReason, ValidationResult


@dataclass(slots=True)
class WordValidator:
    dictionary: DictionaryProvider
    ai_corrector: HFCorrector | None = None
    allow_ai_fallback_validation: bool = False
    min_word_length: int = 3

    @staticmethod
    def normalize_input(text: str) -> str:
        text = text.strip()
        text = unicodedata.normalize("NFC", text)
        return text.lower()


    @staticmethod
    def _is_likely_german_word(word: str) -> bool:
        try:
            from wordfreq import zipf_frequency
        except Exception:
            return False
        return zipf_frequency(word, "de") >= 2.5

    def validate(self, raw_input: str, required_syllable: str, used_words: set[str]) -> ValidationResult:
        word = self.normalize_input(raw_input)
        syllable = self.normalize_input(required_syllable)

        if not word:
            return ValidationResult(False, ValidationReason.EMPTY_INPUT, message="Leere Eingabe.")

        if len(word) < self.min_word_length:
            return ValidationResult(False, ValidationReason.TOO_SHORT, normalized_word=word, message=f"Wort zu kurz (min. {self.min_word_length} Zeichen).")

        if syllable not in word:
            return ValidationResult(False, ValidationReason.MISSING_SYLLABLE, normalized_word=word, message="Silbe fehlt.")

        if word in used_words:
            return ValidationResult(False, ValidationReason.ALREADY_USED, normalized_word=word, message="Wort wurde schon benutzt.")

        if self.dictionary.contains(word):
            return ValidationResult(True, ValidationReason.VALID, normalized_word=word, message="Gültiges Wort.")

        if self.ai_corrector and self.ai_corrector.enabled:
            corrected = self.ai_corrector.correct(word)
            if corrected and syllable in corrected and corrected not in used_words:
                if self.dictionary.contains(corrected):
                    return ValidationResult(
                        True,
                        ValidationReason.VALID,
                        normalized_word=word,
                        corrected_word=corrected,
                        used_ai_correction=True,
                        message=f"Wort via KI korrigiert: {corrected}",
                    )

                if self.allow_ai_fallback_validation and self._is_likely_german_word(corrected):
                    final = corrected
                    return ValidationResult(
                        True,
                        ValidationReason.VALID,
                        normalized_word=word,
                        corrected_word=final,
                        used_ai_correction=True,
                        message=f"Gültig via KI-Fallback: {final}",
                    )

        return ValidationResult(
            False,
            ValidationReason.NOT_IN_DICTIONARY,
            normalized_word=word,
            message="Wort nicht im Wörterbuch gefunden.",
        )
