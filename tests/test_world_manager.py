import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

yaml = pytest.importorskip("yaml")

from engine.world_manager import WorldManager


def test_world_loading():
    wm = WorldManager("game/worlds/montreal.yaml")
    assert wm.world.id == "montreal"
    assert wm.world.start_region == "mileend"
    assert wm.world.global_music == "assets/music/montreal_theme.ogg"
    assert wm.world.loop_time == 6000
    assert wm.world.gravity == 9.8
    assert wm.world.weather == "rain"
    assert "mileend" in wm.world.regions
    assert wm.current_region() is not None
    assert wm.current_region().id == "mileend"
    assert wm.current_scene() == "ruelle_portail"


def test_save_load_state(tmp_path):
    wm = WorldManager("game/worlds/montreal.yaml")
    wm.teleport("vieuxport")
    path = tmp_path / "world_state.json"
    wm.save_state(str(path))

    new_wm = WorldManager("game/worlds/montreal.yaml")
    new_wm.load_state(str(path))
    assert new_wm.state.current_region == "vieuxport"
    assert new_wm.current_scene() == "canal_start"

