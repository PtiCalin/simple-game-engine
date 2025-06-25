from dataclasses import dataclass
from typing import Tuple, Optional
import pygame

@dataclass
class Hotspot:
    """Interactive region that triggers an action when clicked."""

    id: str
    area: Tuple[int, int, int, int]
    action: str
    target: Optional[str] = None

    def rect(self) -> pygame.Rect:
        """Return the pygame.Rect representing this hotspot's area."""
        return pygame.Rect(self.area)

    def check_click(self, pos: Tuple[int, int]) -> bool:
        """Return True if the given position is inside the hotspot."""
        return self.rect().collidepoint(pos)

    def trigger(self, manager: "SceneManager") -> None:
        """Execute the hotspot's action using the provided scene manager."""
        if self.action == "open_scene" and self.target:
            manager.open_scene(self.target)
        elif self.action == "show_dialogue" and self.target:
            manager.show_dialogue(self.target)
        elif self.action == "toggle_flag" and self.target:
            manager.toggle_flag(self.target)
        elif self.action == "teleport" and self.target:
            region, _, scene = self.target.partition(":")
            manager.teleport(region, scene or None)

