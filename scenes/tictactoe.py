import pygame
import numpy as np
from typing import Any
from core.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_BORDER, COLOR_LINE,
    COLOR_TERMINAL, COLOR_ONLINE,
    COLOR_FOOTER, COLOR_TITLE_YELLOW,
    COLOR_GREEN, COLOR_RED_ORANGE,
    RESULT_COLORS, RESULT_LABELS,
    TTT_CELL_SIZE, TTT_BOARD_W, TTT_BOARD_H,
    TTT_BOARD_X, TTT_BOARD_Y,
    COLOR_TTT_LINE, COLOR_TTT_X, COLOR_TTT_O,
)

WINNING_LINES = np.array([
    [0, 1, 2], [3, 4, 5], [6, 7, 8],    # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],    # columns
    [0, 4, 8], [2, 4, 6],               # diagonals
])

def check_winner(board: np.ndarray) -> str | None:
    """
    Check if there's a winner or draw in the board.

    Args:
        board (np.ndarray): flat numpy array of 9 int8 values.
            1 = X (player), -1 = O (CPU), 0 = empty.

    Returns:
        "X"     - player wins
        "O"     - CPU wins
        "draw"  - game is a draw
        None    - game is not over
    """
    for line in WINNING_LINES:
        total = board[line].sum()
        if total == 3:
            return "X"
        elif total == -3:
            return "O"

    if np.all(board != 0):
        return "draw"
    return None

def minimax(board: np.ndarray, is_maximizing: bool) -> int:
    """
    Minimax algorithm - CPU always plays optimally

    CPU is 0 (1) = maximizer (wants to highest score)
    Player is X (-1) = minimizer (wants to lowest score)

    Returns:
        1   - CPU wins from this position
       -1   - Player wins from this position
        0   - draw from this position
    """

    winner = check_winner(board)
    if winner == "O":
        return 1
    elif winner == "X":
        return -1
    elif winner == "draw":
        return 0

    empty_cells = np.where(board == 0)[0]
    scores = []

    for i in empty_cells:
        board[i] = -1 if is_maximizing else 1
        scores.append(minimax(board, not is_maximizing))
        board[i] = 0

    return max(scores) if is_maximizing else min(scores)

def get_cpu_move(board: np.ndarray, difficulty: float = 0.6) -> int:
    """
    Return the index of a move for the CPU.
    Uses minimax, but occasionally makes a random move to allow the player to win.

    Args:
        board (np.ndarray): flat numpy array of 9 int8 values.
        difficulty (float): 0.0 to 1.0.
                            1.0 = unbeatable (100% Minimax).
                            0.6 = 60% chance for perfect play, 40% chance for a random move.

    Returns:
        Index 0-8 of the empty cell for the CPU to play.
    """
    empty_cells = np.where(board == 0)[0]

    # --- THE NERF ---
    # Generate a random number between 0.0 and 1.0.
    # If it's greater than our difficulty threshold, the CPU makes a random move.
    if np.random.random() > difficulty:
        return int(np.random.choice(empty_cells))
    # ----------------

    best_score = -2
    best_index = -1

    for i in empty_cells:
        board[i] = -1
        score = minimax(board, False)
        board[i] = 0
        if score > best_score:
            best_score = score
            best_index = i

    return int(best_index)

class TicTacToeScene(BaseScene):
    """Tic Tac Toe game scene. Player is X, CPU is O."""

    def __init__(self, manager: Any, fonts: dict[str, pygame.font.Font]) -> None:
        super().__init__(manager)
        self.fonts = fonts
        self._reset_game()

    def on_exit(self) -> None:
        """ Clear all state when exiting the scene. """
        self._reset_game()

    def _reset_game(self) -> None:
        """ Reset scores and the board. """
        self.player_score = 0
        self.cpu_score = 0
        self._reset_round()

    def _reset_round(self) -> None:
        """ Start new round with an empty board. """
        self.board = np.zeros(9, dtype=np.int8)
        self.current_turn = "X"  # Player starts first
        self.winner: str | None = None
        self.winning_line: list[int] | None = None
        self.phase = "playing"  # "playing" | "result"
        self.cpu_timer = 0.0
        self.abort_rect = pygame.Rect(28, SCREEN_HEIGHT - 52, 120, 30)
        self.reset_btn_rect: pygame.Rect | None = None

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.switch_to("menu")
                elif event.key == pygame.K_r:
                    self._reset_round()
                elif event.key == pygame.K_RETURN and self.phase == "result":
                    self._reset_round()
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.abort_rect.collidepoint(event.pos):
                    self.manager.switch_to("menu")
                    continue

                if self.reset_btn_rect and self.reset_btn_rect.collidepoint(event.pos):
                    self._reset_round()
                    continue

                if self.phase == "playing" and self.current_turn == "X":
                    cell = self._get_cell_from_mouse(*event.pos)
                    if cell is not None and self.board[cell] == 0:
                        self._place_move(cell, 1)

    def update(self, dt: float) -> None:
        """ Advance game state. CPU moves after a short delay. """
        if self.phase != "playing" or self.current_turn != "O":
            return

        self.cpu_timer += dt
        if self.cpu_timer < 0.6:
            return

        cpu_cell = get_cpu_move(self.board)
        self._place_move(cpu_cell, -1)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BG)
        self._draw_border(screen)
        self._draw_header(screen)
        self._draw_board(screen)
        self._draw_footer(screen)
        if self.phase == "result":
            self._draw_result_overlay(screen)

    # --------------------------------------------------------------- helper methods

    def _place_move(self, cell: int, value: int) -> None:
        """
        Place a move on the board, check for a winner, and advance the turn.

        Args:
            cell:  board index 0-8.
            value: 1 for player (X), -1 for CPU (O).
        """

        self.board[cell] = value
        result = check_winner(self.board)

        if result is not None:
            self.winner = result
            self.winning_line = self._find_winning_line()
            if result == "X":
                self.player_score += 1
            elif result == "O":
                self.cpu_score += 1
            self.phase = "result"
        else:
            self.current_turn = "O" if self.current_turn == "X" else "X"
            self.cpu_timer = 0.0

    def _find_winning_line(self) -> list[int] | None:
        """ Return the list of 3 cell indices that form the winning line, or None if no winner. """
        for line in WINNING_LINES:
            total = self.board[line].sum()
            if total == 3 or total == -3:
                return line.tolist()
        return None

    def _get_cell_from_mouse(self, mx: int, my: int) -> int | None:
        """Convert mouse coordinates to a board cell index (0-8), or None if outside."""

        col = (mx - TTT_BOARD_X) // TTT_CELL_SIZE
        row = (my - TTT_BOARD_Y) // TTT_CELL_SIZE
        if 0 <= col < 3 and 0 <= row < 3:
            return int(row * 3 + col)
        return None

    def _cell_center(self, cell: int) -> tuple[int, int]:
        """ Return the pixel coordinates of the center of a given cell index. """
        row, col = divmod(cell, 3)
        cx = TTT_BOARD_X + col * TTT_CELL_SIZE + TTT_CELL_SIZE // 2
        cy = TTT_BOARD_Y + row * TTT_CELL_SIZE + TTT_CELL_SIZE // 2
        return cx, cy

    # --------------------------------------------------------------- drawing methods

    def _draw_border(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen, COLOR_BORDER,
            pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30), 4,
        )

    def _draw_header(self, screen: pygame.Surface) -> None:
        prompt = self.fonts["tiny"].render(
            "> root@8bit-suite:~$ ./tictactoe.sh", False, COLOR_TERMINAL
        )
        screen.blit(prompt, (28, 32))

        online = self.fonts["tiny"].render("ONLINE", False, COLOR_ONLINE)
        screen.blit(online, (SCREEN_WIDTH - online.get_width() - 30, 32))

        pygame.draw.line(screen, COLOR_LINE, (25, 55), (SCREEN_WIDTH - 28, 55), 2)

        turn_text = "YOUR TURN" if self.current_turn == "X" else "CPU'S THINKING..."
        title_color = COLOR_TTT_X if self.current_turn == "X" else COLOR_TTT_O
        if self.phase == "result":
            turn_text = RESULT_LABELS.get(self.winner or "", "RESULT")
            title_color = RESULT_COLORS.get(self.winner or "", COLOR_TITLE_YELLOW)

        title = self.fonts["small"].render(turn_text, False, title_color)
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 80))

    def _draw_board(self, screen: pygame.Surface) -> None:
        # --- grid lines ---
        for i in range(1, 3):
            # vertical
            x = TTT_BOARD_X + i * TTT_CELL_SIZE
            pygame.draw.line(
                screen, COLOR_TTT_LINE,
                (x, TTT_BOARD_Y), (x, TTT_BOARD_Y + TTT_BOARD_H), 3
            )
            # horizontal
            y = TTT_BOARD_Y + i * TTT_CELL_SIZE
            pygame.draw.line(
                screen, COLOR_TTT_LINE,
                (TTT_BOARD_X, y), (TTT_BOARD_X + TTT_BOARD_W, y), 3,
            )

        # --- X and O markers ---
        pad = 40
        radius = TTT_CELL_SIZE // 2 - pad

        for i in range(9):
            if self.board[i] == 0:
                continue
            cx, cy = self._cell_center(i)
            if self.board[i] == 1:
                pygame.draw.line(screen, COLOR_TTT_X,
                                 (cx - radius, cy - radius),
                                 (cx + radius, cy + radius), 6)
                pygame.draw.line(screen, COLOR_TTT_X,
                                 (cx + radius, cy - radius),
                                 (cx - radius, cy + radius), 6)
            else:
                pygame.draw.circle(screen, COLOR_TTT_O, (cx, cy), radius, 6)

        if self.winning_line:
            start = self._cell_center(self.winning_line[0])
            end = self._cell_center(self.winning_line[2])
            pygame.draw.line(screen, COLOR_TITLE_YELLOW, start, end, 8)

    def _draw_footer(self, screen: pygame.Surface) -> None:
        pygame.draw.line(
            screen, COLOR_LINE,
            (25, SCREEN_HEIGHT - 65), (SCREEN_WIDTH - 28, SCREEN_HEIGHT - 65), 2,
        )
        footer_y = SCREEN_HEIGHT - 48

        mx, my = pygame.mouse.get_pos()
        abort_color = COLOR_GREEN if self.abort_rect.collidepoint(mx, my) else COLOR_FOOTER

        abort = self.fonts["smaller"].render("< ABORT", False, abort_color)
        score = self.fonts["smaller"].render(
            f"SCORE:  P1 {self.player_score} - CPU {self.cpu_score}",
            False, COLOR_FOOTER,
        )
        hint = self.fonts["smaller"].render("CLICK TO PLACE  |  R TO RESET", False, COLOR_FOOTER)

        screen.blit(abort, (28, footer_y))
        screen.blit(score, (SCREEN_WIDTH - score.get_width() - 28, footer_y))
        screen.blit(hint, (((SCREEN_WIDTH - hint.get_width()) // 2) - 88, footer_y))

    def _draw_result_overlay(self, screen: pygame.Surface) -> None:
        if self.winner is None:
            return

        overlay = pygame.Surface((500, 200), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        ox = (SCREEN_WIDTH - overlay.get_width()) // 2
        oy = (SCREEN_HEIGHT - overlay.get_height()) // 2
        screen.blit(overlay, (ox, oy))

        color = RESULT_COLORS.get(self.winner, COLOR_TITLE_YELLOW)
        label = RESULT_LABELS.get(self.winner, "RESULT")
        result_surf = self.fonts["small"].render(label, False, color)
        screen.blit(result_surf, ((SCREEN_WIDTH - result_surf.get_width()) // 2, oy + 30))

        self.reset_btn_rect = pygame.Rect(ox + 60, oy + 110, 380, 50)
        mx, my = pygame.mouse.get_pos()
        hover = self.reset_btn_rect.collidepoint(mx, my)
        btn_color = COLOR_RED_ORANGE if hover else COLOR_TITLE_YELLOW

        pygame.draw.rect(screen, btn_color, self.reset_btn_rect, 3)
        btn_text = self.fonts["smaller"].render("PRESS ENTER TO PLAY AGAIN", False, btn_color)
        screen.blit(btn_text, ((SCREEN_WIDTH - btn_text.get_width()) // 2, oy + 125))
