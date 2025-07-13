import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.game_state import GameState
from engine.save_system import SaveSystem


def test_save_load_delete(tmp_path):
    saves = tmp_path / "saves"
    system = SaveSystem(saves_dir=str(saves))
    state = GameState()
    state.set_flag("demo", True)
    state.set_var("value", 42)

    system.save_game(1, state, "intro")
    path = saves / "slot1.save"
    assert path.exists()

    data = system.load_game(1)
    assert data["scene_id"] == "intro"
    assert data["flags"]["demo"] is True
    assert data["vars"]["value"] == 42

    meta = system.get_slot_metadata(1)
    assert meta["slot_id"] == 1
    assert meta["scene_id"] == "intro"

    system.delete_save(1)
    assert not path.exists()
    assert system.get_slot_metadata(1) == {}
