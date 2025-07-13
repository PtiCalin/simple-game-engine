from __future__ import annotations

from typing import Optional, Tuple, List, Dict

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .hotspot import Hotspot


class UIOverlay:
    """Utility class for drawing simple UI elements on a screen."""

    DEFAULT_THEME: Dict[str, Tuple[int, int, int] | int] = {
        "font_color": (255, 255, 255),
        "box_bg_color": (10, 10, 10, 180),
        "tooltip_bg_color": (0, 0, 0, 200),
        "font_size": 18,
        "padding": 12,
    }

    def __init__(
        self,
        screen: "pygame.Surface",
        font_path: Optional[str] = None,
        font_size: int | None = None,
        theme: Optional[Dict] = None,
    ) -> None:
        self.screen = screen
        self.theme = dict(self.DEFAULT_THEME)
        if theme:
            self.theme.update(theme)
        if font_size is not None:
            self.theme["font_size"] = font_size
        self.font = (
            pygame.font.Font(font_path, int(self.theme["font_size"]))
            if pygame
            else None
        )
        self.hover_text: Optional[str] = None
        self.hover_pos: Tuple[int, int] | None = None

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _draw_box(
        self, rect: "pygame.Rect", color: Tuple[int, int, int, int]
    ) -> "pygame.Surface":
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surf.fill(color)
        self.screen.blit(surf, rect.topleft)
        return surf

    def _render_text(self, text: str) -> Optional["pygame.Surface"]:
        if not pygame or not self.font:
            return None
        return self.font.render(text, True, self.theme["font_color"])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def draw_dialogue_box(self, text: str, speaker: Optional[str] = None) -> None:
        if not pygame or not self.font:
            return
        width, height = self.screen.get_size()
        padding = int(self.theme["padding"])
        box_height = self.font.get_height() * 4 + padding * 2
        rect = pygame.Rect(
            padding,
            height - box_height - padding,
            width - padding * 2,
            box_height,
        )
        self._draw_box(rect, self.theme["box_bg_color"])

        y = rect.top + padding
        if speaker:
            speaker_surf = self._render_text(speaker)
            if speaker_surf:
                self.screen.blit(speaker_surf, (rect.left + padding, y))
                y += speaker_surf.get_height() + 4
        text_surf = self._render_text(text)
        if text_surf:
            self.screen.blit(text_surf, (rect.left + padding, y))

    def draw_options(self, options: List[str]) -> None:  # pragma: no cover - UI only
        """Render a numbered list of options below the dialogue box."""
        if not pygame or not self.font:
            return
        padding = int(self.theme["padding"])
        width, height = self.screen.get_size()
        y = height - padding - self.font.get_height() * len(options) - 5
        for idx, text in enumerate(options, 1):
            surf = self._render_text(f"{idx}. {text}")
            if surf:
                self.screen.blit(surf, (padding * 2, y))
                y += surf.get_height() + 4

    def draw_tooltip(self, text: str, position: Tuple[int, int]) -> None:
        if not pygame or not self.font:
            return
        surf = self._render_text(text)
        if not surf:
            return
        padding = int(self.theme["padding"] // 2)
        rect = pygame.Rect(
            position[0],
            position[1] - surf.get_height() - padding * 2,
            surf.get_width() + padding * 2,
            surf.get_height() + padding * 2,
        )
        self._draw_box(rect, self.theme["tooltip_bg_color"])
        self.screen.blit(surf, (rect.left + padding, rect.top + padding))

    def draw_label(
        self, text: str, position: Tuple[int, int], style: str = "default"
    ) -> None:
        if not pygame or not self.font:
            return
        surf = self._render_text(text)
        if surf:
            self.screen.blit(surf, position)

    def draw_fps(self, clock: "pygame.time.Clock") -> None:
        if not pygame or not self.font:
            return
        fps_text = f"{clock.get_fps():.1f} FPS"
        self.draw_label(fps_text, (5, 5), style="fps")

    def clear_overlay(self) -> None:
        self.hover_text = None
        self.hover_pos = None

    def update_mouse_hover(self, hotspots: List[Hotspot]) -> None:
        if not pygame:
            return
        pos = pygame.mouse.get_pos()
        self.hover_text = None
        self.hover_pos = pos
        for hs in hotspots:
            if hs.rect().collidepoint(pos):
                self.hover_text = hs.id
                break
        if self.hover_text and self.hover_pos:
            self.draw_tooltip(self.hover_text, self.hover_pos)
