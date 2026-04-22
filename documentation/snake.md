# Snake and Apple - Implementation Deep Dive

---

## Table of Contents

- [Snake and Apple - Implementation Deep Dive](#snake-and-apple---implementation-deep-dive)
    - [Table of Contents](#table-of-contents)
    - [1. The Complete File at a Glance](#1-the-complete-file-at-a-glance)
    - [2. Imports and Constants](#2-imports-and-constants)
    - [3. SnakeScene.**init** and Scene Lifecycle](#3-snakescene__init__-and-scene-lifecycle)
        - [on_exit()](#on_exit)
    - [4. \_reset_game() and \_reset_round() - Two Levels of Reset](#4-_reset_game-and-_reset_round---two-levels-of-reset)
    - [5. \_spawn_apple() - Safe Spawn Logic](#5-_spawn_apple---safe-spawn-logic)
    - [6. handle_events() - Input and Direction Buffering](#6-handle_events---input-and-direction-buffering)
    - [7. update() - Time-Based Movement and State Changes](#7-update---time-based-movement-and-state-changes)
    - [8. Collision Handling Details](#8-collision-handling-details)
    - [9. Growth, Score, and Full-Board End Condition](#9-growth-score-and-full-board-end-condition)
    - [10. \_die() - Terminal State Entry](#10-_die---terminal-state-entry)
    - [11. draw() - Rendering Pipeline](#11-draw---rendering-pipeline)
    - [12. \_draw_border() and \_draw_header()](#12-_draw_border-and-_draw_header)
    - [13. \_draw_board() - Board, Apple, and Body Gradient](#13-_draw_board---board-apple-and-body-gradient)
    - [14. \_draw_cell() - Rounded Cells and Alpha Rendering](#14-_draw_cell---rounded-cells-and-alpha-rendering)
    - [15. \_draw_footer() - Score HUD and Hover Abort](#15-_draw_footer---score-hud-and-hover-abort)
    - [16. \_draw_game_over() - Overlay and Restart Button](#16-_draw_game_over---overlay-and-restart-button)
    - [17. Full Round Flow - Start to Death to Replay](#17-full-round-flow---start-to-death-to-replay)
    - [18. Testing - What and Why](#18-testing---what-and-why)
        - [What We Test vs What We Do Not](#what-we-test-vs-what-we-do-not)
        - [Fixture Setup](#fixture-setup)
        - [Test Classes Explained](#test-classes-explained)
    - [19. Running the Tests](#19-running-the-tests)

---

## 1. The Complete File at a Glance

Before diving into each part, here is a compact view of how the Snake scene is organized:

```python
import pygame
import random
from core.base_scene import BaseScene
from core.settings import ...

class SnakeScene(BaseScene):
    def __init__(self, manager, fonts): ...
    def on_exit(self): ...
    def _reset_game(self): ...
    def _reset_round(self): ...
    def _spawn_apple(self): ...
    def handle_events(self, events): ...
    def update(self, dt): ...
    def _die(self): ...
    def draw(self, screen): ...
    def _draw_border(self, screen): ...
    def _draw_header(self, screen): ...
    def _draw_board(self, screen): ...
    def _draw_footer(self, screen): ...
    def _draw_cell(self, screen, cell, color): ...
    def _draw_game_over(self, screen): ...
```

This scene intentionally keeps all game logic inside one class because Snake state is tightly coupled: body list, apple position, movement timer, and phase transitions all evolve together.

---

## 2. Imports and Constants

```python
import pygame
import random
from typing import Any
```

- `pygame` handles events, drawing, rectangles, and surfaces.
- `random` is used only in apple spawning.
- `Any` is used for manager typing in the constructor.

Constants from `core.settings` define:

- global layout (`SCREEN_WIDTH`, `SCREEN_HEIGHT`)
- color palette
- board geometry (`SNAKE_COLS`, `SNAKE_ROWS`, `SNAKE_CELL`, board X/Y/W/H)
- speed curve (`SNAKE_BASE_SPEED`, `SNAKE_SPEED_STEP`)

Keeping constants in one shared file prevents magic numbers inside scene logic and makes visual tuning safe.

---

## 3. SnakeScene.**init** and Scene Lifecycle

```python
def __init__(self, manager, fonts):
    super().__init__(manager)
    self.fonts = fonts
    self._reset_game()
```

Key points:

- `super().__init__(manager)` initializes scene-manager linkage.
- Fonts are injected, not loaded inside this scene.
- Constructor delegates all mutable state setup to `_reset_game()`.

This keeps initialization and reset behavior consistent.

### on_exit()

```python
def on_exit(self):
    self._reset_game()
```

When player leaves Snake and comes back later, the scene restarts cleanly with no leftover score or dead phase.

---

## 4. \_reset_game() and \_reset_round() - Two Levels of Reset

```python
def _reset_game(self):
    self.hi_score = 0
    self._reset_round()
```

`_reset_game` means full-session reset, including high score.

```python
def _reset_round(self):
    mid_c = SNAKE_COLS // 2
    mid_r = SNAKE_ROWS // 2
    self.snake = [(mid_c, mid_r), (mid_c - 1, mid_r), (mid_c - 2, mid_r)]
    self.direction = (1, 0)
    self.next_dir = (1, 0)
    self.score = 0
    self.phase = "playing"
    self.move_timer = 0.0
    self.apple = self._spawn_apple()
```

`_reset_round` clears only round state and preserves `hi_score`.

Why two methods?

- Replay in same scene should preserve high score.
- Entering/leaving scene should fully reset high score.

---

## 5. \_spawn_apple() - Safe Spawn Logic

```python
def _spawn_apple(self):
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
```

Why this works well:

- Never places apple on top of snake.
- Works for all board states without custom edge-case branching.
- Returning `None` gives a clean signal for full-board state.

The full-board return path is used as a terminal condition after growth.

---

## 6. handle_events() - Input and Direction Buffering

Input behavior is phase-aware and includes keyboard plus mouse.

Direction map includes arrow keys and WASD:

```python
DIR_MAP = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}
```

Reverse prevention:

```python
dx, dy = self.direction
if nd[0] != -dx or nd[1] != -dy:
    self.next_dir = nd
```

This is important: it compares against currently applied `direction`, not `next_dir`, so rapid key presses cannot force illegal immediate reversal.

Phase-specific behavior:

- `ESC`: always exit to menu.
- Dead phase: `SPACE` or `ENTER` resets round.
- Mouse click on abort rect: exit.
- Mouse click on overlay reset button: reset round.

---

## 7. update() - Time-Based Movement and State Changes

`update(dt)` runs only while phase is `playing`.

Speed ramp:

```python
speed = SNAKE_BASE_SPEED + (self.score // 10) * SNAKE_SPEED_STEP
```

Movement gate:

```python
self.move_timer += dt
if self.move_timer < 1.0 / speed:
    return
self.move_timer = 0.0
```

This gives deterministic cell stepping independent of frame rate. Increasing score gradually reduces tick interval.

After timer gate passes:

1. Apply buffered direction.
2. Compute new head.
3. Resolve collisions.
4. Insert new head.
5. Either grow (apple) or pop tail.

---

## 8. Collision Handling Details

Wall collision:

```python
if not (0 <= nx < SNAKE_COLS and 0 <= ny < SNAKE_ROWS):
    self._die()
```

Self collision is subtle:

```python
growing = new_head == self.apple
collision_body = self.snake if growing else self.snake[:-1]
if new_head in collision_body:
    self._die()
```

Why `snake[:-1]` when not growing?

- On non-growth moves, tail will be removed at end of tick.
- Moving into the current tail position is legal in classic Snake.
- Excluding tail avoids false self-collisions.

---

## 9. Growth, Score, and Full-Board End Condition

When apple is eaten:

```python
self.score += 1
self.hi_score = max(self.hi_score, self.score)
self.apple = self._spawn_apple()
```

No tail pop occurs in growth path, so snake length increases by one.

If spawn returns `None`:

```python
if self.apple is None:
    self._die()
```

This represents a board-fill victory state implemented using existing dead-phase overlay flow.

---

## 10. \_die() - Terminal State Entry

```python
def _die(self):
    self.hi_score = max(self.hi_score, self.score)
    self.phase = "dead"
```

Single-purpose transition method with two responsibilities:

- preserve best score
- lock gameplay updates

Consolidating this in one method avoids duplicated end-state logic.

---

## 11. draw() - Rendering Pipeline

```python
def draw(self, screen):
    screen.fill(COLOR_BG)
    self._draw_border(screen)
    self._draw_header(screen)
    self._draw_board(screen)
    self._draw_footer(screen)
    if self.phase == "dead":
        self._draw_game_over(screen)
```

Order matters. Overlay must be last so it appears above board and HUD.

---

## 12. \_draw_border() and \_draw_header()

Border:

- draws the terminal frame inset from screen edges

Header:

- renders terminal-style command line text
- renders `ONLINE` status right-aligned
- draws separator line
- centers title

All typography uses injected font dictionary for consistency across scenes.

---

## 13. \_draw_board() - Board, Apple, and Body Gradient

Board rendering order:

1. board background rectangle
2. board outline
3. apple cell (if present)
4. body cells
5. head cell

Body gradient logic:

```python
body = self.snake[1:]
n_body = len(body)
for i, seg in enumerate(reversed(body)):
    fraction = 0.4 + 0.6 * (i / max(1, n_body - 1)) if n_body > 1 else 1.0
    alpha = int(255 * fraction)
    color = (*COLOR_SNAKE_BODY[:3], alpha)
```

What this gives:

- Tail starts at 40 percent alpha.
- Opacity increases toward neck.
- Head remains fully opaque with dedicated head color.

---

## 14. \_draw_cell() - Rounded Cells and Alpha Rendering

Cell rectangle:

```python
rect = pygame.Rect(x, y, SNAKE_CELL - 2, SNAKE_CELL - 2)
```

RGB path:

```python
pygame.draw.rect(screen, color, rect, border_radius=3)
```

RGBA path:

```python
s = pygame.Surface(rect.size, pygame.SRCALPHA)
pygame.draw.rect(s, color, s.get_rect(), border_radius=3)
screen.blit(s, rect.topleft)
```

Why separate paths?

- Standard `pygame.draw.rect` on screen surface is fine for opaque colors.
- Alpha blending for per-segment transparency is reliable when drawn on an intermediate alpha surface, then blitted.

---

## 15. \_draw_footer() - Score HUD and Hover Abort

Footer responsibilities:

- separator line above footer
- hover-sensitive abort label color
- right-aligned score/hi-score text

Hover color check:

```python
mx, my = pygame.mouse.get_pos()
abort_color = COLOR_GREEN if self.abort_rect.collidepoint(mx, my) else COLOR_FOOTER
```

Shared rect usage between drawing and event handling keeps clickable area and visual affordance aligned.

---

## 16. \_draw_game_over() - Overlay and Restart Button

This method draws:

- semi-transparent dark backdrop
- bordered result panel
- `GAME OVER` title
- final score
- hover-reactive restart button

It also updates `reset_btn_rect` each frame so click detection matches visual button position exactly.

---

## 17. Full Round Flow - Start to Death to Replay

```text
Scene enter
  -> __init__
  -> _reset_game
  -> _reset_round
  -> phase = playing

Every frame while playing:
  handle_events (buffer direction)
  update(dt)
    -> timer gate
    -> apply next_dir
    -> compute new head
    -> collision checks
    -> grow or move
  draw

On death:
  _die -> phase = dead
  draw shows overlay
  Enter/Space/click reset -> _reset_round
```

---

## 18. Testing - What and Why

Snake tests are intentionally logic-focused and headless-safe.

### What We Test vs What We Do Not

We test:

- state transitions
- movement timing
- collision correctness
- apple spawning/growth
- score behavior
- reset behavior

We do not test:

- pixel-perfect rendering
- font rasterization
- visual color gradients at image level

### Fixture Setup

`tests/test_snake.py` provides:

- `MockManager` to capture `switch_to` calls
- session-wide pygame init/quit fixture
- lightweight font fixture
- scene fixture creating a fresh `SnakeScene` per test
- helper `make_keydown` for event generation

### Test Classes Explained

- `TestSpawnApple`: spawn validity and full-board `None` path
- `TestSceneInit`: constructor/reset defaults
- `TestInput`: keyboard/mouse input and dead-phase replay controls
- `TestMovement`: tick gating and buffered turn application
- `TestCollisions`: wall hit, self hit, legal tail-entry case
- `TestAppleAndScore`: growth behavior and hi-score logic
- `TestResetAndLifecycle`: full-game reset and on-exit behavior

Together these tests lock down the gameplay contract without requiring a display window.

---

## 19. Running the Tests

```bash
# Snake-only tests
python -m pytest tests/test_snake.py -v

# Full suite
python -m pytest tests/ -v
```

For compact tracebacks:

```bash
python -m pytest tests/test_snake.py -v --tb=short
```
