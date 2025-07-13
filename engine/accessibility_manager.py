from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import typing
import os
import json

try:  # pragma: no cover - allow tests without PyYAML
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None

try:  # pragma: no cover - allow running tests without pygame installed
    import pygame  # type: ignore
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

if typing.TYPE_CHECKING:  # pragma: no cover - only for type hints
    from .ui_overlay import UIOverlay


@dataclass
class AccessibilityManager:
    """Manage accessibility preferences and apply them across the UI."""

    font_scale: float = 1.0
    contrast_mode: str = "default"
    subtitles_enabled: bool = True
    captions_enabled: bool = False
    motion_reduction: bool = False
    input_delay_buffer: float = 0.0
    ui_theme: str = "default"
    save_file: str = "config/accessibility.yaml"
    ui_overlay: Optional["UIOverlay"] = None

    def __post_init__(self) -> None:
        if os.path.exists(self.save_file):
            self.load_settings(self.save_file)
        else:
            self.apply_ui_settings()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def load_settings(self, path: str) -> None:
        """Load accessibility options from ``path``."""
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as fh:
            if path.endswith(".json"):
                data = json.load(fh)
            else:
                if yaml:
                    data = yaml.safe_load(fh) or {}
                else:  # pragma: no cover - fallback when PyYAML missing
                    data = json.load(fh)
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.apply_ui_settings()

    def save_settings(self, path: Optional[str] = None) -> None:
        """Persist current settings to ``path`` or ``save_file``."""
        path = path or self.save_file
        data = {
            "font_scale": self.font_scale,
            "contrast_mode": self.contrast_mode,
            "subtitles_enabled": self.subtitles_enabled,
            "captions_enabled": self.captions_enabled,
            "motion_reduction": self.motion_reduction,
            "input_delay_buffer": self.input_delay_buffer,
            "ui_theme": self.ui_theme,
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            if path.endswith(".json"):
                json.dump(data, fh, indent=2, ensure_ascii=False)
            else:
                if yaml:
                    yaml.safe_dump(data, fh)
                else:  # pragma: no cover - fallback when PyYAML missing
                    json.dump(data, fh, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Application helpers
    # ------------------------------------------------------------------
    def apply_ui_settings(self) -> None:
        """Apply visual settings to the active :class:`UIOverlay`."""
        if not self.ui_overlay or not pygame:
            return
        base_size = self.ui_overlay.theme.get("font_size", 18)
        scaled_size = int(base_size * self.font_scale)
        if scaled_size != self.ui_overlay.theme.get("font_size"):
            self.ui_overlay.theme["font_size"] = scaled_size
            self.ui_overlay.font = pygame.font.Font(None, scaled_size)

        if self.contrast_mode == "high_contrast":
            self.ui_overlay.theme["font_color"] = (0, 0, 0)
            self.ui_overlay.theme["box_bg_color"] = (255, 255, 255, 230)
        elif self.contrast_mode == "night":
            self.ui_overlay.theme["font_color"] = (200, 200, 200)
            self.ui_overlay.theme["box_bg_color"] = (20, 20, 20, 230)
        else:
            from .ui_overlay import UIOverlay

            self.ui_overlay.theme["font_color"] = UIOverlay.DEFAULT_THEME["font_color"]
            self.ui_overlay.theme["box_bg_color"] = UIOverlay.DEFAULT_THEME["box_bg_color"]

    # ------------------------------------------------------------------
    # Options API
    # ------------------------------------------------------------------
    def set_option(self, key: str, value: Any) -> None:
        """Set a single option and apply changes."""
        if hasattr(self, key):
            setattr(self, key, value)
            if key != "save_file" and key != "ui_overlay":
                self.apply_ui_settings()

    def get_option(self, key: str) -> Any:
        """Retrieve the value of ``key`` if available."""
        return getattr(self, key, None)
