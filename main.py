import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, FONT_PATH, MENU_ITEMS, BOOT_LINES, load_fonts
from scenes.menu import (
    draw_boot, draw_loading,
    draw_border, draw_text, draw_menu,
    get_item_rect, BOOT_DURATION,
)

def main():
    pygame.init()

    fonts = load_fonts()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    selected      = 0
    elapsed       = 0.0
    state         = "boot"
    loading_label = ""

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
        screen.fill((8, 12, 18))

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
