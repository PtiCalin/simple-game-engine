import os
import sys
import types
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

yaml = pytest.importorskip("yaml")

from engine.inventory_system import InventorySystem
from engine.game_state import GameState


class DummyPygame(types.SimpleNamespace):
    Rect = type("Rect", (), {"__init__": lambda self, *a: None})
    def draw_rect(*args, **kwargs):
        pass
    draw = types.SimpleNamespace(rect=draw_rect)
    Surface = type("Surface", (), {"get_height": lambda self: 100})


def test_load_and_basic_ops(tmp_path, monkeypatch):
    item_yaml = """
item:
  id: key
  name: Key
  usable_on: [door]
  combine_with:
    - item: oil
      result: shiny_key
"""
    item_dir = tmp_path / "items"
    item_dir.mkdir()
    (item_dir / "key.yaml").write_text(item_yaml)

    recipe_yaml = """
recipe:
  id: make_torch
  ingredients: [stick, cloth]
  result: torch
"""
    recipe_dir = tmp_path / "recipes"
    recipe_dir.mkdir()
    (recipe_dir / "torch.yaml").write_text(recipe_yaml)

    state = GameState()
    inv = InventorySystem(state)
    inv.load_items_from_folder(str(item_dir))
    inv.load_recipes_from_folder(str(recipe_dir))

    assert "key" in inv.item_data
    assert "make_torch" in inv.recipes

    inv.add_item("key")
    inv.add_item("oil")
    assert inv.has_item("key") is True
    assert state.has_item("key") is True

    result = inv.combine_items("key", "oil")
    assert result == "shiny_key"
    assert inv.has_item("shiny_key") is True

    inv.add_item("stick")
    inv.add_item("cloth")
    craft_result = inv.craft("make_torch")
    assert craft_result == "torch"
    assert inv.has_item("torch") is True


def test_use_item_on_target(monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    from engine import inventory_system
    monkeypatch.setattr(inventory_system, "pygame", dummy_pg)

    state = GameState()
    inv = InventorySystem(state)
    inv.item_data = {
        "key": {"usable_on": ["door"]}
    }
    inv.add_item("key")
    inv.select_item("key")
    used = inv.use_item_on_target("door")
    assert used == "key"
    assert inv.selected_item is None
    assert inv.has_item("key") is False
