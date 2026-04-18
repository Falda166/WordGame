from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random


@dataclass(slots=True)
class SyllablePool:
    syllables: list[str]

    @classmethod
    def from_words(
        cls,
        words: list[str],
        min_len: int = 2,
        max_len: int = 3,
        min_occurrence: int = 8,
        max_candidates: int = 300,
    ) -> "SyllablePool":
        counts: Counter[str] = Counter()
        for word in words:
            cleaned = word.strip().lower()
            if len(cleaned) < min_len:
                continue
            for width in range(min_len, max_len + 1):
                if len(cleaned) < width:
                    continue
                for i in range(len(cleaned) - width + 1):
                    part = cleaned[i : i + width]
                    if part.isalpha() and not part.startswith("-") and not part.endswith("-"):
                        counts[part] += 1

        common = [s for s, c in counts.items() if c >= min_occurrence]
        common.sort(key=lambda s: counts[s], reverse=True)

        if len(common) > max_candidates:
            common = common[:max_candidates]

        if not common:
            common = ["en", "er", "ch", "sch", "ei", "un", "an", "ge"]

        return cls(common)

    def choose_random(self) -> str:
        return random.choice(self.syllables)
