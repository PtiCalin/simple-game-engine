import os
import sys
import types
import pytest

yaml = pytest.importorskip("yaml")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class DummyPygame(types.SimpleNamespace):
    KEYDOWN = 1
    KEYUP = 2
    JOYBUTTONDOWN = 3
    JOYBUTTONUP = 4
    K_w = 119
    K_ESCAPE = 27

    def __init__(self):
        key_module = types.SimpleNamespace(
            name=lambda code: {self.K_w: "w", self.K_ESCAPE: "escape"}.get(code, "")
        )
        super().__init__(key=key_module, joystick=types.SimpleNamespace(get_count=lambda: 0))


def test_load_and_save(tmp_path, monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    from engine import input_manager

    monkeypatch.setattr(input_manager, "pygame", dummy_pg)

    cfg = {
        "controls": {"interact": "E"},
        "gamepad": {"interact": 0},
    }
    path = tmp_path / "bindings.yaml"
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(cfg, fh)

    mgr = input_manager.InputManager(binding_file=str(path))
    assert mgr.bindings["interact"] == "E"
    assert mgr.gamepad_bindings["interact"] == 0

    mgr.bind_action("interact", "F")
    mgr.save_bindings(str(path))

    loaded = yaml.safe_load(path.read_text())
    assert loaded["controls"]["interact"] == "F"


def test_handle_events(monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    from engine import input_manager

    monkeypatch.setattr(input_manager, "pygame", dummy_pg)

    mgr = input_manager.InputManager(binding_file="")
    mgr.bind_action("jump", "w")
    mgr.bind_gamepad_action("jump", 0)

    key_event = types.SimpleNamespace(type=dummy_pg.KEYDOWN, key=dummy_pg.K_w)
    mgr.handle_event(key_event)
    assert mgr.is_action_pressed("jump") is True
    assert mgr.input_source == "keyboard"

    key_up = types.SimpleNamespace(type=dummy_pg.KEYUP, key=dummy_pg.K_w)
    mgr.handle_event(key_up)
    assert mgr.is_action_pressed("jump") is False

    pad_event = types.SimpleNamespace(type=dummy_pg.JOYBUTTONDOWN, button=0)
    mgr.handle_event(pad_event)
    assert mgr.is_action_pressed("jump") is True
    assert mgr.input_source == "gamepad"

