from __future__ import annotations

import getpass
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class GameExporter:
    """Package a game into a platform specific bundle."""

    target_platform: str  # "windows", "mac", "web"
    game_title: str
    version: str
    include_dev_tools: bool = False
    optimize_assets: bool = False
    export_path: str = "dist"

    export_dir: str = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def export(self, target: str | None = None) -> str:
        """Run the export pipeline and return the export directory."""
        if target:
            self.target_platform = target
        logger.info("Exporting for %s", self.target_platform)
        self.prepare_export_dir()
        self.copy_core_files()
        if not self.include_dev_tools:
            self.strip_dev_modules()
        if self.optimize_assets:
            self.minify_assets()
        self.inject_metadata()
        if self.target_platform == "windows":
            self.build_executable_windows()
        elif self.target_platform == "mac":
            self.build_bundle_mac()
        elif self.target_platform == "web":
            self.build_web_package()
        else:
            raise ValueError(f"Unknown target platform: {self.target_platform}")
        return self.export_dir

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------
    def prepare_export_dir(self) -> None:
        safe_title = self.game_title.replace(" ", "")
        self.export_dir = os.path.join(
            self.export_path, f"{safe_title}-v{self.version}"
        )
        if os.path.exists(self.export_dir):
            shutil.rmtree(self.export_dir)
        os.makedirs(self.export_dir, exist_ok=True)

    def copy_core_files(self) -> None:
        """Copy engine, assets and config to the export directory."""
        for name in ["main.py", "config.yaml", "LICENSE"]:
            if os.path.exists(name):
                shutil.copy(name, self.export_dir)
        for dirname in ["engine", "game", "scenes", "assets", "ui"]:
            if os.path.exists(dirname):
                shutil.copytree(dirname, os.path.join(self.export_dir, dirname))

    def strip_dev_modules(self) -> None:
        """Remove development only modules from the export bundle."""
        editor_path = os.path.join(self.export_dir, "editor")
        if os.path.isdir(editor_path):
            shutil.rmtree(editor_path)
        dbg_overlay = os.path.join(self.export_dir, "engine", "debug_overlay.py")
        if os.path.isfile(dbg_overlay):
            os.remove(dbg_overlay)

    def minify_assets(self) -> None:
        """Placeholder asset compression step."""
        assets_dir = os.path.join(self.export_dir, "assets")
        for root, _dirs, files in os.walk(assets_dir):
            for fname in files:
                path = os.path.join(root, fname)
                logger.debug("Would compress %s", path)

    def inject_metadata(self) -> None:
        """Write metadata.yaml with basic export information."""
        author = os.environ.get("USER") or getpass.getuser()
        metadata = [
            f'title: "{self.game_title}"',
            f'version: "{self.version}"',
            f'author: "{author}"',
            f'platform: "{self.target_platform.capitalize()}"',
            f'exported_at: "{datetime.now().isoformat(timespec="minutes")}"',
        ]
        with open(
            os.path.join(self.export_dir, "metadata.yaml"), "w", encoding="utf-8"
        ) as fh:
            fh.write("\n".join(metadata) + "\n")

    # ------------------------------------------------------------------
    # Platform build steps
    # ------------------------------------------------------------------
    def build_executable_windows(self) -> None:  # pragma: no cover - external call
        """Invoke pyinstaller to build a Windows executable."""
        cmd = [
            "pyinstaller",
            "--onefile",
            "main.py",
            "--name",
            self.game_title,
            "--distpath",
            self.export_dir,
        ]
        subprocess.run(cmd, check=False)

    def build_bundle_mac(self) -> None:  # pragma: no cover - external call
        """Invoke pyinstaller to build a macOS app bundle."""
        cmd = [
            "pyinstaller",
            "--onefile",
            "main.py",
            "--name",
            self.game_title,
            "--distpath",
            self.export_dir,
        ]
        subprocess.run(cmd, check=False)

    def build_web_package(self) -> None:  # pragma: no cover - placeholder
        """Create a simple web export folder."""
        web_dir = os.path.join(self.export_dir, "web_export")
        os.makedirs(web_dir, exist_ok=True)
        shutil.copytree(
            os.path.join(self.export_dir, "assets"), os.path.join(web_dir, "assets")
        )
        with open(os.path.join(web_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write("<html><body><p>Web build placeholder</p></body></html>")
