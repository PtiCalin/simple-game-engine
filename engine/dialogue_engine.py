from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML is missing
    yaml = None
import json
try:
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .game_state import GameState


@dataclass
class DialogueOption:
    """Option the player can choose during a dialogue."""

    text: str
    next: Optional[str] = None
    set_flag: Optional[str] = None


@dataclass
class DialogueNode:
    """Single node in a dialogue tree."""

    speaker: Optional[str] = None
    text: Optional[str] = None
    options: List[DialogueOption] = field(default_factory=list)
    set_flag: Optional[str] = None
    next: Optional[str] = None


@dataclass
class Dialogue:
    """Dialogue tree parsed from YAML."""

    id: str
    lines: List[DialogueNode] = field(default_factory=list)


class DialogueEngine:
    """Manage dialogue trees and render them on screen."""

    def __init__(self, state: GameState):
        self.state = state
        self.dialogues: Dict[str, Dialogue] = {}
        self.current: Optional[Dialogue] = None
        self.index: int = 0
        self.font = pygame.font.Font(None, 24) if pygame else None
        self.active: bool = False

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def load_file(self, path: str) -> None:
        """Load one or more dialogues from a YAML file."""
        with open(path, "r") as fh:
            if yaml:
                data = yaml.safe_load(fh) or {}
            else:
                data = json.load(fh)
        if "dialogues" in data:
            entries = data.get("dialogues", []) or []
        else:
            entries = [data.get("dialogue", {})]
        for entry in entries:
            if not entry:
                continue
            dialog_id = entry.get("id")
            if not dialog_id:
                continue
            lines_data = entry.get("lines", []) or []
            lines = [self._parse_line(item) for item in lines_data if isinstance(item, dict)]
            self.dialogues[dialog_id] = Dialogue(id=dialog_id, lines=lines)

    def _parse_line(self, item: Dict) -> DialogueNode:
        if "options" in item:
            options = [
                DialogueOption(
                    text=opt.get("text", ""),
                    next=opt.get("next"),
                    set_flag=opt.get("set_flag"),
                )
                for opt in item.get("options", [])
                if isinstance(opt, dict)
            ]
            return DialogueNode(options=options)
        return DialogueNode(
            speaker=item.get("speaker"),
            text=item.get("text"),
            set_flag=item.get("set_flag"),
            next=item.get("next"),
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def start(self, dialogue_id: str) -> None:
        self.current = self.dialogues.get(dialogue_id)
        self.index = 0
        self.active = self.current is not None

    def current_node(self) -> Optional[DialogueNode]:
        if not self.current or self.index >= len(self.current.lines):
            return None
        return self.current.lines[self.index]

    def advance(self) -> Optional[DialogueNode]:
        node = self.current_node()
        if not node:
            self.active = False
            return None
        if node.options:
            # Waiting for player choice
            return node
        if node.set_flag:
            self.state.set_flag(node.set_flag, True)
        if node.next:
            self.start(node.next)
            return self.current_node()
        self.index += 1
        if self.index >= len(self.current.lines):
            self.active = False
            return None
        return self.current_node()

    def choose(self, option_index: int) -> Optional[DialogueNode]:
        node = self.current_node()
        if not node or not node.options:
            return None
        if option_index < 0 or option_index >= len(node.options):
            return None
        choice = node.options[option_index]
        if choice.set_flag:
            self.state.set_flag(choice.set_flag, True)
        if choice.next:
            self.start(choice.next)
        else:
            self.index += 1
        return self.current_node()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        if not self.active or not pygame:
            return
        node = self.current_node()
        if not node or not self.font:
            return
        width, height = screen.get_size()
        box = pygame.Rect(40, height - 120, width - 80, 80)
        pygame.draw.rect(screen, (0, 0, 0), box)
        pygame.draw.rect(screen, (255, 255, 255), box, 2)
        y = box.top + 10
        if node.speaker:
            speaker_surf = self.font.render(node.speaker, True, (255, 215, 0))
            screen.blit(speaker_surf, (box.left + 10, y))
            y += speaker_surf.get_height() + 5
        text = node.text or ""
        text_surf = self.font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (box.left + 10, y))

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.active or not pygame:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.advance()
            elif pygame.K_1 <= event.key <= pygame.K_9:
                self.choose(event.key - pygame.K_1)
