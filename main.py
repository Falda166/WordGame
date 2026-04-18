from __future__ import annotations

import argparse
import logging

from game.config import GameConfig
from game.ui_cli import CLIApp
from game.ui_tk import TkApp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deutsches Silben-Bombenspiel")
    parser.add_argument("--cli", action="store_true", help="CLI statt Tkinter-GUI verwenden")
    parser.add_argument(
        "--difficulty",
        choices=["leicht", "normal", "schwer"],
        default="normal",
        help="Schwierigkeitsgrad",
    )
    parser.add_argument("--ai-correction", action="store_true", help="HF-Tippfehlerkorrektur aktivieren")
    parser.add_argument("--debug", action="store_true", help="Debug-Logs aktivieren")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    config = GameConfig(use_ai_correction=args.ai_correction)
    difficulty = config.difficulties[args.difficulty]

    if args.cli:
        CLIApp(config, difficulty).run()
    else:
        try:
            TkApp(config, difficulty).run()
        except Exception as exc:
            logging.exception("GUI-Start fehlgeschlagen (%s). Fallback auf CLI.", exc)
            CLIApp(config, difficulty).run()


if __name__ == "__main__":
    main()
