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

    state.set_var("code", "1234")
    assert state.get_var("code") == "1234"
    assert state.get_var("missing") is None

    state.add_item("rusty_key")
    assert state.has_item("rusty_key") is True
    assert state.list_inventory() == ["rusty_key"]
    state.remove_item("rusty_key")
    assert state.has_item("rusty_key") is False
    assert state.list_inventory() == []

    state.set_scene("garden")
    assert state.get_scene() == "garden"

    state.clear()
    assert state.get_flag("door_opened") is False
    assert state.flags == {}
    assert state.variables == {}
    assert state.inventory == []
    assert state.get_scene() == ""


def test_save_load(tmp_path):
    path = tmp_path / "save.json"
    state = GameState(save_path=str(path))
    state.set_flag("key_found", True)
    state.set_var("puzzle_code", 7391)
    state.add_item("key")
    state.set_scene("intro")
    state.clues.append("note")
    state.unlocked_scenes.append("intro")
    state.save()

    new_state = GameState(save_path=str(path))
    new_state.load()
    assert new_state.get_flag("key_found") is True
    assert new_state.get_var("puzzle_code") == 7391
    assert new_state.has_item("key") is True
    assert new_state.list_inventory() == ["key"]
    assert new_state.get_scene() == "intro"
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


def test_export_debug(capsys):
    state = GameState()
    state.set_flag("debug", True)
    state.set_var("value", 42)
    state.export_debug()
    captured = capsys.readouterr().out
    assert '"debug": true' in captured
    assert '"value": 42' in captured
