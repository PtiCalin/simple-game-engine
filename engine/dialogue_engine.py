"""Advanced branching dialogue system with memory and UI integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

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
    from .locale_manager import LocaleManager


@dataclass
class DialogueOption:
    """Single selectable option in a dialogue line."""

    text: str
    next: Optional[str] = None
    condition: Optional[str] = None
    set_flag: Optional[str] = None
    requires_flag: Optional[str] = None
    clear_flag: Optional[str] = None
    requires_memory: Optional[str] = None
    set_memory: Dict[str, Any] = field(default_factory=dict)


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
    requires_flag: Optional[str] = None
    clear_flag: Optional[str] = None
    requires_memory: Optional[str] = None
    set_memory: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dialogue:
    """Parsed dialogue container."""

    id: str
    lines: List[DialogueLine] = field(default_factory=list)
    memory_flag: Optional[str] = None
    on_complete: Dict[str, str] = field(default_factory=dict)


class DialogueEngine:
    """Manage dialogue trees and render them through :class:`UIOverlay`."""

    def __init__(
        self,
        game_state: GameState,
        ui_overlay: Optional["UIOverlay"] = None,
        locale_manager: Optional["LocaleManager"] = None,
    ) -> None:
        self.game_state = game_state
        self.ui_overlay = ui_overlay
        self.locale_manager = locale_manager

        self.dialogues: Dict[str, Dialogue] = {}
        self.active_dialogue_id: Optional[str] = None
        self.current_line_index: int = 0
        self.awaiting_choice: bool = False
        self._option_cache: List[DialogueOption] = []
        self._memory_history: Dict[str, List[str]] = {}
        self._memory_store: Dict[str, Dict[str, Any]] = {}
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
                    requires_flag=opt.get("requires_flag"),
                    clear_flag=opt.get("clear_flag"),
                    requires_memory=opt.get("requires_memory"),
                    set_memory=opt.get("set_memory", {}) or {},
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
            requires_flag=item.get("requires_flag"),
            clear_flag=item.get("clear_flag"),
            requires_memory=item.get("requires_memory"),
            set_memory=item.get("set_memory", {}) or {},
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

        self._memory_history.setdefault(dialogue_id, [])
        self._memory_store.setdefault(dialogue_id, {})

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

    def _check_memory(self, expression: Optional[str]) -> bool:
        """Evaluate a simple memory expression."""
        if not expression:
            return True
        expr = expression.strip()
        op = None
        if "==" in expr:
            op = "=="
        elif "!=" in expr:
            op = "!="
        if op:
            left, right = expr.split(op, 1)
            right = right.strip().strip("\"'")
        else:
            left, right = expr, None
        left = left.strip()
        if "." in left:
            dlg_id, key = left.split(".", 1)
        else:
            dlg_id, key = self.active_dialogue_id or "", left
        value = self._memory_store.get(dlg_id, {}).get(key)
        if op == "==":
            return str(value) == right
        if op == "!=":
            return str(value) != right
        return value is not None

    def _set_memory(self, data: Dict[str, Any], dialogue_id: Optional[str] = None) -> None:
        dlg_id = dialogue_id or (self.active_dialogue_id or "")
        store = self._memory_store.setdefault(dlg_id, {})
        store.update({k: str(v) for k, v in (data or {}).items()})

    def current_node(self) -> Optional[DialogueLine]:
        dlg = self._current_dialogue()
        if not dlg:
            return None

        lines = dlg.lines
        while self.current_line_index < len(lines):
            line = lines[self.current_line_index]
            if not self.game_state.check_condition(line.condition):
                self.current_line_index += 1
                continue
            if line.requires_flag and not self.game_state.get_flag(line.requires_flag):
                self.current_line_index += 1
                continue
            if not self._check_memory(line.requires_memory):
                self.current_line_index += 1
                continue
            return line

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
                opt
                for opt in node.options
                if self.game_state.check_condition(opt.condition)
                and (not opt.requires_flag or self.game_state.get_flag(opt.requires_flag))
                and self._check_memory(opt.requires_memory)
            ]
            self.awaiting_choice = True
            return node

        if node.set_flag:
            self.game_state.set_flag(node.set_flag, True)
        if node.clear_flag:
            self.game_state.set_flag(node.clear_flag, False)
        if node.set_memory:
            self._set_memory(node.set_memory)

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
                opt
                for opt in node.options
                if self.game_state.check_condition(opt.condition)
                and (not opt.requires_flag or self.game_state.get_flag(opt.requires_flag))
                and self._check_memory(opt.requires_memory)
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
        if choice.clear_flag:
            self.game_state.set_flag(choice.clear_flag, False)
        if choice.set_memory:
            self._set_memory(choice.set_memory)

        self.awaiting_choice = False
        hist = self._memory_history.setdefault(self.active_dialogue_id or "", [])
        hist.append(choice.text)

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

        text = self.resolve_localized_text(node.text or "")
        speaker = node.speaker
        self.ui_overlay.draw_dialogue_box(text, speaker)

        if self.awaiting_choice:
            options_text = [self.resolve_localized_text(opt.text) for opt in self._option_cache]
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

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def resolve_localized_text(self, key: str) -> str:
        if self.locale_manager and self.locale_manager.has_translation(key):
            return self.locale_manager.translate(key)
        return key

    def get_current_line(self) -> Optional[str]:
        node = self.current_node()
        if not node:
            return None
        return self.resolve_localized_text(node.text or "")

    def next_line(self, choice_index: Optional[int] = None) -> Optional[str]:
        if choice_index is not None:
            node = self.choose(choice_index)
        else:
            node = self.advance()
        if not node:
            return None
        return self.resolve_localized_text(node.text or "")

