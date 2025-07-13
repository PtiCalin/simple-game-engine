import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.timeline_engine import TimelineEngine
from engine.game_state import GameState


def test_delay_event_triggers():
    state = GameState()
    engine = TimelineEngine(state)
    engine.load_events([
        {
            "id": "door_event",
            "trigger": "delay",
            "time": 1.0,
            "action": "set_flag",
            "params": {"flag": "door"},
        }
    ])

    engine.update(current_ticks=500)
    assert state.get_flag("door") is False

    engine.update(current_ticks=1100)
    assert state.get_flag("door") is True


def test_condition_event(tmp_path):
    state = GameState(save_path=str(tmp_path / "save.json"))
    engine = TimelineEngine(state)
    engine.load_events([
        {
            "id": "gate",
            "trigger": "condition",
            "time": 0.2,
            "condition": "open",
            "action": "set_flag",
            "params": {"flag": "gate"},
        }
    ])

    engine.update(current_ticks=300)
    assert state.get_flag("gate") is False

    state.set_flag("open", True)
    engine.update(current_ticks=600)
    assert state.get_flag("gate") is True


def test_time_loop_resets():
    state = GameState()
    engine = TimelineEngine(state)
    engine.loop_enabled = True
    engine.loop_duration = 2.0
    engine.load_events([
        {
            "id": "toggle",
            "trigger": "delay",
            "time": 1.0,
            "action": "toggle_flag",
            "params": {"flag": "door"},
        }
    ])

    engine.update(current_ticks=1100)
    assert state.get_flag("door") is True

    engine.update(current_ticks=2100)
    assert engine.elapsed_time < 0.1

    engine.update(current_ticks=1200 + 2100)  # another second after reset
    assert state.get_flag("door") is False
