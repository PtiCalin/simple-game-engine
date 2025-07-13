from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - allow tests without PyYAML
    yaml = None

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .game_state import GameState
from .ui_overlay import UIOverlay


@dataclass
class InventorySystem:
    """Manage player inventory and item definitions."""

    game_state: GameState
    ui_overlay: UIOverlay | None = None
    items: List[str] = field(default_factory=list)
    item_data: Dict[str, Dict] = field(default_factory=dict)
    selected_item: Optional[str] = None
    recipes: Dict[str, Dict] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------
    def load_items_from_folder(self, path: str) -> None:
        """Load all ``*.yaml`` files in ``path`` into ``item_data``."""
        if not os.path.isdir(path):
            return
        for fname in os.listdir(path):
            if not fname.endswith(".yaml"):
                continue
            fpath = os.path.join(path, fname)
            with open(fpath, "r", encoding="utf-8") as fh:
                if yaml:
                    data = yaml.safe_load(fh) or {}
                else:  # pragma: no cover - fallback when PyYAML missing
                    import json

                    data = json.load(fh)
            entry = data.get("item")
            if isinstance(entry, dict) and entry.get("id"):
                self.item_data[entry["id"]] = entry

    def load_recipes_from_folder(self, path: str) -> None:
        """Load crafting recipes from ``path``."""
        if not os.path.isdir(path):
            return
        for fname in os.listdir(path):
            if not fname.endswith(".yaml"):
                continue
            fpath = os.path.join(path, fname)
            with open(fpath, "r", encoding="utf-8") as fh:
                if yaml:
                    data = yaml.safe_load(fh) or {}
                else:  # pragma: no cover - fallback when PyYAML missing
                    import json

                    data = json.load(fh)
            entry = data.get("recipe")
            if isinstance(entry, dict) and entry.get("id"):
                self.recipes[entry["id"]] = entry

    # ------------------------------------------------------------------
    # Inventory management
    # ------------------------------------------------------------------
    def add_item(self, item_id: str) -> None:
        if item_id not in self.items:
            self.items.append(item_id)
            self.game_state.add_item(item_id)
            self.update_inventory_ui()

    def remove_item(self, item_id: str) -> None:
        if item_id in self.items:
            self.items.remove(item_id)
            self.game_state.remove_item(item_id)
            if self.selected_item == item_id:
                self.selected_item = None
            self.update_inventory_ui()

    def has_item(self, item_id: str) -> bool:
        return item_id in self.items

    def select_item(self, item_id: Optional[str]) -> None:
        if item_id and item_id in self.items:
            self.selected_item = item_id
        else:
            self.selected_item = None
        self.update_inventory_ui()

    # ------------------------------------------------------------------
    # Item interactions
    # ------------------------------------------------------------------
    def combine_items(self, item1: str, item2: str) -> Optional[str]:
        """Return resulting item id when combining, if defined."""
        data1 = self.item_data.get(item1, {})
        combos = data1.get("combine_with", []) or []
        for entry in combos:
            if entry.get("item") == item2:
                result = entry.get("result")
                if result:
                    self.remove_item(item1)
                    self.remove_item(item2)
                    self.add_item(result)
                    return result
        return None

    def use_item_on_target(self, target_id: str) -> Optional[str]:
        """Return item id that was used on target if usable."""
        if not self.selected_item:
            return None
        data = self.item_data.get(self.selected_item, {})
        usable_on = data.get("usable_on", []) or []
        if target_id in usable_on:
            used = self.selected_item
            self.remove_item(used)
            self.selected_item = None
            self.update_inventory_ui()
            return used
        return None

    def craft(self, recipe_id: str) -> Optional[str]:
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return None
        ingredients = recipe.get("ingredients", []) or []
        if not all(item in self.items for item in ingredients):
            return None
        for item in ingredients:
            self.remove_item(item)
        result = recipe.get("result")
        if result:
            self.add_item(result)
        return result

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def render_inventory(self, surface: "pygame.Surface") -> None:  # pragma: no cover - UI only
        if not pygame:
            return
        icon_size = 32
        padding = 4
        for idx, item_id in enumerate(self.items):
            x = padding + idx * (icon_size + padding)
            y = surface.get_height() - icon_size - padding
            rect = pygame.Rect(x, y, icon_size, icon_size)
            pygame.draw.rect(surface, (50, 50, 50), rect)
            if self.selected_item == item_id:
                pygame.draw.rect(surface, (200, 200, 50), rect, 2)

    def update_inventory_ui(self) -> None:
        """Hook for UI updates when inventory changes."""
        # Placeholder: real implementation would update a UI overlay
        pass
