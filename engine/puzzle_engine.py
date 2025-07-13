from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Optional, Type

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
    data: dict[str, Any] = field(default_factory=dict)
    solution: Any = None
    condition: Optional[str] = None
    on_solve: Any = field(default_factory=dict)


class PuzzleBase:
    """Base class for all puzzle implementations."""

    def __init__(self, meta: PuzzleMeta, engine: "PuzzleEngine") -> None:
        self.meta = meta
        self.engine = engine
        self.solved = False

    def start(self) -> None:
        """Initialize puzzle state when activated."""
        return None

    def update(self) -> None:
        """Update internal state each frame."""
        return None

    def render(self, screen) -> None:  # pragma: no cover - UI only
        if not pygame:
            return

    def handle_input(self, event) -> None:  # pragma: no cover - UI only
        if not pygame:
            return

    def mark_solved(self) -> None:
        self.solved = True
        self.engine.mark_solved(self.meta.id)

    def is_solved(self) -> bool:
        return self.solved

    def check_solution(self, player_input: Any) -> bool:
        """Check ``player_input`` against ``meta.solution``."""
        if player_input == self.meta.solution:
            self.mark_solved()
            return True
        return False


class LogicPuzzle(PuzzleBase):
    """Simple sequence/logic puzzle."""

    def check_solution(self, player_input: Any) -> bool:
        solution = self.meta.solution or self.meta.data.get("solution")
        if player_input == solution:
            self.mark_solved()
            return True
        return False


class ManipulationPuzzle(PuzzleBase):
    """Drag or arrange items into the correct order."""

    def check_solution(self, player_input: Any) -> bool:
        solution = self.meta.solution or self.meta.data.get("solution")
        if player_input == solution:
            self.mark_solved()
            return True
        return False


class DeductionPuzzle(PuzzleBase):
    """Combine clues to reach the correct conclusion."""

    def __init__(self, meta: PuzzleMeta, engine: "PuzzleEngine") -> None:
        super().__init__(meta, engine)
        self.clues: set[Any] = set()

    def add_clue(self, clue: Any) -> None:
        self.clues.add(clue)
        required = set(self.meta.solution or self.meta.data.get("solution", []))
        if required and required.issubset(self.clues):
            self.mark_solved()


# backward compatibility alias
BasePuzzle = PuzzleBase


class PuzzleEngine:
    """Load puzzles from YAML and instantiate puzzle handlers."""

    def __init__(
        self,
        state: GameState,
        ui_overlay: "UIOverlay | None" = None,
        scene_manager: "SceneManager | None" = None,
    ) -> None:
        self.state = state
        self.registry: Dict[str, PuzzleMeta] = {}
        self.handlers: Dict[str, Type[PuzzleBase]] = {
            "logic": LogicPuzzle,
            "manipulation": ManipulationPuzzle,
            "deduction": DeductionPuzzle,
        }
        self._load_builtin_types()
        self.active_puzzle: Optional[PuzzleBase] = None
        self.ui_overlay = ui_overlay
        self.scene_manager = scene_manager

    def _load_builtin_types(self) -> None:
        """Import puzzle modules from ``engine.puzzle_types`` if available."""
        pkg_path = Path(__file__).with_name("puzzle_types")
        if not pkg_path.exists():
            return
        try:
            loader = import_module("engine.puzzle_types").load_types
        except Exception:
            return
        for name, cls in loader().items():
            self.handlers[name] = cls

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def load_file(self, path: str) -> None:
        """Load puzzle metadata from a YAML or JSON file."""
        with open(path, "r", encoding="utf-8") as fh:
            if yaml:
                data = yaml.safe_load(fh) or {}
            else:  # pragma: no cover - fallback when PyYAML missing
                import json

                data = json.load(fh)

        entries = []
        if "puzzles" in data and isinstance(data["puzzles"], list):
            entries = data["puzzles"]
        elif "puzzle" in data and isinstance(data["puzzle"], dict):
            entries = [data["puzzle"]]

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            puzzle = PuzzleMeta(
                id=entry.get("id", ""),
                type=entry.get("type", "logic"),
                scene=entry.get("scene", ""),
                solved=bool(entry.get("solved", False)),
                description=entry.get("description", ""),
                data=entry.get("data", {}) or {},
                solution=entry.get("solution"),
                condition=entry.get("condition"),
                on_solve=entry.get("on_solve", {}) or {},
            )
            self.registry[puzzle.id] = puzzle

    def load_from_yaml(self, scene_id: str, data: Dict[str, Any]) -> None:
        """Load puzzle definitions from already parsed scene YAML."""
        entries = data.get("puzzles", [])
        if not isinstance(entries, list):
            return
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            puzzle = PuzzleMeta(
                id=entry.get("id", ""),
                type=entry.get("type", "logic"),
                scene=scene_id,
                solved=bool(entry.get("solved", False)),
                description=entry.get("description", ""),
                data=entry.get("data", {}) or {},
                solution=entry.get("solution"),
                condition=entry.get("conditions") or entry.get("condition"),
                on_solve=entry.get("on_solve", {}) or {},
            )
            self.registry[puzzle.id] = puzzle

    def register_type(self, name: str, cls: Type[PuzzleBase]) -> None:
        """Register a new puzzle handler class."""
        self.handlers[name] = cls

    def load_puzzle(self, puzzle_data: dict[str, Any]) -> PuzzleBase:
        """Instantiate a puzzle from raw data and set it active."""
        meta = PuzzleMeta(
            id=puzzle_data.get("id", ""),
            type=puzzle_data.get("type", "logic"),
            scene=puzzle_data.get("scene", ""),
            solved=bool(puzzle_data.get("solved", False)),
            description=puzzle_data.get("description", ""),
            data=puzzle_data.get("data", {}) or {},
            solution=puzzle_data.get("solution"),
            condition=puzzle_data.get("condition"),
            on_solve=puzzle_data.get("on_solve", {}) or {},
        )
        cls = self.handlers.get(meta.type, PuzzleBase)
        puzzle = cls(meta, self)
        self.active_puzzle = puzzle
        puzzle.start()
        return puzzle

    # ------------------------------------------------------------------
    # Puzzle status
    # ------------------------------------------------------------------
    def mark_solved(self, puzzle_id: str) -> None:
        """Set the solved flag for ``puzzle_id`` and handle actions."""
        self.state.set_flag(f"puzzle_{puzzle_id}", True)
        self.state.save()
        meta = self.registry.get(puzzle_id)
        if meta:
            meta.solved = True
            actions = meta.on_solve
        else:
            actions = {}
        if isinstance(actions, list):
            acts = actions
        else:
            acts = [actions]
        for act in acts:
            if not isinstance(act, dict):
                continue
            if act.get("set_flag"):
                self.state.set_flag(act["set_flag"], True)
            if act.get("go_to_scene") and self.scene_manager:
                self.scene_manager.open_scene(act["go_to_scene"])
            if act.get("show_dialogue") and self.ui_overlay:
                self.ui_overlay.draw_dialogue_box(act["show_dialogue"])

    def is_solved(self, puzzle_id: str) -> bool:
        """Return True if ``puzzle_id`` is marked solved."""
        return self.state.get_flag(f"puzzle_{puzzle_id}")

    # ------------------------------------------------------------------
    # Active Puzzle
    # ------------------------------------------------------------------
    def update(self) -> None:
        if self.active_puzzle:
            self.active_puzzle.update()

    def render(self, surface) -> None:  # pragma: no cover - UI only
        if self.active_puzzle:
            self.active_puzzle.render(surface)

    def handle_input(self, event) -> None:  # pragma: no cover - UI only
        if self.active_puzzle:
            self.active_puzzle.handle_input(event)

    def active_solved(self) -> bool:
        return self.active_puzzle.is_solved() if self.active_puzzle else False

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    def create(self, puzzle_id: str) -> Optional[PuzzleBase]:
        meta = self.registry.get(puzzle_id)
        if not meta:
            return None
        cls = self.handlers.get(meta.type, PuzzleBase)
        return cls(meta, self)

    def check(self, puzzle_id: str, player_input: Any) -> bool:
        """Validate ``player_input`` for ``puzzle_id`` and mark solved if correct."""
        puzzle = self.create(puzzle_id)
        if not puzzle:
            return False
        return puzzle.check_solution(player_input)
