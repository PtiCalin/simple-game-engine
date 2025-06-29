import os
import logging
from typing import Dict, Optional

try:
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .scene import Scene

logger = logging.getLogger(__name__)


class AssetManager:
    """Load and cache images and music files."""

    def __init__(self) -> None:
        self.images: Dict[str, "pygame.Surface"] = {}
        self.music: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Image helpers
    # ------------------------------------------------------------------
    def get_image(self, path: str) -> Optional["pygame.Surface"]:
        """Return a cached :class:`pygame.Surface` for ``path``."""
        if path in self.images:
            return self.images[path]
        if not pygame:
            logger.info("pygame not available, skipping image load: %s", path)
            return None
        if not os.path.exists(path):
            logger.warning("Image not found: %s", path)
            return None
        try:
            image = pygame.image.load(path).convert_alpha()
        except Exception as exc:  # pragma: no cover - only when pygame fails
            logger.error("Failed to load image '%s': %s", path, exc)
            return None
        self.images[path] = image
        return image

    # ------------------------------------------------------------------
    # Music helpers
    # ------------------------------------------------------------------
    def get_music(self, path: str) -> Optional[str]:
        """Preload a music file and cache its path."""
        if path in self.music:
            return self.music[path]
        if not pygame:
            logger.info("pygame not available, skipping music load: %s", path)
            self.music[path] = path
            return path
        if not os.path.exists(path):
            logger.warning("Music not found: %s", path)
            return None
        try:
            pygame.mixer.music.load(path)
        except Exception as exc:  # pragma: no cover - only when pygame fails
            logger.error("Failed to load music '%s': %s", path, exc)
            return None
        self.music[path] = path
        return path

    # ------------------------------------------------------------------
    # Scene helpers
    # ------------------------------------------------------------------
    def preload_scene(self, scene: Scene) -> None:
        """Load assets referenced by ``scene`` into the cache."""
        if scene.background:
            self.get_image(scene.background)
        for overlay in scene.overlays:
            self.get_image(overlay)
        music_path = scene.features.get("music") if scene.features else None
        if music_path:
            self.get_music(music_path)

