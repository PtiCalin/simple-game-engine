import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.dialogue_engine import DialogueEngine
from engine.game_state import GameState
from engine.locale_manager import LocaleManager


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


def test_flag_injection_and_clearing(tmp_path):
    path = tmp_path / "dialogue.json"
    data = {
        "dialogues": [
            {
                "id": "flag_test",
                "lines": [
                    {"text": "Hello", "set_flag": "met"},
                    {"text": "Secret", "requires_flag": "met", "clear_flag": "met"},
                ],
            }
        ]
    }
    with open(path, "w") as fh:
        json.dump(data, fh)

    state = GameState()
    engine = DialogueEngine(state)
    engine.load_file(str(path))
    engine.start("flag_test")

    node = engine.current_node()
    assert node.text == "Hello"
    engine.advance()
    node = engine.current_node()
    assert node.text == "Secret"
    engine.advance()
    assert state.get_flag("met") is False


def test_memory_branching(tmp_path):
    path = tmp_path / "dialogue.json"
    data = {
        "dialogues": [
            {
                "id": "memory_test",
                "lines": [
                    {
                        "id": "ask",
                        "text": "Ask",
                        "options": [
                            {
                                "text": "Yes",
                                "next": "yes",
                                "set_memory": {"last_choice": "yes"},
                            },
                            {
                                "text": "No",
                                "next": "no",
                                "set_memory": {"last_choice": "no"},
                            },
                        ],
                    },
                    {"id": "yes", "text": "Great", "next": "follow"},
                    {"id": "no", "text": "Too bad", "next": "follow"},
                    {"id": "follow", "requires_memory": "last_choice == no", "text": "You said no"},
                ],
            }
        ]
    }
    with open(path, "w") as fh:
        json.dump(data, fh)

    state = GameState()
    engine = DialogueEngine(state)
    engine.load_file(str(path))
    engine.start("memory_test")

    engine.advance()
    engine.choose(1)  # choose "No"
    node = engine.current_node()
    assert node.text == "Too bad"
    engine.advance()
    node = engine.current_node()
    assert node.text == "You said no"


def test_localized_dialogue(tmp_path):
    yaml = pytest.importorskip("yaml")
    loc_dir = tmp_path / "loc"
    loc_dir.mkdir()
    with open(loc_dir / "en.yaml", "w") as fh:
        fh.write("hello: 'Hello'")
    with open(loc_dir / "fr.yaml", "w") as fh:
        fh.write("hello: 'Bonjour'")

    path = tmp_path / "dialogue.json"
    data = {"dialogues": [{"id": "loc", "lines": [{"text": "hello"}]}]}
    with open(path, "w") as fh:
        json.dump(data, fh)

    lm = LocaleManager()
    lm.load_locales(str(loc_dir))
    lm.set_locale("fr")
    state = GameState()
    engine = DialogueEngine(state, locale_manager=lm)
    engine.load_file(str(path))
    engine.start("loc")
    node = engine.current_node()
    assert engine.resolve_localized_text(node.text) == "Bonjour"
