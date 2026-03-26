import pygame
from core.base_scene import BaseScene

class SceneManager:
    """
    Owns the game loop and the currently active scene.
    Scenes register themselves by key name.
    """

    def __init__ (self, screen: pygame.Surface, clock: pygame.time.Clock, fonts: dict):
        self.screen = screen
        self.clock = clock
        self.fonts = fonts
        self._scenes: dict = {}
        self._current: BaseScene | None = None

    def register (self, key: str, scene) -> None:
        """ Register a scene by key name. """

        self._scenes[key] = scene
        if key == "loading":
            self.loading = scene

    def switch_to (self, key: str) -> None:
        """ Switch to active scene by key. """

        self._current = self._scenes[key]

    def run (self) -> None:
        """ Main game loop - runs until the window is closed. """

        running = True

        while running:
            dt = self.clock.tick(60) / 1000  # Delta time in seconds
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            if self._current:
                self._current.handle_events(events)
                self._current.update(dt)
                self._current.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
