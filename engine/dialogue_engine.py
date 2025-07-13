"""Advanced branching dialogue system with memory and UI integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:  # pragma: no cover - optional dependency for runtime
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML is missing
    yaml = None

try:  # pragma: no cover - allow running tests without pygame installed
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .game_state import GameState
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from .ui_overlay import UIOverlay


@dataclass
class DialogueOption:
    """Single selectable option in a dialogue line."""

    text: str
    next: Optional[str] = None
    condition: Optional[str] = None
    set_flag: Optional[str] = None


@dataclass
class DialogueLine:
    """Represents one dialogue entry."""

    id: Optional[str] = None
    speaker: Optional[str] = None
    text: Optional[str] = None
    options: List[DialogueOption] = field(default_factory=list)
    next: Optional[str] = None
    condition: Optional[str] = None
    set_flag: Optional[str] = None


@dataclass
class Dialogue:
    """Parsed dialogue container."""

    id: str
    lines: List[DialogueLine] = field(default_factory=list)
    memory_flag: Optional[str] = None
    on_complete: Dict[str, str] = field(default_factory=dict)


class DialogueEngine:
    """Manage dialogue trees and render them through :class:`UIOverlay`."""

    def __init__(self, game_state: GameState, ui_overlay: Optional["UIOverlay"] = None) -> None:
        self.game_state = game_state
        self.ui_overlay = ui_overlay

        self.dialogues: Dict[str, Dialogue] = {}
        self.active_dialogue_id: Optional[str] = None
        self.current_line_index: int = 0
        self.awaiting_choice: bool = False
        self._option_cache: List[DialogueOption] = []
        self._memory: Dict[str, List[str]] = {}
        self._branch_end: bool = False

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------
    def load_dialogue(self, dialogue_id: str, data: Dict) -> None:
        """Parse a single dialogue entry from a mapping."""

        lines: List[DialogueLine] = []
        for item in data.get("lines", []) or []:
            lines.append(self._parse_line(item))

        dialogue = Dialogue(
            id=dialogue_id,
            lines=lines,
            memory_flag=data.get("memory_flag"),
            on_complete=data.get("on_complete", {}) or {},
        )
        self.dialogues[dialogue_id] = dialogue

    def load_file(self, path: str) -> None:
        """Load one or many dialogues from a YAML or JSON file."""

        with open(path, "r", encoding="utf-8") as fh:
            if yaml:
                data = yaml.safe_load(fh) or {}
            else:  # pragma: no cover - fallback when PyYAML missing
                import json

                data = json.load(fh)

        entries = []
        if "dialogues" in data:
            entries = data.get("dialogues", []) or []
        elif "dialogue" in data:
            entries = [data.get("dialogue", {})]

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            dialogue_id = entry.get("id")
            if dialogue_id:
                self.load_dialogue(dialogue_id, entry)

    def _parse_line(self, item: Dict) -> DialogueLine:
        options: List[DialogueOption] = []
        for opt in item.get("options", []) or []:
            if not isinstance(opt, dict):
                continue
            options.append(
                DialogueOption(
                    text=opt.get("text", ""),
                    next=opt.get("next"),
                    condition=opt.get("condition"),
                    set_flag=opt.get("set_flag"),
                )
            )
        return DialogueLine(
            id=item.get("id"),
            speaker=item.get("speaker"),
            text=item.get("text"),
            options=options,
            next=item.get("next"),
            condition=item.get("condition"),
            set_flag=item.get("set_flag"),
        )

    # ------------------------------------------------------------------
    # Dialogue navigation helpers
    # ------------------------------------------------------------------
    def start(self, dialogue_id: str) -> None:
        """Begin a dialogue by its identifier."""

        if dialogue_id not in self.dialogues:
            self.active_dialogue_id = None
            return
        self.active_dialogue_id = dialogue_id
        self.current_line_index = 0
        self.awaiting_choice = False
        self._option_cache = []
        self._branch_end = False

        dlg = self.dialogues[dialogue_id]
        if dlg.memory_flag:
            self.game_state.set_flag(dlg.memory_flag, True)

        self._memory.setdefault(dialogue_id, [])

    def is_active(self) -> bool:
        return self.active_dialogue_id is not None

    # Internal ----------------------------------------------------------
    def _find_line_index(self, dialogue: Dialogue, line_id: str) -> Optional[int]:
        for idx, line in enumerate(dialogue.lines):
            if line.id == line_id:
                return idx
        return None

    def _current_dialogue(self) -> Optional[Dialogue]:
        if self.active_dialogue_id:
            return self.dialogues.get(self.active_dialogue_id)
        return None

    def current_node(self) -> Optional[DialogueLine]:
        dlg = self._current_dialogue()
        if not dlg:
            return None

        lines = dlg.lines
        while self.current_line_index < len(lines):
            line = lines[self.current_line_index]
            if self.game_state.check_condition(line.condition):
                return line
            self.current_line_index += 1
        return None

    # ------------------------------------------------------------------
    # Progression
    # ------------------------------------------------------------------
    def _goto(self, target: str) -> Optional[DialogueLine]:
        dlg = self._current_dialogue()
        if not dlg:
            return None

        idx = self._find_line_index(dlg, target)
        if idx is not None:
            self.current_line_index = idx
            self.awaiting_choice = False
            self._branch_end = True
            return self.current_node()

        if target in self.dialogues:
            self.start(target)
            self._branch_end = False
            return self.current_node()

        self._finish_dialogue()
        return None

    def advance(self) -> Optional[DialogueLine]:
        """Advance to the next line or display options."""

        node = self.current_node()
        if not node:
            self._finish_dialogue()
            return None

        if node.options:
            self._option_cache = [
                opt for opt in node.options if self.game_state.check_condition(opt.condition)
            ]
            self.awaiting_choice = True
            return node

        if node.set_flag:
            self.game_state.set_flag(node.set_flag, True)

        if node.next:
            return self._goto(node.next)

        if self._branch_end:
            self._finish_dialogue()
            return None

        self.current_line_index += 1
        if self.current_line_index >= len(self._current_dialogue().lines):
            self._finish_dialogue()
            return None

        node = self.current_node()
        if node and node.options:
            self._option_cache = [
                opt for opt in node.options if self.game_state.check_condition(opt.condition)
            ]
            self.awaiting_choice = True
        return node

    def choose(self, option_index: int) -> Optional[DialogueLine]:
        """Resolve a choice from the current options."""

        if not self.awaiting_choice or option_index < 0 or option_index >= len(self._option_cache):
            return None

        choice = self._option_cache[option_index]
        if choice.set_flag:
            self.game_state.set_flag(choice.set_flag, True)

        self.awaiting_choice = False
        mem = self._memory.setdefault(self.active_dialogue_id or "", [])
        mem.append(choice.text)

        if choice.next:
            return self._goto(choice.next)

        self.current_line_index += 1
        if self.current_line_index >= len(self._current_dialogue().lines):
            self._finish_dialogue()
            return None
        return self.current_node()

    def _finish_dialogue(self) -> None:
        dlg = self._current_dialogue()
        if not dlg:
            self.active_dialogue_id = None
            return

        if dlg.on_complete.get("set_flag"):
            self.game_state.set_flag(dlg.on_complete["set_flag"], True)

        self.active_dialogue_id = None
        self.awaiting_choice = False
        self._option_cache = []
        self._branch_end = False

    # ------------------------------------------------------------------
    # Update/Render/Input
    # ------------------------------------------------------------------
    def update(self) -> None:
        """Placeholder for potential timed behaviour."""

    def render(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not pygame or not self.ui_overlay or not self.is_active():
            return

        node = self.current_node()
        if not node:
            return

        text = node.text or ""
        speaker = node.speaker
        self.ui_overlay.draw_dialogue_box(text, speaker)

        if self.awaiting_choice:
            options_text = [opt.text for opt in self._option_cache]
            self.ui_overlay.draw_options(options_text)

    # Backwards compatibility -------------------------------------------------
    draw = render

    def handle_input(self, event: "pygame.event.Event") -> None:  # pragma: no cover - UI only
        if not pygame or not self.is_active():
            return

        if event.type == pygame.KEYDOWN:
            if self.awaiting_choice and pygame.K_1 <= event.key <= pygame.K_9:
                self.choose(event.key - pygame.K_1)
            elif event.key == pygame.K_SPACE:
                self.advance()

