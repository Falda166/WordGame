from __future__ import annotations

from dataclasses import dataclass, field
import logging

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class HFCorrector:
    model_name: str
    enabled: bool = False
    _is_loaded: bool = field(default=False, init=False)
    _cache: dict[str, str] = field(default_factory=dict, init=False)
    _tokenizer: object | None = field(default=None, init=False, repr=False)
    _model: object | None = field(default=None, init=False, repr=False)

    def _lazy_load(self) -> bool:
        if not self.enabled:
            return False
        if self._is_loaded:
            return True

        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except Exception as exc:  # pragma: no cover - optional dependency
            LOGGER.warning("Transformers nicht verfügbar, KI-Korrektur deaktiviert: %s", exc)
            self.enabled = False
            return False

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self._is_loaded = True
            LOGGER.info("HF-Korrekturmodell geladen: %s", self.model_name)
            return True
        except Exception as exc:  # pragma: no cover - model/download errors
            LOGGER.warning("HF-Korrekturmodell konnte nicht geladen werden: %s", exc)
            self.enabled = False
            return False

    def correct(self, text: str) -> str | None:
        normalized = text.strip().lower()
        if not normalized:
            return None
        if normalized in self._cache:
            return self._cache[normalized]
        if not self._lazy_load():
            return None

        try:
            inputs = self._tokenizer([normalized], return_tensors="pt", truncation=True)
            output_ids = self._model.generate(**inputs, max_new_tokens=5, num_beams=4)
            corrected = self._tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip().lower()
            corrected = corrected.split()[0] if corrected else ""
            if corrected:
                self._cache[normalized] = corrected
                return corrected
            return None
        except Exception as exc:  # pragma: no cover - runtime errors
            LOGGER.warning("HF-Inferenz fehlgeschlagen: %s", exc)
            return None
