import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class GameState:
    """Track persistent game state like flags and inventory."""

    save_path: str = "save.json"
    flags: Dict[str, bool] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)
    clues: List[str] = field(default_factory=list)
    unlocked_scenes: List[str] = field(default_factory=list)

    def set_flag(self, name: str, value: bool = True) -> None:
        self.flags[name] = bool(value)

    def get_flag(self, name: str) -> bool:
        return self.flags.get(name, False)

    def toggle_flag(self, name: str) -> None:
        self.flags[name] = not self.flags.get(name, False)

    def check_condition(self, condition: Optional[str]) -> bool:
        if not condition:
            return True
        if condition.startswith("!"):
            return not self.get_flag(condition[1:])
        return self.get_flag(condition)

    def save(self) -> None:
        data = {
            "flags": self.flags,
            "inventory": self.inventory,
            "clues": self.clues,
            "unlocked_scenes": self.unlocked_scenes,
        }
        with open(self.save_path, "w") as fh:
            json.dump(data, fh)

    def load(self) -> None:
        if not os.path.exists(self.save_path):
            return
        with open(self.save_path, "r") as fh:
            data = json.load(fh)
        self.flags = data.get("flags", {})
        self.inventory = data.get("inventory", [])
        self.clues = data.get("clues", [])
        self.unlocked_scenes = data.get("unlocked_scenes", [])
