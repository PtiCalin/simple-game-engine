import os
import sys
import types
import types as _types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_scene_stack_changes(monkeypatch):
    # Stub pygame and yaml before importing EngineLoop
    class DummyClock:
        def tick(self, fps=None):
            pass

        def get_fps(self):
            return 60.0

    dummy_pg = types.SimpleNamespace(
        event=types.SimpleNamespace(get=lambda: []),
        time=types.SimpleNamespace(get_ticks=lambda: 0, Clock=DummyClock),
        QUIT=0,
        MOUSEBUTTONDOWN=1,
    )
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    monkeypatch.setitem(sys.modules, "yaml", _types.ModuleType("yaml"))
    monkeypatch.setattr("engine.engine_loop.pygame", dummy_pg, raising=False)

    from engine.engine_loop import EngineLoop

    class DummySceneManager:
        def __init__(self):
            self.opened = []
            self.hotspots = []
            self.overlays = []
            self.game_state = types.SimpleNamespace()
            self.dialogue_engine = types.SimpleNamespace(active=False, handle_event=lambda e: None, draw=lambda s: None)
            self.timeline_engine = types.SimpleNamespace(update=lambda t, scene: None)
            self.active_features = {}
            self.scene_start_time = 0
            self.current_scene_id = None
            self.current_scene = None

        def open_scene(self, path: str) -> None:
            self.opened.append(path)
            self.current_scene_id = path

    manager = DummySceneManager()
    loop = EngineLoop(None, "start", manager)

    loop.change_scene("start")
    assert loop.scene_stack == ["start"]
    assert manager.opened[-1] == "start"

    loop.push_scene("overlay")
    assert loop.scene_stack == ["start", "overlay"]
    assert manager.opened[-1] == "overlay"

    loop.pop_scene()
    assert loop.scene_stack == ["start"]
    assert manager.opened[-1] == "start"

    loop.pop_scene()
    assert loop.running is False
