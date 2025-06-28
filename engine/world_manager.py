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
    """Load world data and keep track of the current region and scene."""

    def __init__(self, path: str):
        self.path = path
        self.world = self.load_world(path)
        self.state = WorldState(
            current_region=self.world.start_region,
            current_scene=None,
        )
        if self.state.current_region:
            region = self.world.regions.get(self.state.current_region)
            if region and region.scenes:
                self.state.current_scene = region.scenes[0]

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def load_world(self, path: str) -> World:
        if not os.path.exists(path):
            raise FileNotFoundError(f"World file not found: {path}")
        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}
        world_data = data.get("world", {})
        regions_data = world_data.get("regions", []) or []
        regions: Dict[str, Region] = {}
        for entry in regions_data:
            if not isinstance(entry, dict):
                continue
            rid = entry.get("id")
            scenes = entry.get("scenes", []) or []
            if rid:
                regions[rid] = Region(id=rid, scenes=list(scenes))
        return World(
            id=world_data.get("id", ""),
            title=world_data.get("title", ""),
            start_region=world_data.get("start_region"),
            global_music=world_data.get("global_music"),
            loop_time=world_data.get("loop_time"),
            gravity=world_data.get("gravity"),
            weather=world_data.get("weather"),
            regions=regions,
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

    # ------------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------------
    def teleport(self, region_id: str, scene_id: Optional[str] = None) -> None:
        region = self.world.regions.get(region_id)
        if not region:
            return
        self.state.current_region = region_id
        self.state.current_scene = scene_id or (region.scenes[0] if region.scenes else None)

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
