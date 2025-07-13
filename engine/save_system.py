from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any
from datetime import datetime

from .game_state import GameState


@dataclass
class SaveSlot:
    slot_id: int
    timestamp: str
    scene_id: str
    flags: Dict[str, bool]
    vars: Dict[str, Any]

    def get_preview_data(self) -> Dict[str, Any]:
        return {
            "scene": self.scene_id,
            "time": self.timestamp,
        }


class SaveSystem:
    """Simple multi-slot save management using JSON files."""

    def __init__(self, saves_dir: str = "saves") -> None:
        self.saves_dir = saves_dir
        self.save_slots: Dict[int, SaveSlot] = {}
        self.current_slot: Optional[int] = None
        self._load_metadata()

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _slot_path(self, slot_id: int) -> str:
        filename = f"slot{slot_id}.save"
        return os.path.join(self.saves_dir, filename)

    def _load_metadata(self) -> None:
        """Populate ``save_slots`` with available slot data."""
        if not os.path.exists(self.saves_dir):
            return
        for name in os.listdir(self.saves_dir):
            if not name.startswith("slot") or not name.endswith(".save"):
                continue
            try:
                sid = int(name[4:-5])
            except ValueError:
                continue
            data = self._read_file(self._slot_path(sid))
            if not data:
                continue
            slot = SaveSlot(
                slot_id=sid,
                timestamp=data.get("timestamp", ""),
                scene_id=data.get("scene_id", ""),
                flags=data.get("flags", {}),
                vars=data.get("vars", {}),
            )
            self.save_slots[sid] = slot

    def _read_file(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_file(self, path: str, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def save_game(self, slot_id: int, game_state: GameState, scene_id: str) -> None:
        data = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "scene_id": scene_id,
            "flags": dict(game_state.flags),
            "vars": dict(game_state.variables),
        }
        self._write_file(self._slot_path(slot_id), data)
        self.save_slots[slot_id] = SaveSlot(
            slot_id=slot_id,
            timestamp=data["timestamp"],
            scene_id=scene_id,
            flags=data["flags"],
            vars=data["vars"],
        )
        self.current_slot = slot_id

    def load_game(self, slot_id: int) -> Dict[str, Any]:
        data = self._read_file(self._slot_path(slot_id))
        if not data:
            return {}
        self.current_slot = slot_id
        return data

    def delete_save(self, slot_id: int) -> None:
        path = self._slot_path(slot_id)
        if os.path.exists(path):
            os.remove(path)
        self.save_slots.pop(slot_id, None)
        if self.current_slot == slot_id:
            self.current_slot = None

    def get_slot_metadata(self, slot_id: int) -> Dict[str, Any]:
        slot = self.save_slots.get(slot_id)
        if not slot:
            return {}
        return asdict(slot)
