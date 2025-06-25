from dataclasses import dataclass
from typing import Optional

from .hotspot import Hotspot
from .scene_manager import SceneManager


@dataclass
class NPC:
    """Simple non-player character linked to a hotspot."""

    id: str
    dialogue: Optional[str] = None
    flag_on_talk: Optional[str] = None
    hotspot: Optional[Hotspot] = None

    def attach_hotspot(self, hotspot: Hotspot) -> None:
        self.hotspot = hotspot

    def interact(self, manager: SceneManager) -> None:
        if self.flag_on_talk:
            manager.game_state.set_flag(self.flag_on_talk, True)
            manager.game_state.save()
        if self.dialogue:
            manager.show_dialogue(self.dialogue)

