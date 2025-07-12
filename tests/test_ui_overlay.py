import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class DummyRect:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.x, self.y, self.width, self.height = args
        self.left = self.x
        self.top = self.y
        self.topleft = (self.x, self.y)

    def collidepoint(self, pos):
        return (
            self.x <= pos[0] < self.x + self.width
            and self.y <= pos[1] < self.y + self.height
        )


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
        return types.SimpleNamespace(
            get_width=lambda: len(text) * 5, get_height=lambda: self.height
        )

    def get_height(self):
        return self.height


class DummyClock:
    def __init__(self, fps=60.0):
        self._fps = fps

    def get_fps(self):
        return self._fps


class DummyPygame(types.SimpleNamespace):
    SRCALPHA = 1
    Rect = DummyRect
    Surface = DummySurface
    font = types.SimpleNamespace(Font=lambda path, size: DummyFont())
    mouse = types.SimpleNamespace(get_pos=lambda: (15, 15))
    draw = types.SimpleNamespace(rect=lambda surf, color, rect, width=0: None)


def test_update_mouse_hover(monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    from engine import ui_overlay, hotspot

    monkeypatch.setattr(ui_overlay, "pygame", dummy_pg)
    monkeypatch.setattr(hotspot, "pygame", dummy_pg)

    screen = DummySurface()
    overlay = ui_overlay.UIOverlay(screen)
    hotspots = [hotspot.Hotspot(id="test", area=(10, 10, 20, 20), action="noop")]

    overlay.update_mouse_hover(hotspots)
    assert overlay.hover_text == "test"


def test_custom_theme(monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    from engine import ui_overlay

    monkeypatch.setattr(ui_overlay, "pygame", dummy_pg)

    screen = DummySurface()
    theme = {"font_color": (10, 10, 10), "font_size": 24}
    overlay = ui_overlay.UIOverlay(screen, theme=theme)
    assert overlay.theme["font_color"] == (10, 10, 10)
    assert overlay.theme["font_size"] == 24

    clock = DummyClock(30.0)
    overlay.draw_fps(clock)
