from __future__ import annotations

from typing import Optional

try:
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .game_state import GameState
from .puzzle_engine import PuzzleEngine, PuzzleBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from .ui_overlay import UIOverlay
    from .scene_manager import SceneManager


class PuzzleManager:
    """Handle puzzle lifecycle and rendering."""

    def __init__(
        self,
        state: GameState,
        ui_overlay: "UIOverlay | None" = None,
        scene_manager: "SceneManager | None" = None,
    ) -> None:
        self.state = state
        self.engine = PuzzleEngine(
            state, ui_overlay=ui_overlay, scene_manager=scene_manager
        )
        self.active: Optional[PuzzleBase] = None
        self.active_id: Optional[str] = None

    def load_file(self, path: str) -> None:
        """Load puzzle registry from ``path``."""
        self.engine.load_file(path)

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------
    def start(self, puzzle_id: str) -> None:
        puzzle = self.engine.create(puzzle_id)
        if not puzzle:
            return
        self.active = puzzle
        self.active_id = puzzle_id
        self.engine.active_puzzle = puzzle
        puzzle.start()

    def complete_puzzle(self) -> None:
        if self.active_id:
            self.engine.mark_solved(self.active_id)
        self.active = None
        self.engine.active_puzzle = None
        self.active_id = None

    # ------------------------------------------------------------------
    # Interaction helpers
    # ------------------------------------------------------------------
    def handle_event(self, event) -> None:  # pragma: no cover - UI only
        if self.active:
            self.active.handle_input(event)

    def draw(self, screen) -> None:  # pragma: no cover - UI only
        if self.active:
            self.active.render(screen)

    def update(self) -> None:
        if self.active:
            self.active.update()
