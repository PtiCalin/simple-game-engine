import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.timeline_engine import TimelineEngine
from engine.game_state import GameState


def test_delay_event_triggers(tmp_path):
    state = GameState(save_path=str(tmp_path / "save.json"))
    engine = TimelineEngine(state)
    engine.add_events([
        {"trigger": "delay", "time": 1, "action": "set_flag", "flag": "door"}
    ], current_ticks=0)

    engine.update(current_ticks=500)
    assert state.get_flag("door") is False

    engine.update(current_ticks=1100)
    assert state.get_flag("door") is True


def test_scene_local_event(tmp_path):
    state = GameState(save_path=str(tmp_path / "save.json"))
    engine = TimelineEngine(state)
    engine.add_events([
        {"trigger": "delay", "time": 1, "action": "set_flag", "flag": "door"}
    ], current_ticks=0, scene="intro")

    engine.update(current_ticks=1500, current_scene="other")
    assert state.get_flag("door") is False

    engine.update(current_ticks=1500, current_scene="intro")
    assert state.get_flag("door") is True
