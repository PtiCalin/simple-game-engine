from __future__ import annotations

from typing import Optional, List, Dict, Any

try:  # pragma: no cover - optional pygame
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

try:  # pragma: no cover - optional PyYAML
    import yaml
except Exception:  # pragma: no cover - allow tests without PyYAML
    yaml = None

from engine.game_state import GameState


class VisualConditionTester:
    """Dev helper for previewing trigger and condition logic."""

    def __init__(
        self,
        game_state: GameState,
        trigger_system: Any | None = None,
        puzzle_engine: Any | None = None,
        npc_system: Any | None = None,
        font_path: Optional[str] = None,
        font_size: int = 16,
    ) -> None:
        self.game_state = game_state
        self.trigger_system = trigger_system
        self.puzzle_engine = puzzle_engine
        self.npc_system = npc_system
        self.visible: bool = False
        self.selected_flag: Optional[str] = None
        self.preview_results: List[Dict[str, Any]] = []
        if pygame:
            self.font = pygame.font.Font(font_path, font_size)
        else:  # pragma: no cover - fallback for tests without pygame
            self.font = None

    # ------------------------------------------------------------------
    # Basic helpers
    # ------------------------------------------------------------------
    def toggle_visibility(self) -> None:
        self.visible = not self.visible

    def evaluate_condition(self, expression: str) -> bool:
        """Evaluate a boolean expression against current flags."""
        if not expression:
            return True
        local = {k: bool(v) for k, v in self.game_state.flags.items()}
        expr = expression.replace("true", "True").replace("false", "False")
        try:
            return bool(eval(expr, {}, local))
        except Exception:
            return False

    def simulate_flag_change(self, flag: str, value: bool) -> None:
        self.game_state.set_flag(flag, value)
        self.refresh_preview_results()

    # ------------------------------------------------------------------
    # Preview management
    # ------------------------------------------------------------------
    def refresh_preview_results(self) -> None:
        for entry in self.preview_results:
            expr = entry.get("expression", "")
            entry["passed"] = self.evaluate_condition(expr)

    def load_conditions_from_yaml(self, file_path: str) -> None:
        """Load trigger conditions from a YAML file."""
        if not yaml:
            raise RuntimeError("PyYAML is required to load condition files")

        with open(file_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        entries = data.get("triggers", [])
        self.preview_results = []
        for trig in entries:
            if not isinstance(trig, dict):
                continue
            expr = trig.get("condition", "")
            self.preview_results.append(
                {
                    "id": trig.get("id", ""),
                    "expression": expr,
                    "passed": self.evaluate_condition(expr),
                }
            )

    # ------------------------------------------------------------------
    # UI (minimal placeholder)
    # ------------------------------------------------------------------
    def render(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not self.visible or not pygame or not self.font:
            return
        padding = 8
        y = padding
        for entry in self.preview_results:
            result = "✅" if entry.get("passed") else "❌"
            text = f"{result} {entry.get('expression')}"
            surf = self.font.render(text, True, (255, 255, 255))
            surface.blit(surf, (padding, y))
            y += surf.get_height() + 4

    def handle_input(self, event: "pygame.event.Event") -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        # Minimal: left/right arrow cycle through flags and toggle with space
        if event.type == pygame.KEYDOWN and self.game_state.flags:
            keys = list(self.game_state.flags.keys())
            if self.selected_flag is None:
                self.selected_flag = keys[0]
            if event.key == pygame.K_RIGHT:
                idx = (keys.index(self.selected_flag) + 1) % len(keys)
                self.selected_flag = keys[idx]
            elif event.key == pygame.K_LEFT:
                idx = (keys.index(self.selected_flag) - 1) % len(keys)
                self.selected_flag = keys[idx]
            elif event.key == pygame.K_SPACE and self.selected_flag:
                current = self.game_state.get_flag(self.selected_flag)
                self.simulate_flag_change(self.selected_flag, not current)
