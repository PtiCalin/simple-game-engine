from __future__ import annotations

import os
from typing import Any, List

try:  # pragma: no cover - allow running tests without pygame
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

import yaml

from engine.asset_manager import AssetManager
from engine.ui_overlay import UIOverlay
from engine.hotspot import Hotspot


class SceneBuilder:
    """Simple helper for editing and previewing scene YAML files."""

    def __init__(self, screen: "pygame.Surface", scenes_dir: str = "scenes") -> None:
        self.screen = screen
        self.scenes_dir = scenes_dir
        self.scene_id: str = ""
        self.scene_data: dict = {}
        self.file_path: str = ""
        self.asset_manager = AssetManager()
        self.ui_overlay = UIOverlay(screen)
        self.hotspots: List[Hotspot] = []
        self.editing_mode: str = "background"
        self.live_preview: bool = True
        self.background_image: "pygame.Surface | None" = None

    # ------------------------------------------------------------------
    # Loading & Saving
    # ------------------------------------------------------------------
    def load_scene_yaml(self, path: str) -> None:
        """Load a scene definition from a YAML file."""
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}

        scene = data.get("scene", {}) or {}
        self.scene_id = scene.get("id", "")
        self.scene_data = scene
        self.file_path = path

        hotspots_data = scene.get("hotspots") or data.get("hotspots", []) or []
        self.hotspots = []
        for hs in hotspots_data:
            if not isinstance(hs, dict):
                continue
            rect = hs.get("rect") or hs.get("area") or [0, 0, 0, 0]
            if len(rect) != 4:
                rect = [0, 0, 0, 0]
            on_click = hs.get("on_click") or {}
            action = on_click.get("type") or hs.get("action", "")
            target = on_click.get("scene") or hs.get("target")
            self.hotspots.append(
                Hotspot(
                    id=hs.get("id", ""),
                    area=tuple(rect),
                    action=action,
                    target=target,
                    condition=hs.get("condition"),
                )
            )

        bg = self.scene_data.get("background")
        if bg:
            self.background_image = self.asset_manager.get_image(bg)
        else:
            self.background_image = None

    def save_to_yaml(self) -> None:
        """Write the current scene data back to ``file_path``."""
        if not self.file_path:
            return
        data = {
            "scene": self.scene_data,
            "hotspots": [
                {
                    "id": hs.id,
                    "area": list(hs.area),
                    "action": hs.action,
                    "target": hs.target,
                    "condition": hs.condition,
                }
                for hs in self.hotspots
            ],
        }
        with open(self.file_path, "w") as fh:
            yaml.safe_dump(data, fh)

    # ------------------------------------------------------------------
    # Editing Helpers
    # ------------------------------------------------------------------
    def edit_property(self, key: str, value: Any) -> None:
        """Modify a property inside ``scene_data``."""
        self.scene_data[key] = value

    def toggle_live_preview(self, enabled: bool) -> None:
        """Enable or disable live preview rendering."""
        self.live_preview = bool(enabled)

    # ------------------------------------------------------------------
    # Rendering & Input (UI only)
    # ------------------------------------------------------------------
    def render_preview(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        for hs in self.hotspots:
            pygame.draw.rect(surface, (255, 0, 0), hs.area, 2)
        self.ui_overlay.update_mouse_hover(self.hotspots)

    def handle_input(self, event: "pygame.event.Event") -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        # Placeholder for future interactive editing
        pass

    def draw_scene_editor_ui(self) -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        # Extend with UI widgets as needed
        self.ui_overlay.update_mouse_hover(self.hotspots)
