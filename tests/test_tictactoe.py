"""
tests/test_tictactoe.py

Tests for Tic-Tac-Toe game logic.
Rules:
  - No pygame.display initialization (headless-safe).
  - pygame.init() is called once via a session fixture.
  - Board encoding: 0 = empty, 1 = X (player), -1 = O (CPU).
"""

import pytest
import numpy as np
import pygame

from scenes.tictactoe import (
    WINNING_LINES,
    check_winner,
    minimax,
    get_cpu_move,
    #TicTacToeScene,
)

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
def scene(manager, fonts, monkeypatch):
    monkeypatch.setattr(
        "scenes.tictactoe.load_ttt_images",
        lambda: {
            1: pygame.Surface((136, 136), pygame.SRCALPHA),
            -1: pygame.Surface((136, 136), pygame.SRCALPHA),
        },
    )
    return TicTacToeScene(manager, fonts)


def board(*values) -> np.ndarray:
    """Helper — build a board from 9 positional int args."""
    return np.array(values, dtype=np.int8)


# ------------------------------------------------------------------ check_winner


class TestCheckWinner:
    def test_x_wins_top_row(self):
        b = board(1, 1, 1, 0, 0, 0, 0, 0, 0)
        assert check_winner(b) == "X"

    def test_o_wins_middle_row(self):
        b = board(0, 0, 0, -1, -1, -1, 0, 0, 0)
        assert check_winner(b) == "O"

    def test_x_wins_left_column(self):
        b = board(1, 0, 0, 1, 0, 0, 1, 0, 0)
        assert check_winner(b) == "X"

    def test_o_wins_diagonal(self):
        b = board(-1, 0, 0, 0, -1, 0, 0, 0, -1)
        assert check_winner(b) == "O"

    def test_x_wins_anti_diagonal(self):
        b = board(0, 0, 1, 0, 1, 0, 1, 0, 0)
        assert check_winner(b) == "X"

    def test_draw(self):
        b = board(1, -1, 1, 1, -1, -1, -1, 1, 1)
        assert check_winner(b) == "draw"

    def test_in_progress_returns_none(self):
        b = board(1, 0, 0, 0, -1, 0, 0, 0, 0)
        assert check_winner(b) is None

    def test_empty_board_returns_none(self):
        assert check_winner(np.zeros(9, dtype=np.int8)) is None

    def test_win_takes_priority_over_full_board(self):
        # Full board but X has a winning line — must return "X" not "draw"
        b = board(1, 1, 1, -1, -1, 1, 1, -1, -1)
        assert check_winner(b) == "X"


# ------------------------------------------------------------------ get_cpu_move


class TestGetCpuMove:
    def test_returns_valid_index(self):
        b = np.zeros(9, dtype=np.int8)
        move = get_cpu_move(b)
        assert 0 <= move <= 8

    def test_never_picks_occupied_cell(self):
        # Only index 4 is empty
        b = board(1, -1, 1, -1, 0, -1, 1, -1, 1)
        assert get_cpu_move(b) == 4

    def test_cpu_takes_winning_move(self):
        # O can win at index 2
        b = board(0, 0, 0, 1, 1, 0, -1, -1, 0)
        assert (
            get_cpu_move(b, difficulty=1.0) == 8
        )  # completes O's bottom row (-1,-1,_)
        assert (
            get_cpu_move(b, difficulty=1.0) == 8
        )  # completes O's bottom row (-1,-1,_)

    def test_cpu_blocks_player_win(self):
        # X will win at index 2 unless CPU blocks
        b = board(1, 1, 0, -1, -1, 0, 0, 0, 0)
        assert get_cpu_move(b, difficulty=1.0) == 2
        assert get_cpu_move(b, difficulty=1.0) == 2

    def test_does_not_mutate_board(self):
        b = np.zeros(9, dtype=np.int8)
        original = b.copy()
        get_cpu_move(b)
        np.testing.assert_array_equal(b, original)


# ------------------------------------------------------------------ scene init


class TestSceneInit:
    def test_phase_is_playing(self, scene):
        assert scene.phase == "playing"

    def test_board_is_all_zeros(self, scene):
        assert np.all(scene.board == 0)

    def test_scores_start_at_zero(self, scene):
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_player_goes_first(self, scene):
        assert scene.current_turn == "X"

    def test_winner_is_none(self, scene):
        assert scene.winner is None


# ------------------------------------------------------------------ player move


def make_keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")


class TestPlayerMove:
    def test_click_empty_cell_places_x(self, scene):
        # Click the center of cell 0 (top-left)
        cx, cy = scene._cell_center(0)
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        assert scene.board[0] == 1

    def test_click_occupied_cell_does_nothing(self, scene):
        scene.board[0] = -1  # already occupied
        scene.board[0] = -1  # already occupied
        cx, cy = scene._cell_center(0)
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        assert scene.board[0] == -1  # unchanged
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        assert scene.board[0] == -1  # unchanged

    def test_player_click_switches_turn_to_cpu(self, scene):
        cx, cy = scene._cell_center(4)
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        assert scene.current_turn == "O"


# ------------------------------------------------------------------ CPU move


class TestCpuMove:
    def test_cpu_moves_after_delay(self, scene):
        # Place player's move, then advance time past the CPU delay
        scene.board[0] = 1
        scene.current_turn = "O"
        scene.update(0.7)
        empty_after = np.sum(scene.board == 0)
        assert empty_after == 7  # one more cell filled by CPU
        assert empty_after == 7  # one more cell filled by CPU

    def test_cpu_does_not_move_before_delay(self, scene):
        scene.board[0] = 1
        scene.current_turn = "O"
        scene.update(0.3)
        assert np.sum(scene.board == 0) == 8  # nothing placed yet
        assert np.sum(scene.board == 0) == 8  # nothing placed yet


# ------------------------------------------------------------------ win / draw detection


class TestWinDetection:
    def test_player_win_sets_phase_to_result(self, scene):
        # Set up a board where player's next move wins
        scene.board = board(1, 1, 0, -1, -1, 0, 0, 0, 0)
        cx, cy = scene._cell_center(2)
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        assert scene.phase == "result"
        assert scene.winner == "X"

    def test_player_win_increments_score(self, scene):
        scene.board = board(1, 1, 0, -1, -1, 0, 0, 0, 0)
        cx, cy = scene._cell_center(2)
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        scene.handle_events(
            [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx, cy), button=1)]
        )
        assert scene.player_score == 1
        assert scene.cpu_score == 0

    def test_cpu_win_increments_cpu_score(self, scene):
        # Force CPU to win immediately
        scene.board = board(1, 1, 0, -1, -1, 0, 0, 0, 0)
        scene.current_turn = "O"
        scene._place_move(5, -1)  # O completes middle row
        scene._place_move(5, -1)  # O completes middle row
        assert scene.cpu_score == 1

    def test_draw_sets_winner_to_draw(self, scene):
        # One move away from a draw — no winner possible
        scene.board = board(1, -1, 1, 1, -1, -1, -1, 1, 0)
        scene.current_turn = "X"
        scene._place_move(8, 1)
        assert scene.winner == "draw"


# ------------------------------------------------------------------ reset


class TestResetRound:
    def test_clears_board(self, scene):
        scene.board[3] = 1
        scene._reset_round()
        assert np.all(scene.board == 0)

    def test_restores_playing_phase(self, scene):
        scene.phase = "result"
        scene._reset_round()
        assert scene.phase == "playing"

    def test_preserves_scores(self, scene):
        scene.player_score = 3
        scene.cpu_score = 1
        scene._reset_round()
        assert scene.player_score == 3
        assert scene.cpu_score == 1

    def test_clears_winner(self, scene):
        scene.winner = "X"
        scene._reset_round()
        assert scene.winner is None


class TestResetGame:
    def test_zeroes_scores(self, scene):
        scene.player_score = 4
        scene.cpu_score = 2
        scene._reset_game()
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_also_clears_board(self, scene):
        scene.board[0] = 1
        scene._reset_game()
        assert np.all(scene.board == 0)


# ------------------------------------------------------------------ on_exit


class TestOnExit:
    def test_on_exit_resets_scores(self, scene):
        scene.player_score = 5
        scene.on_exit()
        assert scene.player_score == 0

    def test_on_exit_resets_phase(self, scene):
        scene.phase = "result"
        scene.on_exit()
        assert scene.phase == "playing"


# ------------------------------------------------------------------ keyboard


class TestKeyboard:
    def test_escape_goes_to_menu(self, scene, manager):
        scene.handle_events([make_keydown(pygame.K_ESCAPE)])
        assert manager.current_scene == "menu"

    def test_r_resets_round(self, scene):
        scene.board[0] = 1
        scene.handle_events([make_keydown(pygame.K_r)])
        assert np.all(scene.board == 0)

    def test_enter_resets_in_result_phase(self, scene):
        scene.phase = "result"
        scene.winner = "X"
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "playing"
