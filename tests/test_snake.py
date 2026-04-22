"""
tests/test_snake.py

Tests for Snake game logic.
Rules:
  - No pygame.display initialization (headless-safe).
  - pygame.init() is called once via a session fixture.
"""

import pytest
import pygame

from scenes.snake import SnakeScene
from core.settings import SNAKE_COLS, SNAKE_ROWS

# ------------------------------------------------------------------ fixtures


class MockManager:
    """Minimal stand-in for SceneManager."""

    def __init__(self):
        self.current_scene: str | None = None

    def switch_to(self, key: str) -> None:
        self.current_scene = key


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def manager():
    return MockManager()


@pytest.fixture
def fonts():
    font = pygame.font.SysFont(None, 16)
    return {k: font for k in ("title", "small", "smaller", "tiny", "menu")}


@pytest.fixture
def scene(manager, fonts):
    return SnakeScene(manager, fonts)


# ------------------------------------------------------------------ spawn_apple


class TestSpawnApple:
    def test_spawn_apple_returns_tuple(self, scene):
        apple = scene._spawn_apple()
        assert apple is not None
        assert isinstance(apple, tuple)

    def test_spawn_apple_returns_none_when_full(self, scene):
        """When the snake fills the entire grid, _spawn_apple returns None."""
        scene.snake = [(c, r) for r in range(SNAKE_ROWS) for c in range(SNAKE_COLS)]
        assert scene._spawn_apple() is None
