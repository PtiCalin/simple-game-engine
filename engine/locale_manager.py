from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set, List
import os

try:  # pragma: no cover - allow tests without PyYAML
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None


@dataclass
class LocaleManager:
    """Manage text translations and current language."""

    current_locale: str = "en"
    translations: Dict[str, Dict[str, str]] = field(default_factory=dict)
    fallback_locale: str = "en"
    locales_dir: str = "locales/"
    missing_keys: Set[str] = field(default_factory=set)

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------
    def load_locales(self, path: str) -> None:
        """Load all ``*.yaml`` files from ``path`` into ``translations``."""
        if not os.path.isdir(path):
            return
        self.locales_dir = path
        for fname in os.listdir(path):
            if not fname.endswith(".yaml"):
                continue
            locale_code = os.path.splitext(fname)[0]
            fpath = os.path.join(path, fname)
            with open(fpath, "r", encoding="utf-8") as fh:
                if yaml:
                    data = yaml.safe_load(fh) or {}
                else:  # pragma: no cover - fallback when PyYAML missing
                    import json

                    data = json.load(fh)
            flat: Dict[str, str] = {}
            self._flatten(data, flat)
            self.translations[locale_code] = flat

    def _flatten(self, data: Dict, out: Dict[str, str], prefix: str = "") -> None:
        for key, value in (data or {}).items():
            compound = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                self._flatten(value, out, compound)
            else:
                out[compound] = str(value)

    # ------------------------------------------------------------------
    # Locale helpers
    # ------------------------------------------------------------------
    def set_locale(self, locale_code: str) -> None:
        """Switch the active locale to ``locale_code``."""
        self.current_locale = locale_code

    def _locale_chain(self, locale_code: str) -> List[str]:
        chain = [locale_code]
        if "-" in locale_code:
            base = locale_code.split("-")[0]
            if base not in chain:
                chain.append(base)
        if self.fallback_locale not in chain:
            chain.append(self.fallback_locale)
        return chain

    def translate(self, key: str) -> str:
        """Return the translated string for ``key``."""
        for loc in self._locale_chain(self.current_locale):
            entry = self.translations.get(loc, {}).get(key)
            if entry is not None:
                return entry
        self.log_missing_key(key)
        return key

    def has_translation(self, key: str) -> bool:
        """Return ``True`` if ``key`` exists in the current locale chain."""
        for loc in self._locale_chain(self.current_locale):
            if key in self.translations.get(loc, {}):
                return True
        return False

    def get_available_locales(self) -> List[str]:
        """Return all loaded locale codes."""
        return sorted(self.translations.keys())

    # ------------------------------------------------------------------
    # Missing key helpers
    # ------------------------------------------------------------------
    def log_missing_key(self, key: str) -> None:
        self.missing_keys.add(key)

    def export_missing_keys(self, file_path: str) -> None:
        if not self.missing_keys:
            return
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            for key in sorted(self.missing_keys):
                fh.write(key + "\n")

