# Silben-Bombe (Deutsch)

Eine robuste Python-Anwendung für ein deutsches Wortspiel mit **hybrider Wortvalidierung**:

1. **Harte Entscheidung über Wörterbuch (Hunspell/igerman98-kompatibel)**
2. **Optionale KI-Tippfehlerkorrektur** (`oliverguhr/spelling-correction-german-base`) nur als zweite Stufe

Warum hybrid? Ein Sprachmodell alleine liefert keine verlässliche Ja/Nein-Entscheidung für echte Wörter. Deshalb bleibt das Wörterbuch immer die autoritative Instanz.

---

## Features

- Tkinter-GUI (primär) + CLI-Fallback
- 6 Leben, Bomben-Countdown pro Runde
- Zufällige 2-3-Buchstaben-Silben (aus Wortschatz extrahiert)
- Wortvalidierung inkl.:
  - Normalisierung (Unicode NFC, lowercase)
  - Silben-Check
  - Duplicate-Check
  - Wörterbuch-Check
  - optionale HF-Korrektur + Re-Check gegen Wörterbuch
- Punktesystem mit Basis-, Längen-, Geschwindigkeits- und Präzisionsbonus
- Lokale Highscores (JSON)
- Deutsche Sonderzeichen (ä, ö, ü, ß)

---

## Projektstruktur

```text
.
├── main.py
├── requirements.txt
├── README.md
├── data/
│   ├── wordlist_de_fallback.txt
│   └── highscores.json (wird automatisch erzeugt)
└── game/
    ├── config.py
    ├── dictionary.py
    ├── engine.py
    ├── hf_correction.py
    ├── highscore.py
    ├── models.py
    ├── scoring.py
    ├── syllables.py
    ├── timer.py
    ├── ui_cli.py
    ├── ui_tk.py
    └── validator.py
```

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Optional: KI-Korrektur aktivieren

```bash
pip install transformers torch
```

> Hinweis: Das erste Laden des HF-Modells kann spürbar dauern.

---

## Wörterbuch-Setup (empfohlen)

Für produktive Qualität sollten Hunspell-Dateien bereitgestellt werden:

- `dictionaries/de_DE.aff`
- `dictionaries/de_DE.dic`

Die App erkennt diese automatisch und nutzt sie als Hauptquelle.
Wenn die Dateien fehlen, wird eine lokale Fallback-Wortliste verwendet.

---

## Starten

### GUI (Standard)

```bash
python main.py
```

### CLI

```bash
python main.py --cli
```

### Mit Optionen

```bash
python main.py --difficulty schwer --ai-correction
python main.py --cli --difficulty leicht
```

---

## Regeln

- Start mit 6 Leben
- Pro Runde wird eine Silbe/Buchstabenfolge (2-3 Zeichen) angezeigt
- Eingabe muss:
  - ein gültiges deutsches Wort sein (Wörterbuch)
  - die Silbe enthalten
  - noch nicht im aktuellen Spiel benutzt worden sein
- Zeit abgelaufen oder ungültige Eingabe: -1 Leben
- Spiel endet bei 0 Leben

---

## Qualitäts- und Robustheitsaspekte

- Klare Trennung von UI, Spiellogik und Validierung
- Strukturierte Rückgaben (`ValidationResult`)
- Fail-safe KI-Integration (bei Fehlern läuft Spiel ohne KI weiter)
- Keine magischen Zahlen in der Logik (zentral in `GameConfig`)

