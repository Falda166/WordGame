from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .config import DifficultyConfig, GameConfig
from .engine import GameEngine
from .highscore import HighscoreStore
from .timer import RoundTimer


class TkApp:
    def __init__(self, config: GameConfig, difficulty: DifficultyConfig) -> None:
        self.config = config
        self.engine = GameEngine(config=config, difficulty=difficulty)
        self.store = HighscoreStore(config.highscore_path)

        self.root = tk.Tk()
        self.root.title("Silben-Bombe")
        self.root.geometry("760x460")
        self.root.minsize(700, 420)

        self.timer: RoundTimer | None = None
        self.round_open = False

        self._build_ui()
        self._show_start_screen()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.container = ttk.Frame(self.root, padding=16)
        self.container.grid(sticky="nsew")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self.start_frame = ttk.Frame(self.container, padding=16)
        self.game_frame = ttk.Frame(self.container, padding=16)
        self.over_frame = ttk.Frame(self.container, padding=16)

        # Startscreen
        title = ttk.Label(self.start_frame, text="Silben-Bombe", font=("Segoe UI", 26, "bold"))
        subtitle = ttk.Label(
            self.start_frame,
            text="Finde schnell ein deutsches Wort, das die angezeigte Silbe enthält.",
            font=("Segoe UI", 11),
        )
        self.ai_var = tk.BooleanVar(value=self.config.use_ai_correction)
        ai_check = ttk.Checkbutton(self.start_frame, text="KI-Tippfehlerkorrektur aktivieren", variable=self.ai_var)

        self.diff_var = tk.StringVar(value=self.engine.difficulty.name)
        diff_box = ttk.Combobox(
            self.start_frame,
            textvariable=self.diff_var,
            values=list(self.config.difficulties.keys()),
            state="readonly",
            width=14,
        )
        start_btn = ttk.Button(self.start_frame, text="Spiel starten", command=self._start_game)

        title.grid(row=0, column=0, pady=(18, 8))
        subtitle.grid(row=1, column=0, pady=(0, 20))
        ttk.Label(self.start_frame, text="Schwierigkeit:").grid(row=2, column=0, pady=4)
        diff_box.grid(row=3, column=0, pady=4)
        ai_check.grid(row=4, column=0, pady=(12, 8))
        start_btn.grid(row=5, column=0, pady=18)

        # Spielscreen
        self.info_label = ttk.Label(self.game_frame, text="", font=("Segoe UI", 12, "bold"))
        self.syllable_label = ttk.Label(self.game_frame, text="", font=("Segoe UI", 36, "bold"))
        self.bomb_label = ttk.Label(self.game_frame, text="", font=("Segoe UI", 20))
        self.entry = ttk.Entry(self.game_frame, font=("Segoe UI", 16), width=30)
        self.entry.bind("<Return>", self._submit_event)
        submit_btn = ttk.Button(self.game_frame, text="Wort prüfen", command=self._submit)
        self.status_label = ttk.Label(self.game_frame, text="", font=("Segoe UI", 11))

        self.info_label.grid(row=0, column=0, pady=(0, 14), sticky="w")
        self.syllable_label.grid(row=1, column=0, pady=(8, 12))
        self.bomb_label.grid(row=2, column=0, pady=(0, 12))
        self.entry.grid(row=3, column=0, pady=(6, 8))
        submit_btn.grid(row=4, column=0, pady=4)
        self.status_label.grid(row=5, column=0, pady=(10, 4))

        # Game Over
        self.over_title = ttk.Label(self.over_frame, text="GAME OVER", font=("Segoe UI", 30, "bold"))
        self.over_stats = ttk.Label(self.over_frame, text="", font=("Segoe UI", 11), justify="left")
        restart_btn = ttk.Button(self.over_frame, text="Nochmal spielen", command=self._show_start_screen)
        self.over_title.grid(row=0, column=0, pady=(16, 10))
        self.over_stats.grid(row=1, column=0, pady=10)
        restart_btn.grid(row=2, column=0, pady=12)

    def _show_frame(self, frame: ttk.Frame) -> None:
        for child in (self.start_frame, self.game_frame, self.over_frame):
            child.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")

    def _show_start_screen(self) -> None:
        self.round_open = False
        self._show_frame(self.start_frame)

    def _start_game(self) -> None:
        chosen = self.diff_var.get()
        difficulty = self.config.difficulties.get(chosen, self.config.default_difficulty)
        self.config.use_ai_correction = self.ai_var.get()
        self.engine = GameEngine(self.config, difficulty=difficulty)
        self._show_frame(self.game_frame)
        self._prepare_round()

    def _prepare_round(self) -> None:
        if self.engine.is_game_over:
            self._show_game_over()
            return
        syllable = self.engine.next_round()
        self.timer = RoundTimer(duration_seconds=self.engine.difficulty.round_time_seconds)
        self.timer.start()
        self.round_open = True
        self.entry.delete(0, tk.END)
        self.entry.focus_set()
        self.syllable_label.config(text=syllable.upper())
        self.status_label.config(text="")
        self._refresh_info()
        self._tick_timer()

    def _refresh_info(self) -> None:
        self.info_label.config(
            text=(
                f"Leben: {self.engine.state.lives}   "
                f"Punkte: {self.engine.state.score}   "
                f"Gültig: {self.engine.state.stats.valid_words}"
            )
        )

    def _tick_timer(self) -> None:
        if not self.round_open or not self.timer:
            return
        remaining = self.timer.remaining
        self.bomb_label.config(text=f"💣 {remaining:0.1f}s")
        if self.timer.is_expired:
            self.round_open = False
            self.engine.resolve_timeout()
            self.status_label.config(text="💥 Zeit abgelaufen! -1 Leben")
            self._refresh_info()
            self.root.after(900, self._prepare_round)
            return
        self.root.after(100, self._tick_timer)

    def _submit_event(self, _event: tk.Event) -> None:
        self._submit()

    def _submit(self) -> None:
        if not self.round_open or not self.timer:
            return
        self.round_open = False
        reaction_time = self.timer.elapsed
        text = self.entry.get()
        resolution = self.engine.submit_word(text, reaction_time)

        if resolution.lost_life:
            reason = resolution.result.message if resolution.result else "Ungültig"
            self.status_label.config(text=f"❌ {reason} (-1 Leben)")
        else:
            self.status_label.config(text=f"✅ +{resolution.gained_points} Punkte")

        self._refresh_info()
        self.root.after(900, self._prepare_round)

    def _show_game_over(self) -> None:
        state = self.engine.state
        self.store.save_entry(state.score, state.stats.rounds_played, state.stats.valid_words)
        highscores = self.store.load()[:5]
        highscore_text = "\n".join(
            f"{idx + 1}. {entry.score} Punkte ({entry.timestamp_utc[:10]})" for idx, entry in enumerate(highscores)
        )

        self.over_stats.config(
            text=(
                f"Punkte: {state.score}\n"
                f"Runden: {state.stats.rounds_played}\n"
                f"Gültige Wörter: {state.stats.valid_words}\n"
                f"Ungültige Wörter: {state.stats.invalid_words}\n"
                f"Ø Reaktionszeit: {state.stats.average_reaction_time:.2f}s\n"
                f"KI-Korrekturen: {state.stats.ai_corrections_used}\n\n"
                f"Top Highscores:\n{highscore_text if highscore_text else 'Noch keine Einträge'}"
            )
        )
        self._show_frame(self.over_frame)

    def run(self) -> None:
        self.root.mainloop()
