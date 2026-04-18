from __future__ import annotations


def calculate_points(
    base_points: int,
    word: str,
    remaining_seconds: float,
    used_ai_correction: bool,
) -> int:
    length_bonus = max(0, len(word) - 4) * 2
    speed_bonus = int(max(0.0, remaining_seconds) * 1.5)
    no_ai_bonus = 3 if not used_ai_correction else 1
    return base_points + length_bonus + speed_bonus + no_ai_bonus
