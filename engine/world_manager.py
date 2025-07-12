from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import yaml
import json


@dataclass
class Region:
    """Simple region containing a list of scene identifiers."""

    id: str
    title: str = ""
    entry_scene: Optional[str] = None
    scenes: List[str] = field(default_factory=list)


@dataclass
class World:
    """World data parsed from YAML."""

    id: str
    title: str
    start_region: Optional[str] = None
    global_music: Optional[str] = None
    loop_time: Optional[int] = None
    gravity: Optional[float] = None
    weather: Optional[str] = None
    regions: Dict[str, Region] = field(default_factory=dict)


@dataclass
class WorldState:
    """Track the player's current position in the world."""

    current_region: Optional[str] = None
    current_scene: Optional[str] = None


class WorldManager:
    """High-level world management.

    The manager loads a YAML world definition and exposes convenience
    accessors for world metadata, regions and entry scenes.  It also
    maintains the currently active region and scene for compatibility
    with the rest of the engine.
    """

    def __init__(self, path_or_id: str | None = None, worlds_dir: str = "game/worlds"):
        self.worlds_dir = worlds_dir

        # new attributes used by the simplified API
        self.world_id: str = ""
        self.world_data: dict = {}
        self.world_metadata: dict = {}
        self.current_region_id: str = ""
        self.region_data: Dict[str, dict] = {}

        # legacy attributes retained for backwards compatibility
        self.path: str | None = None
        self.world: World | None = None
        self.state: WorldState | None = None

        if path_or_id:
            self.load_world(path_or_id)

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------
    def _load_world_file(self, path: str) -> World:
        if not os.path.exists(path):
            raise FileNotFoundError(f"World file not found: {path}")
        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}
        world_data = data.get("world", {}) or {}

        # expose raw data and metadata for the simplified API
        self.world_data = data
        self.world_metadata = {k: v for k, v in world_data.items() if k != "regions"}
        self.world_id = world_data.get("id", "")

        regions_data = world_data.get("regions", []) or []
        regions: Dict[str, Region] = {}
        self.region_data = {}
        for entry in regions_data:
            if not isinstance(entry, dict):
                continue
            rid = entry.get("id")
            scenes = entry.get("scenes", []) or []
            if rid:
                regions[rid] = Region(
                    id=rid,
                    title=entry.get("title", ""),
                    entry_scene=entry.get("entry_scene"),
                    scenes=list(scenes),
                )
                self.region_data[rid] = entry

        return World(
            id=self.world_id,
            title=world_data.get("title", ""),
            start_region=world_data.get("start_region"),
            global_music=world_data.get("global_music"),
            loop_time=world_data.get("loop_time"),
            gravity=world_data.get("gravity"),
            weather=world_data.get("weather"),
            regions=regions,
        )

    def load_world(self, path: str) -> None:
        """Load a new world from a file path or identifier."""
        if os.path.exists(path):
            file_path = path
        else:
            file_path = os.path.join(self.worlds_dir, f"{path}.yaml")

        self.path = file_path
        self.world = self._load_world_file(file_path)

        start_region = self.world.start_region
        self.current_region_id = start_region or ""
        self.state = WorldState(current_region=start_region, current_scene=None)

        if start_region:
            region = self.world.regions.get(start_region)
            if region:
                self.state.current_scene = (
                    region.entry_scene
                    or (region.scenes[0] if region.scenes else None)
                )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def current_region(self) -> Optional[Region]:
        if not self.state.current_region:
            return None
        return self.world.regions.get(self.state.current_region)

    def current_scene(self) -> Optional[str]:
        return self.state.current_scene

    def get_current_region(self) -> Optional[str]:
        """Return the identifier of the active region."""
        return self.state.current_region

    # ------------------------------------------------------------------
    # Simplified API accessors
    # ------------------------------------------------------------------

    def get_start_region(self) -> str:
        """Return the ID of the start region for the loaded world."""
        return self.world_metadata.get("start_region", "")

    def get_start_scene(self) -> str | None:
        """Return the entry scene for the start region, if any."""
        start_region = self.get_start_region()
        if not start_region:
            return None
        region = self.region_data.get(start_region)
        if not region:
            return None
        entry = region.get("entry_scene")
        if entry:
            return entry
        scenes = region.get("scenes") or []
        return scenes[0] if scenes else None

    def get_regions(self) -> List[dict]:
        """Return a list of region dictionaries."""
        return list(self.region_data.values())

    def get_region(self, region_id: str) -> dict | None:
        """Return a specific region dictionary."""
        return self.region_data.get(region_id)

    def set_region(self, region_id: str) -> None:
        """Set the current active region if it exists."""
        if region_id in self.region_data:
            self.current_region_id = region_id
            self.state.current_region = region_id

    def get_current_region_id(self) -> str:
        """Return the currently active region identifier."""
        return self.current_region_id

    def get_current_entry_scene(self) -> str | None:
        """Return the entry scene for the current region, if any."""
        region = self.region_data.get(self.current_region_id)
        if not region:
            return None
        entry = region.get("entry_scene")
        if entry:
            return entry
        scenes = region.get("scenes") or []
        return scenes[0] if scenes else None

    def get_world_metadata(self) -> Dict[str, Optional[str]]:
        """Return key metadata about the loaded world."""
        return dict(self.world_metadata)

    # ------------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------------
    def teleport(self, region_id: str, scene_id: Optional[str] = None) -> None:
        region = self.world.regions.get(region_id)
        if not region:
            return
        self.state.current_region = region_id
        self.state.current_scene = (
            scene_id
            or region.entry_scene
            or (region.scenes[0] if region.scenes else None)
        )

    def save_state(self, path: str) -> None:
        data = {
            "current_region": self.state.current_region,
            "current_scene": self.state.current_scene,
        }
        with open(path, "w") as fh:
            json.dump(data, fh)

    def load_state(self, path: str) -> None:
        if not os.path.exists(path):
            return
        with open(path, "r") as fh:
            data = json.load(fh)
        self.state.current_region = data.get("current_region")
        self.state.current_scene = data.get("current_scene")

