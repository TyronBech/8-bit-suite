import pygame
import random
from typing import Any

from pygame.event import EventType
from core.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_BORDER, COLOR_LINE,
    COLOR_TERMINAL, COLOR_ONLINE, COLOR_FOOTER,
    COLOR_GREEN, COLOR_RED_ORANGE, COLOR_TITLE_YELLOW,
    SNAKE_COLS, SNAKE_ROWS, SNAKE_CELL,
    SNAKE_BOARD_X, SNAKE_BOARD_Y,
    SNAKE_BOARD_W, SNAKE_BOARD_H,
    SNAKE_BASE_SPEED, SNAKE_SPEED_STEP,
    COLOR_SNAKE_HEAD, COLOR_SNAKE_BODY,
    COLOR_APPLE, COLOR_BOARD_BG, COLOR_BOARD_BORDER,
)

class SnakeScene(BaseScene):
    """ Snake and Apple game scene. """

    def __init__(self, manager: Any, fonts: dict[str, pygame.font.Font]) -> None:
        super().__init__(manager)
        self.fonts = fonts
        self._reset_game()

    def on_exit(self) -> None:
        self._reset_game()

    def _reset_game(self) -> None:
        """ Resets scores and board. """
        self.hi_score = 0
        self._reset_round()

    def _reset_round(self) -> None:
        """ Start a fresh snake with new apple. """
        mid_c = SNAKE_COLS // 2
        mid_r = SNAKE_ROWS // 2

        self.snake = [(mid_c, mid_r), (mid_c-1, mid_r), (mid_c-2, mid_r)]
        self.direction = (1, 0)  # (dx, dy)
        self.next_dir = (1, 0) # buffer the next direction to prevent reversing
        self.score = 0
        self.phase = "playing" # "playing" or "dead"
        self.move_timer = 0.0
        self.apple = self._spawn_apple()
        self.abort_rect = pygame.Rect(28, SCREEN_HEIGHT - 52, 120, 30)

    def _spawn_apple(self) -> tuple[int, int]:
        """ Return a random (col, row) for the apple that is not on the snake. """
        occupied = set(self.snake)
        empty = [(c, r)
                 for c in range(SNAKE_COLS)
                 for r in range(SNAKE_ROWS)
                 if (c, r) not in occupied]
        return random.choice(empty)

    def handle_events(self, events) -> None:
        DIR_MAP = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0),
        }

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.switch_to("menu")
                elif self.phase == "dead":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self._reset_round()
                elif event.key in DIR_MAP:
                    nd = DIR_MAP[event.key]
                    # Prevent reversing direction
                    dx, dy = self.direction
                    if (nd[0] != -dx or nd[1] != -dy):
                        self.next_dir = nd
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.abort_rect.collidepoint(event.pos):
                    self.manager.switch_to("menu")

    def update(self, dt: float) -> None:
        if self.phase != "playing":
            return

        speed = (SNAKE_BASE_SPEED + (self.score // 10) * SNAKE_SPEED_STEP)
        self.move_timer += dt

        if self.move_timer < 1.0 / speed:
            return
        self.move_timer = 0.0

        # Apply buffered direction
        self.direction = self.next_dir
        dx, dy = self.direction
        hx, hy = self.snake[0]
        new_head = (hx + dx, hy + dy)

        # Wall collision
        nx, ny = new_head
        if not (0 <= nx < SNAKE_COLS and 0 <= ny < SNAKE_ROWS):
            self._die()
            return

        # Self Collision
        if new_head in self.snake:
            self._die()
            return

        self.snake.insert(0, new_head)

        if new_head == self.apple:
            self.score += 1
            self.hi_score = max(self.hi_score, self.score)
            self.apple = self._spawn_apple()
        else:
            self.snake.pop()  # remove tail

    def _die(self) -> None:
        self.hi_score = max(self.hi_score, self.score)
        self.phase = "dead"

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BG)
        self._draw_border(screen)
        self._draw_header(screen)
        self._draw_board(screen)
        self._draw_footer(screen)
        if self.phase == "dead":
            self._draw_game_over(screen)

    def _draw_border(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            COLOR_BORDER,
            pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30),
            4,
        )

    def _draw_header(self, screen: pygame.Surface) -> None:
        prompt = self.fonts["tiny"].render(
            "> root@8bit-suite:~$ ./tictactoe.sh", False, COLOR_TERMINAL
        )
        screen.blit(prompt, (28, 32))

        online = self.fonts["tiny"].render("ONLINE", False, COLOR_ONLINE)
        screen.blit(online, (SCREEN_WIDTH - online.get_width() - 30, 32))

        pygame.draw.line(screen, COLOR_LINE, (25, 55), (SCREEN_WIDTH - 28, 55), 2)

        title = self.fonts["small"].render("SNAKE", False, COLOR_TITLE_YELLOW)
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 80))

    def _draw_board(self, screen) -> None:
        # Board background + border
        board_rect = pygame.Rect(
            SNAKE_BOARD_X, SNAKE_BOARD_Y,
            SNAKE_BOARD_W, SNAKE_BOARD_H)
        pygame.draw.rect(screen, COLOR_BOARD_BG, board_rect)
        pygame.draw.rect(screen, COLOR_BOARD_BORDER,
                        board_rect, 2)
        # Apple
        self._draw_cell(screen, self.apple, COLOR_APPLE)
        # Snake body (reversed so head draws last / on top)
        for seg in reversed(self.snake[1:]):
            self._draw_cell(screen, seg, COLOR_SNAKE_BODY)
        self._draw_cell(screen, self.snake[0],
                        COLOR_SNAKE_HEAD)

    def _draw_footer(self, screen: pygame.Surface) -> None:
        score_text = self.fonts["tiny"].render(
            f"SCORE: {self.score}   HI-SCORE: {self.hi_score}",
            False, COLOR_FOOTER)
        screen.blit(score_text, (28, SCREEN_HEIGHT - 52))

    def _draw_cell(self, screen, cell, color) -> None:
        c, r = cell
        x = SNAKE_BOARD_X + c * SNAKE_CELL + 1
        y = SNAKE_BOARD_Y + r * SNAKE_CELL + 1
        pygame.draw.rect(screen, color,
            pygame.Rect(x, y,
                        SNAKE_CELL - 2,
                        SNAKE_CELL - 2))

    def _draw_game_over(self, screen) -> None:
        overlay = pygame.Surface((500, 220),
                                pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        ox = (SCREEN_WIDTH - 500) // 2
        oy = (SCREEN_HEIGHT - 220) // 2
        screen.blit(overlay, (ox, oy))

        # Red border (like the screenshot)
        pygame.draw.rect(screen, COLOR_RED_ORANGE,
            pygame.Rect(ox, oy, 500, 220), 3)

        go = self.fonts["small"].render(
            "GAME OVER", False, COLOR_RED_ORANGE)
        screen.blit(go, (ox + (500 - go.get_width()) // 2,
                        oy + 30))
        fs = self.fonts["smaller"].render(
            f"FINAL SCORE: {self.score}",
            False, COLOR_FOOTER)
        screen.blit(fs, (ox + (500 - fs.get_width()) // 2,
                        oy + 90))
        btn = self.fonts["smaller"].render(
            "PLAY AGAIN", False, COLOR_TITLE_YELLOW)
        pygame.draw.rect(screen, COLOR_TITLE_YELLOW,
            pygame.Rect(ox + 100, oy + 145, 300, 44), 2)
        screen.blit(btn, (ox + (500 - btn.get_width()) // 2,
                            oy + 158))
