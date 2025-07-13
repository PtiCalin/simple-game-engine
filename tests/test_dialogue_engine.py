import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.dialogue_engine import DialogueEngine
from engine.game_state import GameState


def _write_dialogue(path):
    data = {
        "dialogues": [
            {
                "id": "gatekeeper_intro",
                "memory_flag": "talked_to_gatekeeper",
                "lines": [
                    {"speaker": "Gatekeeper", "text": "You're not from around here, are you?"},
                    {
                        "options": [
                            {"text": "I'm just passing through.", "next": "reply_chill"},
                            {"text": "Who are you?", "next": "reply_defensive", "condition": "!npc_hostile"},
                        ]
                    },
                    {"id": "reply_chill", "speaker": "Gatekeeper", "text": "Then don't get lost in these ruins."},
                    {"id": "reply_defensive", "speaker": "Gatekeeper", "text": "That's none of your business, outsider."},
                ],
                "on_complete": {"set_flag": "gatekeeper_intro_complete"},
            }
        ]
    }
    with open(path, "w") as fh:
        json.dump(data, fh)


def test_dialogue_flow(tmp_path):
    path = tmp_path / "dialogue.json"
    _write_dialogue(path)

    state = GameState()
    state.set_flag("npc_hostile", False)
    engine = DialogueEngine(state)
    engine.load_file(str(path))
    engine.start("gatekeeper_intro")

    node = engine.current_node()
    assert node.text == "You're not from around here, are you?"
    assert state.get_flag("talked_to_gatekeeper") is True

    engine.advance()
    assert engine.awaiting_choice is True
    assert len(engine._option_cache) == 2

    engine.choose(0)
    node = engine.current_node()
    assert node.text == "Then don't get lost in these ruins."
    engine.advance()
    assert state.get_flag("gatekeeper_intro_complete") is True


def test_option_condition(tmp_path):
    path = tmp_path / "dialogue.json"
    _write_dialogue(path)

    state = GameState()
    state.set_flag("npc_hostile", True)
    engine = DialogueEngine(state)
    engine.load_file(str(path))
    engine.start("gatekeeper_intro")
    engine.advance()

    assert engine.awaiting_choice is True
    assert len(engine._option_cache) == 1
    assert engine._option_cache[0].text == "I'm just passing through."
