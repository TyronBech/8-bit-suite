# 8-Bit Suite — Code Walkthrough

A personal reference guide explaining how every part of the menu system works.
Written to be read top-to-bottom, or jumped into at any section.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [core/settings.py — All Constants & Config](#2-coresettingspy)
3. [scenes/menu.py — Everything Visual](#3-scenesmenupy)
   - [draw_centered_text](#31-draw_centered_text--the-reusable-helper)
   - [draw_border](#32-draw_border)
   - [draw_title](#33-draw_title--drop-shadow-effect)
   - [draw_text](#34-draw_text--the-full-ui-layer)
   - [draw_boot](#35-draw_boot--the-terminal-boot-sequence)
   - [draw_loading](#36-draw_loading--the-progress-bar-screen)
   - [draw_selected_item](#37-draw_selected_item--the-highlight-box)
   - [draw_menu](#38-draw_menu--the-item-list)
   - [get_item_rect](#39-get_item_rect--mouse-hit-testing)
4. [main.py — The Game Loop](#4-mainpy--the-game-loop)
   - [Fonts setup](#41-fonts-setup)
   - [State machine](#42-the-state-machine)
   - [Events](#43-events)
   - [Update](#44-update)
   - [Draw](#45-draw)
5. [Key Concepts Glossary](#5-key-concepts-glossary)

---

## 1. Project Structure

```
8-bit-suite/
├── main.py               ← Entry point. Runs the game loop.
├── core/
│   └── settings.py       ← All constants, colors, data, font loader.
├── scenes/
│   └── menu.py           ← All draw functions for the menu screen.
├── assets/
│   └── fonts/
│       └── PressStart2P-Regular.ttf
└── requirements.txt
```

**The rule behind this structure:**

- `main.py` is the **director** — it only decides *when* to switch states and *which* screen to show.
- `scenes/menu.py` is the **artist** — it only knows *how* to draw things.
- `core/settings.py` is the **rulebook** — raw data that both files share.

This means if you want to change a color, you only touch `settings.py`.
If you want to change how something looks, you only touch `menu.py`.
If you want to change how the game flows, you only touch `main.py`.

---

## 2. `core/settings.py`

This file holds all the raw data for the program. Nothing in here actually *does* anything — it just defines values that other files import and use.

### Paths

```python
import os
FONT_PATH = os.path.join("assets", "fonts", "PressStart2P-Regular.ttf")
```

`os.path.join` builds a file path safely for any operating system.
On Windows it produces `assets\fonts\PressStart2P-Regular.ttf`.
On Mac/Linux it produces `assets/fonts/PressStart2P-Regular.ttf`.
Always use this instead of hardcoding slashes.

### Window constants

```python
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "8-Bit Suite"
```

`FPS` stands for *Frames Per Second*. The game loop runs 60 times every second.
`TITLE` is the text that appears in the window's title bar.

### Colors

```python
COLOR_BG           = (  8,  12,  18)
COLOR_TITLE_YELLOW = (238, 176,  32)
```

Every color in pygame is a **tuple of three numbers: (Red, Green, Blue)**.
Each number goes from `0` (none of that color) to `255` (maximum).

- `(0, 0, 0)` = pure black
- `(255, 255, 255)` = pure white
- `(8, 12, 18)` = near-black with a very faint blue-green tint (the background)
- `(238, 176, 32)` = golden yellow (the title)

### Menu data

```python
MENU_ITEMS = [
    ("ROCK-PAPER-SCISSORS", "rps"),
    ("TIC-TAC-TOE",         "tictactoe"),
    ("SNAKE AND APPLE",     "snake"),
]
```

A **list of tuples**. Each tuple has two values:
1. The label shown on screen
2. The scene ID used later when launching that game

`ITEM_COLORS` is a parallel list — index 0 of `ITEM_COLORS` is the color for index 0 of `MENU_ITEMS`.

### Boot lines

```python
BOOT_LINES = [
    "PY-OS v1.0.4",
    "Loading core modules...",
    ...
]
```

A plain list of strings. `draw_boot` reads this list to know what to print during the startup sequence.

### load_fonts()

```python
def load_fonts():
    return {
        "title"  : pygame.font.Font(FONT_PATH, 42),
        "menu"   : pygame.font.Font(FONT_PATH, 16),
        ...
    }
```

**Why a function instead of a plain constant?**
`pygame.font.Font()` requires `pygame.init()` to have been called first.
If you put font objects directly in the file, they would be created the moment Python
imports `settings.py` — before `pygame.init()` runs — and the program would crash.

By wrapping them in a function, font objects are only created when you *call*
`load_fonts()` inside `main()`, which happens safely after `pygame.init()`.

The function returns a **dictionary** — a collection of named items.
`fonts["title"]` gives you the big title font. `fonts["menu"]` gives you the menu font.
Using names instead of positions (`fonts[0]`) makes the code much easier to read.

---

## 3. `scenes/menu.py`

This file contains every function that draws something onto the screen.
It imports what it needs from `settings.py` and uses pygame's drawing tools.

### 3.1 `draw_centered_text` — The Reusable Helper

```python
def draw_centered_text(surface, text, font, color, y):
    text_surf = font.render(text, False, color)
    x = (SCREEN_WIDTH - text_surf.get_width()) // 2
    surface.blit(text_surf, (x, y))
```

**What it does:** Draws any text horizontally centered at a given `y` position.

**Step by step:**

1. `font.render(text, False, color)` — converts the string into a pygame Surface
   (a small image of the text). The `False` means no anti-aliasing — keeps the
   pixel-font sharp and crisp.

2. `text_surf.get_width()` — asks the rendered surface how wide it is in pixels.

3. `x = (SCREEN_WIDTH - text_surf.get_width()) // 2` — centering math.
   If the screen is 1000px wide and the text is 400px wide, there are 600px left over.
   Split that evenly: 300px on each side. So `x = 300`.
   The `//` means integer division (no decimal point).

4. `surface.blit(text_surf, (x, y))` — stamps the text surface onto the main surface
   at position `(x, y)`. `(x, y)` is always the **top-left corner** of what's being drawn.

This is called a **helper function** because it's reused everywhere else. Any time
you need centered text, you call this one function instead of repeating those 3 lines.

---

### 3.2 `draw_border`

```python
def draw_border(surface):
    pygame.draw.rect(
        surface,
        COLOR_BORDER,
        pygame.Rect(15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30),
        4
    )
```

`pygame.draw.rect` draws a rectangle. It takes 4 arguments:
1. `surface` — where to draw it
2. `COLOR_BORDER` — what color
3. `pygame.Rect(x, y, width, height)` — the rectangle's position and size.
   `(15, 15)` starts 15px from the top-left. `SCREEN_WIDTH - 30` makes it end 15px
   from the right edge (15px inset on each side, so subtract 30 total).
4. `4` — border thickness in pixels. If this were `0`, the rectangle would be filled solid.

---

### 3.3 `draw_title` — Drop Shadow Effect

```python
def draw_title(surface, fonts):
    shadow_color = (180, 80, 0)
    title_text   = "8-BIT SUITE"

    shadow_surf = fonts["title"].render(title_text, False, shadow_color)
    title_surf  = fonts["title"].render(title_text, False, COLOR_TITLE_YELLOW)

    title_x = (SCREEN_WIDTH - title_surf.get_width()) // 2
    title_y = 110

    surface.blit(shadow_surf, (title_x + 4, title_y + 4))  # draw shadow first
    surface.blit(title_surf,  (title_x, title_y))           # draw real text on top
```

**The drop shadow trick:** Render the same text twice.
- First render: dark orange color, drawn 4px to the right and 4px down from the real position.
- Second render: gold color, drawn at the real position — on top of the shadow.

Because the shadow is drawn first, the gold text covers it slightly, leaving only
the bottom-right edge of the shadow peeking out. This creates the 3D depth effect.

This same trick is used in CSS with `text-shadow: 4px 4px 0 orange`.

---

### 3.4 `draw_text` — The Full UI Layer

```python
def draw_text(surface, fonts, elapsed):
```

This function draws everything that isn't the menu items:
title, subtitle, terminal prompt, ONLINE indicator, separator lines, and the footer.

**The separator lines:**
```python
pygame.draw.line(surface, (30, 35, 40), (15, 55), (SCREEN_WIDTH - 15, 55), 2)
```
`pygame.draw.line(surface, color, start_point, end_point, thickness)`
- `(15, 55)` is the left end of the line
- `(SCREEN_WIDTH - 15, 55)` is the right end — 15px from the right edge, same y position
- `2` = 2px thick

**The blinking INSERT COIN:**
```python
if int(elapsed / 0.6) % 2 == 0:
    draw_centered_text(surface, "INSERT COIN", ...)
```

`elapsed` is the total seconds since the menu became active.
Dividing by `0.6` tells you how many 0.6-second chunks have passed.
`int()` rounds it down. `% 2` checks if it's even or odd.
- Even chunk → `== 0` is True → text is drawn (visible)
- Odd chunk → `== 0` is False → text is skipped (invisible)

This creates a blink every 0.6 seconds with zero extra variables.

---

### 3.5 `draw_boot` — The Terminal Boot Sequence

```python
def draw_boot(surface, fonts, elapsed):
    lines_to_show = min(int(elapsed / 0.4) + 1, len(BOOT_LINES))

    for i in range(lines_to_show):
        line_surf = fonts["tiny"].render(BOOT_LINES[i], False, COLOR_GREEN)
        surface.blit(line_surf, (x, y + i * line_height))
```

**How lines appear one by one:**

Every 0.4 seconds, `lines_to_show` increases by 1.
- At 0.0s → `int(0.0 / 0.4) + 1 = 1` → show 1 line
- At 0.4s → `int(0.4 / 0.4) + 1 = 2` → show 2 lines
- At 0.8s → `int(0.8 / 0.4) + 1 = 3` → show 3 lines

`min(..., len(BOOT_LINES))` makes sure it never tries to show more lines than exist.

**Vertical positioning:**
`y + i * line_height` — each line is drawn `line_height` pixels below the previous one.
When `i = 0`, it draws at `y`. When `i = 1`, it draws at `y + 36`. And so on.

---

### 3.6 `draw_loading` — The Progress Bar Screen

```python
progress = min(elapsed / 2.5, 1.0)
fill_w   = int(BAR_W * progress)

pygame.draw.rect(surface, COLOR_GREEN, pygame.Rect(BAR_X, BAR_Y, BAR_W, BAR_H), 2)
pygame.draw.rect(surface, COLOR_GREEN, pygame.Rect(BAR_X, BAR_Y, fill_w, BAR_H))
```

**Two rectangles make the bar:**
1. First `draw.rect` with thickness `2` — draws just the outline box.
2. Second `draw.rect` with no thickness argument — fills a growing rectangle inside it.

**The progress math:**
- `elapsed / 2.5` gives a number from `0.0` to `1.0` over 2.5 seconds.
- `min(..., 1.0)` caps it so it never exceeds 100%.
- Multiply by `BAR_W` to convert that fraction into pixels.
- At 0.0s → `fill_w = 0px`. At 1.25s → `fill_w = 200px`. At 2.5s → `fill_w = 400px`.

---

### 3.7 `draw_selected_item` — The Highlight Box

```python
def draw_selected_item(surface, fonts, label, cy, elapsed):
    BOX_W = 560
    BOX_H = 60
    BOX_X = (SCREEN_WIDTH - BOX_W) // 2
    BOX_Y = cy - BOX_H // 2
```

`cy` is the **center y** of the item. `BOX_Y = cy - BOX_H // 2` shifts the box up
so that `cy` lands in the middle of the box, not the top. This keeps all
vertical measurements consistent — you always work with center points.

**The bouncing arrows:**
```python
offset      = int(math.sin(elapsed * 4) * 4)
surface.blit(left_arrow,  (BOX_X + 32 - offset, arrow_y))
surface.blit(right_arrow, (BOX_X + BOX_W - 44 + offset, arrow_y))
```

`math.sin()` produces a smooth wave that oscillates between `-1` and `+1`.
- `elapsed * 4` controls speed — higher number = faster oscillation.
- `* 4` at the end scales the movement to ±4 pixels.
- `int()` snaps to whole pixels so it looks crisp.

The left arrow subtracts the offset (moves left when sin is positive).
The right arrow adds the offset (moves right when sin is positive).
They bounce away from the text and back in sync.

---

### 3.8 `draw_menu` — The Item List

```python
def draw_menu(surface, fonts, selected, elapsed):
    start_y = 350
    spacing = 110

    for i, (label, scene) in enumerate(MENU_ITEMS):
        cy = start_y + i * spacing
        if i == selected:
            draw_selected_item(surface, fonts, label, cy, elapsed)
        else:
            draw_centered_text(surface, label, fonts["menu"], ITEM_COLORS[i], cy)
```

`enumerate(MENU_ITEMS)` loops through the list and gives you both:
- `i` — the index number (0, 1, 2)
- `(label, scene)` — the tuple unpacked into two variables

`cy = start_y + i * spacing` positions each item:
- Item 0: `cy = 350`
- Item 1: `cy = 460`
- Item 2: `cy = 570`

If `i == selected`, draw the fancy highlight box. Otherwise, draw plain colored text.
`selected` is just a number passed in from `main.py` — the menu doesn't decide what's
selected, it just draws whatever `main.py` tells it to.

---

### 3.9 `get_item_rect` — Mouse Hit Testing

```python
def get_item_rect(i):
    BOX_W   = 560
    BOX_H   = 60
    BOX_X   = (SCREEN_WIDTH - BOX_W) // 2
    start_y = 350
    spacing = 110
    cy      = start_y + i * spacing
    return pygame.Rect(BOX_X, cy - BOX_H // 2, BOX_W, BOX_H)
```

Returns the invisible rectangle that represents where menu item `i` sits on screen.
Used in `main.py` to check if the mouse is over an item:

```python
if get_item_rect(i).collidepoint(mx, my):
```

`collidepoint(x, y)` returns `True` if the point is inside the rectangle.

**Important:** The numbers here (`BOX_W`, `BOX_H`, `start_y`, `spacing`) must always
match what `draw_selected_item` and `draw_menu` use. If you change the layout, update
both places. That's why centralizing these in a shared constant would be even better
as the project grows.

---

## 4. `main.py` — The Game Loop

This file is the heart of the program. It runs one loop, 60 times per second,
that does three things every frame: handle events, update state, draw.

### 4.1 Fonts setup

```python
pygame.init()
fonts = load_fonts()
```

`pygame.init()` starts all pygame systems (display, audio, input).
`load_fonts()` is called immediately after — this is why the function exists in
`settings.py` rather than plain constants. Fonts need pygame ready first.

### 4.2 The State Machine

```python
state = "boot"   # can be "boot", "menu", or "loading"
```

A **state machine** is a variable that tracks which "mode" the program is in.
Only one state is active at a time. Each state:
- Draws something different
- Responds to input differently
- Transitions to another state when conditions are met

```
"boot" ──(boot finishes)──► "menu" ──(game selected)──► "loading" ──(2.5s pass)──► "menu"
```

`elapsed` is reset to `0.0` on every transition so each state starts its timer fresh.

### 4.3 Events

```python
for event in pygame.event.get():
```

pygame collects everything the user does (key presses, mouse moves, clicking X)
into a queue. `pygame.event.get()` empties that queue and returns a list of events.
You loop through them and check what each one is.

**Key event structure:**
```python
elif event.type == pygame.KEYDOWN:      # a key was pressed
    if event.key == pygame.K_UP:        # which key?
        selected = (selected - 1) % len(MENU_ITEMS)
```

`KEYDOWN` fires once when a key is pressed down — not every frame while held.
`event.key` tells you which specific key.

**Mouse events:**
```python
elif event.type == pygame.MOUSEMOTION:      # mouse moved
    mx, my = event.pos                      # current position
    for i in range(len(MENU_ITEMS)):
        if get_item_rect(i).collidepoint(mx, my):
            selected = i                    # hover = highlight
```

`MOUSEMOTION` fires every time the mouse moves.
`event.pos` is a tuple `(x, y)` of the cursor's current pixel position.
`collidepoint` checks if that position is inside a rectangle.

`MOUSEBUTTONUP` fires when a mouse button is released — used for clicks because
it feels more intentional than `MOUSEBUTTONDOWN` (same reason real buttons fire on release).

**Why mouse events are at the same level as KEYDOWN:**
All event types must be separate `elif` branches under the same `for event` loop.
Nesting `MOUSEMOTION` inside `KEYDOWN` would mean the mouse check only runs when
a key is also being pressed at the same time — which is almost never.

### 4.4 Update

```python
dt       = clock.tick(FPS) / 1000.0
elapsed += dt
```

`clock.tick(FPS)` does two things:
1. Waits until 1/60th of a second has passed (caps the loop at 60 FPS)
2. Returns how many **milliseconds** actually passed since last frame

Dividing by `1000` converts milliseconds to seconds.
`dt` (delta time) is typically around `0.0167` seconds (1/60).

Adding `dt` to `elapsed` every frame gives you a running total of seconds —
the "elapsed time" that drives all animations and timers.

**State transitions:**
```python
if state == "boot" and elapsed >= BOOT_DURATION:
    state   = "menu"
    elapsed = 0.0
```

Check these after updating `elapsed` so transitions happen on time.
Always reset `elapsed = 0.0` when switching states.

### 4.5 Draw

```python
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
```

**Why `screen.fill` comes first:**
Whatever was drawn last frame is still on the surface. Filling with the background
color wipes the slate clean before drawing the new frame. Without this, moving
elements leave a smear trail.

**Why `pygame.display.flip()` comes last:**
pygame uses double buffering — you draw onto a hidden back-buffer, then `flip()`
swaps it to the screen all at once. This prevents flickering that would happen if
the screen updated mid-draw.

---

## 5. Key Concepts Glossary

| Term | What it means |
|---|---|
| **Surface** | A pygame image/canvas. The screen is a surface. Rendered text is a surface. |
| **blit** | Copy one surface onto another at a given position. |
| **Rect** | A rectangle defined by `(x, y, width, height)`. `x, y` is the top-left corner. |
| **collidepoint** | Method on a Rect that returns True if a point is inside it. |
| **delta time (dt)** | Seconds since the last frame. Used to keep animations speed-consistent. |
| **elapsed** | Total seconds since the current state started. Drives all timers and animations. |
| **state machine** | A variable that tracks which mode the program is in. Only one state active at a time. |
| **enumerate** | Python built-in that gives you both index and value while looping a list. |
| **modulo (%)** | Remainder after division. Used for wrapping (menu navigation) and blinking. |
| **FPS** | Frames Per Second. How many times the game loop runs each second. |
| **double buffering** | Drawing to a hidden canvas then flipping it all at once to prevent flicker. |
| **sin wave** | `math.sin()` produces a smooth -1 to +1 oscillation. Used for bounce animations. |
| **tuple** | An immutable pair/group of values in Python. Colors and positions are tuples. |
| **hit test** | Checking if a mouse position overlaps a clickable area (using `collidepoint`). |

---

*Built part by part across one session. Each concept introduced only when needed.*