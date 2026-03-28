"""
tests/test_rps.py

Test suite for the Rock-Paper-Scissors game logic.

Rules for these tests:
  - pygame.display is NEVER initialized here (no window = safe for CI).
  - pygame.init() is called once via the module-level fixture so that
    font/surface operations used inside RPSScene.__init__ don't crash.
  - All tests that touch RPSScene use a lightweight MockManager so the
    scene never needs a real SceneManager or screen.
"""

import pytest
import pygame

from scenes.rps import CHOICES, get_winner, RPSScene


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────


class MockManager:
    """Minimal stand-in for SceneManager used by RPSScene."""

    def __init__(self):
        self.current_scene: str | None = None

    def switch_to(self, key: str) -> None:
        self.current_scene = key


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """
    Initialize pygame once for the whole test session.
    No pygame.display window is created here to remain safe for headless CI.
    """
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def manager():
    return MockManager()


@pytest.fixture
def fonts():
    """Tiny real fonts — small enough to be fast, real enough to not crash."""
    font = pygame.font.SysFont(None, 16)
    return {
        "title":   font,
        "small":   font,
        "smaller": font,
        "tiny":    font,
        "menu":    font,
    }


@pytest.fixture
def scene(manager, fonts, monkeypatch):
    """
    RPSScene with image loading patched out so no asset files are needed.
    monkeypatch replaces load_rps_images with a function that returns
    plain 1×1 surfaces — enough for the scene to initialize without error.
    """
    import scenes.rps as rps_module

    dummy_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
    monkeypatch.setattr(
        rps_module,
        "load_rps_images",
        lambda: {name: dummy_surface for name in ["rock", "paper", "scissors"]},
    )
    return RPSScene(manager, fonts)


# ──────────────────────────────────────────────────────────────
# 1. get_winner — pure logic (no pygame needed)
# ──────────────────────────────────────────────────────────────


class TestGetWinner:
    """All nine possible match-ups."""

    # --- wins ---
    def test_rock_beats_scissors(self):
        assert get_winner("ROCK", "SCISSORS") == "win"

    def test_scissors_beats_paper(self):
        assert get_winner("SCISSORS", "PAPER") == "win"

    def test_paper_beats_rock(self):
        assert get_winner("PAPER", "ROCK") == "win"

    # --- losses ---
    def test_scissors_loses_to_rock(self):
        assert get_winner("SCISSORS", "ROCK") == "lose"

    def test_paper_loses_to_scissors(self):
        assert get_winner("PAPER", "SCISSORS") == "lose"

    def test_rock_loses_to_paper(self):
        assert get_winner("ROCK", "PAPER") == "lose"

    # --- draws ---
    def test_rock_draw(self):
        assert get_winner("ROCK", "ROCK") == "draw"

    def test_paper_draw(self):
        assert get_winner("PAPER", "PAPER") == "draw"

    def test_scissors_draw(self):
        assert get_winner("SCISSORS", "SCISSORS") == "draw"

    # --- return values are always one of three strings ---
    @pytest.mark.parametrize("player", CHOICES)
    @pytest.mark.parametrize("cpu", CHOICES)
    def test_always_returns_valid_value(self, player, cpu):
        assert get_winner(player, cpu) in {"win", "lose", "draw"}


# ──────────────────────────────────────────────────────────────
# 2. CHOICES constant
# ──────────────────────────────────────────────────────────────


class TestChoices:
    def test_choices_has_three_items(self):
        assert len(CHOICES) == 3

    def test_choices_are_uppercase(self):
        for choice in CHOICES:
            assert choice == choice.upper()

    def test_choices_contains_expected_values(self):
        assert set(CHOICES) == {"ROCK", "PAPER", "SCISSORS"}


# ──────────────────────────────────────────────────────────────
# 3. RPSScene — initial state
# ──────────────────────────────────────────────────────────────


class TestRPSSceneInit:
    def test_starts_in_choosing_phase(self, scene):
        assert scene.phase == "choosing"

    def test_scores_start_at_zero(self, scene):
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_player_index_starts_at_zero(self, scene):
        assert scene.player_index == 0

    def test_choices_start_as_none(self, scene):
        assert scene.player_choice is None
        assert scene.cpu_choice is None

    def test_result_starts_as_none(self, scene):
        assert scene.result is None

    def test_reveal_timer_starts_at_zero(self, scene):
        assert scene.reveal_timer == 0.0


# ──────────────────────────────────────────────────────────────
# 4. Choice cycling with arrow keys
# ──────────────────────────────────────────────────────────────


def make_keydown(key: int) -> pygame.event.Event:
    """Helper — create a KEYDOWN event for the given key constant."""
    return pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")


class TestChoiceCycling:
    def test_right_arrow_advances_index(self, scene):
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.player_index == 1

    def test_left_arrow_decrements_index(self, scene):
        scene.player_index = 1
        scene.handle_events([make_keydown(pygame.K_LEFT)])
        assert scene.player_index == 0

    def test_right_wraps_from_last_to_first(self, scene):
        scene.player_index = len(CHOICES) - 1   # SCISSORS
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.player_index == 0           # wraps to ROCK

    def test_left_wraps_from_first_to_last(self, scene):
        scene.player_index = 0                   # ROCK
        scene.handle_events([make_keydown(pygame.K_LEFT)])
        assert scene.player_index == len(CHOICES) - 1  # wraps to SCISSORS

    def test_cycling_does_not_change_phase(self, scene):
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.phase == "choosing"


# ──────────────────────────────────────────────────────────────
# 5. Confirming a choice (ENTER)
# ──────────────────────────────────────────────────────────────


class TestConfirmChoice:
    def test_enter_sets_player_choice(self, scene):
        scene.player_index = 0   # ROCK
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_choice == "ROCK"

    def test_enter_sets_cpu_choice(self, scene):
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.cpu_choice in CHOICES

    def test_enter_sets_result(self, scene):
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.result in {"win", "lose", "draw"}

    def test_enter_transitions_to_revealing(self, scene):
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "revealing"

    def test_enter_resets_reveal_timer(self, scene):
        scene.reveal_timer = 99.0
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.reveal_timer == 0.0


# ──────────────────────────────────────────────────────────────
# 6. Score tracking
# ──────────────────────────────────────────────────────────────


class TestScoreTracking:
    def test_win_increments_player_score(self, scene, monkeypatch):
        monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "win")
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_score == 1
        assert scene.cpu_score == 0

    def test_lose_increments_cpu_score(self, scene, monkeypatch):
        monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "lose")
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.cpu_score == 1
        assert scene.player_score == 0

    def test_draw_does_not_change_scores(self, scene, monkeypatch):
        monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "draw")
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_score_accumulates_across_rounds(self, scene, monkeypatch):
        monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "win")
        # Round 1
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        scene.phase = "result"
        scene.handle_events([make_keydown(pygame.K_RETURN)])   # reset round
        # Round 2
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_score == 2


# ──────────────────────────────────────────────────────────────
# 7. Reveal timer → phase transition
# ──────────────────────────────────────────────────────────────


class TestRevealTimer:
    def test_revealing_advances_timer(self, scene):
        scene.phase = "revealing"
        scene.update(0.5)
        assert scene.reveal_timer == pytest.approx(0.5)

    def test_revealing_transitions_to_result_after_1_5s(self, scene):
        scene.phase = "revealing"
        scene.update(1.5)
        assert scene.phase == "result"

    def test_timer_does_not_advance_in_choosing_phase(self, scene):
        scene.phase = "choosing"
        scene.update(1.0)
        assert scene.reveal_timer == 0.0

    def test_timer_does_not_advance_in_result_phase(self, scene):
        scene.phase = "result"
        scene.result = "win"
        scene.reveal_timer = 0.0
        scene.update(1.0)
        assert scene.reveal_timer == 0.0


# ──────────────────────────────────────────────────────────────
# 8. Input is blocked during revealing phase
# ──────────────────────────────────────────────────────────────


class TestRevealingPhaseBlocksInput:
    def test_right_arrow_ignored_during_revealing(self, scene):
        scene.phase = "revealing"
        scene.player_index = 0
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.player_index == 0   # unchanged

    def test_enter_ignored_during_revealing(self, scene):
        scene.phase = "revealing"
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "revealing"   # still revealing


# ──────────────────────────────────────────────────────────────
# 9. Result phase — play again and exit
# ──────────────────────────────────────────────────────────────


class TestResultPhase:
    def _put_in_result(self, scene):
        """Helper — fast-forward scene to result phase."""
        scene.phase = "result"
        scene.player_choice = "ROCK"
        scene.cpu_choice = "SCISSORS"
        scene.result = "win"
        scene.player_score = 1

    def test_enter_resets_round_in_result(self, scene):
        self._put_in_result(scene)
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "choosing"
        assert scene.player_choice is None
        assert scene.cpu_choice is None
        assert scene.result is None

    def test_enter_preserves_scores_on_reset(self, scene):
        self._put_in_result(scene)
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_score == 1   # score kept

    def test_escape_switches_to_menu_from_result(self, scene, manager):
        self._put_in_result(scene)
        scene.handle_events([make_keydown(pygame.K_ESCAPE)])
        assert manager.current_scene == "menu"


# ──────────────────────────────────────────────────────────────
# 10. Escape key during choosing phase
# ──────────────────────────────────────────────────────────────


class TestEscapeKey:
    def test_escape_switches_to_menu_from_choosing(self, scene, manager):
        scene.handle_events([make_keydown(pygame.K_ESCAPE)])
        assert manager.current_scene == "menu"


# ──────────────────────────────────────────────────────────────
# 11. _reset_round keeps scores, clears round state
# ──────────────────────────────────────────────────────────────


class TestResetRound:
    def test_reset_round_clears_choices(self, scene):
        scene.player_choice = "ROCK"
        scene.cpu_choice = "SCISSORS"
        scene._reset_round()
        assert scene.player_choice is None
        assert scene.cpu_choice is None

    def test_reset_round_clears_result(self, scene):
        scene.result = "win"
        scene._reset_round()
        assert scene.result is None

    def test_reset_round_restores_choosing_phase(self, scene):
        scene.phase = "result"
        scene._reset_round()
        assert scene.phase == "choosing"

    def test_reset_round_preserves_scores(self, scene):
        scene.player_score = 3
        scene.cpu_score = 2
        scene._reset_round()
        assert scene.player_score == 3
        assert scene.cpu_score == 2


# ──────────────────────────────────────────────────────────────
# 12. _reset_game wipes scores
# ──────────────────────────────────────────────────────────────


class TestResetGame:
    def test_reset_game_zeroes_scores(self, scene):
        scene.player_score = 5
        scene.cpu_score = 3
        scene._reset_game()
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_reset_game_also_resets_round(self, scene):
        scene.player_choice = "PAPER"
        scene.phase = "result"
        scene._reset_game()
        assert scene.player_choice is None
        assert scene.phase == "choosing"


# ──────────────────────────────────────────────────────────────
# 13. on_exit resets the full game
# ──────────────────────────────────────────────────────────────


class TestOnExit:
    def test_on_exit_resets_scores(self, scene):
        scene.player_score = 4
        scene.cpu_score = 2
        scene.on_exit()
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_on_exit_resets_phase(self, scene):
        scene.phase = "result"
        scene.on_exit()
        assert scene.phase == "choosing"
