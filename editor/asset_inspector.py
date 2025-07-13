from __future__ import annotations

import os
from typing import List, Optional, Dict

try:  # pragma: no cover - allow running tests without pygame
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from engine.asset_manager import AssetManager


class AssetInspector:
    """Browse assets and build a visual layer stack."""

    def __init__(
        self, preview_size: tuple[int, int] | None = None, assets_dir: str = "assets"
    ) -> None:
        if preview_size is None:
            preview_size = (320, 240)
        self.asset_type: str = ""
        self.asset_list: List[str] = []
        self.selected_asset: Optional[str] = None
        self.scene_data: Dict = {}
        self.layer_stack: List[str] = []
        self.asset_manager = AssetManager(base_path=assets_dir)
        self.preview_surface = (
            pygame.Surface(preview_size, pygame.SRCALPHA) if pygame else None
        )

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------
    def load_assets_from_folder(self, asset_type: str) -> None:
        """Populate ``asset_list`` with filenames from ``asset_type`` folder."""
        folder = os.path.join(self.asset_manager.base_path, asset_type)
        self.asset_type = asset_type
        if not os.path.isdir(folder):
            self.asset_list = []
            return
        self.asset_list = [
            os.path.join(asset_type, name)
            for name in sorted(os.listdir(folder))
            if not name.startswith(".") and os.path.isfile(os.path.join(folder, name))
        ]

    # ------------------------------------------------------------------
    # UI stubs
    # ------------------------------------------------------------------
    def render(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not pygame or not self.preview_surface:
            return
        self.preview_layer_stack()
        surface.blit(self.preview_surface, (0, 0))

    def handle_input(
        self, event: "pygame.event.Event"
    ) -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        # Placeholder for future interactive controls
        pass

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------
    def select_asset(self, asset_id: str) -> None:
        if asset_id in self.asset_list:
            self.selected_asset = asset_id

    def add_to_layer_stack(self, asset_id: str) -> None:
        if asset_id not in self.layer_stack:
            self.layer_stack.append(asset_id)

    def remove_from_layer_stack(self, asset_id: str) -> None:
        if asset_id in self.layer_stack:
            self.layer_stack.remove(asset_id)

    def preview_layer_stack(self) -> None:
        if not pygame or not self.preview_surface:
            return
        self.preview_surface.fill((0, 0, 0, 0))
        for asset in self.layer_stack:
            image = self.asset_manager.get_image(asset)
            if image:
                self.preview_surface.blit(image, (0, 0))

    def assign_asset_to_scene(self, scene_id: str, target: str) -> None:
        """Assign ``selected_asset`` to a property in ``scene_data``."""
        if not self.selected_asset:
            return
        self.scene_data.setdefault("id", scene_id)
        if target == "background":
            self.scene_data["background"] = self.selected_asset
        elif target == "overlay":
            self.scene_data.setdefault("overlays", [])
            if self.selected_asset not in self.scene_data["overlays"]:
                self.scene_data["overlays"].append(self.selected_asset)
        else:
            self.scene_data[target] = self.selected_asset
