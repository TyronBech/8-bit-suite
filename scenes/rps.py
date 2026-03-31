import pygame
import random
import os
from typing import Any
from core.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_GREEN,
    COLOR_TITLE_YELLOW,
    COLOR_FOOTER,
    COLOR_LINE,
    COLOR_TERMINAL,
    COLOR_ONLINE,
    PLAYER_CARD_X,
    CPU_CARD_X,
    CARD_W,
    CARD_H,
    CARD_Y,
    COLOR_PLAYER_BORDER,
    COLOR_CPU_BORDER,
    COLOR_CARD_BG,
    COLOR_CARD_TEXT,
    COLOR_RED_ORANGE,
    RESULT_COLORS,
    RESULT_LABELS,
)

CHOICES = ["ROCK", "PAPER", "SCISSORS"]


def load_rps_images() -> dict[str, pygame.Surface]:
    """Load and return the images used in the RPS scene."""

    names = ["rock", "paper", "scissors"]
    images = {}
    for name in names:
        path = os.path.join("assets", "images", f"{name}.png")
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (140, 140))
        images[name] = img
    return images


def get_winner(player: str, cpu: str) -> str:
    """Determine the winner of the round."""

    if player == cpu:
        return "draw"
    wins = {("ROCK", "SCISSORS"), ("SCISSORS", "PAPER"), ("PAPER", "ROCK")}
    return "win" if (player, cpu) in wins else "lose"


class RPSScene(BaseScene):
    def __init__(self, manager: Any, fonts: dict[str, pygame.font.Font]) -> None:
        super().__init__(manager)
        self.fonts = fonts
        self.images = load_rps_images()
        self._reset_game()

    def on_exit(self) -> None:
        """Clear the current match so reopening starts fresh."""

        self._reset_game()

    def _reset_game(self) -> None:
        """Reset the full game state, including scores."""

        self.player_score = 0
        self.cpu_score = 0
        self._reset_round()

    def _reset_round(self) -> None:
        """Reset the round state to start a new game."""

        self.player_index = 0
        self.player_choice = None
        self.cpu_choice = None
        self.result = None
        self.phase = "choosing"
        self.reveal_timer = 0.0
        self.abort_rect = pygame.Rect(28, SCREEN_HEIGHT - 52, 120, 30)
        self.reset_btn_rect = None

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.phase == "choosing":
                    if event.key == pygame.K_LEFT:
                        self.player_index = (self.player_index - 1) % len(CHOICES)
                    elif event.key == pygame.K_RIGHT:
                        self.player_index = (self.player_index + 1) % len(CHOICES)
                    elif event.key == pygame.K_RETURN:
                        self.player_choice = CHOICES[self.player_index]
                        self.cpu_choice = random.choice(CHOICES)
                        self.result = get_winner(self.player_choice, self.cpu_choice)
                        if self.result == "win":
                            self.player_score += 1
                        elif self.result == "lose":
                            self.cpu_score += 1
                        self.phase = "revealing"
                        self.reveal_timer = 0.0
                    elif event.key == pygame.K_ESCAPE:
                        self.manager.switch_to("menu")
                elif self.phase == "result":
                    if event.key == pygame.K_RETURN:
                        self._reset_round()
                    elif event.key == pygame.K_ESCAPE:
                        self.manager.switch_to("menu")
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.abort_rect.collidepoint(event.pos):
                    self.manager.switch_to("menu")
                if self.reset_btn_rect and self.reset_btn_rect.collidepoint(event.pos):
                    self._reset_round()

    def update(self, dt: float) -> None:
        if self.phase == "revealing":
            self.reveal_timer += dt
            if self.reveal_timer >= 1.5:
                self.phase = "result"

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BG)
        self._draw_border(screen)
        self._draw_header(screen)
        self._draw_cards(screen)
        self._draw_footer(screen)
        if self.phase == "result":
            self._draw_result_overlay(screen)

    def _draw_border(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            COLOR_BORDER,
            pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30),
            4,
        )

    def _draw_header(self, screen):
        # Terminal prompt style header
        prompt = self.fonts["tiny"].render(
            "> root@8bit-suite:~$ ./rps.sh", False, COLOR_TERMINAL
        )
        screen.blit(prompt, (28, 32))

        # ONLINE
        online = self.fonts["tiny"].render("ONLINE", False, COLOR_ONLINE)
        screen.blit(online, (SCREEN_WIDTH - online.get_width() - 30, 32))

        # Separator line
        pygame.draw.line(screen, COLOR_LINE, (25, 55), (SCREEN_WIDTH - 28, 55), 2)

        # Title
        title = self.fonts["small"].render(
            "BATTLE IN PROGRESS", False, COLOR_TITLE_YELLOW
        )
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 80))

    def _draw_cards(self, screen):
        for label_text, card_x in [("PLAYER 1", PLAYER_CARD_X), ("CPU", CPU_CARD_X)]:
            lbl = self.fonts["smaller"].render(label_text, False, (180, 180, 180))
            screen.blit(lbl, (card_x + (CARD_W - lbl.get_width()) // 2, CARD_Y - 30))

        if self.phase == "choosing":
            player_text = CHOICES[self.player_index]
            cpu_text = "?"
            self._draw_single_card(
                screen, player_text, PLAYER_CARD_X, COLOR_PLAYER_BORDER
            )
            self._draw_single_card(
                screen, cpu_text, CPU_CARD_X, COLOR_CPU_BORDER, show_image=False
            )

        elif self.phase == "revealing":
            # Both shown, no overlay yet
            self._draw_single_card(
                screen, self.player_choice, PLAYER_CARD_X, COLOR_PLAYER_BORDER
            )
            self._draw_single_card(
                screen, self.cpu_choice, CPU_CARD_X, COLOR_CPU_BORDER
            )

        elif self.phase == "result":
            self._draw_single_card(
                screen, self.player_choice, PLAYER_CARD_X, COLOR_PLAYER_BORDER
            )
            self._draw_single_card(
                screen, self.cpu_choice, CPU_CARD_X, COLOR_CPU_BORDER
            )

        # VS in the middle
        vs = self.fonts["small"].render("VS", False, (200, 60, 60))
        screen.blit(
            vs,
            (
                (SCREEN_WIDTH - vs.get_width()) // 2,
                CARD_Y + (CARD_H - vs.get_height()) // 2,
            ),
        )

    def _draw_single_card(self, screen, text, x, border_color, show_image=True):
        rect = pygame.Rect(x, CARD_Y, CARD_W, CARD_H)
        pygame.draw.rect(screen, COLOR_CARD_BG, rect)
        pygame.draw.rect(screen, border_color, rect, 3)

        if show_image and text.lower() in self.images:
            # Draw the pixel art image centered in the card
            img = self.images[text.lower()]
            img_x = x + (CARD_W - img.get_width()) // 2
            img_y = CARD_Y + (CARD_H - img.get_height()) // 2
            screen.blit(img, (img_x, img_y))
        else:
            # Fallback: draw "?" for hidden CPU card
            label = self.fonts["small"].render(text, False, COLOR_CARD_TEXT)
            screen.blit(
                label,
                (
                    x + (CARD_W - label.get_width()) // 2,
                    CARD_Y + (CARD_H - label.get_height()) // 2,
                ),
            )

    def _draw_footer(self, screen):
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
            f"SCORE:  P1 {self.player_score}  -  CPU {self.cpu_score}",
            False,
            COLOR_FOOTER,
        )
        screen.blit(abort, (28, footer_y))
        screen.blit(score, (SCREEN_WIDTH - score.get_width() - 28, footer_y))

    def _draw_result_overlay(self, screen):
        # Dark box
        overlay = pygame.Surface((500, 200), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        ox = (SCREEN_WIDTH - 500) // 2
        oy = (SCREEN_HEIGHT - 200) // 2
        screen.blit(overlay, (ox, oy))

        # Result text
        if self.result is None:
            return
        color = RESULT_COLORS[self.result]
        label = RESULT_LABELS[self.result]
        result_surf = self.fonts["small"].render(label, False, color)
        screen.blit(
            result_surf, ((SCREEN_WIDTH - result_surf.get_width()) // 2, oy + 30)
        )

        # Play Again button
        self.reset_btn_rect = pygame.Rect(ox + 60, oy + 110, 380, 50)
        mx, my = pygame.mouse.get_pos()

        pygame.draw.rect(screen, COLOR_TERMINAL if self.reset_btn_rect.collidepoint(mx, my) else COLOR_TITLE_YELLOW, self.reset_btn_rect, 3)
        btn_text = self.fonts["smaller"].render(
            "PRESS ENTER TO PLAY AGAIN", False, COLOR_TERMINAL if self.reset_btn_rect.collidepoint(mx, my) else COLOR_TITLE_YELLOW
        )
        screen.blit(btn_text, ((SCREEN_WIDTH - btn_text.get_width()) // 2, oy + 125))
