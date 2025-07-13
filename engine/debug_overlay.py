from __future__ import annotations

from typing import List, Optional

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .game_state import GameState
from .scene_manager import SceneManager
from .world_manager import WorldManager
from .dialogue_engine import DialogueEngine


class DebugOverlay:
    """Render runtime debug information on top of the game."""

    def __init__(
        self,
        game_state: GameState,
        scene_manager: SceneManager,
        world_manager: WorldManager,
        dialogue_engine: DialogueEngine,
        font_path: Optional[str] = None,
        font_size: int = 16,
    ) -> None:
        self.game_state = game_state
        self.scene_manager = scene_manager
        self.world_manager = world_manager
        self.dialogue_engine = dialogue_engine
        self.visible: bool = False
        self.fps: float = 0.0
        if pygame:
            self.font = pygame.font.Font(font_path, font_size)
            self.clock = pygame.time.Clock()
        else:  # pragma: no cover - fallback for tests without pygame
            self.font = None
            self.clock = None

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def toggle_visibility(self) -> None:
        self.visible = not self.visible

    # ------------------------------------------------------------------
    # Update & gather
    # ------------------------------------------------------------------
    def update(self, delta_time: float) -> None:
        if self.clock:
            self.clock.tick()
            self.fps = self.clock.get_fps()
        else:
            self.fps = 1.0 / delta_time if delta_time > 0 else 0.0

    def gather_debug_info(self) -> List[str]:
        info: List[str] = []
        # System panel
        info.append(f"FPS: {self.fps:.1f}")
        if pygame:
            info.append(f"Ticks: {pygame.time.get_ticks()}")
        # World/Scene
        if self.world_manager:
            info.append(f"World: {self.world_manager.world_id}")
            info.append(f"Region: {self.world_manager.current_region_id}")
        info.append(f"Scene: {self.scene_manager.current_scene_id}")
        # Game state flags
        flags = [name for name, val in self.game_state.flags.items() if val]
        if flags:
            info.append("Flags:")
            for name in flags:
                info.append(f"  ✅ {name}")
        if self.game_state.variables:
            info.append("Variables:")
            for key, val in self.game_state.variables.items():
                info.append(f"  {key}: {val}")
        if self.dialogue_engine.active_dialogue_id:
            info.append(f"Dialogue: {self.dialogue_engine.active_dialogue_id}")
        return info

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    def render(self, surface: "pygame.Surface") -> None:
        if not self.visible or not pygame or not self.font:
            return

        lines = self.gather_debug_info()
        if not lines:
            return

        padding = 8
        line_height = self.font.get_height()
        width = max(self.font.size(line)[0] for line in lines) + padding * 2
        height = line_height * len(lines) + padding * 2
        rect = pygame.Rect(5, 5, width, height)
        box = pygame.Surface((width, height), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        surface.blit(box, rect.topleft)
        y = rect.top + padding
        for line in lines:
            text_surf = self.font.render(line, True, (255, 255, 255))
            surface.blit(text_surf, (rect.left + padding, y))
            y += line_height


