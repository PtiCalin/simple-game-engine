"""Scene loading and basic game loop management."""

import os
import yaml
import pygame

from .scene import Scene


class SceneManager:
    """Manage scene loading and update the main loop."""

    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.running = True
        self.current_scene = None
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

    def load_scene(self, path):
        """Read a YAML file and return a :class:`Scene` instance."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Scene file not found: {path}")

        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}

        scene_data = data.get("scene", {})
        return Scene(
            id=scene_data.get("id"),
            background=scene_data.get("background"),
            mode=scene_data.get("mode", "simple"),
        )

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((30, 30, 30))  # Dark background
            pygame.display.flip()
            clock.tick(60)
