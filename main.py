import pygame
import yaml
import sys
import os

from engine.scene_manager import SceneManager

def load_config(path="config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, 'r') as f:
        return yaml.safe_load(f)

class Launcher:
    def __init__(self, config):
        self.config = config
        self.screen = None
        self.scene_manager = None

    def init_window(self):
        width = self.config.get("window", {}).get("width", 800)
        height = self.config.get("window", {}).get("height", 600)
        title = self.config.get("window", {}).get("title", "game-engine")

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

    def run(self):
        print("🚀 Launching game-engine...")
        self.init_window()
        self.scene_manager = SceneManager(self.screen, self.config)
        self.scene_manager.run()

if __name__ == "__main__":
    try:
        config = load_config()
        launcher = Launcher(config)
        launcher.run()
    except Exception as e:
        print("❌ Game crashed:", e)
        pygame.quit()
        sys.exit(1)
