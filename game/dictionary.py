from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging
import re

LOGGER = logging.getLogger(__name__)
_WORD_RE = re.compile(r"^[a-zäöüß][a-zäöüß-]*$", re.IGNORECASE)


class DictionaryProvider:
    """Abstrakte Wörterbuch-Quelle."""

    def contains(self, word: str) -> bool:  # pragma: no cover - Interface
        raise NotImplementedError

    def iter_words(self) -> list[str]:
        return []


@dataclass(slots=True)
class FallbackWordListProvider(DictionaryProvider):
    wordlist_path: Path

    def __post_init__(self) -> None:
        if not self.wordlist_path.exists():
            raise FileNotFoundError(f"Fallback-Wortliste fehlt: {self.wordlist_path}")
        with self.wordlist_path.open("r", encoding="utf-8") as handle:
            words = [line.strip().lower() for line in handle if line.strip()]
        self._words = set(words)

    def contains(self, word: str) -> bool:
        return word.lower() in self._words

    def iter_words(self) -> list[str]:
        return list(self._words)


@dataclass(slots=True)
class HunspellProvider(DictionaryProvider):
    aff_path: Path
    dic_path: Path

    def __post_init__(self) -> None:
        try:
            from spylls.hunspell import Dictionary
        except ImportError as exc:  # pragma: no cover - von Umgebung abhängig
            raise RuntimeError("spylls-hunspell ist nicht installiert") from exc

        base = str(self.aff_path.with_suffix(""))
        self._dictionary = Dictionary.from_files(base)
        self._words = self._read_dic_word_stems(self.dic_path)

    def _read_dic_word_stems(self, dic_path: Path) -> set[str]:
        words: set[str] = set()
        with dic_path.open("r", encoding="utf-8", errors="ignore") as handle:
            for idx, line in enumerate(handle):
                if idx == 0 and line.strip().isdigit():
                    continue
                candidate = line.strip().split("/", maxsplit=1)[0].lower()
                if candidate and _WORD_RE.match(candidate):
                    words.add(candidate)
        return words

    def contains(self, word: str) -> bool:
        return bool(self._dictionary.lookup(word))

    def iter_words(self) -> list[str]:
        return list(self._words)


class DictionaryFactory:
    """Erzeugt den bestmöglichen Provider.

    Priorität:
    1) Hunspell-Dateien in dictionaries/de_DE.aff und dictionaries/de_DE.dic
    2) lokale Fallback-Wortliste
    """

    @staticmethod
    def create(dictionaries_dir: Path, fallback_wordlist_path: Path, allow_fallback: bool) -> DictionaryProvider:
        aff_path = dictionaries_dir / "de_DE.aff"
        dic_path = dictionaries_dir / "de_DE.dic"

        if aff_path.exists() and dic_path.exists():
            try:
                provider = HunspellProvider(aff_path=aff_path, dic_path=dic_path)
                LOGGER.info("Hunspell-Wörterbuch geladen: %s", dic_path)
                return provider
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning("Hunspell konnte nicht geladen werden: %s", exc)

        if allow_fallback:
            LOGGER.warning("Nutze Fallback-Wortliste. Für volle Qualität Hunspell-Dateien bereitstellen.")
            return FallbackWordListProvider(wordlist_path=fallback_wordlist_path)

        raise RuntimeError("Kein Wörterbuch verfügbar. Bitte Hunspell-Dateien hinterlegen.")
