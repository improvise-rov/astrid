import pygame

from src.client.ui import UiContainer
from src.client.ui import UiTexture
from src.client.ui import UiServerConnectionStatusIndicator
from src.client.ui import UiCameraFeed
from src.client.ui import UiControlMonitor
from src.client.ui import UiCorrectionSubsysStatus
from src.client.ui import UiTextLog
from src.client.logger import Logger
from src.client.irov import RovInterface
from src.client.gamepad import GamepadManager
from src.client.gamepad import Gamepad
from src.client.callback import Callback
from src.common.network import Netsock
from src.common import packets
from src.common import consts


class Window():
    """
    Pygame Window Manager Class.
    """

    def __init__(self, ip: str, port: int):

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

        # ICON
        astrid_texture = pygame.image.load('docs/astrid_pixelart.png').convert_alpha()
        self.window.set_icon(astrid_texture)

        # MANAGEMENT
        self.keep_window_open = False # this boolean is important as it keeps the window loop going. if its ever false at the end of a loop, the window closes.
        self.fullscreen = False # true if window should fullscreen

        # TIMING
        self.clock = pygame.Clock() # pygame clock ; helps keep time (see further down for note on delta time)
        self.target_fps = 0 # target fps (0 means unlimited)

        # GAMEPAD
        self.gamepad_manager = GamepadManager()
        self.gamepad_manager.load_mappings('src/resource/keymap.json')
        Gamepad.NINTENDOIFIED_MAPPING = True

        ### NETWORK ###
        self.net = Netsock(ip, port)

        self.net.add_packet_handler(packets.DISCONNECT, lambda id, data, args: Logger.log("Server closed!", False))

        ## ROV ##
        self.rov = RovInterface(self.net, self.gamepad_manager)


        ###############


        ### UI Container ###
        self.container = UiContainer()

        self.container.add(UiTexture(
            pygame.Vector2(1850, 20), 
            astrid_texture,
            scale=pygame.Vector2(1, 1),
            centered=False
        ))

        self.container.add(UiServerConnectionStatusIndicator(
            pygame.Vector2(20, 20),
            self.net
        ))

        self.container.add(UiCameraFeed(
            pygame.Vector2(20, 50),
            pygame.transform.scale_by(
                pygame.image.load("src/resource/no_camera.jpg"),
                10
            ),
            self.net
        ))

        self.container.add(UiTextLog(
            pygame.Vector2(20, 710),
            pygame.Vector2(850, 350),
            16
        ))

        self.container.add(UiCorrectionSubsysStatus(
            pygame.Vector2(1000, 20),
            self.rov
        ))

        self.container.add(UiControlMonitor(
            pygame.Vector2(1000, 40),
            self.rov
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

        self.shutdown()

    def update(self, dt: float):
        # poll gamepad
        if self.gamepad_manager.has():
            self.gamepad_manager.fetch_first().poll_states()

        # update rov
        self.rov.update(dt)

        # update everything in ui container
        self.container.update(dt, self.draw_surface)

        # send status of controller
        if self.gamepad_manager.has():
            gp = self.gamepad_manager.fetch_first()

            lstick = gp.read_vector(*Gamepad.LEFT_STICK)

            self.net.send(packets.MSG, f"{lstick}".encode('utf-8'))

        # keycheck
        just_pressed = pygame.key.get_just_pressed()
        # check if f11 is pressed to toggle fullscreen
        if just_pressed[pygame.K_F11]:
            self.fullscreen = not self.fullscreen

            if self.fullscreen:
                self.window.set_fullscreen(True)
            else:
                self.window.set_windowed()


        # check if connect button is pressed
        if just_pressed[pygame.K_SPACE]:
            if not self.net.is_open():
                Logger.log("Trying to connect..", False)
                connected = self.net.start_client()
                if connected:
                    self.rov.correction_enabled = True
                    self.net.send(packets.ENABLE_CORRECTION, bytes())
                    Logger.log("Connected!", False)
                else:
                    Logger.log("Connection failed! (the server is probably not open)", False)


        # correction
        if just_pressed[pygame.K_RETURN]:
            self.rov.correction_enabled = not self.rov.correction_enabled
            if self.rov.correction_enabled:
                self.net.send(packets.ENABLE_CORRECTION, bytes())
                Logger.log("Enabled correction")
            else:
                self.net.send(packets.DISABLE_CORRECTION, bytes())
                Logger.log("Disabled correction")

        # server die
        if just_pressed[pygame.K_BACKSPACE]:
            if self.net.is_open():
                Logger.log("killing remote server")
                self.net.close()
                self.net.send(packets.STOP_SERVER, bytes())
        

    def event(self):
        for e in pygame.event.get(): # fetch every event from this frame
            if e.type == pygame.QUIT:
                self.keep_window_open = False

            # call callbacks
            if e.type in Callback.CALLBACKS:
                for function in Callback.CALLBACKS[e.type]:
                    function(e)

    def draw(self):
        # clear the surface with black (0x0 is a shortcut for 0x000000, which is like the hexcode #000000 (or black). replace the hash in a hexcode with 0x, and you can use it for colorlike objects)
        self.wnd_surface.fill(0x0) # fill window surface

        # from here draw to the draw surface
        self.draw_surface.fill(0x5980b1) # fill with a nice improvise blue

        # draw ui container (and therefore everything within it)
        self.container.draw(self.draw_surface)

        # draw draw surface to window surface
        self.wnd_surface.blit(pygame.transform.scale(self.draw_surface, self.window.size))


    def shutdown(self):

        # net
        self.net.disconnect()
        self.net.close()
