# Tic-Tac-Toe - Implementation Deep Dive

---

## Table of Contents

- [Tic-Tac-Toe - Implementation Deep Dive](#tic-tac-toe---implementation-deep-dive)
    - [Table of Contents](#table-of-contents)
    - [1. The Complete File at a Glance](#1-the-complete-file-at-a-glance)
    - [2. Imports and Core Constants](#2-imports-and-core-constants)
    - [3. WINNING_LINES - The Board Truth Table](#3-winning_lines---the-board-truth-table)
    - [4. load_ttt_images() - Asset Loading with Headless Safety](#4-load_ttt_images---asset-loading-with-headless-safety)
    - [5. check_winner() - Pure Board Evaluation](#5-check_winner---pure-board-evaluation)
    - [6. minimax() - Perfect-Play Search](#6-minimax---perfect-play-search)
    - [7. get_cpu_move() - Difficulty and Move Selection](#7-get_cpu_move---difficulty-and-move-selection)
    - [8. TicTacToeScene.**init**, on_exit, and Reset Lifecycle](#8-tictactoescene__init__-on_exit-and-reset-lifecycle)
    - [9. handle_events() - Keyboard and Mouse Rules](#9-handle_events---keyboard-and-mouse-rules)
    - [10. update() - CPU Delay and Turn Execution](#10-update---cpu-delay-and-turn-execution)
    - [11. \_place_move() - Single Source of State Transition](#11-_place_move---single-source-of-state-transition)
    - [12. Helper Methods](#12-helper-methods)
        - [\_find_winning_line()](#_find_winning_line)
        - [\_get_cell_from_mouse()](#_get_cell_from_mouse)
        - [\_cell_center()](#_cell_center)
        - [\_draw_marker_image()](#_draw_marker_image)
    - [13. draw() and Visual Subsystems](#13-draw-and-visual-subsystems)
    - [14. \_draw_board() - Grid, Markers, and Winning Stroke](#14-_draw_board---grid-markers-and-winning-stroke)
    - [15. \_draw_result_overlay() - Result UX and Replay Button](#15-_draw_result_overlay---result-ux-and-replay-button)
    - [16. Full Round Flow - Player Move to Result](#16-full-round-flow---player-move-to-result)
    - [17. Testing - Why This Suite Is Structured This Way](#17-testing---why-this-suite-is-structured-this-way)
        - [Core Test Fixtures](#core-test-fixtures)
        - [Logic Tests](#logic-tests)
        - [Scene Behavior Tests](#scene-behavior-tests)
    - [18. Running the Tests](#18-running-the-tests)

---

## 1. The Complete File at a Glance

`scenes/tictactoe.py` has two major layers:

- standalone pure/gameplay functions
- scene orchestration and rendering methods

```python
WINNING_LINES = np.array([...])

def load_ttt_images() -> dict[int, pygame.Surface]: ...
def check_winner(board: np.ndarray) -> str | None: ...
def minimax(board: np.ndarray, is_maximizing: bool) -> int: ...
def get_cpu_move(board: np.ndarray, difficulty: float = 0.6) -> int: ...

class TicTacToeScene(BaseScene):
        def __init__(self, manager, fonts): ...
        def on_exit(self): ...
        def _reset_game(self): ...
        def _reset_round(self): ...
        def handle_events(self, events): ...
        def update(self, dt): ...
        def draw(self, screen): ...
        def _place_move(self, cell, value): ...
        def _find_winning_line(self): ...
        def _get_cell_from_mouse(self, mx, my): ...
        def _cell_center(self, cell): ...
        def _draw_marker_image(self, screen, center, value): ...
        def _draw_border(self, screen): ...
        def _draw_header(self, screen): ...
        def _draw_board(self, screen): ...
        def _draw_footer(self, screen): ...
        def _draw_result_overlay(self, screen): ...
```

This split is intentional: pure logic is easy to test independently, while scene methods manage event/update/draw lifecycle.

---

## 2. Imports and Core Constants

Imports include:

- `numpy` for board arithmetic and line checks
- `pygame` for scene/input/rendering
- `os` for robust cross-platform asset pathing

Settings constants provide:

- geometry (`TTT_CELL_SIZE`, `TTT_BOARD_X`, `TTT_BOARD_Y`, etc.)
- palette (`COLOR_TTT_X`, `COLOR_TTT_O`, UI colors)
- shared result labels/colors used across scenes

Centralized constants make it easy to tune board size or palette without touching logic functions.

---

## 3. WINNING_LINES - The Board Truth Table

```python
WINNING_LINES = np.array(
        [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],
                [0, 3, 6], [1, 4, 7], [2, 5, 8],
                [0, 4, 8], [2, 4, 6],
        ]
)
```

Each row in this constant is one terminal win pattern. That allows winner detection and winning-line rendering to use exactly the same source of truth.

---

## 4. load_ttt_images() - Asset Loading with Headless Safety

Responsibilities:

1. Build absolute image paths for `X.png` and `O.png`.
2. Load both images.
3. Convert with alpha only when display surface exists.
4. Scale to marker size based on cell size.
5. Fallback to transparent placeholder surfaces if loading fails.

Important detail:

```python
if pygame.display.get_init():
        display_surface = pygame.display.get_surface()
```

This avoids `convert_alpha()` errors in headless test runs where no active display exists.

---

## 5. check_winner() - Pure Board Evaluation

```python
def check_winner(board):
        for line in WINNING_LINES:
                total = board[line].sum()
                if total == 3:
                        return "X"
                elif total == -3:
                        return "O"
        if np.all(board != 0):
                return "draw"
        return None
```

Board encoding:

- `1` means X
- `-1` means O
- `0` means empty

Using sums is elegant:

- 3 cells of X -> sum is 3
- 3 cells of O -> sum is -3

This function is pure and deterministic, so it is heavily unit tested.

---

## 6. minimax() - Perfect-Play Search

`minimax(board, is_maximizing)` recursively explores future board states.

Role convention:

- CPU is O (`-1`) and is maximizing.
- Player is X (`1`) and is minimizing.

Terminal scoring:

- O win -> `1`
- X win -> `-1`
- draw -> `0`

Recursive step:

1. For each empty cell, place symbol for current side.
2. Recurse with flipped maximizing flag.
3. Undo move.
4. Return best (max or min) score.

Because Tic-Tac-Toe state space is small, full-depth minimax is fast enough.

---

## 7. get_cpu_move() - Difficulty and Move Selection

`get_cpu_move(board, difficulty=0.6)` blends perfect play and random play.

Nerf gate:

```python
if np.random.random() > difficulty:
        return int(np.random.choice(empty_cells))
```

So at default difficulty 0.6:

- 60 percent chance: minimax best move
- 40 percent chance: random legal move

If AI does not nerf, function evaluates every legal move with minimax and picks highest score.

---

## 8. TicTacToeScene.**init**, on_exit, and Reset Lifecycle

Initialization:

```python
def __init__(...):
        super().__init__(manager)
        self.fonts = fonts
        self.marker_images = load_ttt_images()
        self._reset_game()
```

Reset layers:

- `_reset_game()` clears scores and starts new round.
- `_reset_round()` clears board and phase state but keeps scores.

`on_exit()` calls `_reset_game()`, guaranteeing fresh state when returning from menu.

---

## 9. handle_events() - Keyboard and Mouse Rules

Keyboard:

- `ESC`: go to menu
- `R`: reset round
- `ENTER` in result phase: reset round

Mouse click handling order:

1. abort rect -> menu
2. reset button rect (if visible) -> reset round
3. board click (only in playing phase and player turn) -> place move if empty

This sequence prevents accidental board input when clicking overlay controls.

---

## 10. update() - CPU Delay and Turn Execution

Update runs CPU only when all conditions are true:

- phase is `playing`
- current turn is `O`
- `cpu_timer >= 0.6`

Then:

```python
cpu_cell = get_cpu_move(self.board)
self._place_move(cpu_cell, -1)
```

Delay creates readable pacing and gives player visible turn separation.

---

## 11. \_place_move() - Single Source of State Transition

`_place_move` is the most important scene helper.

Validation guard:

```python
if self.phase != "playing" or not (0 <= cell < 9) or self.board[cell] != 0:
        return
```

Then it performs atomic state transition:

1. Write symbol to board.
2. Evaluate result via `check_winner`.
3. If terminal:
    - set `winner`
    - compute `winning_line`
    - increment score for winner
    - set phase to `result`
4. Else:
    - switch turn
    - reset cpu timer

Having one placement method avoids duplicated logic between player and CPU paths.

---

## 12. Helper Methods

### \_find_winning_line()

Scans `WINNING_LINES`, returns first line whose sum is `3` or `-3`. Used for rendering strike-through line on winning trio.

### \_get_cell_from_mouse()

Converts pixel coordinates to board index:

```python
col = (mx - TTT_BOARD_X) // TTT_CELL_SIZE
row = (my - TTT_BOARD_Y) // TTT_CELL_SIZE
```

Returns `None` for out-of-bounds clicks.

### \_cell_center()

Converts board index to pixel center. Shared by marker drawing and winning-line endpoints.

### \_draw_marker_image()

Draws cached marker surface centered in target cell.

---

## 13. draw() and Visual Subsystems

Top-level draw order:

1. fill background
2. border
3. header
4. board
5. footer
6. result overlay (if needed)

Overlay is drawn last so it sits on top of all gameplay visuals.

---

## 14. \_draw_board() - Grid, Markers, and Winning Stroke

`_draw_board` has three stages:

1. draw 2 vertical + 2 horizontal grid lines
2. draw markers for all non-zero cells
3. if winner exists, draw thick winning line from first to third cell center

Because marker images are loaded once and reused, per-frame rendering stays cheap.

---

## 15. \_draw_result_overlay() - Result UX and Replay Button

Overlay behavior:

- Draws translucent panel centered on screen.
- Displays winner label and color via shared `RESULT_LABELS` and `RESULT_COLORS`.
- Creates `reset_btn_rect` for click replay.
- Applies hover color change for button border and text.

This produces keyboard and mouse parity for replay actions.

---

## 16. Full Round Flow - Player Move to Result

```text
Round start
    -> _reset_round
    -> phase = playing, turn = X

Player click empty cell
    -> _place_move(cell, 1)
    -> check_winner
    -> if no result, turn -> O

update(dt)
    -> wait 0.6s
    -> cpu cell = get_cpu_move(board)
    -> _place_move(cell, -1)

Repeat until winner/draw
    -> phase = result
    -> draw overlay
    -> Enter/click replay -> _reset_round
```

---

## 17. Testing - Why This Suite Is Structured This Way

`tests/test_tictactoe.py` isolates pure logic and scene behavior with headless-safe patterns.

### Core Test Fixtures

- session pygame init fixture
- lightweight font fixture
- `MockManager` for `switch_to` assertions
- monkeypatched marker loader to avoid asset dependency

### Logic Tests

- `TestCheckWinner` validates all line types, draw, and in-progress paths
- `TestGetCpuMove` validates legal move output, blocking/winning choices, and no board mutation

### Scene Behavior Tests

- `TestSceneInit` validates initial defaults
- `TestPlayerMove` and `TestCpuMove` validate input and delayed AI timing
- `TestWinDetection` validates winner/score transitions
- reset/lifecycle classes validate round reset, full reset, and exit behavior
- `TestKeyboard` validates escape/reset/replay shortcuts

This layered suite catches regressions quickly while staying fast and deterministic.

---

## 18. Running the Tests

```bash
# Tic-Tac-Toe tests only
python -m pytest tests/test_tictactoe.py -v

# Full repository tests
python -m pytest tests/ -v
```

Run with short tracebacks:

```bash
python -m pytest tests/test_tictactoe.py --tb=short -v
```
