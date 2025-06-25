from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Type, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - allow tests without PyYAML
    yaml = None

try:
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .game_state import GameState


@dataclass
class PuzzleMeta:
    """Metadata describing a puzzle entry."""

    id: str
    type: str
    scene: str
    solved: bool = False
    description: str = ""


class BasePuzzle:
    """Base class for all puzzle implementations."""

    def __init__(self, meta: PuzzleMeta, engine: "PuzzleEngine") -> None:
        self.meta = meta
        self.engine = engine

    def start(self) -> None:
        """Initialize puzzle state when activated."""
        pass

    def handle_event(self, event) -> None:  # pragma: no cover - UI only
        if not pygame:
            return

    def render(self, screen) -> None:  # pragma: no cover - UI only
        if not pygame:
            return

    def solve(self) -> None:
        """Mark this puzzle as solved through the engine."""
        self.engine.mark_solved(self.meta.id)


class LogicPuzzle(BasePuzzle):
    pass


class MemoryPuzzle(BasePuzzle):
    pass


class SymbolPuzzle(BasePuzzle):
    pass


class PhysicsPuzzle(BasePuzzle):
    pass


class PuzzleEngine:
    """Load puzzles from YAML and instantiate puzzle handlers."""

    def __init__(self, state: GameState) -> None:
        self.state = state
        self.registry: Dict[str, PuzzleMeta] = {}
        self.handlers: Dict[str, Type[BasePuzzle]] = {
            "logic": LogicPuzzle,
            "memory": MemoryPuzzle,
            "symbol": SymbolPuzzle,
            "physics": PhysicsPuzzle,
        }

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def load_file(self, path: str) -> None:
        """Load puzzle metadata from a YAML file."""
        with open(path, "r") as fh:
            if yaml:
                data = yaml.safe_load(fh) or {}
            else:  # pragma: no cover - fallback when PyYAML missing
                import json

                data = json.load(fh)
        for entry in data.get("puzzles", []):
            if not isinstance(entry, dict):
                continue
            puzzle = PuzzleMeta(
                id=entry.get("id", ""),
                type=entry.get("type", "logic"),
                scene=entry.get("scene", ""),
                solved=bool(entry.get("solved", False)),
                description=entry.get("description", ""),
            )
            self.registry[puzzle.id] = puzzle

    # ------------------------------------------------------------------
    # Puzzle status
    # ------------------------------------------------------------------
    def mark_solved(self, puzzle_id: str) -> None:
        """Set the solved flag for ``puzzle_id`` in :class:`GameState`."""
        self.state.set_flag(f"puzzle_{puzzle_id}", True)
        self.state.save()

    def is_solved(self, puzzle_id: str) -> bool:
        """Return True if ``puzzle_id`` is marked solved."""
        return self.state.get_flag(f"puzzle_{puzzle_id}")

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    def create(self, puzzle_id: str) -> Optional[BasePuzzle]:
        meta = self.registry.get(puzzle_id)
        if not meta:
            return None
        cls = self.handlers.get(meta.type, BasePuzzle)
        return cls(meta, self)
