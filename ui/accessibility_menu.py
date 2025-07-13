from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

try:  # pragma: no cover - allow running tests without pygame
    import pygame  # type: ignore
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from engine.accessibility_manager import AccessibilityManager


@dataclass
class MenuEntry:
    label: str
    key: str
    values: List
    index: int = 0


class AccessibilityMenu:
    """Simple in-game menu to tweak :class:`AccessibilityManager` options."""

    def __init__(self, manager: AccessibilityManager, font_path: Optional[str] = None) -> None:
        self.manager = manager
        self.visible = False
        self.entries: List[MenuEntry] = [
            MenuEntry("Text Size", "font_scale", [0.8, 1.0, 1.3, 1.6]),
            MenuEntry("Contrast", "contrast_mode", ["default", "high_contrast", "night"]),
            MenuEntry("Subtitles", "subtitles_enabled", [True, False]),
            MenuEntry("Captions", "captions_enabled", [True, False]),
            MenuEntry("Reduce Motion", "motion_reduction", [True, False]),
            MenuEntry("Input Delay", "input_delay_buffer", [0.0, 0.1, 0.2, 0.5]),
        ]
        for entry in self.entries:
            current = self.manager.get_option(entry.key)
            if current in entry.values:
                entry.index = entry.values.index(current)
        self.selected = 0
        if pygame:
            self.font = pygame.font.Font(font_path, 24)
        else:
            self.font = None

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
    def navigate(self, direction: int) -> None:
        self.selected = (self.selected + direction) % len(self.entries)

    def adjust(self, delta: int) -> None:
        entry = self.entries[self.selected]
        entry.index = (entry.index + delta) % len(entry.values)
        self.manager.set_option(entry.key, entry.values[entry.index])

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------
    def handle_input(self, event: "pygame.event.Event") -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.navigate(-1)
            elif event.key == pygame.K_DOWN:
                self.navigate(1)
            elif event.key == pygame.K_LEFT:
                self.adjust(-1)
            elif event.key == pygame.K_RIGHT:
                self.adjust(1)
            elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.visible = False
                self.manager.save_settings()

    # ------------------------------------------------------------------
    # Rendering (minimal placeholder)
    # ------------------------------------------------------------------
    def render(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not pygame or not self.font or not self.visible:
            return
        surface.fill((0, 0, 0))
        for idx, entry in enumerate(self.entries):
            prefix = "-> " if idx == self.selected else "   "
            value = entry.values[entry.index]
            label = f"{prefix}{entry.label}: {value}"
            color = (255, 255, 0) if idx == self.selected else (255, 255, 255)
            surf = self.font.render(label, True, color)
            surface.blit(surf, (40, 40 + idx * 30))
