import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.puzzle_manager import PuzzleManager
from engine.game_state import GameState


def test_load_puzzles(tmp_path):
    data = {
        "puzzles": [
            {
                "id": "sun_mirror",
                "type": "logic",
                "scene": "garden_observatory",
                "solved": False,
                "description": "Reflect sunlight to open the sealed gate",
            }
        ]
    }
    path = tmp_path / "puzzles.json"
    with open(path, "w") as fh:
        json.dump(data, fh)

    state = GameState(save_path=str(tmp_path / "save.json"))
    manager = PuzzleManager(state)
    manager.load_file(str(path))

    assert "sun_mirror" in manager.engine.registry
    puzzle = manager.engine.registry["sun_mirror"]
    assert puzzle.description.startswith("Reflect")


def test_mark_solved(tmp_path):
    data = {
        "puzzles": [
            {"id": "mirror", "type": "logic", "scene": "obs", "solved": False}
        ]
    }
    path = tmp_path / "puzzles.json"
    with open(path, "w") as fh:
        json.dump(data, fh)

    state = GameState(save_path=str(tmp_path / "save.json"))
    manager = PuzzleManager(state)
    manager.load_file(str(path))

    manager.start("mirror")
    manager.complete_puzzle()

    assert state.get_flag("puzzle_mirror") is True
