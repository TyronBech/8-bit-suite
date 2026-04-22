import pygame
from core.base_scene import BaseScene
from core.settings import FPS


class SceneManager:
    """
    Owns the game loop and the currently active scene.
    Scenes register themselves by key name.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        clock: pygame.time.Clock,
        fonts: dict[str, pygame.font.Font],
    ):
        self.screen = screen
        self.clock = clock
        self.fonts = fonts
        self._scenes: dict[str, BaseScene] = {}
        self._current: BaseScene | None = None
        self.loading: BaseScene | None = None

    def register(self, key: str, scene: BaseScene) -> None:
        """Register a scene by key name."""

        self._scenes[key] = scene
        if key == "loading":
            self.loading = scene

    def switch_to(self, key: str) -> None:
        """Switch to active scene by key.

        If the requested scene key is not registered, this method will attempt to
        fall back to the "menu" scene if it exists. If neither the requested key
        nor the fallback is available, a ValueError is raised with details.
        """

        target_scene = self._scenes.get(key)
        if target_scene is None:
            fallback_key = "menu"
            target_scene = self._scenes.get(fallback_key)
            if target_scene is not None:
                self._set_current_scene(target_scene)
                return

            available_scenes = ", ".join(sorted(self._scenes.keys()))
            raise ValueError(
                f"Scene '{key}' is not registered. Available scenes: {available_scenes}"
            )

        self._set_current_scene(target_scene)

    def _set_current_scene(self, scene: BaseScene) -> None:
        """Transition between scenes and run lifecycle hooks."""

        if self._current is scene:
            return

        if self._current is not None:
            self._current.on_exit()

        self._current = scene
        self._current.on_enter()

    def run(self) -> None:
        """Main game loop - runs until the window is closed."""

        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000  # Delta time in seconds
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
