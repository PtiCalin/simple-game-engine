import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.dialogue_engine import DialogueEngine
from engine.game_state import GameState


def test_dialogue_flow(tmp_path):
    data = {
        "dialogues": [
            {
                "id": "gatekeeper_intro",
                "lines": [
                    {"speaker": "Gatekeeper", "text": "You're not from here, are you?"},
                    {
                        "options": [
                            {"text": "I'm just passing through.", "next": "gatekeeper_reply1"},
                            {"text": "Who are you?", "next": "gatekeeper_reply2"},
                        ]
                    },
                ],
            },
            {
                "id": "gatekeeper_reply1",
                "lines": [
                    {"speaker": "Gatekeeper", "text": "Keep moving then.", "set_flag": "passed_gate"}
                ],
            },
            {
                "id": "gatekeeper_reply2",
                "lines": [
                    {"speaker": "Gatekeeper", "text": "I'm the guardian of this gate.", "set_flag": "asked_name"}
                ],
            },
        ]
    }
    path = tmp_path / "dialogue.json"
    with open(path, "w") as fh:
        json.dump(data, fh)

    state = GameState()
    engine = DialogueEngine(state)
    engine.load_file(str(path))
    engine.start("gatekeeper_intro")

    node = engine.current_node()
    assert node.text == "You're not from here, are you?"
    engine.advance()

    node = engine.current_node()
    assert len(node.options) == 2

    engine.choose(0)
    node = engine.current_node()
    assert node.text == "Keep moving then."
    engine.advance()
    assert state.get_flag("passed_gate") is True

