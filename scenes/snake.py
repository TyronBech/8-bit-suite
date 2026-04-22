import pygame
import random
from typing import Any

from core.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_LINE,
    COLOR_TERMINAL,
    COLOR_ONLINE,
    COLOR_FOOTER,
    COLOR_GREEN,
    COLOR_RED_ORANGE,
    COLOR_TITLE_YELLOW,
    SNAKE_COLS,
    SNAKE_ROWS,
    SNAKE_CELL,
    SNAKE_BOARD_X,
    SNAKE_BOARD_Y,
    SNAKE_BOARD_W,
    SNAKE_BOARD_H,
    SNAKE_BASE_SPEED,
    SNAKE_SPEED_STEP,
    COLOR_SNAKE_HEAD,
    COLOR_SNAKE_BODY,
    COLOR_APPLE,
    COLOR_BOARD_BG,
    COLOR_BOARD_BORDER,
    COLOR_SPRING_GREEN,
)


class SnakeScene(BaseScene):
    """Snake and Apple game scene."""

    def __init__(self, manager: Any, fonts: dict[str, pygame.font.Font]) -> None:
        super().__init__(manager)
        self.fonts = fonts
        self._reset_game()

    def on_exit(self) -> None:
        self._reset_game()

    def _reset_game(self) -> None:
        """Resets scores and board."""
        self.hi_score = 0
        self._reset_round()

    def _reset_round(self) -> None:
        """Start a fresh snake with new apple."""
        mid_c = SNAKE_COLS // 2
        mid_r = SNAKE_ROWS // 2

        self.snake = [(mid_c, mid_r), (mid_c - 1, mid_r), (mid_c - 2, mid_r)]
        self.direction = (1, 0)  # (dx, dy)
        self.next_dir = (1, 0)  # buffer the next direction to prevent reversing
        self.score = 0
        self.phase = "playing"  # "playing" or "dead"
        self.move_timer = 0.0
        self.apple = self._spawn_apple()
        self.abort_rect = pygame.Rect(28, SCREEN_HEIGHT - 52, 120, 30)
        self.reset_btn_rect: pygame.Rect | None = None

    def _spawn_apple(self) -> tuple[int, int] | None:
        """Return a random (col, row) for the apple that is not on the snake, or None if full."""
        occupied = set(self.snake)
        empty = [
            (c, r)
            for c in range(SNAKE_COLS)
            for r in range(SNAKE_ROWS)
            if (c, r) not in occupied
        ]
        if not empty:
            return None
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
                    if nd[0] != -dx or nd[1] != -dy:
                        self.next_dir = nd
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.abort_rect.collidepoint(event.pos):
                    self.manager.switch_to("menu")
                elif self.reset_btn_rect and self.reset_btn_rect.collidepoint(
                    event.pos
                ):
                    self._reset_round()

    def update(self, dt: float) -> None:
        if self.phase != "playing":
            return

        speed = SNAKE_BASE_SPEED + (self.score // 10) * SNAKE_SPEED_STEP
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

        growing = new_head == self.apple

        # Self collision
        collision_body = self.snake if growing else self.snake[:-1]
        if new_head in collision_body:
            self._die()
            return

        self.snake.insert(0, new_head)

        if growing:
            self.score += 1
            self.hi_score = max(self.hi_score, self.score)
            self.apple = self._spawn_apple()
            if self.apple is None:
                # Snake fills the entire grid — player wins
                self._die()
                return
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
            "> root@8bit-suite:~$ ./snake.sh", False, COLOR_TERMINAL
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
            SNAKE_BOARD_X, SNAKE_BOARD_Y, SNAKE_BOARD_W, SNAKE_BOARD_H
        )
        pygame.draw.rect(screen, COLOR_BOARD_BG, board_rect)
        pygame.draw.rect(screen, COLOR_BOARD_BORDER, board_rect, 2)
        # Apple
        if self.apple is not None:
            self._draw_cell(screen, self.apple, COLOR_APPLE)
        # Snake body (reversed so head draws last / on top)
        body = self.snake[1:]
        n_body = len(body)
        for i, seg in enumerate(reversed(body)):
            # lowest opacity at tail (i=0), highest at neck
            fraction = 0.4 + 0.6 * (i / max(1, n_body - 1)) if n_body > 1 else 1.0
            alpha = int(255 * fraction)
            color = (*COLOR_SNAKE_BODY[:3], alpha)
            self._draw_cell(screen, seg, color)
        self._draw_cell(screen, self.snake[0], COLOR_SNAKE_HEAD)

    def _draw_footer(self, screen: pygame.Surface) -> None:
        pygame.draw.line(
            screen,
            COLOR_LINE,
            (25, SCREEN_HEIGHT - 65),
            (SCREEN_WIDTH - 28, SCREEN_HEIGHT - 65),
            2,
        )

        footer_y = SCREEN_HEIGHT - 48

        mx, my = pygame.mouse.get_pos()
        abort_color = (
            COLOR_GREEN if self.abort_rect.collidepoint(mx, my) else COLOR_FOOTER
        )

        abort = self.fonts["smaller"].render("< ABORT", False, abort_color)
        score = self.fonts["smaller"].render(
            f"SCORE:  {self.score} | {self.hi_score}",
            False,
            COLOR_FOOTER,
        )

        screen.blit(abort, (28, footer_y))
        screen.blit(score, (SCREEN_WIDTH - score.get_width() - 36, footer_y))

    def _draw_cell(self, screen, cell, color) -> None:
        c, r = cell
        x = SNAKE_BOARD_X + c * SNAKE_CELL + 1
        y = SNAKE_BOARD_Y + r * SNAKE_CELL + 1
        rect = pygame.Rect(x, y, SNAKE_CELL - 2, SNAKE_CELL - 2)
        if len(color) == 4:
            s = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(s, color, s.get_rect(), border_radius=3)
            screen.blit(s, rect.topleft)
        else:
            pygame.draw.rect(screen, color, rect, border_radius=3)

    def _draw_game_over(self, screen) -> None:
        overlay = pygame.Surface((500, 220), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        ox = (SCREEN_WIDTH - overlay.get_width()) // 2
        oy = (SCREEN_HEIGHT - overlay.get_height()) // 2
        screen.blit(overlay, (ox, oy))

        # Yellow border (like the screenshot)
        pygame.draw.rect(screen, COLOR_TITLE_YELLOW, pygame.Rect(ox, oy, 500, 220), 3)

        go = self.fonts["small"].render("GAME OVER", False, COLOR_RED_ORANGE)
        screen.blit(go, (ox + (500 - go.get_width()) // 2, oy + 30))
        fs = self.fonts["smaller"].render(
            f"FINAL SCORE: {self.score}", False, COLOR_SPRING_GREEN
        )

        screen.blit(fs, (ox + (500 - fs.get_width()) // 2, oy + 90))
        self.reset_btn_rect = pygame.Rect(ox + 45, oy + 143, 380 + 30, 44)
        mx, my = pygame.mouse.get_pos()
        hover = self.reset_btn_rect.collidepoint(mx, my)
        btn_color = COLOR_RED_ORANGE if hover else COLOR_TITLE_YELLOW
        pygame.draw.rect(screen, btn_color, self.reset_btn_rect, 2)
        btn_text = self.fonts["smaller"].render("PRESS TO PLAY AGAIN", False, btn_color)
        screen.blit(btn_text, (ox + (500 - btn_text.get_width()) // 2, oy + 158))
