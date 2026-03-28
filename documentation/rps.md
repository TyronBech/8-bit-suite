# Rock-Paper-Scissors — Implementation Deep Dive

---

## Table of Contents

- [Rock-Paper-Scissors — Implementation Deep Dive](#rock-paper-scissors--implementation-deep-dive)
  - [Table of Contents](#table-of-contents)
  - [1. The Complete File at a Glance](#1-the-complete-file-at-a-glance)
  - [2. Imports](#2-imports)
  - [3. `CHOICES` — The Game's Core Data](#3-choices--the-games-core-data)
  - [4. `load_rps_images()` — Loading the Pixel Art](#4-load_rps_images--loading-the-pixel-art)
  - [5. `get_winner()` — The Pure Logic Function](#5-get_winner--the-pure-logic-function)
  - [6. `RPSScene.__init__` — Setting Up the Scene](#6-rpsscene__init__--setting-up-the-scene)
    - [`on_exit()`](#on_exit)
  - [7. The Phase System — How the Game Flows](#7-the-phase-system--how-the-game-flows)
  - [8. `_reset_game()` and `_reset_round()` — Two Levels of Reset](#8-_reset_game-and-_reset_round--two-levels-of-reset)
  - [9. `handle_events()` — Reacting to Input](#9-handle_events--reacting-to-input)
  - [10. `update()` — Time-Based Logic](#10-update--time-based-logic)
  - [11. `draw()` — The Rendering Pipeline](#11-draw--the-rendering-pipeline)
  - [12. `_draw_border()` — The Outer Frame](#12-_draw_border--the-outer-frame)
  - [13. `_draw_header()` — The Terminal Bar](#13-_draw_header--the-terminal-bar)
  - [14. `_draw_cards()` — The Two Choice Cards](#14-_draw_cards--the-two-choice-cards)
  - [15. `_draw_single_card()` — One Card's Internals](#15-_draw_single_card--one-cards-internals)
  - [16. `_draw_footer()` — Score Bar and Clickable Abort](#16-_draw_footer--score-bar-and-clickable-abort)
  - [17. `_draw_result_overlay()` — The Win/Lose/Draw Screen](#17-_draw_result_overlay--the-winlosedraw-screen)
  - [18. The Full Round Flow — Start to Finish](#18-the-full-round-flow--start-to-finish)
  - [19. Testing — How and Why We Test](#19-testing--how-and-why-we-test)
    - [What Is a Test?](#what-is-a-test)
    - [Why Not Just Play the Game to Test?](#why-not-just-play-the-game-to-test)
    - [The Golden Rule — Don't Test pygame in Unit Tests](#the-golden-rule--dont-test-pygame-in-unit-tests)
    - [What We Test vs What We Don't](#what-we-test-vs-what-we-dont)
  - [20. Test Setup — Fixtures and MockManager](#20-test-setup--fixtures-and-mockmanager)
    - [What Is a Fixture?](#what-is-a-fixture)
    - [`MockManager` — Faking the SceneManager](#mockmanager--faking-the-scenemanager)
    - [The `pygame_init` Fixture](#the-pygame_init-fixture)
    - [The `fonts` Fixture](#the-fonts-fixture)
    - [The `scene` Fixture — Patching Image Loading](#the-scene-fixture--patching-image-loading)
    - [The `make_keydown` Helper](#the-make_keydown-helper)
  - [21. `TestGetWinner` — Testing Pure Logic](#21-testgetwinner--testing-pure-logic)
  - [22. `TestChoices` — Testing the Constant](#22-testchoices--testing-the-constant)
  - [23. `TestRPSSceneInit` — Testing Initial State](#23-testrpssceneinit--testing-initial-state)
  - [24. `TestChoiceCycling` — Testing Arrow Keys](#24-testchoicecycling--testing-arrow-keys)
  - [25. `TestConfirmChoice` — Testing the ENTER Key](#25-testconfirmchoice--testing-the-enter-key)
  - [26. `TestScoreTracking` — Testing Score Updates](#26-testscoretracking--testing-score-updates)
  - [27. `TestRevealTimer` — Testing the Timer](#27-testrevealtimer--testing-the-timer)
  - [28. `TestRevealingPhaseBlocksInput` — Testing Lockout](#28-testrevealingphaseblocksinput--testing-lockout)
  - [29. `TestResultPhase` — Testing Play Again and Exit](#29-testresultphase--testing-play-again-and-exit)
  - [30. `TestResetRound` and `TestResetGame` — Testing Resets](#30-testresetround-and-testresetgame--testing-resets)
  - [31. `TestOnExit` — Testing the Lifecycle Hook](#31-testonexit--testing-the-lifecycle-hook)
    - [Running the Tests](#running-the-tests)

---

## 1. The Complete File at a Glance

Before diving into each piece, here is the full `scenes/rps.py` so you can see how everything fits together:

```python
import pygame
import random
import os
from core.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_BORDER, COLOR_GREEN,
    COLOR_TITLE_YELLOW, COLOR_FOOTER, COLOR_LINE,
    COLOR_TERMINAL, COLOR_ONLINE,
    PLAYER_CARD_X, CPU_CARD_X, CARD_W, CARD_H, CARD_Y,
    COLOR_PLAYER_BORDER, COLOR_CPU_BORDER,
    COLOR_CARD_BG, COLOR_CARD_TEXT,
    RESULT_COLORS, RESULT_LABELS,
)

CHOICES = ["ROCK", "PAPER", "SCISSORS"]

def load_rps_images() -> dict[str, pygame.Surface]: ...
def get_winner(player: str, cpu: str) -> str: ...

class RPSScene(BaseScene):
    def __init__(self, manager, fonts): ...
    def on_exit(self): ...
    def _reset_game(self): ...
    def _reset_round(self): ...
    def handle_events(self, events): ...
    def update(self, dt): ...
    def draw(self, screen): ...
    def _draw_border(self, screen): ...
    def _draw_header(self, screen): ...
    def _draw_cards(self, screen): ...
    def _draw_single_card(self, screen, text, x, border_color, show_image=True): ...
    def _draw_footer(self, screen): ...
    def _draw_result_overlay(self, screen): ...
```

The file has two sections — **standalone functions** above the class, and **methods** inside the class. This split is intentional and important, explained below.

---

## 2. Imports

```python
import pygame
import random
import os
```

- **`pygame`** — the game library. Everything visual comes from here.
- **`random`** — used for one line: `random.choice(CHOICES)` to pick the CPU's move.
- **`os`** — used for one line: `os.path.join(...)` to build file paths safely across Windows/Mac/Linux.

```python
from core.base_scene import BaseScene
```

`RPSScene` inherits from `BaseScene`, which means it must implement `handle_events`, `update`, and `draw`. Think of it as a contract — `BaseScene` says *"any scene must have these three methods"*, and `RPSScene` fulfills that contract.

```python
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_TITLE_YELLOW,
    PLAYER_CARD_X, CPU_CARD_X, CARD_W, CARD_H, CARD_Y,
    COLOR_PLAYER_BORDER, COLOR_CPU_BORDER,
    RESULT_COLORS, RESULT_LABELS,
    # ... etc
)
```

All visual constants — positions, colors, sizes — live in `settings.py`. Importing them here means if you ever want to move a card or change a color, you change it in one file and it updates everywhere. Never hardcode numbers like `180` or `(52, 220, 100)` directly in your draw functions.

---

## 3. `CHOICES` — The Game's Core Data

```python
CHOICES = ["ROCK", "PAPER", "SCISSORS"]
```

A simple list of three strings. This list does three jobs:

**Job 1 — Cycling through options with the arrow keys:**
```python
self.player_index = (self.player_index + 1) % len(CHOICES)
```
`player_index` is a number: 0, 1, or 2. The `% len(CHOICES)` (modulo) makes it wrap around. When `player_index` is `2` (SCISSORS) and you press Right, `(2 + 1) % 3 = 0` — it jumps back to ROCK.

**Job 2 — Looking up the current choice:**
```python
player_text = CHOICES[self.player_index]  # e.g. "ROCK"
```

**Job 3 — Random CPU pick:**
```python
self.cpu_choice = random.choice(CHOICES)
```
`random.choice` picks a random element from any list. Clean and simple.

**Why uppercase?** The image files are named `rock.png`, `paper.png`, `scissors.png` (lowercase). The choices are stored uppercase. This intentional mismatch is handled by calling `.lower()` when looking up images — more on this in `_draw_single_card`.

---

## 4. `load_rps_images()` — Loading the Pixel Art

```python
def load_rps_images() -> dict[str, pygame.Surface]:
    names = ["rock", "paper", "scissors"]
    images = {}
    for name in names:
        path = os.path.join("assets", "images", f"{name}.png")
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (140, 140))
        images[name] = img
    return images
```

This function lives **outside the class** because it's a utility — it has no need to access `self`. It just loads files and returns a dictionary.

**Line by line:**

`os.path.join("assets", "images", f"{name}.png")`
Builds the path to each image. On Windows this produces `assets\images\rock.png`, on Mac/Linux it produces `assets/images/rock.png`. Always use `os.path.join` instead of manually writing slashes — it's the only correct cross-platform approach.

`pygame.image.load(path)`
Reads the PNG file from disk and creates a pygame Surface (a drawable image object).

`.convert_alpha()`
Converts the image into a pixel format that pygame can draw much faster, while keeping transparency intact. Your Canva images have transparent backgrounds — without `convert_alpha()`, the transparency would be lost or drawing would be slow. **Always call this after loading images with transparent areas.**

`pygame.transform.scale(img, (140, 140))`
Resizes the image to 140×140 pixels. The cards are 200×200 — the 30-pixel margin on each side gives the image breathing room inside the card border.

The result is a dictionary:
```python
{
    "rock":     <Surface 140x140>,
    "paper":    <Surface 140x140>,
    "scissors": <Surface 140x140>,
}
```

---

## 5. `get_winner()` — The Pure Logic Function

```python
def get_winner(player: str, cpu: str) -> str:
    if player == cpu:
        return "draw"
    wins = {("ROCK", "SCISSORS"), ("SCISSORS", "PAPER"), ("PAPER", "ROCK")}
    return "win" if (player, cpu) in wins else "lose"
```

This is arguably the most important function in the file — not because it's complicated, but because of **where it lives and what it doesn't touch**.

**It lives outside the class.** It takes two strings, returns a string. No `self`, no `screen`, no pygame at all. This makes it a **pure function** — given the same inputs, it always returns the same output, with no side effects.

**Why does this matter?** Because you can test it without running the game:

```python
# tests/test_rps.py
from scenes.rps import get_winner

def test_rock_beats_scissors():
    assert get_winner("ROCK", "SCISSORS") == "win"

def test_draw():
    assert get_winner("PAPER", "PAPER") == "draw"

def test_paper_loses_to_scissors():
    assert get_winner("PAPER", "SCISSORS") == "lose"
```

No window, no pygame init, no game loop. Just pure logic being verified.

**The `wins` set:**
```python
wins = {("ROCK", "SCISSORS"), ("SCISSORS", "PAPER"), ("PAPER", "ROCK")}
```

A **set of tuples**, where each tuple is `(winner, loser)`. Checking membership with `in` is instant — Python doesn't loop through all three, it checks a hash. So `("ROCK", "SCISSORS") in wins` is `True`, meaning Rock beats Scissors.

**The ternary on the last line:**
```python
return "win" if (player, cpu) in wins else "lose"
```
This reads as: *"if the player's combination is a winning one, return 'win', otherwise return 'lose'."* Since draws are already handled at the top, at this point we know the choices are different — so it's either a win or a loss.

---

## 6. `RPSScene.__init__` — Setting Up the Scene

```python
class RPSScene(BaseScene):
    def __init__(self, manager, fonts):
        super().__init__(manager)
        self.fonts = fonts
        self.images = load_rps_images()
        self._reset_game()
```

`super().__init__(manager)` calls `BaseScene`'s constructor, which sets `self.manager`. This is what gives you the ability to call `self.manager.switch_to("menu")` anywhere in the scene. Never skip this line.

`self.images = load_rps_images()` — images are loaded once here and stored. If you loaded images inside `draw()`, they'd reload from disk 60 times per second — extremely slow. Load once, reuse forever.

`self._reset_game()` — rather than setting every variable here manually, the constructor delegates to `_reset_game()`. This means the initialization logic lives in one place, and both "starting fresh" and "reset on exit" use the same code.

### `on_exit()`

```python
def on_exit(self) -> None:
    self._reset_game()
```

Called automatically by `SceneManager._set_current_scene()` when leaving this scene. By resetting the full game state here, returning from the menu and selecting RPS again always starts with `P1 0 - CPU 0`. Without this, scores would carry over between visits.

---

## 7. The Phase System — How the Game Flows

The entire RPS game revolves around one variable: `self.phase`. It's a string that can be one of three values:

```
"choosing"  →  "revealing"  →  "result"
     ↑                              │
     └──────────── ENTER ───────────┘
```

| Phase | What the Player Sees | What Input Does |
|---|---|---|
| `"choosing"` | Player card shows current choice, CPU card shows `?` | ← → changes choice, Enter confirms |
| `"revealing"` | Both cards shown, no overlay | Nothing (1.5 second auto-timer) |
| `"result"` | Both cards shown + WIN/LOSE/DRAW overlay | Enter resets round, Escape goes to menu |

**Why three phases instead of two?**

Without `"revealing"`, pressing Enter would instantly show the result overlay. The player would never get a satisfying moment of seeing both choices side by side before the verdict. The reveal phase creates **tension** — you see the CPU's choice and have a split second to react before the result appears. This is pure game feel.

---

## 8. `_reset_game()` and `_reset_round()` — Two Levels of Reset

```python
def _reset_game(self):
    """Reset the full game state, including scores."""
    self.player_score = 0
    self.cpu_score = 0
    self._reset_round()

def _reset_round(self):
    """Reset the round state to start a new game."""
    self.player_index = 0
    self.player_choice = None
    self.cpu_choice = None
    self.result = None
    self.phase = "choosing"
    self.reveal_timer = 0.0
    self.abort_rect = pygame.Rect(28, SCREEN_HEIGHT - 52, 120, 30)
```

Two functions because there are two different situations:

- **`_reset_game()`** — called when leaving the scene entirely (`on_exit`). Wipes scores so the next session starts clean.
- **`_reset_round()`** — called when pressing Enter after a result. Keeps the scores, just clears the round choices. `_reset_game` calls this too, so no duplication.

**`abort_rect` is initialized here** rather than in `__init__` because `_reset_round` is called every round, ensuring the clickable area is always correctly positioned. It's a `pygame.Rect(x, y, width, height)` — a rectangle that both `_draw_footer` and `handle_events` reference. Storing it as `self.abort_rect` means both methods share the exact same region definition.

**The underscore prefix** on `_reset_game` and `_reset_round` is a Python convention signaling *"this is an internal method — don't call it from outside the class."* It's not enforced by Python, but it communicates intent.

---

## 9. `handle_events()` — Reacting to Input

```python
def handle_events(self, events):
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
```

**The outer loop** — `events` is a list of everything that happened since the last frame. You iterate through all of them so nothing gets missed.

**Phase-gated input** — input is only accepted in certain phases. During `"revealing"`, nothing is inside that phase's block, so all key presses are silently ignored. This prevents the player from skipping the reveal animation.

**What happens on Enter (choosing phase):**
```python
self.player_choice = CHOICES[self.player_index]   # lock in player's pick
self.cpu_choice = random.choice(CHOICES)           # CPU picks randomly
self.result = get_winner(...)                      # evaluate who won
if self.result == "win": self.player_score += 1    # update score NOW
self.phase = "revealing"                           # start reveal timer
self.reveal_timer = 0.0                            # reset timer
```

**Scores are updated here**, not when the overlay appears. This is important — the score reflects the actual outcome, which is determined the moment Enter is pressed, not when the player sees the overlay.

**`pygame.MOUSEBUTTONUP` vs `MOUSEBUTTONDOWN`** — clicks are detected on button *release*, not press. This matches how real UI works: a button activates when you lift your finger, not when you press down. It also feels better because if you accidentally click, you can move your mouse away before releasing to cancel.

**`event.pos`** — for mouse events, `event.pos` is a tuple `(x, y)` of where the mouse was when the event fired. `abort_rect.collidepoint(event.pos)` checks if that position is inside the abort button rectangle.

---

## 10. `update()` — Time-Based Logic

```python
def update(self, dt):
    if self.phase == "revealing":
        self.reveal_timer += dt
        if self.reveal_timer >= 1.5:
            self.phase = "result"
```

`update` is called every frame with `dt` — the number of seconds since the last frame (typically `0.016` at 60 FPS).

**`self.reveal_timer += dt`** accumulates time. After 1.5 seconds of accumulated time, the phase advances to `"result"` and the overlay appears.

**Why use time instead of frames?** If you counted `90 frames` instead, the delay would be 1.5 seconds on a 60Hz monitor but only 0.75 seconds on a 120Hz monitor. Using `dt` makes the delay exactly 1.5 seconds regardless of frame rate.

---

## 11. `draw()` — The Rendering Pipeline

```python
def draw(self, screen):
    screen.fill(COLOR_BG)
    self._draw_border(screen)
    self._draw_header(screen)
    self._draw_cards(screen)
    self._draw_footer(screen)
    if self.phase == "result":
        self._draw_result_overlay(screen)
```

`draw` is called every frame. It always draws everything from scratch — background, border, header, cards, footer — and then conditionally adds the overlay on top.

**The order matters.** pygame draws like a painter — later calls paint over earlier ones. The background must be first (otherwise old frames show through). The overlay must be last (otherwise cards would draw over it).

**`screen.fill(COLOR_BG)`** — clears the entire screen to the background color before drawing anything. Without this, previous frames would bleed through.

The method is deliberately short. Each visual element is delegated to a private method. This makes `draw` read like a table of contents — you can understand what's on screen just by reading the method names.

---

## 12. `_draw_border()` — The Outer Frame

```python
def _draw_border(self, screen):
    pygame.draw.rect(
        screen, COLOR_BORDER,
        pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30), 4
    )
```

`pygame.draw.rect(surface, color, rect, width)` — draws a rectangle.
- Without `width` (or `width=0`): fills the rectangle solid
- With `width=4`: draws only the border, 4 pixels thick

`pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30)` — a rectangle inset 15 pixels from each edge of the window, creating the terminal-style frame seen around the whole game.

---

## 13. `_draw_header()` — The Terminal Bar

```python
def _draw_header(self, screen):
    prompt = self.fonts["tiny"].render(
        "> root@8bit-suite:~$ ./rps.sh", False, COLOR_TERMINAL
    )
    screen.blit(prompt, (28, 32))

    online = self.fonts["tiny"].render("ONLINE", False, COLOR_ONLINE)
    screen.blit(online, (SCREEN_WIDTH - online.get_width() - 30, 32))

    pygame.draw.line(screen, COLOR_LINE, (25, 55), (SCREEN_WIDTH - 28, 55), 2)

    title = self.fonts["small"].render(
        "BATTLE IN PROGRESS", False, COLOR_TITLE_YELLOW
    )
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 80))
```

**`font.render(text, antialias, color)`** — converts a string into a pygame Surface (an image of that text). The second argument `False` disables antialiasing — keeping the hard pixel edges of the bitmap font, which is what gives it the retro 8-bit look.

**`screen.blit(surface, (x, y))`** — draws a surface onto another surface at position `(x, y)`. This is how all text and images appear on screen in pygame.

**Centering the ONLINE text on the right:**
```python
screen.blit(online, (SCREEN_WIDTH - online.get_width() - 30, 32))
```
The text starts at `SCREEN_WIDTH - text_width - 30`. This places the right edge of the text 30 pixels from the right edge of the window, regardless of how wide the text is.

**Centering the title:**
```python
(SCREEN_WIDTH - title.get_width()) // 2
```
The standard centering formula: total width minus text width gives leftover space. Half of that is the left margin needed to center the text.

---

## 14. `_draw_cards()` — The Two Choice Cards

```python
def _draw_cards(self, screen):
    # Draw labels above each card
    for label_text, card_x in [("PLAYER 1", PLAYER_CARD_X), ("CPU", CPU_CARD_X)]:
        lbl = self.fonts["smaller"].render(label_text, False, (180, 180, 180))
        screen.blit(lbl, (card_x + (CARD_W - lbl.get_width()) // 2, CARD_Y - 30))

    if self.phase == "choosing":
        player_text = CHOICES[self.player_index]
        self._draw_single_card(screen, player_text, PLAYER_CARD_X, COLOR_PLAYER_BORDER)
        self._draw_single_card(screen, "?", CPU_CARD_X, COLOR_CPU_BORDER, show_image=False)

    elif self.phase in ("revealing", "result"):
        self._draw_single_card(screen, self.player_choice, PLAYER_CARD_X, COLOR_PLAYER_BORDER)
        self._draw_single_card(screen, self.cpu_choice, CPU_CARD_X, COLOR_CPU_BORDER)

    # VS between cards
    vs = self.fonts["small"].render("VS", False, (200, 60, 60))
    screen.blit(vs, (
        (SCREEN_WIDTH - vs.get_width()) // 2,
        CARD_Y + (CARD_H - vs.get_height()) // 2
    ))
```

The label loop handles both labels with one loop — each iteration gets the label text and its card's X position as a tuple, avoiding code duplication.

**The phase check controls what each card shows:**

- `"choosing"` → Player shows their currently highlighted choice. CPU shows `?` with `show_image=False` — the image is hidden.
- `"revealing"` / `"result"` → Both cards show actual choices with images.

The CPU card's `?` is the moment of tension — it's hidden while you're deciding, then revealed the moment you lock in your choice.

---

## 15. `_draw_single_card()` — One Card's Internals

```python
def _draw_single_card(self, screen, text, x, border_color, show_image=True):
    rect = pygame.Rect(x, CARD_Y, CARD_W, CARD_H)
    pygame.draw.rect(screen, COLOR_CARD_BG, rect)      # dark fill
    pygame.draw.rect(screen, border_color, rect, 3)    # colored border

    if show_image and text.lower() in self.images:
        img = self.images[text.lower()]
        img_x = x + (CARD_W - img.get_width()) // 2
        img_y = CARD_Y + (CARD_H - img.get_height()) // 2
        screen.blit(img, (img_x, img_y))
    else:
        label = self.fonts["small"].render(text, False, COLOR_CARD_TEXT)
        screen.blit(label, (
            x + (CARD_W - label.get_width()) // 2,
            CARD_Y + (CARD_H - label.get_height()) // 2
        ))
```

**`show_image=True`** is a default argument. When you call the function without specifying it, it defaults to `True`. Passing `show_image=False` explicitly skips the image and draws text instead — used for the CPU's `?` card.

**`text.lower()`** — this is the fix for the original bug. `CHOICES` stores `"ROCK"` but `self.images` has keys `"rock"`. Without `.lower()`, `"ROCK" in self.images` is `False` and it falls through to the text fallback. With `.lower()`, `"rock" in self.images` correctly finds the image.

**The centering math for the image:**
```python
img_x = x + (CARD_W - img.get_width()) // 2
img_y = CARD_Y + (CARD_H - img.get_height()) // 2
```
The card's top-left corner is at `(x, CARD_Y)`. The image is 140px, the card is 200px — so there's 60px of leftover space. Half of that is 30px. The image starts 30px from the card's left edge and 30px from its top edge, landing it perfectly centered.

**Two `pygame.draw.rect` calls:**
```python
pygame.draw.rect(screen, COLOR_CARD_BG, rect)     # filled rectangle (no width arg)
pygame.draw.rect(screen, border_color, rect, 3)   # border only (width=3)
```
The first fills the card background. The second draws the colored border on top. The border color is passed in — green for the player card, blue for the CPU card — making the same function work for both cards.

---

## 16. `_draw_footer()` — Score Bar and Clickable Abort

```python
def _draw_footer(self, screen):
    pygame.draw.line(
        screen, COLOR_LINE,
        (25, SCREEN_HEIGHT - 65), (SCREEN_WIDTH - 28, SCREEN_HEIGHT - 65), 2
    )
    footer_y = SCREEN_HEIGHT - 48

    mx, my = pygame.mouse.get_pos()
    abort_color = COLOR_GREEN if self.abort_rect.collidepoint(mx, my) else COLOR_FOOTER

    abort = self.fonts["smaller"].render("< ABORT", False, abort_color)
    score = self.fonts["smaller"].render(
        f"SCORE:  P1 {self.player_score}  -  CPU {self.cpu_score}",
        False, COLOR_FOOTER
    )
    screen.blit(abort, (28, footer_y))
    screen.blit(score, (SCREEN_WIDTH - score.get_width() - 28, footer_y))
```

**The separator line:**
`pygame.draw.line(surface, color, start_pos, end_pos, width)` — draws a straight line between two points.

**Hover detection:**
```python
mx, my = pygame.mouse.get_pos()
abort_color = COLOR_GREEN if self.abort_rect.collidepoint(mx, my) else COLOR_FOOTER
```
`pygame.mouse.get_pos()` returns the current mouse position every frame. `abort_rect.collidepoint(mx, my)` returns `True` if that position is inside the abort rectangle. This runs every frame inside `draw`, so the color updates instantly as you move the mouse — no event needed.

**`self.abort_rect`** is defined in `_reset_round()` and shared between `_draw_footer` and `handle_events`. Both methods refer to the same rectangle, so the clickable area and the visual text are always perfectly aligned.

**The f-string score:**
```python
f"SCORE:  P1 {self.player_score}  -  CPU {self.cpu_score}"
```
f-strings embed variables directly into strings. `{self.player_score}` is replaced by the actual number. This re-renders every frame, so the score always reflects the current state.

---

## 17. `_draw_result_overlay()` — The Win/Lose/Draw Screen

```python
def _draw_result_overlay(self, screen):
    overlay = pygame.Surface((500, 200), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    ox = (SCREEN_WIDTH - 500) // 2
    oy = (SCREEN_HEIGHT - 200) // 2
    screen.blit(overlay, (ox, oy))

    if self.result is None:
        return
    color = RESULT_COLORS[self.result]
    label = RESULT_LABELS[self.result]
    result_surf = self.fonts["small"].render(label, False, color)
    screen.blit(result_surf, (
        (SCREEN_WIDTH - result_surf.get_width()) // 2, oy + 30
    ))

    btn_rect = pygame.Rect(ox + 60, oy + 110, 380, 50)
    pygame.draw.rect(screen, COLOR_TITLE_YELLOW, btn_rect, 3)
    btn_text = self.fonts["smaller"].render(
        "PRESS ENTER TO PLAY AGAIN", False, COLOR_TITLE_YELLOW
    )
    screen.blit(btn_text, (
        (SCREEN_WIDTH - btn_text.get_width()) // 2, oy + 125
    ))
```

**`pygame.Surface((500, 200), pygame.SRCALPHA)`** — creates a blank surface 500×200 pixels. The `pygame.SRCALPHA` flag is critical — without it, the surface cannot support transparency.

**`overlay.fill((0, 0, 0, 200))`** — fills with RGBA color. The four values are Red, Green, Blue, Alpha. Alpha `200` out of `255` means ~78% opaque. You can see the cards dimly through the overlay — it darkens them but doesn't fully hide them.

**`ox` and `oy`** — the top-left corner of the overlay, calculated to center it on screen using the same centering formula.

**`RESULT_COLORS` and `RESULT_LABELS`** are dictionaries defined in `settings.py`:
```python
RESULT_COLORS = {"win": (52, 220, 100), "lose": (220, 60, 60), "draw": (180, 180, 180)}
RESULT_LABELS = {"win": "YOU WIN!", "lose": "CPU WINS!", "draw": "DRAW!"}
```
`self.result` is `"win"`, `"lose"`, or `"draw"` — using it as a dictionary key retrieves the correct color and label in one clean line.

**`if self.result is None: return`** — a safety guard. During `"revealing"` phase the overlay isn't shown, but if somehow `_draw_result_overlay` were called with `self.result` not yet set, this prevents a `KeyError` crash.

---

## 18. The Full Round Flow — Start to Finish

Here is exactly what happens during one complete round:

```
Game starts
    │
    ├─ __init__ called
    ├─ images loaded once
    ├─ _reset_game() → _reset_round()
    │   phase = "choosing", player_index = 0
    │
    │  [Every frame]
    ├─ handle_events: LEFT/RIGHT changes player_index
    ├─ update: nothing (phase is "choosing")
    └─ draw: player card shows CHOICES[player_index], CPU shows "?"
    │
    │  [Player presses ENTER]
    │
    ├─ player_choice = CHOICES[player_index]   e.g. "ROCK"
    ├─ cpu_choice = random.choice(CHOICES)     e.g. "SCISSORS"
    ├─ result = get_winner("ROCK","SCISSORS")  → "win"
    ├─ player_score += 1
    ├─ phase = "revealing"
    └─ reveal_timer = 0.0
    │
    │  [Next 1.5 seconds — every frame]
    ├─ handle_events: all key input ignored (no "revealing" block)
    ├─ update: reveal_timer += dt → when >= 1.5, phase = "result"
    └─ draw: both cards shown with images, no overlay
    │
    │  [reveal_timer hits 1.5s]
    │  phase = "result"
    │
    │  [Every frame]
    ├─ handle_events: ENTER → _reset_round(), ESCAPE → menu
    ├─ update: nothing
    └─ draw: both cards + dark overlay + "YOU WIN!" + "PLAY AGAIN" button
    │
    │  [Player presses ENTER]
    │
    └─ _reset_round() called
        player_choice = None, cpu_choice = None
        result = None, phase = "choosing"
        player_index = 0, reveal_timer = 0.0
        scores preserved ✓
        → Back to the top
```

---

*The implementation is complete. The next section covers how to verify it all works correctly with automated tests.*

---

## 19. Testing — How and Why We Test

### What Is a Test?

A test is a piece of code that calls your code and checks that the result is what you expected. If the result is wrong, the test fails and tells you exactly which check broke.

```python
def test_rock_beats_scissors():
    assert get_winner("ROCK", "SCISSORS") == "win"
```

This test calls `get_winner` with two known inputs and asserts the output is `"win"`. If you accidentally broke the win logic, this test fails immediately — instead of you having to manually play the game to notice.

### Why Not Just Play the Game to Test?

Manual testing has three problems:

1. **It's slow.** Every time you change code, you have to relaunch, navigate to RPS, play several rounds, and hope you hit the right combinations.
2. **It's incomplete.** You probably won't test every single combination of Rock/Paper/Scissors every time.
3. **It's unreliable.** You might miss a bug if you forget to test a specific case.

Automated tests fix all three — they run in seconds, cover every case, and run identically every time.

### The Golden Rule — Don't Test pygame in Unit Tests

Your test file **never opens a window**. It never calls `pygame.display.set_mode` with a real size, never renders to a screen. Why? Because:

- Tests need to run in CI (automated servers with no monitor)
- Tests need to run headlessly on any machine
- Opening windows in tests makes them slow and fragile

The trick is to initialize pygame with a tiny hidden display:
```python
pygame.display.set_mode((1, 1), pygame.NOFRAME)
```
This satisfies pygame's requirement that a display exists, without ever showing a window.

### What We Test vs What We Don't

| ✅ We test | ❌ We don't test |
|---|---|
| `get_winner` logic | Pixel colors on screen |
| Phase transitions | Font rendering |
| Score updates | Image positioning |
| Input handling | Visual layout |
| Reset behavior | Mouse hover color |

The rule: test **behavior and state**, not **visual output**.

---

## 20. Test Setup — Fixtures and MockManager

Before any test can run, we need three things: pygame initialized, a fake manager, and a fake scene. Pytest **fixtures** provide these automatically.

### What Is a Fixture?

A fixture is a function that sets up something a test needs. Instead of writing setup code in every test, you write it once as a fixture and pytest injects it wherever it's needed.

```python
@pytest.fixture
def manager():
    return MockManager()
```

Any test that lists `manager` as a parameter gets a fresh `MockManager` automatically.

### `MockManager` — Faking the SceneManager

```python
class MockManager:
    """Minimal stand-in for SceneManager used by RPSScene."""

    def __init__(self):
        self.current_scene: str | None = None

    def switch_to(self, key: str) -> None:
        self.current_scene = key
```

`RPSScene` only ever calls one thing on its manager: `self.manager.switch_to("menu")`. So `MockManager` only needs to implement `switch_to`. Instead of actually switching scenes, it just records which scene was requested in `self.current_scene`. Tests can then check:

```python
assert manager.current_scene == "menu"
```

This is the **Mock pattern** — replace a complex dependency with a simple fake that records what was called.

### The `pygame_init` Fixture

```python
@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield
    pygame.quit()
```

- `scope="session"` — runs once for the entire test session, not once per test. pygame only needs to start and stop once.
- `autouse=True` — runs automatically for every test without needing to be listed as a parameter.
- `yield` — everything before `yield` is setup, everything after is teardown. `pygame.quit()` runs after all tests finish.

### The `fonts` Fixture

```python
@pytest.fixture
def fonts():
    font = pygame.font.SysFont(None, 16)
    return {
        "title": font, "small": font,
        "smaller": font, "tiny": font, "menu": font,
    }
```

`RPSScene.__init__` requires a fonts dictionary. Instead of loading the real `PressStart2P` font file, we use `SysFont(None, 16)` — pygame's built-in default font. It's fast, always available, and the tests don't care what the font looks like.

### The `scene` Fixture — Patching Image Loading

```python
@pytest.fixture
def scene(manager, fonts, monkeypatch):
    import scenes.rps as rps_module

    dummy_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
    monkeypatch.setattr(
        rps_module,
        "load_rps_images",
        lambda: {name: dummy_surface for name in ["rock", "paper", "scissors"]},
    )
    return RPSScene(manager, fonts)
```

The problem: `RPSScene.__init__` calls `load_rps_images()`, which tries to open PNG files from `assets/images/`. Those files don't exist in the test environment.

The solution: `monkeypatch.setattr` replaces `load_rps_images` with a lambda that returns three tiny 1×1 dummy surfaces. The scene gets a valid `self.images` dictionary, no files are touched, and tests run instantly.

`monkeypatch` is a built-in pytest fixture — you never have to import it. Any fixture or test can request it as a parameter.

### The `make_keydown` Helper

```python
def make_keydown(key: int) -> pygame.event.Event:
    """Helper — create a KEYDOWN event for the given key constant."""
    return pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")
```

`handle_events` receives a list of pygame events. To test it, we need to create fake events. `pygame.event.Event(type, **attrs)` creates an event with any attributes you specify. `mod=0` means no modifier keys (Shift/Ctrl/Alt), `unicode=""` is the character representation.

Usage in tests:
```python
scene.handle_events([make_keydown(pygame.K_RIGHT)])
```

---

## 21. `TestGetWinner` — Testing Pure Logic

```python
class TestGetWinner:
    def test_rock_beats_scissors(self):
        assert get_winner("ROCK", "SCISSORS") == "win"

    def test_scissors_beats_paper(self):
        assert get_winner("SCISSORS", "PAPER") == "win"

    def test_paper_beats_rock(self):
        assert get_winner("PAPER", "ROCK") == "win"

    def test_scissors_loses_to_rock(self):
        assert get_winner("SCISSORS", "ROCK") == "lose"

    def test_paper_loses_to_scissors(self):
        assert get_winner("PAPER", "SCISSORS") == "lose"

    def test_rock_loses_to_paper(self):
        assert get_winner("ROCK", "PAPER") == "lose"

    def test_rock_draw(self):
        assert get_winner("ROCK", "ROCK") == "draw"

    def test_paper_draw(self):
        assert get_winner("PAPER", "PAPER") == "draw"

    def test_scissors_draw(self):
        assert get_winner("SCISSORS", "SCISSORS") == "draw"

    @pytest.mark.parametrize("player", CHOICES)
    @pytest.mark.parametrize("cpu", CHOICES)
    def test_always_returns_valid_value(self, player, cpu):
        assert get_winner(player, cpu) in {"win", "lose", "draw"}
```

All nine match-ups are tested explicitly — three wins, three losses, three draws. This covers the entire truth table.

**The parametrize test** is the most interesting one:

```python
@pytest.mark.parametrize("player", CHOICES)
@pytest.mark.parametrize("cpu", CHOICES)
def test_always_returns_valid_value(self, player, cpu):
    assert get_winner(player, cpu) in {"win", "lose", "draw"}
```

`@pytest.mark.parametrize` makes pytest run the test multiple times with different values. Two nested parametrize decorators with 3 values each = **9 automatic test runs** — one for every combination of player and cpu. This is the same as writing nine separate tests but in two lines.

---

## 22. `TestChoices` — Testing the Constant

```python
class TestChoices:
    def test_choices_has_three_items(self):
        assert len(CHOICES) == 3

    def test_choices_are_uppercase(self):
        for choice in CHOICES:
            assert choice == choice.upper()

    def test_choices_contains_expected_values(self):
        assert set(CHOICES) == {"ROCK", "PAPER", "SCISSORS"}
```

These tests protect against accidental changes to `CHOICES`. If someone adds a fourth choice or changes casing, these tests catch it immediately. The uppercase test matters because `get_winner` and the image lookup both depend on consistent casing.

---

## 23. `TestRPSSceneInit` — Testing Initial State

```python
class TestRPSSceneInit:
    def test_starts_in_choosing_phase(self, scene):
        assert scene.phase == "choosing"

    def test_scores_start_at_zero(self, scene):
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_player_index_starts_at_zero(self, scene):
        assert scene.player_index == 0

    def test_choices_start_as_none(self, scene):
        assert scene.player_choice is None
        assert scene.cpu_choice is None

    def test_result_starts_as_none(self, scene):
        assert scene.result is None

    def test_reveal_timer_starts_at_zero(self, scene):
        assert scene.reveal_timer == 0.0
```

These verify the scene initializes cleanly. If you add a new variable to `_reset_round` or `__init__` but forget to set a default value, one of these tests will fail.

Notice each test uses `scene` as a parameter — pytest sees this and injects the `scene` fixture automatically, giving each test a fresh scene.

---

## 24. `TestChoiceCycling` — Testing Arrow Keys

```python
class TestChoiceCycling:
    def test_right_arrow_advances_index(self, scene):
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.player_index == 1

    def test_left_arrow_decrements_index(self, scene):
        scene.player_index = 1
        scene.handle_events([make_keydown(pygame.K_LEFT)])
        assert scene.player_index == 0

    def test_right_wraps_from_last_to_first(self, scene):
        scene.player_index = len(CHOICES) - 1   # SCISSORS (index 2)
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.player_index == 0           # wraps to ROCK

    def test_left_wraps_from_first_to_last(self, scene):
        scene.player_index = 0                   # ROCK
        scene.handle_events([make_keydown(pygame.K_LEFT)])
        assert scene.player_index == len(CHOICES) - 1   # wraps to SCISSORS

    def test_cycling_does_not_change_phase(self, scene):
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.phase == "choosing"
```

The wrap-around tests are the critical ones — they verify the modulo arithmetic works in both directions. Without the `% len(CHOICES)`, going left from index 0 would give `-1` (an invalid index), and going right from index 2 would give `3` (out of range).

The last test confirms that cycling choices doesn't accidentally trigger a phase change — a side-effect bug that would be easy to introduce.

---

## 25. `TestConfirmChoice` — Testing the ENTER Key

```python
class TestConfirmChoice:
    def test_enter_sets_player_choice(self, scene):
        scene.player_index = 0   # ROCK
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_choice == "ROCK"

    def test_enter_sets_cpu_choice(self, scene):
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.cpu_choice in CHOICES

    def test_enter_sets_result(self, scene):
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.result in {"win", "lose", "draw"}

    def test_enter_transitions_to_revealing(self, scene):
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "revealing"

    def test_enter_resets_reveal_timer(self, scene):
        scene.reveal_timer = 99.0
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.reveal_timer == 0.0
```

Each test checks one specific thing that ENTER should do. Splitting them into separate tests means that when something breaks, you know *exactly* which effect of the ENTER key failed.

`test_enter_sets_cpu_choice` uses `in CHOICES` because `random.choice` means we can't predict the exact value — but we know it must be one of the three valid choices.

`test_enter_resets_reveal_timer` pre-sets `reveal_timer = 99.0` to prove the timer is reset to zero — not just "happens to be zero because it hasn't been used yet".

---

## 26. `TestScoreTracking` — Testing Score Updates

```python
class TestScoreTracking:
    def test_win_increments_player_score(self, scene, monkeypatch):
        monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "win")
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_score == 1
        assert scene.cpu_score == 0

    def test_lose_increments_cpu_score(self, scene, monkeypatch):
        monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "lose")
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.cpu_score == 1
        assert scene.player_score == 0

    def test_draw_does_not_change_scores(self, scene, monkeypatch):
        monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "draw")
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_score == 0
        assert scene.cpu_score == 0
```

The problem: `handle_events` calls `random.choice` for the CPU pick, making the result unpredictable. We need a win to test win-score logic, but we can't guarantee a win with random choices.

The solution: `monkeypatch.setattr("scenes.rps.get_winner", lambda p, c: "win")` replaces `get_winner` *inside the `scenes.rps` module* with a lambda that always returns `"win"`. Now the outcome is completely controlled, and the test always passes for the right reason.

This is **dependency injection via patching** — you swap out a dependency to isolate the thing you're actually testing (score update logic) from the thing you're not testing (winner determination).

---

## 27. `TestRevealTimer` — Testing the Timer

```python
class TestRevealTimer:
    def test_revealing_advances_timer(self, scene):
        scene.phase = "revealing"
        scene.update(0.5)
        assert scene.reveal_timer == pytest.approx(0.5)

    def test_revealing_transitions_to_result_after_1_5s(self, scene):
        scene.phase = "revealing"
        scene.update(1.5)
        assert scene.phase == "result"

    def test_timer_does_not_advance_in_choosing_phase(self, scene):
        scene.phase = "choosing"
        scene.update(1.0)
        assert scene.reveal_timer == 0.0

    def test_timer_does_not_advance_in_result_phase(self, scene):
        scene.phase = "result"
        scene.result = "win"
        scene.reveal_timer = 0.0
        scene.update(1.0)
        assert scene.reveal_timer == 0.0
```

**`pytest.approx`** — floating point numbers can't be compared exactly. `0.1 + 0.2` in Python is `0.30000000000000004`, not `0.3`. `pytest.approx(0.5)` checks that the value is *close enough* to `0.5` (within a tiny tolerance). Always use `pytest.approx` when comparing floats.

The last two tests verify the timer **only advances in the right phase**. Directly setting `scene.phase = "choosing"` before calling `update` is valid in tests — you're setting up a specific scenario to test one behavior.

---

## 28. `TestRevealingPhaseBlocksInput` — Testing Lockout

```python
class TestRevealingPhaseBlocksInput:
    def test_right_arrow_ignored_during_revealing(self, scene):
        scene.phase = "revealing"
        scene.player_index = 0
        scene.handle_events([make_keydown(pygame.K_RIGHT)])
        assert scene.player_index == 0   # unchanged

    def test_enter_ignored_during_revealing(self, scene):
        scene.phase = "revealing"
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "revealing"   # still revealing
```

These test the *absence* of behavior — proving that during the reveal animation, input is completely locked out. This is just as important as testing that input *works* in other phases.

---

## 29. `TestResultPhase` — Testing Play Again and Exit

```python
class TestResultPhase:
    def _put_in_result(self, scene):
        """Helper — fast-forward scene to result phase."""
        scene.phase = "result"
        scene.player_choice = "ROCK"
        scene.cpu_choice = "SCISSORS"
        scene.result = "win"
        scene.player_score = 1

    def test_enter_resets_round_in_result(self, scene):
        self._put_in_result(scene)
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.phase == "choosing"
        assert scene.player_choice is None
        assert scene.cpu_choice is None
        assert scene.result is None

    def test_enter_preserves_scores_on_reset(self, scene):
        self._put_in_result(scene)
        scene.handle_events([make_keydown(pygame.K_RETURN)])
        assert scene.player_score == 1   # score kept

    def test_escape_switches_to_menu_from_result(self, scene, manager):
        self._put_in_result(scene)
        scene.handle_events([make_keydown(pygame.K_ESCAPE)])
        assert manager.current_scene == "menu"
```

`_put_in_result` is a **helper method** inside the test class — a private function used only by the tests in this class to avoid repeating setup code. It's not a test itself (it doesn't start with `test_`).

`test_enter_preserves_scores_on_reset` is the most important test in this class — it verifies the key design decision that scores survive round resets. If someone accidentally calls `_reset_game` instead of `_reset_round`, this test catches it.

`test_escape_switches_to_menu_from_result` uses the `manager` fixture to check that `switch_to("menu")` was actually called — this is where `MockManager.current_scene` pays off.

---

## 30. `TestResetRound` and `TestResetGame` — Testing Resets

```python
class TestResetRound:
    def test_reset_round_clears_choices(self, scene):
        scene.player_choice = "ROCK"
        scene.cpu_choice = "SCISSORS"
        scene._reset_round()
        assert scene.player_choice is None
        assert scene.cpu_choice is None

    def test_reset_round_preserves_scores(self, scene):
        scene.player_score = 3
        scene.cpu_score = 2
        scene._reset_round()
        assert scene.player_score == 3
        assert scene.cpu_score == 2


class TestResetGame:
    def test_reset_game_zeroes_scores(self, scene):
        scene.player_score = 5
        scene.cpu_score = 3
        scene._reset_game()
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_reset_game_also_resets_round(self, scene):
        scene.player_choice = "PAPER"
        scene.phase = "result"
        scene._reset_game()
        assert scene.player_choice is None
        assert scene.phase == "choosing"
```

These tests call the private methods `_reset_round()` and `_reset_game()` directly. In pytest you can call private methods from tests — the underscore convention is a hint to developers, not a hard restriction.

Pre-setting values before calling the reset (`scene.player_score = 5`) is intentional — it proves the reset actively changes the value, not just that the value happens to already be zero.

---

## 31. `TestOnExit` — Testing the Lifecycle Hook

```python
class TestOnExit:
    def test_on_exit_resets_scores(self, scene):
        scene.player_score = 4
        scene.cpu_score = 2
        scene.on_exit()
        assert scene.player_score == 0
        assert scene.cpu_score == 0

    def test_on_exit_resets_phase(self, scene):
        scene.phase = "result"
        scene.on_exit()
        assert scene.phase == "choosing"
```

`on_exit` is called by the `SceneManager` whenever you leave the RPS scene. These tests verify that leaving the scene fully resets everything — so returning later always starts fresh. Without this, a player could leave mid-game and return to a broken state.

---

### Running the Tests

```bash
# Run all RPS tests
python -m pytest tests/test_rps.py -v

# Run only a specific class
python -m pytest tests/test_rps.py::TestGetWinner -v

# Run a single test
python -m pytest tests/test_rps.py::TestScoreTracking::test_win_increments_player_score -v

# Show a summary of passed/failed counts
python -m pytest tests/test_rps.py -v --tb=short
```

The `-v` flag means **verbose** — it prints each test name and whether it passed or failed, rather than just a dot per test.

---

*End of document. With implementation and tests complete, the RPS game is fully verified and ready. The same patterns — pure logic function, phase system, MockManager, monkeypatch — apply directly to the next game: Tic-Tac-Toe.*
