"""Scene loading and basic game loop management."""

import os
import yaml
import pygame

from .scene import Scene
from .hotspot import Hotspot
from .world_loader import WorldLoader, Region


class SceneManager:
    """Manage scene loading and update the main loop."""

    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.running = True
        self.current_scene = None
        self.overlays = []
        self.active_features = {}
        self.hotspots = []
        self.flags = {}
        self.scene_start_time = 0
        self.scenes_dir = self.config.get("scenes_dir", "game/scenes")
        self.world_loader: WorldLoader | None = None
        self.current_region: Region | None = None
        self.current_scene_id: str | None = None

        if self.config.get("start_world"):
            self.load_start_world()
        else:
            self.load_start_scene()

    # ------------------------------------------------------------------
    # Scene Loading
    # ------------------------------------------------------------------
    def load_start_scene(self):
        """Load the starting scene defined in ``config.yaml``."""
        scene_path = self.config.get("start_scene")
        if not scene_path:
            raise ValueError("Missing 'start_scene' in config")

        self.current_scene = self.load_scene(scene_path)
        self.current_scene_id = self.current_scene.id
        self.activate_scene(self.current_scene)

    def load_start_world(self) -> None:
        """Load the starting world and initialize the first region."""
        world_path = self.config.get("start_world")
        if not world_path:
            raise ValueError("Missing 'start_world' in config")

        self.world_loader = WorldLoader(world_path)
        self.current_region = self.world_loader.first_region()
        if not self.current_region or not self.current_region.scenes:
            raise ValueError("World file has no regions or scenes")
        self.open_scene(self.current_region.scenes[0])

    def load_scene(self, path):
        """Read a YAML file and return a :class:`Scene` instance."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Scene file not found: {path}")

        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}

        scene_data = data.get("scene", {})
        hotspots_data = data.get("hotspots", []) or []
        hotspots: list[Hotspot] = []
        for hs in hotspots_data:
            if not isinstance(hs, dict):
                continue
            area = tuple(hs.get("area", [0, 0, 0, 0]))
            if len(area) != 4:
                area = (0, 0, 0, 0)
            hotspots.append(
                Hotspot(
                    id=hs.get("id", ""),
                    area=area,
                    action=hs.get("action", ""),
                    target=hs.get("target"),
                )
            )
        return Scene(
            id=scene_data.get("id"),
            background=scene_data.get("background"),
            mode=scene_data.get("mode", "simple"),
            features=scene_data.get("features", {}) or {},
            overlays=scene_data.get("overlays", []) or [],
            hotspots=hotspots,
        )

    def activate_scene(self, scene: Scene):
        """Load assets and enable features for the given scene."""
        self.overlays = []
        self.active_features = scene.features or {}
        self.hotspots = scene.hotspots or []
        self.scene_start_time = pygame.time.get_ticks()

        music_path = self.active_features.get("music")
        if music_path and os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
            except pygame.error as exc:
                print(f"Failed to play music '{music_path}': {exc}")

        for overlay_path in scene.overlays:
            if os.path.exists(overlay_path):
                try:
                    image = pygame.image.load(overlay_path).convert_alpha()
                    self.overlays.append(image)
                except pygame.error as exc:
                    print(f"Failed to load overlay '{overlay_path}': {exc}")

    # ------------------------------------------------------------------
    # Hotspot Actions
    # ------------------------------------------------------------------
    def scene_path_from_id(self, scene_id: str) -> str:
        return os.path.join(self.scenes_dir, f"{scene_id}.yaml")

    def open_scene(self, path: str) -> None:
        """Load another scene from ``path`` or scene id and activate it."""
        if not os.path.exists(path):
            path = self.scene_path_from_id(path)
            self.current_scene_id = os.path.splitext(os.path.basename(path))[0]
        else:
            self.current_scene_id = os.path.splitext(os.path.basename(path))[0]
        scene = self.load_scene(path)
        self.current_scene = scene
        self.activate_scene(scene)

    def teleport(self, region_id: str, scene_id: str | None = None) -> None:
        if not self.world_loader:
            return
        region = self.world_loader.get_region(region_id)
        if not region:
            return
        self.current_region = region
        target_scene = scene_id or (region.scenes[0] if region.scenes else None)
        if target_scene:
            self.open_scene(target_scene)

    def show_dialogue(self, text: str) -> None:
        """Display dialogue text or integrate with a dialogue system."""
        # Placeholder: print to console for now
        print(text)

    def toggle_flag(self, flag: str) -> None:
        """Flip the boolean value of ``flag`` in ``self.flags``."""
        self.flags[flag] = not self.flags.get(flag, False)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for hs in self.hotspots:
                        if hs.check_click(event.pos):
                            hs.trigger(self)

            self.screen.fill((30, 30, 30))  # Dark background

            for overlay in self.overlays:
                self.screen.blit(overlay, (0, 0))

            if self.active_features.get("time_loop"):
                duration = self.active_features.get("time_loop")
                if isinstance(duration, bool):
                    duration = 5000  # Default duration when True
                try:
                    duration = int(duration)
                except (TypeError, ValueError):
                    duration = 5000

                if pygame.time.get_ticks() - self.scene_start_time >= duration:
                    self.activate_scene(self.current_scene)

            pygame.display.flip()
            clock.tick(60)
