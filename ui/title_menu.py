from __future__ import annotations

from typing import List, Optional
from dataclasses import dataclass

try:  # pragma: no cover - allow running tests without pygame
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from engine.save_system import SaveSystem, SaveSlot


@dataclass
class MenuOption:
    label: str
    action: str


class TitleMenu:
    """Basic title menu with save slot handling."""

    def __init__(self, save_system: SaveSystem, font_path: Optional[str] = None) -> None:
        self.save_system = save_system
        self.visible = True
        self.selected_option = "new_game"
        self.menu_state = "main"
        self.save_slots: List[SaveSlot] = []
        self.options: List[MenuOption] = [
            MenuOption("New Game", "new_game"),
            MenuOption("Continue", "continue"),
            MenuOption("Quit", "quit"),
        ]
        if pygame:
            self.font = pygame.font.Font(font_path, 24)
        else:
            self.font = None
        self.load_save_slots()

    # ------------------------------------------------------------------
    # Slot helpers
    # ------------------------------------------------------------------
    def load_save_slots(self) -> None:
        self.save_slots = [self.save_system.save_slots.get(i) for i in range(1, 4)]

    def start_new_game(self, slot_id: int) -> None:
        self.save_system.current_slot = slot_id
        # Actual game start logic would go here

    def load_game(self, slot_id: int) -> None:
        self.save_system.load_game(slot_id)
        # Actual game load logic would go here

    def delete_save(self, slot_id: int) -> None:
        self.save_system.delete_save(slot_id)
        self.load_save_slots()

    # ------------------------------------------------------------------
    # Input handling (minimal placeholder logic)
    # ------------------------------------------------------------------
    def navigate_menu(self, direction: int) -> None:
        idx = next((i for i, o in enumerate(self.options) if o.action == self.selected_option), 0)
        idx = (idx + direction) % len(self.options)
        self.selected_option = self.options[idx].action

    def select_option(self) -> str:
        return self.selected_option

    def handle_input(self, event: "pygame.event.Event") -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.navigate_menu(-1)
            elif event.key == pygame.K_DOWN:
                self.navigate_menu(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.select_option()

    # ------------------------------------------------------------------
    # Rendering (minimal placeholder)
    # ------------------------------------------------------------------
    def render(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not pygame or not self.font:
            return
        surface.fill((0, 0, 0))
        for idx, option in enumerate(self.options):
            color = (255, 255, 0) if option.action == self.selected_option else (255, 255, 255)
            surf = self.font.render(option.label, True, color)
            surface.blit(surf, (50, 50 + idx * 30))
