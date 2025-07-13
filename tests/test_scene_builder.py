import os
import sys
import types
import pytest
yaml = pytest.importorskip("yaml")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from editor.scene_builder import SceneBuilder


class DummyRect:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.x, self.y, self.w, self.h = args
        self.left = self.x
        self.top = self.y
        self.topleft = (self.x, self.y)

    def collidepoint(self, pos):
        return (
            self.x <= pos[0] < self.x + self.w and self.y <= pos[1] < self.y + self.h
        )


class DummySurface:
    def __init__(self, size=(100, 100)):
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
        return types.SimpleNamespace(get_width=lambda: len(text), get_height=lambda: self.height)

    def get_height(self):
        return self.height


class DummyPygame(types.SimpleNamespace):
    SRCALPHA = 1
    Rect = DummyRect
    Surface = DummySurface
    font = types.SimpleNamespace(Font=lambda path, size: DummyFont())
    mouse = types.SimpleNamespace(get_pos=lambda: (0, 0))
    draw = types.SimpleNamespace(rect=lambda *a, **k: None)
    MOUSEBUTTONDOWN = 1
    MOUSEBUTTONUP = 2
    event = types.SimpleNamespace(Event=object)


def test_load_edit_save(tmp_path, monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    from engine import ui_overlay, hotspot

    monkeypatch.setattr(ui_overlay, "pygame", dummy_pg)
    monkeypatch.setattr(hotspot, "pygame", dummy_pg)
    monkeypatch.setattr("editor.scene_builder.pygame", dummy_pg)

    yaml_data = """
scene:
  id: sample
  background: bg.png
hotspots:
  - id: door
    area: [1, 2, 3, 4]
    action: open_scene
    target: next
"""
    path = tmp_path / "sample.yaml"
    path.write_text(yaml_data)

    screen = DummySurface()
    builder = SceneBuilder(screen, scenes_dir=str(tmp_path))
    builder.load_scene_yaml(str(path))

    assert builder.scene_id == "sample"
    assert len(builder.hotspots) == 1

    builder.edit_property("title", "Title")
    assert builder.scene_data["title"] == "Title"

    builder.toggle_live_preview(False)
    assert builder.live_preview is False

    builder.save_to_yaml()
    saved = yaml.safe_load(path.read_text())
    assert saved["scene"]["title"] == "Title"
    assert saved["hotspots"][0]["id"] == "door"
