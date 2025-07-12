import logging
import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class DummyRect:
    def __init__(self, *args, **kwargs):
        pass

    def collidepoint(self, pos):
        return False


class DummyPygame(types.SimpleNamespace):
    Rect = DummyRect
    class image:
        @staticmethod
        def load(path):
            class DummySurf:
                def convert_alpha(self):
                    return self

            return DummySurf()

    class mixer:
        class music:
            @staticmethod
            def load(path):
                return None


def test_preload_without_pygame(monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "pygame", DummyPygame)
    from engine.asset_manager import AssetManager
    Scene = types.SimpleNamespace

    monkeypatch.setattr("engine.asset_manager.pygame", None)
    manager = AssetManager()
    scene = Scene(id="s", background="bg.png", overlays=["ov.png"], features={"music": "song.mp3"})
    with caplog.at_level(logging.INFO):
        manager.preload_scene(scene)
    assert manager.images == {}
    assert manager.music == {"song.mp3": "song.mp3"}
    assert "pygame not available" in caplog.text


def test_getters_with_stub(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygame", DummyPygame)
    from engine.asset_manager import AssetManager

    monkeypatch.setattr("engine.asset_manager.os.path.exists", lambda p: True)
    monkeypatch.setattr("engine.asset_manager.pygame", DummyPygame)

    manager = AssetManager()
    surf = manager.get_image("img.png")
    assert surf is not None
    assert manager.get_image("img.png") is surf
    manager.get_music("music.mp3")
    assert manager.music["music.mp3"] == "music.mp3"


def test_load_real_files(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "pygame", DummyPygame)
    from engine.asset_manager import AssetManager

    monkeypatch.setattr("engine.asset_manager.pygame", DummyPygame)

    image_path = tmp_path / "image.png"
    audio_path = tmp_path / "sound.ogg"
    image_path.write_bytes(b"img")
    audio_path.write_bytes(b"aud")

    manager = AssetManager()

    surf = manager.get_image(str(image_path))
    assert surf is not None
    assert manager.get_image(str(image_path)) is surf

    music = manager.get_music(str(audio_path))
    assert music == str(audio_path)
    assert manager.get_music(str(audio_path)) == str(audio_path)

