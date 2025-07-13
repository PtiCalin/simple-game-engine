from __future__ import annotations

import logging
import os
import sys
from typing import List, Dict, Optional

try:  # pragma: no cover - allow running tests without pygame
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None

try:
    import yaml
except Exception:  # pragma: no cover - allow running tests without PyYAML
    yaml = None

from .asset_manager import AssetManager

logger = logging.getLogger(__name__)


class PerformanceManager:
    """Runtime performance tuning and diagnostics."""

    def __init__(self, config_path: str = "config/performance.yaml") -> None:
        self.config: Dict = self._load_config(config_path)
        perf = self.config.get("performance", {})
        self.target_fps: int = int(perf.get("target_fps", 60))
        self.clock = pygame.time.Clock() if pygame else None
        self.asset_cache = AssetManager()
        self.resource_log: List[str] = []
        self.frame_times: List[float] = []
        self.diagnostics_enabled: bool = bool(perf.get("diagnostics_enabled", False))
        self.max_cache_size_mb: int = int(perf.get("asset_cache_limit_mb", 200))
        self._profiles: Dict[str, Dict] = self.config.get("profiles", {})

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------
    def _load_config(self, path: str) -> Dict:
        if not yaml or not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    # ------------------------------------------------------------------
    # Framerate helpers
    # ------------------------------------------------------------------
    def set_target_fps(self, fps: int) -> None:
        self.target_fps = int(fps)

    def track_frame(self) -> None:
        if not self.clock:
            return
        ms = self.clock.tick(self.target_fps)
        self.frame_times.append(ms / 1000.0)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)

    def enforce_frame_delay(self) -> None:
        if self.clock:
            self.clock.tick(self.target_fps)

    # ------------------------------------------------------------------
    # Diagnostics & cache helpers
    # ------------------------------------------------------------------
    def log_resource_usage(self) -> None:
        if not self.diagnostics_enabled:
            return
        current = self.cache_size_mb()
        msg = f"Cache size: {current:.2f} MB"
        self.resource_log.append(msg)
        logger.debug(msg)

    def cache_size_mb(self) -> float:
        size = 0
        for coll in (self.asset_cache.image_cache, self.asset_cache.sound_cache, self.asset_cache.music_cache):
            for obj in coll.values():
                try:
                    size += sys.getsizeof(obj)
                except Exception:
                    pass
        return size / (1024 * 1024)

    def clear_unused_assets(self) -> None:
        self.asset_cache.clear_cache()

    def trim_cache(self) -> None:
        if self.cache_size_mb() > self.max_cache_size_mb:
            self.clear_unused_assets()

    def get_diagnostics(self) -> Dict:
        avg_fps = 0.0
        if self.frame_times:
            avg_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
        return {
            "average_fps": avg_fps,
            "cache_size_mb": self.cache_size_mb(),
            "frames_tracked": len(self.frame_times),
        }

    def flush_scene_cache(self, scene_id: str) -> None:
        self.clear_unused_assets()

    def apply_performance_profile(self, profile_name: str) -> None:
        profile = self._profiles.get(profile_name, {})
        if not profile:
            return
        if "target_fps" in profile:
            self.target_fps = int(profile["target_fps"])
        if "cache_limit" in profile:
            self.max_cache_size_mb = int(profile["cache_limit"])
        if "diagnostics" in profile:
            self.diagnostics_enabled = bool(profile["diagnostics"])
