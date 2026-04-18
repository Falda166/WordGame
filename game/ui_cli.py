from __future__ import annotations

import queue
import threading
import time

from .config import DifficultyConfig, GameConfig
from .engine import GameEngine
from .highscore import HighscoreStore


class CLIApp:
    """CLI-Fallback mit Countdown pro Runde."""

    def __init__(self, config: GameConfig, difficulty: DifficultyConfig) -> None:
        self.engine = GameEngine(config=config, difficulty=difficulty)
        self.store = HighscoreStore(config.highscore_path)

    def _timed_input(self, prompt: str, timeout: float) -> tuple[str | None, float]:
        q: queue.Queue[tuple[str, float]] = queue.Queue()
        start = time.monotonic()

        def reader() -> None:
            text = input(prompt)
            q.put((text, time.monotonic() - start))

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()

        while True:
            try:
                return q.get_nowait()
            except queue.Empty:
                elapsed = time.monotonic() - start
                remaining = timeout - elapsed
                if remaining <= 0:
                    return None, timeout
                print(f"\r⏳ Bombe: {remaining:4.1f}s ", end="", flush=True)
                time.sleep(0.1)

    def run(self) -> None:
        print("=== Deutsches Silben-Bombenspiel (CLI) ===")
        while not self.engine.is_game_over:
            syllable = self.engine.next_round()
            print(f"\nSilbe: [{syllable}] | Leben: {self.engine.state.lives} | Punkte: {self.engine.state.score}")
            answer, reaction_time = self._timed_input("Dein Wort: ", self.engine.difficulty.round_time_seconds)
            print("")

            if answer is None:
                self.engine.resolve_timeout()
                print("💥 Zeit abgelaufen! -1 Leben")
                continue

            resolution = self.engine.submit_word(answer, reaction_time)
            if resolution.lost_life:
                reason = resolution.result.message if resolution.result else "Zeit abgelaufen"
                print(f"❌ Ungültig: {reason} (-1 Leben)")
            else:
                message = resolution.result.message if resolution.result else "Gültig"
                print(f"✅ {message} (+{resolution.gained_points} Punkte)")

        state = self.engine.state
        self.store.save_entry(state.score, state.stats.rounds_played, state.stats.valid_words)
        print("\n=== GAME OVER ===")
        print(f"Punkte: {state.score}")
        print(f"Runden: {state.stats.rounds_played}")
        print(f"Gültige Wörter: {state.stats.valid_words}")
        print(f"Ø Reaktionszeit: {state.stats.average_reaction_time:.2f}s")
