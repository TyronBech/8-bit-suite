import pygame
from core.base_scene import BaseScene
import math
from core.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_TITLE_YELLOW,
    COLOR_GREEN,
    COLOR_TERMINAL,
    COLOR_ONLINE,
    COLOR_FOOTER,
    COLOR_RED_ORANGE,
    COLOR_SELECTED_BG,
    COLOR_SELECTED_TEXT,
    MENU_ITEMS,
    ITEM_COLORS,
    BOOT_LINES,
    COLOR_LINE,
)

BOOT_DURATION = len(BOOT_LINES) * 0.4 + 0.4

# --- Shared menu layout constants ---
MENU_BOX_W = 560
MENU_BOX_H = 60
MENU_BOX_X = (SCREEN_WIDTH - MENU_BOX_W) // 2
MENU_START_Y = 350
MENU_SPACING = 110


class MenuScene(BaseScene):
    def __init__(self, manager, fonts):
        super().__init__(manager)
        self.fonts = fonts
        self.selected = 0
        self.elapsed = 0.0
        self.state = "boot"
        self.loading_label = ""

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(MENU_ITEMS)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(MENU_ITEMS)
                    elif event.key == pygame.K_RETURN:
                        key = MENU_ITEMS[self.selected][1]
                        label = MENU_ITEMS[self.selected][0]
                        self.manager.loading.setup(key, label)
                        self.manager.switch_to("loading")
                    elif event.key == pygame.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

            elif event.type == pygame.MOUSEMOTION and self.state == "menu":
                mx, my = event.pos
                for i in range(len(MENU_ITEMS)):
                    if get_item_rect(i).collidepoint(mx, my):
                        self.selected = i

            elif event.type == pygame.MOUSEBUTTONUP and self.state == "menu":
                mx, my = event.pos
                for i in range(len(MENU_ITEMS)):
                    if get_item_rect(i).collidepoint(mx, my):
                        self.selected = i
                        label = MENU_ITEMS[i][0]
                        key = MENU_ITEMS[i][1]
                        self.manager.loading.setup(key, label)
                        self.manager.switch_to("loading")

    def update(self, dt):
        self.elapsed += dt

        if self.state == "boot" and self.elapsed >= BOOT_DURATION:
            self.state = "menu"
            self.elapsed = 0.0

    def draw(self, screen):
        screen.fill(COLOR_BG)
        if self.state == "boot":
            draw_boot(screen, self.fonts, self.elapsed)
        else:
            draw_border(screen)
            draw_text(screen, self.fonts, self.elapsed)
            draw_menu(screen, self.fonts, self.selected, self.elapsed)

class LoadingScene(BaseScene):
    def __init__ (self, manager, fonts):
        super().__init__(manager)
        self.fonts = fonts
        self.elapsed = 0.0
        self.target = ""
        self.label = ""

    def setup (self, target: str, label: str):
        """ Prepare the loading screen for a specific target scene. """

        self.target = target
        self.label = label
        self.elapsed = 0.0

    def handle_events (self, events):
        pass

    def update (self, dt):
        self.elapsed += dt
        if self.elapsed >= 2.5:
            self.manager.switch_to(self.target)

    def draw (self, screen):
        draw_loading(screen, self.fonts, self.label, self.elapsed)


# ------------------------------------------------------------------ helpers


def draw_centered_text(surface, text, font, color, y):
    """Draw text horizontally centered at y."""
    text_surf = font.render(text, False, color)
    x = (SCREEN_WIDTH - text_surf.get_width()) // 2
    surface.blit(text_surf, (x, y))


# ------------------------------------------------------------------ drawing


def draw_border(surface):
    pygame.draw.rect(
        surface,
        COLOR_BORDER,
        pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30),
        4,
    )


def draw_title(surface, fonts):
    """Big title with orange drop shadow."""
    shadow_color = (180, 80, 0)
    title_text = "8-BIT SUITE"

    shadow_surf = fonts["title"].render(title_text, False, shadow_color)
    title_surf = fonts["title"].render(title_text, False, COLOR_TITLE_YELLOW)

    title_x = (SCREEN_WIDTH - title_surf.get_width()) // 2
    title_y = 110

    surface.blit(shadow_surf, (title_x + 4, title_y + 4))
    surface.blit(title_surf, (title_x, title_y))


def draw_text(surface, fonts, elapsed):
    draw_title(surface, fonts)
    draw_centered_text(surface, "COLLECTION VOL. 1",
                       fonts["small"], COLOR_GREEN, 175)

    # Terminal prompt top-left
    prompt = fonts["tiny"].render(
        "> root@8bit-suite:~$ ./menu.sh", False, COLOR_TERMINAL
    )
    surface.blit(prompt, (28, 32))

    # ONLINE top-right
    online = fonts["tiny"].render("ONLINE", False, COLOR_ONLINE)
    surface.blit(online, (SCREEN_WIDTH - online.get_width() - 30, 32))

    # Top bar separator
    pygame.draw.line(surface, COLOR_LINE, (25, 55), (SCREEN_WIDTH - 28, 55), 2)

    # Footer separator
    pygame.draw.line(
        surface,
        COLOR_LINE,
        (25, SCREEN_HEIGHT - 65),
        (SCREEN_WIDTH - 28, SCREEN_HEIGHT - 65),
        2,
    )

    # Footer labels
    footer_y = SCREEN_HEIGHT - 48
    left = fonts["smaller"].render("USE ARROWS TO SELECT", False, COLOR_FOOTER)
    right = fonts["smaller"].render("PRESS ENTER TO START", False, COLOR_FOOTER)
    surface.blit(left, (28, footer_y))
    surface.blit(right, (SCREEN_WIDTH - right.get_width() - 28, footer_y))

    # Blinking INSERT COIN
    if int(elapsed / 0.6) % 2 == 0:
        draw_centered_text(
            surface, "INSERT COIN", fonts["smaller"], COLOR_RED_ORANGE, footer_y
        )


def draw_selected_item(surface, fonts, label, cy, elapsed):
    BOX_Y = cy - MENU_BOX_H // 2

    pygame.draw.rect(
        surface,
        COLOR_SELECTED_BG,
        pygame.Rect(MENU_BOX_X, BOX_Y, MENU_BOX_W, MENU_BOX_H),
        border_radius=12,
    )

    text_surf = fonts["menu"].render(label, False, COLOR_SELECTED_TEXT)
    text_x = (SCREEN_WIDTH - text_surf.get_width()) // 2
    text_y = cy - text_surf.get_height() // 2
    surface.blit(text_surf, (text_x, text_y))

    offset = int(math.sin(elapsed * 4) * 4)
    left_arrow = fonts["menu"].render(">", False, COLOR_SELECTED_TEXT)
    right_arrow = fonts["menu"].render("<", False, COLOR_SELECTED_TEXT)
    arrow_y = cy - left_arrow.get_height() // 2

    surface.blit(left_arrow, (MENU_BOX_X + 32 - offset, arrow_y))
    surface.blit(right_arrow, (MENU_BOX_X + MENU_BOX_W - 44 + offset, arrow_y))


def draw_menu(surface, fonts, selected, elapsed):
    for i, (label, _) in enumerate(MENU_ITEMS):
        cy = MENU_START_Y + i * MENU_SPACING
        if i == selected:
            draw_selected_item(surface, fonts, label, cy, elapsed)
        else:
            draw_centered_text(surface, label, fonts["menu"], ITEM_COLORS[i], cy)


def draw_boot(surface, fonts, elapsed):
    """Terminal boot sequence — one new line every 0.4s."""
    surface.fill(COLOR_BG)

    lines_to_show = min(int(elapsed / 0.4) + 1, len(BOOT_LINES))
    x = 40
    y = 80
    line_height = 36

    for i in range(lines_to_show):
        line_surf = fonts["tiny"].render(BOOT_LINES[i], False, COLOR_GREEN)
        surface.blit(line_surf, (x, y + i * line_height))

    if int(elapsed / 0.5) % 2 == 0:
        cursor_y = y + lines_to_show * line_height
        cursor = fonts["tiny"].render("_", False, COLOR_GREEN)
        surface.blit(cursor, (x, cursor_y))


def draw_loading(surface, fonts, game_label, elapsed):
    """Progress bar loading screen."""
    surface.fill(COLOR_BG)

    if int(elapsed / 0.5) % 2 == 0:
        draw_centered_text(
            surface, f"LOADING {game_label}...", fonts["small"], COLOR_GREEN, 240
        )

    BAR_W = 400
    BAR_H = 20
    BAR_X = (SCREEN_WIDTH - BAR_W) // 2
    BAR_Y = 310

    pygame.draw.rect(surface, COLOR_GREEN, pygame.Rect(
        BAR_X, BAR_Y, BAR_W, BAR_H), 2)

    fill_w = int(BAR_W * min(elapsed / 2.5, 1.0))
    if fill_w > 0:
        pygame.draw.rect(surface, COLOR_GREEN, pygame.Rect(
            BAR_X, BAR_Y, fill_w, BAR_H))


# ------------------------------------------------------------------ hit test


def get_item_rect(i):
    """Return the clickable Rect for menu item at index i."""
    cy = MENU_START_Y + i * MENU_SPACING
    return pygame.Rect(MENU_BOX_X, cy - MENU_BOX_H // 2, MENU_BOX_W, MENU_BOX_H)
