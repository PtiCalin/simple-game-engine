import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GameState:
    """Persistent game memory for flags, variables, inventory and scenes."""

    save_path: str = "save.json"
    flags: Dict[str, bool] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)
    current_scene: str = ""
    clues: List[str] = field(default_factory=list)
    unlocked_scenes: List[str] = field(default_factory=list)

    def set_flag(self, name: str, value: bool = True) -> None:
        self.flags[name] = bool(value)

    def get_flag(self, name: str) -> bool:
        return self.flags.get(name, False)

    def toggle_flag(self, name: str) -> None:
        self.flags[name] = not self.flags.get(name, False)

    def set_var(self, key: str, value: Any) -> None:
        """Store an arbitrary value in ``variables``."""
        self.variables[key] = value

    def get_var(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve a variable value or ``default`` if missing."""
        return self.variables.get(key, default)

    # ------------------------------------------------------------------
    # Backwards compatibility helpers
    # ------------------------------------------------------------------
    def set_variable(self, key: str, value: Any) -> None:
        self.set_var(key, value)

    def get_variable(self, key: str, default: Optional[Any] = None) -> Any:
        return self.get_var(key, default)

    def add_item(self, item_id: str) -> None:
        if item_id not in self.inventory:
            self.inventory.append(item_id)

    def remove_item(self, item_id: str) -> None:
        """Remove ``item_id`` from inventory if present."""
        if item_id in self.inventory:
            self.inventory.remove(item_id)

    def has_item(self, item_id: str) -> bool:
        return item_id in self.inventory

    def list_inventory(self) -> List[str]:
        """Return a copy of the current inventory list."""
        return list(self.inventory)

    def set_scene(self, scene_id: str) -> None:
        self.current_scene = scene_id

    def get_scene(self) -> str:
        return self.current_scene

    def clear(self) -> None:
        """Reset all tracked state to defaults."""
        self.flags.clear()
        self.variables.clear()
        self.inventory.clear()
        self.current_scene = ""
        self.clues.clear()
        self.unlocked_scenes.clear()

    def export_debug(self) -> None:
        """Print the current state as formatted JSON for debugging."""
        data = {
            "flags": self.flags,
            "variables": self.variables,
            "inventory": self.inventory,
            "current_scene": self.current_scene,
            "clues": self.clues,
            "unlocked_scenes": self.unlocked_scenes,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def check_condition(self, condition: Optional[str]) -> bool:
        if not condition:
            return True
        if condition.startswith("!"):
            return not self.get_flag(condition[1:])
        return self.get_flag(condition)

    def save(self, path: Optional[str] = None) -> None:
        filepath = path or self.save_path
        data = {
            "flags": self.flags,
            "variables": self.variables,
            "inventory": self.inventory,
            "current_scene": self.current_scene,
            "clues": self.clues,
            "unlocked_scenes": self.unlocked_scenes,
        }
        try:
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def load(self, path: Optional[str] = None) -> None:
        filepath = path or self.save_path
        if not os.path.exists(filepath):
            return
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return
        self.flags = data.get("flags", {})
        self.variables = data.get("variables", {})
        self.inventory = data.get("inventory", [])
        self.current_scene = data.get("current_scene", "")
        self.clues = data.get("clues", [])
        self.unlocked_scenes = data.get("unlocked_scenes", [])
