import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

yaml = pytest.importorskip("yaml")

from engine.locale_manager import LocaleManager


def _write_locale(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def test_load_and_translate(tmp_path):
    loc_dir = tmp_path / "locales"
    loc_dir.mkdir()
    _write_locale(
        loc_dir / "en.yaml",
        """
ui:
  start_game: "Start Game"
dialogue:
  hello: "Hello"
""",
    )
    _write_locale(
        loc_dir / "fr.yaml",
        """
ui:
  start_game: "Commencer"
""",
    )

    lm = LocaleManager()
    lm.load_locales(str(loc_dir))

    assert set(lm.get_available_locales()) == {"en", "fr"}
    assert lm.translate("ui.start_game") == "Start Game"

    lm.set_locale("fr")
    assert lm.translate("ui.start_game") == "Commencer"
    # fallback to en
    assert lm.translate("dialogue.hello") == "Hello"

    # missing key
    assert lm.translate("missing.key") == "missing.key"
    assert "missing.key" in lm.missing_keys

    out_file = tmp_path / "missing.txt"
    lm.export_missing_keys(str(out_file))
    assert out_file.read_text().strip() == "missing.key"


def test_locale_fallback_chain(tmp_path):
    loc_dir = tmp_path / "locales"
    loc_dir.mkdir()
    _write_locale(loc_dir / "en.yaml", "greet: Hi")
    _write_locale(loc_dir / "fr.yaml", "greet: Salut")

    lm = LocaleManager()
    lm.load_locales(str(loc_dir))
    lm.set_locale("fr-CA")

    assert lm.translate("greet") == "Salut"
    assert lm.has_translation("greet") is True

