import pygame


class BaseScene:
    """
    All game scenes inherit from this.
    The SceneManager calls these three methods every frame.
    """

    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        """Handle keyboard and mouse input."""
        raise NotImplementedError(
            "handle_events method must be implemented by subclasses"
        )

    def update(self, dt: float) -> None:
        """Update game logic. dt = delta time in seconds."""
        raise NotImplementedError("update method must be implemented by subclasses")

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene to the screen."""
        raise NotImplementedError("draw method must be implemented by subclasses")
