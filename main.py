import pygame
import os
import math

FONT_PATH = os.path.join("assets", "fonts", "PressStart2P-Regular.ttf")

# --- Constants ---
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 720
FPS           = 60

# --- Colors ---
COLOR_BG            = (  8,  12,  18)
COLOR_BORDER        = (160, 170, 175)
COLOR_TITLE_YELLOW  = (238, 176,  32)
COLOR_GREEN         = ( 52, 200, 100)
COLOR_TERMINAL      = ( 55, 160, 120)
COLOR_ONLINE        = ( 30, 220,  80)
COLOR_FOOTER        = (120, 130, 140)
COLOR_RED_ORANGE    = (220,  55,  55)
COLOR_SELECTED_BG   = (219, 226, 233)
COLOR_SELECTED_TEXT = ( 67,  70,  75)
COLOR_CYAN          = ( 40, 200, 210)

# --- Data ---
MENU_ITEMS = [
    ("ROCK-PAPER-SCISSORS", "rps"),
    ("TIC-TAC-TOE",         "tictactoe"),
    ("SNAKE AND APPLE",     "snake"),
]

ITEM_COLORS = [
    COLOR_RED_ORANGE,
    COLOR_CYAN,
    COLOR_GREEN,
]

BOOT_LINES = [
    "PY-OS v1.0.4",
    "Loading core modules...",
    "Memory check: 640K OK",
    "Initializing graphic interface...",
    "Ready.",
]

TITLE = "8-Bit Suite"


# ------------------------------------------------------------------ helpers

def draw_centered_text(surface, text, font, color, y):
    """Draw text horizontally centered at y."""
    text_surf = font.render(text, False, color)
    x = (SCREEN_WIDTH - text_surf.get_width()) // 2
    surface.blit(text_surf, (x, y))


# ------------------------------------------------------------------ screens

def draw_border(surface):
    pygame.draw.rect(
        surface,
        COLOR_BORDER,
        pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30),
        4
    )


def draw_title(surface, fonts):
    """Big title with orange drop shadow."""
    shadow_color = (180, 80, 0)
    title_text   = "8-BIT SUITE"

    shadow_surf = fonts["title"].render(title_text, False, shadow_color)
    title_surf  = fonts["title"].render(title_text, False, COLOR_TITLE_YELLOW)

    title_x = (SCREEN_WIDTH - title_surf.get_width()) // 2
    title_y = 110

    surface.blit(shadow_surf, (title_x + 4, title_y + 4))   # shadow behind
    surface.blit(title_surf,  (title_x, title_y))            # text on top


def draw_text(surface, fonts, elapsed):
    draw_title(surface, fonts)

    draw_centered_text(surface, "COLLECTION VOL. 1", fonts["small"], COLOR_GREEN, 175)

    # Terminal prompt top-left
    prompt = fonts["tiny"].render("> root@8bit-suite:~$ ./menu.sh", False, COLOR_TERMINAL)
    surface.blit(prompt, (28, 28))

    # ONLINE top-right
    online = fonts["tiny"].render("ONLINE", False, COLOR_ONLINE)
    surface.blit(online, (SCREEN_WIDTH - online.get_width() - 28, 28))

    # Top bar separator
    pygame.draw.line(surface, (30, 35, 40), (15, 55), (SCREEN_WIDTH - 15, 55), 2)

    # Footer separator
    pygame.draw.line(surface, (40, 55, 58),
                     (25, SCREEN_HEIGHT - 65),
                     (SCREEN_WIDTH - 28, SCREEN_HEIGHT - 65), 1)

    # Footer labels
    footer_y = SCREEN_HEIGHT - 48
    left  = fonts["smaller"].render("USE ARROWS TO SELECT", False, COLOR_FOOTER)
    right = fonts["smaller"].render("PRESS ENTER TO START", False, COLOR_FOOTER)
    surface.blit(left,  (28, footer_y))
    surface.blit(right, (SCREEN_WIDTH - right.get_width() - 28, footer_y))

    # Blinking INSERT COIN
    if int(elapsed / 0.6) % 2 == 0:
        draw_centered_text(surface, "INSERT COIN", fonts["smaller"], COLOR_RED_ORANGE, footer_y)


def draw_boot(surface, fonts, elapsed):
    """Terminal boot sequence — shows one new line every 0.4s."""
    surface.fill(COLOR_BG)

    lines_to_show = min(int(elapsed / 0.4) + 1, len(BOOT_LINES))
    x           = 40
    y           = 80
    line_height = 36

    for i in range(lines_to_show):
        line_surf = fonts["tiny"].render(BOOT_LINES[i], False, COLOR_GREEN)
        surface.blit(line_surf, (x, y + i * line_height))

    # Blinking cursor after last line
    if int(elapsed / 0.5) % 2 == 0:
        cursor_y = y + lines_to_show * line_height
        cursor   = fonts["tiny"].render("_", False, COLOR_GREEN)
        surface.blit(cursor, (x, cursor_y))


def draw_loading(surface, fonts, game_label, elapsed):
    surface.fill(COLOR_BG)

    # Blinking loading text
    if int(elapsed / 0.5) % 2 == 0:
        draw_centered_text(surface, f"LOADING {game_label}...",
                           fonts["small"], COLOR_GREEN, 240)

    # Progress bar
    BAR_W = 400
    BAR_H = 20
    BAR_X = (SCREEN_WIDTH - BAR_W) // 2
    BAR_Y = 310

    # Outline
    pygame.draw.rect(surface, COLOR_GREEN, pygame.Rect(BAR_X, BAR_Y, BAR_W, BAR_H), 2)

    # Fill — grows over 2.5 seconds
    progress = min(elapsed / 2.5, 1.0)
    fill_w   = int(BAR_W * progress)
    if fill_w > 0:
        pygame.draw.rect(surface, COLOR_GREEN, pygame.Rect(BAR_X, BAR_Y, fill_w, BAR_H))


def draw_selected_item(surface, fonts, label, cy, elapsed):
    BOX_W = 560
    BOX_H = 60
    BOX_X = (SCREEN_WIDTH - BOX_W) // 2
    BOX_Y = cy - BOX_H // 2

    pygame.draw.rect(surface, COLOR_SELECTED_BG,
                     pygame.Rect(BOX_X, BOX_Y, BOX_W, BOX_H), border_radius=12)

    text_surf = fonts["menu"].render(label, False, COLOR_SELECTED_TEXT)
    text_x    = (SCREEN_WIDTH - text_surf.get_width()) // 2
    text_y    = cy - text_surf.get_height() // 2
    surface.blit(text_surf, (text_x, text_y))

    offset      = int(math.sin(elapsed * 4) * 4)
    left_arrow  = fonts["menu"].render(">", False, COLOR_SELECTED_TEXT)
    right_arrow = fonts["menu"].render("<", False, COLOR_SELECTED_TEXT)
    arrow_y     = cy - left_arrow.get_height() // 2

    surface.blit(left_arrow,  (BOX_X + 32 - offset, arrow_y))
    surface.blit(right_arrow, (BOX_X + BOX_W - 44 + offset, arrow_y))


def draw_menu(surface, fonts, selected, elapsed):
    start_y = 350
    spacing = 110

    for i, (label, scene) in enumerate(MENU_ITEMS):
        cy = start_y + i * spacing
        if i == selected:
            draw_selected_item(surface, fonts, label, cy, elapsed)
        else:
            draw_centered_text(surface, label, fonts["menu"], ITEM_COLORS[i], cy)


def get_item_rect(i):
    BOX_W   = 560
    BOX_H   = 60
    BOX_X   = (SCREEN_WIDTH - BOX_W) // 2
    start_y = 350
    spacing = 110
    cy      = start_y + i * spacing
    return pygame.Rect(BOX_X, cy - BOX_H // 2, BOX_W, BOX_H)


# ------------------------------------------------------------------ main

def main():
    pygame.init()

    fonts = {
        "title"     : pygame.font.Font(FONT_PATH, 42),
        "small"     : pygame.font.Font(FONT_PATH, 18),
        "smaller"   : pygame.font.Font(FONT_PATH, 14),
        "tiny"      : pygame.font.Font(FONT_PATH, 12),
        "menu"      : pygame.font.Font(FONT_PATH, 16),
    }

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    selected      = 0
    elapsed       = 0.0
    state         = "boot"
    loading_label = ""

    BOOT_DURATION = len(BOOT_LINES) * 0.4 + 0.4

    running = True
    while running:

        # 1. EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(MENU_ITEMS)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(MENU_ITEMS)
                    elif event.key == pygame.K_RETURN:
                        loading_label = MENU_ITEMS[selected][0]
                        state         = "loading"
                        elapsed       = 0.0
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            elif event.type == pygame.MOUSEMOTION and state == "menu":
                mx, my = event.pos
                for i in range(len(MENU_ITEMS)):
                    if get_item_rect(i).collidepoint(mx, my):
                        selected = i

            elif event.type == pygame.MOUSEBUTTONUP and state == "menu":
                mx, my = event.pos
                for i in range(len(MENU_ITEMS)):
                    if get_item_rect(i).collidepoint(mx, my):
                        loading_label = MENU_ITEMS[i][0]
                        state         = "loading"
                        elapsed       = 0.0

        # 2. UPDATE
        dt       = clock.tick(FPS) / 1000.0
        elapsed += dt

        if state == "boot" and elapsed >= BOOT_DURATION:
            state   = "menu"
            elapsed = 0.0

        if state == "loading" and elapsed >= 2.5:
            print(f"Launching: {MENU_ITEMS[selected][1]}")
            state   = "menu"
            elapsed = 0.0

        # 3. DRAW
        screen.fill(COLOR_BG)

        if state == "boot":
            draw_boot(screen, fonts, elapsed)
        elif state == "menu":
            draw_border(screen)
            draw_text(screen, fonts, elapsed)
            draw_menu(screen, fonts, selected, elapsed)
        elif state == "loading":
            draw_loading(screen, fonts, loading_label, elapsed)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
