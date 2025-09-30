import pygame

from src import consts

class Window():
    """
    Pygame Window Manager Class.
    """

    def __init__(self):
        pygame.init()

        # WINDOW
        self.window = pygame.window.Window(
            title=consts.WINDOW_TITLE,
            size=(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT),
        )

        self.wnd_surface = self.window.get_surface()

        # MANAGEMENT
        self.keep_window_open = False

        # TIMING
        self.clock = pygame.Clock()
        self.target_fps = 0

    
    def run(self):
        self.keep_window_open = True
        dt = 0.0

        while self.keep_window_open:
            # UPDATE
            self.update(dt)

            # EVENT
            self.event()

            # DRAW
            self.draw()

            # TICK
            dt = self.clock.tick(self.target_fps) / 1000

            # FLIP
            self.window.flip()

    def update(self, dt: float):
        pass

    def event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.keep_window_open = False

    def draw(self):
        pass