import os
import sys
import types
import pytest
yaml = pytest.importorskip("yaml")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.game_state import GameState


class DummyFont:
    def __init__(self, *args, **kwargs):
        self.height = 10

    def render(self, text, aa, color):
        return types.SimpleNamespace(get_width=lambda: len(text), get_height=lambda: self.height)

    def get_height(self):
        return self.height


class DummyPygame(types.SimpleNamespace):
    SRCALPHA = 1
    font = types.SimpleNamespace(Font=lambda path, size: DummyFont())
    KEYDOWN = 2
    K_RIGHT = 1
    K_LEFT = 3
    K_SPACE = 4


def test_load_and_evaluate(tmp_path, monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)

    from editor.visual_condition_tester import VisualConditionTester

    data = """
triggers:
  - id: open_door
    condition: "flag_a and flag_b"
"""
    yaml_path = tmp_path / "trig.yaml"
    yaml_path.write_text(data)

    gs = GameState(save_path=str(tmp_path / "save.json"))
    gs.set_flag("flag_a", True)
    gs.set_flag("flag_b", False)

    tester = VisualConditionTester(gs)
    tester.load_conditions_from_yaml(str(yaml_path))

    assert tester.preview_results[0]["passed"] is False
    tester.simulate_flag_change("flag_b", True)
    assert tester.preview_results[0]["passed"] is True
