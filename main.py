import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, load_fonts
from core.scene_manager import SceneManager
from scenes.menu import MenuScene, LoadingScene
from scenes.rps import RPSScene


def main():
    """
    Main entry point of the game suite.

    Initializes the pygame library, sets up the display with the correct title and resolution,
    loads the fonts, creates a SceneManager instance, registers the menu scene, and starts the game loop.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    fonts = load_fonts()

    manager = SceneManager(screen, clock, fonts)
    manager.register("loading", LoadingScene(manager, fonts))
    manager.register("menu", MenuScene(manager, fonts))
    manager.register("rps", RPSScene(manager, fonts))
    # We'll add rps, snake, tictactoe later:
    # manager.register("rps", RPSScene(manager, fonts))

    manager.switch_to("menu")
    manager.run()


if __name__ == "__main__":
    main()
