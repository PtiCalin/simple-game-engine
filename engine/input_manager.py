from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict

try:  # pragma: no cover - allow tests without PyYAML
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None

try:  # pragma: no cover - allow running tests without pygame installed
    import pygame  # type: ignore
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None


DEFAULT_BINDINGS: Dict[str, str] = {
    "move_up": "W",
    "move_down": "S",
    "move_left": "A",
    "move_right": "D",
    "interact": "E",
    "pause": "ESCAPE",
    "debug_toggle": "`",
    "inventory": "TAB",
}


@dataclass
class InputManager:
    """Manage keyboard and gamepad input with customizable bindings."""

    binding_file: str = "config/controls.yaml"
    input_source: str = "keyboard"
    bindings: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_BINDINGS))
    gamepad_bindings: Dict[str, int] = field(default_factory=dict)
    input_state: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.joystick = None
        if pygame and pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            if self.input_source == "keyboard":
                self.input_source = "mixed"
        if self.binding_file:
            self.load_bindings(self.binding_file)

    # ------------------------------------------------------------------
    # Binding helpers
    # ------------------------------------------------------------------
    def load_bindings(self, path: str) -> None:
        """Load bindings from a YAML or JSON file."""
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as fh:
            if path.endswith(".json"):
                data = json.load(fh)
            else:
                if yaml:
                    data = yaml.safe_load(fh) or {}
                else:  # pragma: no cover - fallback when PyYAML missing
                    data = json.load(fh)
        self.bindings.update(data.get("controls", {}))
        self.gamepad_bindings.update(data.get("gamepad", {}))

    def save_bindings(self, path: str) -> None:
        """Persist current bindings to ``path``."""
        data = {"controls": self.bindings, "gamepad": self.gamepad_bindings}
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            if path.endswith(".json"):
                json.dump(data, fh, indent=2, ensure_ascii=False)
            else:
                if yaml:
                    yaml.safe_dump(data, fh)
                else:  # pragma: no cover - fallback when PyYAML missing
                    json.dump(data, fh, indent=2, ensure_ascii=False)

    def bind_action(self, action: str, key: str) -> None:
        """Bind ``action`` to keyboard ``key``."""
        self.bindings[action] = key

    def bind_gamepad_action(self, action: str, button_id: int) -> None:
        """Bind ``action`` to a gamepad button."""
        self.gamepad_bindings[action] = int(button_id)

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------
    def handle_event(self, event: "pygame.event.Event") -> None:  # pragma: no cover - interactive
        if not pygame:
            return
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            key_name = pygame.key.name(event.key).upper()
            pressed = event.type == pygame.KEYDOWN
            for action, key in self.bindings.items():
                if key.upper() == key_name:
                    self.input_state[action] = pressed
                    self.input_source = "keyboard"
        elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            pressed = event.type == pygame.JOYBUTTONDOWN
            for action, btn in self.gamepad_bindings.items():
                if event.button == btn:
                    self.input_state[action] = pressed
                    self.input_source = "gamepad"

    def is_action_pressed(self, action: str) -> bool:
        """Return ``True`` if ``action`` is currently active."""
        return bool(self.input_state.get(action))

    def update_input_state(self) -> None:  # pragma: no cover - realtime polling
        if not pygame:
            return
        if pygame.key.get_focused():
            pressed = pygame.key.get_pressed()
            for action, key in self.bindings.items():
                code = getattr(pygame, f"K_{key.lower()}", None)
                if code is not None and code < len(pressed):
                    self.input_state[action] = bool(pressed[code])
        if self.joystick:
            for action, btn in self.gamepad_bindings.items():
                if self.joystick.get_numbuttons() > btn:
                    if self.joystick.get_button(btn):
                        self.input_state[action] = True
                    else:
                        self.input_state[action] = False



