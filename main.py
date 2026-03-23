import pygame
import os
import math

FONT_PATH = os.path.join("assets", "fonts", "PressStart2P-Regular.ttf")

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

COLOR_BG            = (  8,  12,  18)
COLOR_BORDER        = (160, 170, 175)
COLOR_TITLE_YELLOW  = (238, 176,  32)   # PY-ARCADE gold
COLOR_GREEN         = ( 52, 200, 100)   # subtitle + some menu items
COLOR_TERMINAL      = ( 55, 160, 120)   # top-left prompt
COLOR_ONLINE        = ( 30, 220,  80)   # ONLINE indicator
COLOR_FOOTER        = (120, 130, 140)   # footer hint text
COLOR_RED_ORANGE    = (220,  55,  55)   # INSERT COIN
COLOR_SELECTED_BG   = (215, 215, 215)   # light gray box fill
COLOR_SELECTED_TEXT = ( 15,  15,  20)   # dark text inside the box
COLOR_CYAN          = ( 40, 200, 210)   # unselected item color

MENU_ITEMS = [
    ("ROCK-PAPER-SCISSORS", "rps"),
    ("TIC-TAC-TOE", "tictactoe"),
    ("SNAKE AND APPLE", "snake"),
]
ITEM_COLORS = [
    COLOR_SELECTED_BG,
    COLOR_CYAN,
    COLOR_GREEN,
]

TITLE = "8-Bit Suite"

def draw_border(surface):
    w = SCREEN_WIDTH
    h = SCREEN_HEIGHT

    # Gray border
    pygame.draw.rect(
        surface,
        COLOR_BORDER,
        pygame.Rect(15, 15, w - 30, h - 30),
        4
    )

# Helper function to draw centered text
def draw_centered_text(surface, text, font, color, y):
    text_surf = font.render(text, False, color)
    x = (SCREEN_WIDTH - text_surf.get_width()) // 2
    surface.blit(text_surf, (x, y))

def draw_text(surface, fonts, elapsed):
    # Title
    draw_centered_text(surface, "8-BIT SUITE", fonts["title"], COLOR_TITLE_YELLOW, 110)

    # Subtitle
    draw_centered_text(surface, "COLLECTION VOL. 1", fonts["small"], COLOR_GREEN, 175)

    # Terminal prompt
    prompt = fonts["tiny"].render("> root@8bit-suite:~$ ./menu.sh", False, COLOR_TERMINAL)
    surface.blit(prompt, (28, 28))

    # ONLINE top right
    online = fonts["tiny"].render("ONLINE", False, COLOR_ONLINE)
    x = SCREEN_WIDTH - online.get_width() - 28
    surface.blit(online, (x, 28))

    # Footer
    left    = fonts["tiny"].render("USE ARROWS TO SELECT", False, COLOR_FOOTER)
    mid     = fonts["tiny"].render("INSERT COIN", False, COLOR_RED_ORANGE)
    right   = fonts["tiny"].render("PRESS ENTER TO START", False, COLOR_FOOTER)

    footer_y = SCREEN_HEIGHT - 38

    pygame.draw.line(
        surface,
        (40, 55, 58),
        (25, SCREEN_HEIGHT - 65),
        (SCREEN_WIDTH - 28, SCREEN_HEIGHT - 65),
        1,
    )

    surface.blit(left, (28, footer_y))
    if int(elapsed / 0.6) % 2 == 0:
        draw_centered_text(surface, "INSERT COINT", fonts["tiny"], COLOR_RED_ORANGE, footer_y)
    surface.blit(right, (SCREEN_WIDTH - right.get_width() - 28, footer_y))

def draw_selected_item(surface, fonts, label, cy, elapsed):
    BOX_W = 560
    BOX_H = 60
    BOX_X = (SCREEN_WIDTH - BOX_W) // 2
    BOX_Y = cy - BOX_H // 2

    # 1. Draw the light gray box
    pygame.draw.rect(
        surface,
        COLOR_SELECTED_BG,
        pygame.Rect(BOX_X, BOX_Y, BOX_W, BOX_H),
        border_radius=2
    )

    # 2. Draw the label inside the box
    text_surf = fonts["menu"].render(label, False, COLOR_SELECTED_TEXT)
    text_x = (SCREEN_WIDTH - text_surf.get_width()) // 2
    text_y = cy - text_surf.get_height() // 2
    surface.blit(text_surf, (text_x, text_y))

    offset = int(math.sin(elapsed * 4) * 4)

    # 3. Draw > on the left and < on the right
    left_arrow  = fonts["menu"].render(">", False, COLOR_SELECTED_TEXT)
    right_arrow = fonts["menu"].render("<", False, COLOR_SELECTED_TEXT)

    arrow_y = cy - left_arrow.get_height() // 2
    surface.blit(left_arrow, (BOX_X + 12 - offset, arrow_y))
    surface.blit(right_arrow, (BOX_X + BOX_W - 24 + offset, arrow_y))

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
    BOX_W = 560
    BOX_H = 60
    BOX_X = (SCREEN_WIDTH - BOX_W) // 2
    start_y = 350
    spacing = 110
    cy = start_y + i * spacing
    return pygame.Rect(BOX_X, cy - BOX_H // 2, BOX_W, BOX_H)

def main():
    pygame.init()
    selected = 0
    elapsed = 0.0
    fonts = {
        "title": pygame.font.Font(FONT_PATH, 36),   # big gold title
        "small": pygame.font.Font(FONT_PATH, 11),   # subtitle
        "tiny":  pygame.font.Font(FONT_PATH, 8),    # terminal, footer
        "menu":  pygame.font.Font(FONT_PATH, 12),   # menu items
    }
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    running = True
    while running:
        # 1. EVENTS - did the user do something?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_RETURN:
                    label, scene = MENU_ITEMS[selected]
                    print(f"Launching: {scene}")
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i in range(len(MENU_ITEMS)):
                    if get_item_rect(i).collidepoint(mx, my):
                        selected = i
            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                for i in range(len(MENU_ITEMS)):
                    if get_item_rect(i).collidepoint(mx, my):
                        label, scene = MENU_ITEMS[i]
                        print(f"Launching: {scene}")


        # 2. UPDATE - move things, change state
        dt = clock.tick(FPS) / 1000.0
        elapsed += dt

        # 3. DRAW - paint the screen
        screen.fill(COLOR_BG)
        draw_border(screen)
        draw_text(screen, fonts, elapsed)
        draw_menu(screen, fonts, selected, elapsed)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
