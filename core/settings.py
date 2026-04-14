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
    "win": (52, 220, 100),
    "lose": (220, 60, 60),
    "draw": (180, 180, 180),
}
RESULT_LABELS = {
    "win": "YOU WIN!",
    "lose": "CPU WINS!",
    "draw": "DRAW!",
}

# --- TTT Board Layout ---
TTT_CELL_SIZE = 160
TTT_BOARD_W = TTT_CELL_SIZE * 3
TTT_BOARD_H = TTT_CELL_SIZE * 3
TTT_BOARD_X = (SCREEN_WIDTH - TTT_BOARD_W) // 2
TTT_BOARD_Y = 140

# --- TTT Colors ---
COLOR_TTT_LINE = (60, 80, 100)
COLOR_TTT_X = (220, 60, 60)
COLOR_TTT_O = (40, 180, 220)

# --- Snake Layout ---
SNAKE_COLS = 25         # number of grid columns
SNAKE_ROWS = 25         # number of grid rows
SNAKE_CELL = 18         # pixels per cell
SNAKE_BOARD_W = SNAKE_COLS * SNAKE_CELL   # 360px
SNAKE_BOARD_H = SNAKE_ROWS * SNAKE_CELL   # 360px
SNAKE_BOARD_X = (SCREEN_WIDTH - SNAKE_BOARD_W) // 2
SNAKE_BOARD_Y = 155

# --- Snake Speed ---
SNAKE_BASE_SPEED = 8.0   # moves per second at score 0
SNAKE_SPEED_STEP = 0.5  # added per 10 score points

# --- Snake Colors ---
COLOR_SNAKE_HEAD = (52, 220, 100)
COLOR_SNAKE_BODY = (38, 160, 75)
COLOR_APPLE      = (220, 60, 60)
COLOR_BOARD_BG   = (10, 16, 22)
COLOR_BOARD_BORDER = (40, 80, 100)
