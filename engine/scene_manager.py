class SceneManager:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.running = True

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((30, 30, 30))  # Dark background
            pygame.display.flip()
            clock.tick(60)
