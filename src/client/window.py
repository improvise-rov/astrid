import pygame

from src.client.ui import UiContainer
from src.client.ui import UiTexture
from src.client.ui import UiServerConnectionStatusIndicator
from src.client.ui import UiCameraFeed
from src.client.ui import UiControlMonitor
from src.client.ui import UiCorrectionSubsysStatus
from src.client.ui import UiTextLog
from src.client.ui import UiLineGraph
from src.client.ui import UiCountdownClock
from src.client.ui import UiText
from src.client.render import Renderer
from src.client.logger import Logger
from src.client.irov import RovInterface
from src.client.float.ifloat import FloatInterface
from src.client.control.manager import ControllerManager
from src.client.control.gamepad import Gamepad
from src.client.callback import Callback
from src.common.net.worker import Networker#
from src.common.net import packets
from src.common import consts


class Window():
    """
    Pygame Window Manager Class.
    """

    def __init__(self, ip: str, port: int):

        ## WINDOW OBJECTS ##

        # there are several ways to create a window in pygame. for this, im using the newer object oriented api rather than the older procedural one
        # why? because i like it. there arent many differences anyway
        self.window = pygame.window.Window(
            title=consts.WINDOW_TITLE,
            size=(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT),
            resizable=True
            
        )

        self.wnd_surface = self.window.get_surface() # get the surface of the window to draw onto. this initialises everything, too
        self.draw_surface = pygame.Surface((consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT))

        ## ICON ##
        astrid_texture = pygame.image.load('docs/astrid_pixelart.png').convert_alpha()
        self.window.set_icon(astrid_texture)

        ## RENDERER ##
        Renderer.init()

        ## MANAGEMENT ##
        self.keep_window_open = False # this boolean is important as it keeps the window loop going. if its ever false at the end of a loop, the window closes.
        self.fullscreen = False # true if window should fullscreen

        ## TIMING ##
        self.clock = pygame.Clock() # pygame clock ; helps keep time (see further down for note on delta time)
        self.target_fps = 0 # target fps (0 means unlimited)

        ## GAMEPAD ##
        self.controller_manager = ControllerManager(default_gamepads_nintendoified=True)
        self.controller_manager.load_mappings('src/resource/keymap.json')

        ## ROV ##
        self.rov_ip = ip
        self.net = Networker(port, consts.PACKET_SIZE)
        self.net.register_listener(packets.DISCONNECT, lambda addr, data: Logger.log("Server closed!", False))
        self.rov = RovInterface(self.net, self.controller_manager)

        ## FLOAT ##
        self.float = FloatInterface()
        self.float_graph = UiLineGraph(pygame.Vector2(1400, 610), self.float.get_processed_data)

        ## UI CONTAINER ##
        self.container = UiContainer()

        self.container.add(UiServerConnectionStatusIndicator(
            pygame.Vector2(20, 20),
            self.net
        ))

        self.container.add(UiCameraFeed(
            pygame.Vector2(20, 50),
            pygame.transform.scale_by(
                pygame.image.load("src/resource/no_camera.jpg"),
                15
            ),
            self.net
        ))

        self.container.add(UiTextLog(
            pygame.Vector2(1320, 50),
            pygame.Vector2(350, 450),
            15
        ))

        self.container.add(UiCorrectionSubsysStatus(
            pygame.Vector2(800, 20),
            self.rov
        ))

        self.container.add(UiControlMonitor(
            pygame.Vector2(1700, 80),
            self.rov
        ))

        self.container.add(UiText(
            pygame.Vector2(consts.WINDOW_WIDTH - 40, consts.WINDOW_HEIGHT - 70),
            lambda: f"(Morag) Profile: {self.float.profile}\nTemperature: {self.float.temperature:.1f} deg C",
            justify = "right"
        ))
        self.container.add(self.float_graph)

        self.container.add(UiCountdownClock(
            pygame.Vector2(500, 10),
            consts.POOL_RUN_TIME_SECONDS
        ))

        self.container.add(UiText(
            pygame.Vector2(20, consts.WINDOW_HEIGHT-40),
            lambda: "<SPACE>: connect | <BACKSPACE>: kill ROV server & disconnect | <ENTER>: toggle IMU | <A>: toggle stopwatch | <RSHIFT>: run float subroutine"
        ))


        self.container.add(UiTexture(
            pygame.Vector2(consts.WINDOW_WIDTH-30, 30), 
            pygame.image.load('src/resource/scotland.png').convert_alpha(),
            scale=pygame.Vector2(0.05, 0.05),
            centered=True
        ))

        self.container.add(UiText(
            pygame.Vector2(consts.WINDOW_WIDTH-60, 20),
            lambda: "impROVise",
            draw_rect = True,
            justify = 'right',
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
        if self.controller_manager.has():
            self.controller_manager.fetch_first().poll_states()

        # update rov
        self.rov.update(dt)

        # update everything in ui container
        self.container.update(dt, self.draw_surface)

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
                self.net.client(self.rov_ip)

                self.net.send(packets.CONNECT)
                connected = self.net.wait_for_packet(packets.CONNECT_ACK)
                if connected:

                    # remember ip
                    data, addr = connected
                    
                    Logger.log(f"Connected! ({addr[0]}:{addr[1]})", False)

                    self.rov.correction_enabled = True
                    self.net.send(packets.ENABLE_CORRECTION)
                else:
                    Logger.log("Connection failed! (the server is probably not open)", False)


        # correction
        if just_pressed[pygame.K_RETURN]:
            self.rov.correction_enabled = not self.rov.correction_enabled
            if self.rov.correction_enabled:
                self.net.send(packets.ENABLE_CORRECTION)
                Logger.log("Enabled correction")
            else:
                self.net.send(packets.DISABLE_CORRECTION)
                Logger.log("Disabled correction")

        # server die
        if just_pressed[pygame.K_BACKSPACE]:
            if self.net.is_open():
                Logger.log("killing remote server")
                self.net.close()
                self.net.send(packets.STOP_SERVER)

        # float go
        if just_pressed[pygame.K_RSHIFT]:
            if self.float:
                self.float.run()
        

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
        self.draw_surface.fill(consts.GLAUCOUS) # fill with a nice improvise blue
        
        # add a safety orange bit BECAUSE I CAN HAHAHAHAH
        #pygame.draw.rect(self.draw_surface, consts.SAFETY_ORANGE, (pygame.Vector2(0, consts.WINDOW_HEIGHT * 1/2), pygame.Vector2(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT))) 

        # draw ui container (and therefore everything within it)
        self.container.draw(self.draw_surface)


        # draw draw surface to window surface
        self.wnd_surface.blit(pygame.transform.scale(self.draw_surface, self.window.size))


    def shutdown(self):
        self.net.close()

