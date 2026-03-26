import os
import pygame

# --- Paths ---
FONT_PATH = os.path.join("assets", "fonts", "PressStart2P-Regular.ttf")

# --- Window ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "8-Bit Suite"

# --- Colors ---
COLOR_BG = (8, 12, 18)
COLOR_BORDER = (160, 170, 175)
COLOR_TITLE_YELLOW = (238, 176, 32)
COLOR_GREEN = (52, 200, 100)
COLOR_TERMINAL = (55, 160, 120)
COLOR_ONLINE = (30, 220, 80)
COLOR_FOOTER = (120, 130, 140)
COLOR_RED_ORANGE = (220, 55, 55)
COLOR_SELECTED_BG = (219, 226, 233)
COLOR_SELECTED_TEXT = (67, 70, 75)
COLOR_LINE = (54, 69, 79)
COLOR_CYAN = (40, 200, 210)
COLOR_LIGHT_RED = (255, 114, 118)
COLOR_DENIM_BLUE = (21, 96, 189)
COLOR_SPRING_GREEN = (38, 208, 124)

# --- Menu data ---
MENU_ITEMS = [
    ("ROCK-PAPER-SCISSORS", "rps"),
    ("TIC-TAC-TOE", "tictactoe"),
    ("SNAKE AND APPLE", "snake"),
]

ITEM_COLORS = [
    COLOR_LIGHT_RED,
    COLOR_DENIM_BLUE,
    COLOR_SPRING_GREEN,
]

# --- Boot sequence ---
BOOT_LINES = [
    "PY-OS v1.0.4",
    "Loading core modules...",
    "Memory check: 640K OK",
    "Initializing graphic interface...",
    "Ready.",
]


# --- Fonts ---
def load_fonts() -> dict[str, pygame.font.Font]:
    """Load and return the font resources used across the game."""
    return {
        "title": pygame.font.Font(FONT_PATH, 42),
        "small": pygame.font.Font(FONT_PATH, 18),
        "smaller": pygame.font.Font(FONT_PATH, 14),
        "tiny": pygame.font.Font(FONT_PATH, 12),
        "menu": pygame.font.Font(FONT_PATH, 16),
    }

# --- RPS Card Layout ---
CARD_W = 200
CARD_H = 200
CARD_Y = 260
PLAYER_CARD_X = 180
CPU_CARD_X = 620

# --- RPS Card Colors ---
COLOR_CARD_BG = (20, 28, 38)
COLOR_PLAYER_BORDER = (52, 220, 100)
COLOR_CPU_BORDER = (60, 130, 220)
COLOR_CARD_TEXT = (220, 220, 220)

# --- RPS Result Colors ---
RESULT_COLORS = {
    "win":  (52, 220, 100),
    "lose": (220, 60, 60),
    "draw": (180, 180, 180),
}
RESULT_LABELS = {
    "win":  "YOU WIN!",
    "lose": "CPU WINS!",
    "draw": "DRAW!",
}
