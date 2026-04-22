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


def make_keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")


# ------------------------------------------------------------------ spawn_apple


class TestSpawnApple:
    def test_spawn_apple_returns_tuple(self, scene):
        apple = scene._spawn_apple()
        assert apple is not None
        assert isinstance(apple, tuple)

    def test_spawn_apple_returns_none_when_full(self, scene):
        """When the snake fills the entire grid, _spawn_apple returns None."""
        scene.snake = [
            (c, r)
            for r in range(SNAKE_ROWS)
            for c in range(SNAKE_COLS)
        ]
        assert scene._spawn_apple() is None

    def test_spawn_apple_is_inside_board(self, scene):
        apple = scene._spawn_apple()
        assert apple is not None
        ax, ay = apple
        assert 0 <= ax < SNAKE_COLS
        assert 0 <= ay < SNAKE_ROWS

    def test_spawn_apple_not_on_snake(self, scene):
        apple = scene._spawn_apple()
        assert apple is not None
        assert apple not in scene.snake


# ------------------------------------------------------------------ init


class TestSceneInit:
    def test_phase_is_playing(self, scene):
        assert scene.phase == "playing"

    def test_starts_with_three_segments(self, scene):
        assert len(scene.snake) == 3

    def test_starts_moving_right(self, scene):
        assert scene.direction == (1, 0)
        assert scene.next_dir == (1, 0)

    def test_scores_start_at_zero(self, scene):
        assert scene.score == 0
        assert scene.hi_score == 0


# ------------------------------------------------------------------ input


class TestInput:
    def test_escape_goes_to_menu(self, scene, manager):
        scene.handle_events([make_keydown(pygame.K_ESCAPE)])
        assert manager.current_scene == "menu"

    def test_reverse_direction_is_blocked(self, scene):
        scene.handle_events([make_keydown(pygame.K_LEFT)])
        assert scene.next_dir == (1, 0)

    def test_valid_turn_updates_next_direction(self, scene):
        scene.handle_events([make_keydown(pygame.K_UP)])
        assert scene.next_dir == (0, -1)

    def test_dead_enter_resets_round(self, scene):
        scene.phase = "dead"
        scene.score = 4
        scene.snake = [(0, 0)]
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "playing"
        assert scene.score == 0
        assert len(scene.snake) == 3

    def test_mouse_abort_goes_to_menu(self, scene, manager):
        pos = scene.abort_rect.center
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1)]
        )
        assert manager.current_scene == "menu"


# ------------------------------------------------------------------ movement timing


class TestMovement:
    def test_no_move_before_timer_threshold(self, scene):
        old_head = scene.snake[0]
        scene.update(0.001)
        assert scene.snake[0] == old_head

    def test_moves_one_cell_after_enough_time(self, scene):
        old_head = scene.snake[0]
        scene.update(1.0)
        assert scene.snake[0] == (old_head[0] + 1, old_head[1])

    def test_applies_buffered_turn_on_tick(self, scene):
        old_head = scene.snake[0]
        scene.next_dir = (0, -1)
        scene.update(1.0)
        assert scene.direction == (0, -1)
        assert scene.snake[0] == (old_head[0], old_head[1] - 1)


# ------------------------------------------------------------------ collisions


class TestCollisions:
    def test_wall_collision_sets_dead_phase(self, scene):
        row = SNAKE_ROWS // 2
        scene.snake = [
            (SNAKE_COLS - 1, row),
            (SNAKE_COLS - 2, row),
            (SNAKE_COLS - 3, row),
        ]
        scene.direction = (1, 0)
        scene.next_dir = (1, 0)
        scene.apple = (0, 0)
        scene.update(1.0)
        assert scene.phase == "dead"

    def test_self_collision_sets_dead_phase(self, scene):
        scene.snake = [(5, 5), (6, 5), (6, 6), (5, 6)]
        scene.direction = (1, 0)
        scene.next_dir = (1, 0)
        scene.apple = (0, 0)
        scene.update(1.0)
        assert scene.phase == "dead"

    def test_can_move_into_tail_when_not_growing(self, scene):
        scene.snake = [(2, 2), (3, 2), (3, 3), (2, 3)]
        scene.direction = (0, 1)
        scene.next_dir = (0, 1)
        scene.apple = (0, 0)
        scene.update(1.0)
        assert scene.phase == "playing"
        assert scene.snake[0] == (2, 3)


# ------------------------------------------------------------------ apple and score


class TestAppleAndScore:
    def test_eating_apple_grows_and_scores(self, scene, monkeypatch):
        scene.snake = [(4, 4), (3, 4), (2, 4)]
        scene.direction = (1, 0)
        scene.next_dir = (1, 0)
        scene.apple = (5, 4)
        monkeypatch.setattr(scene, "_spawn_apple", lambda: (0, 0))

        prev_len = len(scene.snake)
        scene.update(1.0)

        assert scene.score == 1
        assert scene.hi_score == 1
        assert len(scene.snake) == prev_len + 1
        assert scene.apple == (0, 0)

    def test_full_board_after_eating_ends_round(self, scene, monkeypatch):
        scene.snake = [(4, 4), (3, 4), (2, 4)]
        scene.direction = (1, 0)
        scene.next_dir = (1, 0)
        scene.apple = (5, 4)
        monkeypatch.setattr(scene, "_spawn_apple", lambda: None)

        scene.update(1.0)

        assert scene.score == 1
        assert scene.phase == "dead"

    def test_round_reset_keeps_hi_score(self, scene):
        scene.hi_score = 7
        scene.score = 4
        scene._reset_round()
        assert scene.score == 0
        assert scene.hi_score == 7


# ------------------------------------------------------------------ reset and lifecycle


class TestResetAndLifecycle:
    def test_reset_game_clears_hi_score(self, scene):
        scene.hi_score = 9
        scene.score = 3
        scene._reset_game()
        assert scene.hi_score == 0
        assert scene.score == 0
        assert scene.phase == "playing"

    def test_on_exit_resets_scene(self, scene):
        scene.hi_score = 8
        scene.phase = "dead"
        scene.on_exit()
        assert scene.hi_score == 0
        assert scene.phase == "playing"
