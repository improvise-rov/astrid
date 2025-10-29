import pygame

from src.client.ui import UiContainer
from src.client.ui import UiTexture
from src.common import consts


class Window():
    """
    Pygame Window Manager Class.
    """

    def __init__(self):

        # WINDOW OBJECTS

        # there are several ways to create a window in pygame. for this, im using the newer object oriented api rather than the older procedural one
        # why? because i like it. there arent many differences anyway
        self.window = pygame.window.Window(
            title=consts.WINDOW_TITLE,
            size=(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT),
            resizable=True
            
        )

        self.wnd_surface = self.window.get_surface() # get the surface of the window to draw onto. this initialises everything, too
        self.draw_surface = pygame.Surface((consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT))

        # MANAGEMENT
        self.keep_window_open = False # this boolean is important as it keeps the window loop going. if its ever false at the end of a loop, the window closes.

        # TIMING
        self.clock = pygame.Clock() # pygame clock ; helps keep time (see further down for note on delta time)
        self.target_fps = 0 # target fps (0 means unlimited)

        ### UI Container ###
        self.container = UiContainer()

        astrid = self.container.add(UiTexture(
            pygame.Vector2(100, 100), 
            pygame.image.load('docs/astrid_pixelart.png').convert_alpha(),
            scale=pygame.Vector2(2, 2),
            centered=False
        ))

        ####################


    
    def run(self):
        self.keep_window_open = True # set the keep-open flag to true
        
        # dt, also known as delta time, is INCREDIBLY IMPORTANT
        # delta time is used in game development to keep time related functions independent of framerate
        # lets say we have a player that should move 500 pixels per second
        # 
        # (assume control vector is some (X,Y) pair of numbers {-1..1} that correspond to inputs)
        # def update_player(dt: float):
        #   ...
        #   player.position += control_vector * 500
        #   ...
        #
        # this will move the player 500 pixels every FRAME
        # but we want every SECOND
        # so we multiply by delta time
        #
        # def update_player(dt: float):
        #   ...
        #   player.position += control_vector * 500 * dt
        #   ...
        #
        # this relates the speed to time, and the player will move 500 pixels every SECOND
        # physically, dt is measured as the time since the last frame
        # the clock object made before keeps track of this for us
        # simply put, multiplying by dt overcompensates time related functions by increasing at lower framerates and decreasing at higher framerates
        #
        # the clock object returns dt in terms of milliseconds, but standard practice is to use it in seconds (SI base unit), 
        # so you'll see when i update it using self.clock.tick(...) at the end of the frame i divide it by a thousand
        dt = 0.0

        while self.keep_window_open: # window loop
            # UPDATE - update everything for this frame; do calculations, etc.
            self.update(dt)

            # EVENT - poll pygames event handler system, allowing different things to communicate with each other across the program. like a broadcast messaging system
            self.event()

            # DRAW - draw everything to the window; anything graphical goes under here
            self.draw()

            # TICK - calculate delta time
            dt = self.clock.tick(self.target_fps) / 1000

            # FLIP - flip the framebuffers (rendering works in two buffers; the one on the screen (frontbuffer) and the one you are drawing to (backbuffer). this prevents graphical glitches)
            self.window.flip()

    def update(self, dt: float):
        # update everything in ui container

        self.container.update(dt, self.draw_surface)

    def event(self):
        for e in pygame.event.get(): # fetch every event from this frame
            if e.type == pygame.QUIT:
                self.keep_window_open = False

            # later, ill add a callback system here that allows different areas of the program to listen for events and run code on them without having to do it all here
            # thats a future job though

    def draw(self):
        # clear the surface with black (0x0 is a shortcut for 0x000000, which is like the hexcode #000000 (or black). replace the hash in a hexcode with 0x, and you can use it for colorlike objects)
        self.wnd_surface.fill(0x0) # fill window surface

        # from here draw to the draw surface
        self.draw_surface.fill(0x5980b1) # fill with a nice improvise blue

        # draw ui container (and therefore everything within it)
        self.container.draw(self.draw_surface)

        # draw draw surface to window surface
        self.wnd_surface.blit(pygame.transform.scale(self.draw_surface, self.window.size))
