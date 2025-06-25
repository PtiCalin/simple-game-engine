import os
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.game_state import GameState


def test_flag_management(tmp_path):
    path = tmp_path / "save.json"
    state = GameState(save_path=str(path))
    state.set_flag("door_opened", True)
    assert state.get_flag("door_opened") is True
    state.toggle_flag("door_opened")
    assert state.get_flag("door_opened") is False


def test_save_load(tmp_path):
    path = tmp_path / "save.json"
    state = GameState(save_path=str(path))
    state.set_flag("key_found", True)
    state.inventory.append("key")
    state.clues.append("note")
    state.unlocked_scenes.append("intro")
    state.save()

    new_state = GameState(save_path=str(path))
    new_state.load()
    assert new_state.get_flag("key_found") is True
    assert "key" in new_state.inventory
    assert "note" in new_state.clues
    assert "intro" in new_state.unlocked_scenes


def test_check_condition():
    state = GameState()
    state.set_flag("seen", True)
    assert state.check_condition("seen") is True
    assert state.check_condition("missing") is False
    assert state.check_condition(None) is True
    state.toggle_flag("seen")
    assert state.check_condition("!seen") is True
