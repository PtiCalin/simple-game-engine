from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import yaml

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
    regions: Dict[str, Region] = field(default_factory=dict)

class WorldLoader:
    """Load a world YAML file defining regions and scenes."""

    def __init__(self, path: str):
        self.path = path
        self.world = self.load_world(path)

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
            regions=regions,
        )

    def get_region(self, region_id: str) -> Optional[Region]:
        return self.world.regions.get(region_id)

    def first_region(self) -> Optional[Region]:
        return next(iter(self.world.regions.values()), None)
