import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.game_state import GameState


class DummyRect:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.x, self.y, self.width, self.height = args
        self.left = self.x
        self.top = self.y
        self.topleft = (self.x, self.y)

    def collidepoint(self, pos):
        return False


class DummySurface:
    def __init__(self, size=(100, 100), flags=None):
        self._size = size

    def get_size(self):
        return self._size

    def blit(self, *args, **kwargs):
        pass

    def fill(self, *args, **kwargs):
        pass


class DummyFont:
    def __init__(self, *args, **kwargs):
        self.height = 10

    def render(self, text, aa, color):
        return DummySurface((len(text) * 5, self.height))

    def get_height(self):
        return self.height

    def size(self, text):
        return len(text) * 5, self.height


class DummyClock:
    def __init__(self):
        pass

    def tick(self, fps=None):
        pass

    def get_fps(self):
        return 60.0


class DummyPygame(types.SimpleNamespace):
    SRCALPHA = 1
    Rect = DummyRect
    Surface = DummySurface
    font = types.SimpleNamespace(Font=lambda path, size: DummyFont())
    time = types.SimpleNamespace(get_ticks=lambda: 123)
    def __init__(self):
        super().__init__()
        self.time.Clock = lambda: DummyClock()


def test_gather_info_and_render(monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    monkeypatch.setitem(sys.modules, "yaml", types.ModuleType("yaml"))
    from engine import debug_overlay

    monkeypatch.setattr(debug_overlay, "pygame", dummy_pg)

    state = GameState()
    state.set_flag("started", True)
    state.set_var("score", 5)
    sm = types.SimpleNamespace(current_scene_id="intro")
    wm = types.SimpleNamespace(world_id="w1", current_region_id="r1")
    dlg = types.SimpleNamespace(active_dialogue_id="talk")

    overlay = debug_overlay.DebugOverlay(state, sm, wm, dlg)
    overlay.toggle_visibility()
    overlay.update(0.016)
    lines = overlay.gather_debug_info()

    joined = "\n".join(lines)
    assert "FPS:" in joined
    assert "w1" in joined
    assert "✅ started" in joined
    assert "score: 5" in joined
    assert "talk" in joined

    surf = DummySurface()
    overlay.render(surf)

