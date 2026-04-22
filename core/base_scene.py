import pygame
from typing import Any


class BaseScene:
    """
    All game scenes inherit from this.
    The SceneManager calls these three methods every frame.
    """

    def __init__(self, manager: Any) -> None:
        self.manager = manager

    def on_enter(self) -> None:
        """Run setup when the scene becomes active."""
        # Optional hook: subclasses may override when they need setup logic.
        pass

    def on_exit(self) -> None:
        """Run cleanup when the scene is no longer active."""
        # Optional hook: subclasses may override when they need cleanup logic.
        pass

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
