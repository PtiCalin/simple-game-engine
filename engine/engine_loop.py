from __future__ import annotations

from typing import List

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .scene_manager import SceneManager


class EngineLoop:
    """Central game loop manager with scene stack support."""

    def __init__(self, screen: "pygame.Surface", initial_scene_path: str, scene_manager: SceneManager, debug: bool = False) -> None:
        self.screen = screen
        self.initial_scene = initial_scene_path
        self.scene_manager = scene_manager
        self.scene_stack: List[str] = []
        self.clock = pygame.time.Clock() if pygame else None
        self.running = False
        self.debug = debug
        self.fps_font = pygame.font.Font(None, 18) if debug and pygame else None

    # ------------------------------------------------------------------
    # Scene stack helpers
    # ------------------------------------------------------------------
    def change_scene(self, path: str) -> None:
        """Clear the stack and load a new scene."""
        self.scene_stack = [path]
        self.scene_manager.open_scene(path)

    def push_scene(self, path: str) -> None:
        """Push a new scene onto the stack."""
        self.scene_stack.append(path)
        self.scene_manager.open_scene(path)

    def pop_scene(self) -> None:
        """Pop the top scene from the stack and reopen the previous one."""
        if self.scene_stack:
            self.scene_stack.pop()
        if not self.scene_stack:
            self.stop()
            return
        self.scene_manager.open_scene(self.scene_stack[-1])

    def stop(self) -> None:
        """End the main loop."""
        self.running = False

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:  # pragma: no cover - UI loop
        if not pygame:
            return
        if not self.scene_stack:
            self.change_scene(self.initial_scene)
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.scene_manager.dialogue_engine.active:
                    self.scene_manager.dialogue_engine.handle_event(event)
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for hs in self.scene_manager.hotspots:
                        if not hs.is_active(self.scene_manager.game_state):
                            continue
                        if hs.check_click(event.pos):
                            hs.trigger(self.scene_manager)

            self.screen.fill((0, 0, 0))

            for overlay in self.scene_manager.overlays:
                self.screen.blit(overlay, (0, 0))

            self.scene_manager.timeline_engine.update(
                pygame.time.get_ticks(), self.scene_manager.current_scene_id
            )

            if self.scene_manager.active_features.get("time_loop"):
                duration = self.scene_manager.active_features.get("time_loop")
                if isinstance(duration, bool):
                    duration = 5000
                try:
                    duration = int(duration)
                except (TypeError, ValueError):
                    duration = 5000
                if pygame.time.get_ticks() - self.scene_manager.scene_start_time >= duration:
                    self.scene_manager.activate_scene(self.scene_manager.current_scene)

            self.scene_manager.dialogue_engine.draw(self.screen)

            if self.debug and self.fps_font:
                fps_text = f"{self.clock.get_fps():.1f} FPS" if self.clock else "0 FPS"
                surf = self.fps_font.render(fps_text, True, (255, 0, 0))
                self.screen.blit(surf, (5, 5))

            pygame.display.flip()
            if self.clock:
                self.clock.tick(60)
