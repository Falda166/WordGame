#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip >/dev/null
python -m pip install -r "$ROOT_DIR/requirements.txt" >/dev/null

ai_enabled=1
ai_flag_seen=0
help_only=0
for arg in "$@"; do
  case "$arg" in
    --ai-correction)
      ai_enabled=1
      ai_flag_seen=1
      ;;
    --no-ai-correction)
      ai_enabled=0
      ai_flag_seen=1
      ;;
    -h|--help)
      help_only=1
      ;;
  esac
done

extra_args=()
if [[ $ai_flag_seen -eq 0 ]]; then
  extra_args+=("--ai-correction")
fi

if [[ $ai_enabled -eq 1 && $help_only -eq 0 ]]; then
  if ! python -m pip install transformers torch >/dev/null; then
    echo "WARNUNG: KI-Abhängigkeiten konnten nicht vollständig installiert werden; starte ohne KI-Korrektur." >&2
    extra_args=("--no-ai-correction")
  fi
fi

exec python "$ROOT_DIR/main.py" "$@" "${extra_args[@]}"
