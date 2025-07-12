from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

try:  # pragma: no cover - allow running tests without pygame
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

from .scene import Scene

logger = logging.getLogger(__name__)


class AssetManager:
    """Load and cache game assets with smart caching and fallbacks."""

    def __init__(self, base_path: str = "assets/", search_paths: Optional[List[str]] = None) -> None:
        self.base_path = base_path
        self.search_paths: List[str] = search_paths or []
        self.image_cache: Dict[str, "pygame.Surface"] = {}
        self.music_cache: Dict[str, str] = {}
        self.sound_cache: Dict[str, "pygame.mixer.Sound"] = {}

        # backward compatible attribute names
        self.images = self.image_cache
        self.music = self.music_cache
        self.sounds = self.sound_cache

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------
    def _resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            if os.path.exists(path):
                return path
        else:
            candidate = os.path.join(self.base_path, path)
            if os.path.exists(candidate):
                return candidate
        for root in self.search_paths:
            candidate = os.path.join(root, path)
            if os.path.exists(candidate):
                return candidate
        return os.path.join(self.base_path, path)

    def _placeholder_image(self) -> Optional["pygame.Surface"]:
        if not pygame:
            return None
        surf = pygame.Surface((1, 1), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 255))
        return surf

    # ------------------------------------------------------------------
    # Image helpers
    # ------------------------------------------------------------------
    def get_image(self, path: str) -> Optional["pygame.Surface"]:
        key = os.path.normpath(path)
        if key in self.image_cache:
            return self.image_cache[key]

        resolved = self._resolve_path(path)
        if not pygame:
            logger.info("pygame not available, skipping image load: %s", resolved)
            return None
        if not os.path.exists(resolved):
            logger.warning("Image not found: %s", resolved)
            image = self._placeholder_image()
            if image:
                self.image_cache[key] = image
            return image
        try:
            image = pygame.image.load(resolved).convert_alpha()
        except Exception as exc:  # pragma: no cover - only when pygame fails
            logger.error("Failed to load image '%s': %s", resolved, exc)
            image = self._placeholder_image()
        if image:
            self.image_cache[key] = image
        return image

    # ------------------------------------------------------------------
    # Music helpers
    # ------------------------------------------------------------------
    def get_music(self, path: str) -> Optional[str]:
        key = os.path.normpath(path)
        if key in self.music_cache:
            return self.music_cache[key]

        resolved = self._resolve_path(path)
        if not pygame:
            logger.info("pygame not available, skipping music load: %s", resolved)
            self.music_cache[key] = resolved
            return resolved
        if not os.path.exists(resolved):
            logger.warning("Music not found: %s", resolved)
            self.music_cache[key] = resolved
            return resolved
        try:
            pygame.mixer.music.load(resolved)
        except Exception as exc:  # pragma: no cover - only when pygame fails
            logger.error("Failed to load music '%s': %s", resolved, exc)
        self.music_cache[key] = resolved
        return resolved

    # ------------------------------------------------------------------
    # Sound effect helpers
    # ------------------------------------------------------------------
    def get_sound(self, path: str) -> Optional["pygame.mixer.Sound"]:
        key = os.path.normpath(path)
        if key in self.sound_cache:
            return self.sound_cache[key]

        resolved = self._resolve_path(path)
        if not pygame:
            logger.info("pygame not available, skipping sound load: %s", resolved)
            return None
        if not os.path.exists(resolved):
            logger.warning("Sound not found: %s", resolved)
            return None
        try:
            sound = pygame.mixer.Sound(resolved)
        except Exception as exc:  # pragma: no cover - only when pygame fails
            logger.error("Failed to load sound '%s': %s", resolved, exc)
            return None
        self.sound_cache[key] = sound
        return sound

    # ------------------------------------------------------------------
    # Scene helpers
    # ------------------------------------------------------------------
    def preload_scene_assets(self, scene_data: Scene | Dict) -> None:
        if isinstance(scene_data, dict):
            scene_dict = scene_data
        else:
            scene_dict = {
                "background": getattr(scene_data, "background", None),
                "overlays": getattr(scene_data, "overlays", []),
                "features": getattr(scene_data, "features", {}) or {},
                "id": getattr(scene_data, "id", None),
            }
        if scene_dict.get("background"):
            self.get_image(scene_dict["background"])
        for overlay in scene_dict.get("overlays", []) or []:
            self.get_image(overlay)
        features = scene_dict.get("features") or {}
        music_path = features.get("music")
        if music_path:
            self.get_music(music_path)
        sound_path = features.get("sound")
        if sound_path:
            self.get_sound(sound_path)
        for snd in features.get("sounds", []):
            self.get_sound(snd)
        logger.debug("Preloaded assets for scene: %s", scene_dict.get("id"))

    # backward compatibility
    preload_scene = preload_scene_assets

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------
    def clear_cache(self, category: Optional[str] = None) -> None:
        if category is None:
            self.image_cache.clear()
            self.music_cache.clear()
            self.sound_cache.clear()
        elif category in {"images", "image"}:
            self.image_cache.clear()
        elif category in {"music", "musics"}:
            self.music_cache.clear()
        elif category in {"sounds", "sound"}:
            self.sound_cache.clear()
