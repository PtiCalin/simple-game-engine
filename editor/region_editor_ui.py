from __future__ import annotations

import os
from typing import List, Optional, Tuple, Any, Dict

try:  # pragma: no cover - allow running tests without pygame
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

import yaml

from engine.hotspot import Hotspot
from engine.ui_overlay import UIOverlay
from engine.asset_manager import AssetManager


class RegionEditorUI:
    """Simple visual editor for scenes and hotspots."""

    def __init__(self, screen: "pygame.Surface", scenes_dir: str = "scenes") -> None:
        self.screen = screen
        self.scenes_dir = scenes_dir
        self.asset_manager = AssetManager()
        self.ui_overlay = UIOverlay(screen)

        self.active_scene: Optional[str] = None
        self.scene_data: Dict[str, Any] = {}
        self.hotspots: List[Hotspot] = []
        self.selected_hotspot: Optional[Hotspot] = None
        self.background_image: "pygame.Surface | None" = None
        self.editing_mode: str = "select"

        self._drag_start: Optional[Tuple[int, int]] = None

    # ------------------------------------------------------------------
    # Scene Handling
    # ------------------------------------------------------------------
    def scene_path_from_id(self, scene_id: str) -> str:
        return os.path.join(self.scenes_dir, f"{scene_id}.yaml")

    def load_scene(self, scene_id: str) -> None:
        """Load scene YAML and background image for editing."""
        path = self.scene_path_from_id(scene_id)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}
        scene_info = data.get("scene", {})
        self.active_scene = scene_id
        self.scene_data = scene_info
        self.hotspots = []
        for hs in data.get("hotspots", []) or []:
            area = tuple(hs.get("area", [0, 0, 0, 0]))
            if len(area) != 4:
                area = (0, 0, 0, 0)
            self.hotspots.append(
                Hotspot(
                    id=hs.get("id", ""),
                    area=area,  # type: ignore[arg-type]
                    action=hs.get("action", ""),
                    target=hs.get("target"),
                    condition=hs.get("condition"),
                )
            )
        bg = scene_info.get("background")
        if bg:
            self.background_image = self.asset_manager.get_image(bg)
        else:
            self.background_image = None

    # ------------------------------------------------------------------
    # Input Handling
    # ------------------------------------------------------------------
    def handle_input(self, event: "pygame.event.Event") -> None:
        if not pygame:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.editing_mode == "select":
                self.select_hotspot_at(event.pos)
            elif self.editing_mode == "add":
                self._drag_start = event.pos
            elif self.editing_mode == "delete":
                hs = self.select_hotspot_at(event.pos)
                if hs:
                    self.remove_hotspot(hs.id)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.editing_mode == "add" and self._drag_start:
                x0, y0 = self._drag_start
                x1, y1 = event.pos
                x, y = min(x0, x1), min(y0, y1)
                w, h = abs(x1 - x0), abs(y1 - y0)
                new_id = f"hotspot_{len(self.hotspots)+1}"
                self.add_hotspot(x, y, w, h, new_id, {"action": "noop"})
                self._drag_start = None

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        for hs in self.hotspots:
            color = (0, 255, 0) if hs is self.selected_hotspot else (255, 0, 0)
            pygame.draw.rect(surface, color, hs.area, 2)
        if self._drag_start and self.editing_mode == "add":
            pos = pygame.mouse.get_pos()
            x, y = min(self._drag_start[0], pos[0]), min(self._drag_start[1], pos[1])
            w, h = abs(pos[0] - self._drag_start[0]), abs(pos[1] - self._drag_start[1])
            pygame.draw.rect(surface, (0, 0, 255), (x, y, w, h), 1)
        self.ui_overlay.update_mouse_hover(self.hotspots)

    def update(self) -> None:  # pragma: no cover - UI only
        pass

    # ------------------------------------------------------------------
    # Hotspot Helpers
    # ------------------------------------------------------------------
    def add_hotspot(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        action: Dict[str, Any],
    ) -> Hotspot:
        hs = Hotspot(id=label, area=(x, y, width, height), action=action.get("action", ""), target=action.get("target"), condition=action.get("condition"))
        self.hotspots.append(hs)
        return hs

    def remove_hotspot(self, hotspot_id: str) -> None:
        self.hotspots = [hs for hs in self.hotspots if hs.id != hotspot_id]
        if self.selected_hotspot and self.selected_hotspot.id == hotspot_id:
            self.selected_hotspot = None

    def select_hotspot_at(self, pos: Tuple[int, int]) -> Optional[Hotspot]:
        self.selected_hotspot = None
        for hs in self.hotspots:
            if hs.rect().collidepoint(pos):
                self.selected_hotspot = hs
                break
        return self.selected_hotspot

    def edit_hotspot_property(self, hotspot_id: str, key: str, value: Any) -> None:
        for hs in self.hotspots:
            if hs.id == hotspot_id:
                setattr(hs, key, value)
                break

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------
    def save_scene_to_yaml(self) -> None:
        if not self.active_scene:
            return
        path = self.scene_path_from_id(self.active_scene)
        scene_dict = dict(self.scene_data)
        data = {
            "scene": scene_dict,
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
        with open(path, "w") as fh:
            yaml.safe_dump(data, fh)
