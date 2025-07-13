import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class DummyRect:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.x, self.y, self.w, self.h = args
        self.left = self.x
        self.top = self.y
        self.topleft = (self.x, self.y)

    def collidepoint(self, pos):
        return self.x <= pos[0] < self.x + self.w and self.y <= pos[1] < self.y + self.h


class DummySurface:
    def __init__(self, size=(100, 100), flags=None):
        self._size = size

    def get_size(self):
        return self._size

    def blit(self, *args, **kwargs):
        pass

    def fill(self, *args, **kwargs):
        pass


class DummyPygame(types.SimpleNamespace):
    SRCALPHA = 1
    Rect = DummyRect
    Surface = DummySurface
    event = types.SimpleNamespace(Event=object)

    class image:
        @staticmethod
        def load(path):
            class DummySurf(DummySurface):
                def convert_alpha(self):
                    return self

            return DummySurf()


def test_load_and_preview(tmp_path, monkeypatch):
    dummy_pg = DummyPygame()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pg)
    from editor import asset_inspector
    from engine import asset_manager as am

    monkeypatch.setattr(asset_inspector, "pygame", dummy_pg)
    monkeypatch.setattr(am, "pygame", dummy_pg)

    bg_dir = tmp_path / "backgrounds"
    bg_dir.mkdir()
    (bg_dir / "bg.png").write_text("img")

    inspector = asset_inspector.AssetInspector(
        preview_size=(10, 10), assets_dir=str(tmp_path)
    )
    inspector.load_assets_from_folder("backgrounds")

    assert inspector.asset_list == ["backgrounds/bg.png"]
    inspector.select_asset("backgrounds/bg.png")
    inspector.add_to_layer_stack("backgrounds/bg.png")
    inspector.preview_layer_stack()
    assert inspector.selected_asset == "backgrounds/bg.png"
    assert inspector.layer_stack == ["backgrounds/bg.png"]
