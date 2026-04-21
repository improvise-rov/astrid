##
import sys
sys.path[0] = sys.path[0][:-5] # hack around the fact that this file isnt in the main path so i can access src
##

import pygame
import typing
from src.common import consts
from src.poolside.callback import Callback
from src.poolside.render import Renderer
from src.poolside.control.manager import ControllerManager
from src.poolside.control.gamepad import Gamepad, _Key

class GamepadTest():
    
    TARGET_FPS: int = 60
    TITLE: str = "impROVise gamepad tester"
    W: int = 1280
    H: int = 800
    
    def __init__(self) -> None:
        self.surf = pygame.display.set_mode((GamepadTest.W, GamepadTest.H))
        pygame.display.set_caption(GamepadTest.TITLE)
        self.clock = pygame.Clock()
        self.running = False

        self.controller_manager = ControllerManager(default_gamepads_nintendoified=True)
        self.controller_manager.always_gamepad = True

    def run(self):
        self.running = True
        dt = 0.0
        while self.running:
            self.update(dt)
            self.event()
            self.draw(self.surf)
            pygame.display.flip()
            dt = self.clock.tick(GamepadTest.TARGET_FPS) / 1000
        self.stop()


    def update(self, dt: float):
        if self.controller_manager.has():
            self.controller_manager.fetch_first().poll_states()

    def event(self):
        for e in pygame.event.get(): # fetch every event from this frame
            if e.type == pygame.QUIT:
                self.running = False

            # call callbacks
            if e.type in Callback.CALLBACKS:
                for function in Callback.CALLBACKS[e.type]:
                    function(e)

    def draw(self, s: pygame.Surface):
        s.fill(consts.GLAUCOUS)
        
        Renderer.draw_text(s, GamepadTest.TITLE, (20, 20, 0, 0))
        

        if not self.controller_manager.has():
            Renderer.draw_text(s, 'no gamepad!', (20, 60, 0, 0))
            return

        # draw info about gamepad
        gp = typing.cast(Gamepad, self.controller_manager.fetch_first())
        
        Renderer.draw_text(s, f'Gamepad: {gp._get_gamepad_name()}', (20, 60, 0, 0), scale=0.8)
        Renderer.draw_text(s, f'Instance ID: {gp._get_pygame_joystick().get_instance_id()}', (20, 80, 0, 0), scale=0.8)
        Renderer.draw_text(s, f'GUID: {gp._get_pygame_joystick().get_guid()}', (20, 100, 0, 0), scale=0.8)
        Renderer.draw_text(s, f'Battery: {gp._get_power_status()}', (20, 120, 0, 0), scale=0.8)

        GamepadTest.draw_stick(s, (GamepadTest.W // 2) - 100, 500, gp, Gamepad.LEFT_STICK, Gamepad.KEY_LEFT_STICK, 'Left Stick')
        GamepadTest.draw_stick(s, (GamepadTest.W // 2) + 100, 500, gp, Gamepad.RIGHT_STICK, Gamepad.KEY_RIGHT_STICK, 'Right Stick')

        GamepadTest.draw_dpad(s, (GamepadTest.W // 2) - 200, 400, gp, Gamepad.DPAD, 'DPad')

        bc_x = (GamepadTest.W // 2) + 200
        GamepadTest.draw_button_circle(s, bc_x+30, 400+00, gp, Gamepad.KEY_A, 'A')
        GamepadTest.draw_button_circle(s, bc_x-00, 400+30, gp, Gamepad.KEY_B, 'B')
        GamepadTest.draw_button_circle(s, bc_x+00, 400-30, gp, Gamepad.KEY_X, 'X')
        GamepadTest.draw_button_circle(s, bc_x-30, 400-00, gp, Gamepad.KEY_Y, 'Y')

        GamepadTest.draw_button_circle(s, (GamepadTest.W // 2) - 50, 350, gp, Gamepad.KEY_SELECT, '-')
        GamepadTest.draw_button_circle(s, (GamepadTest.W // 2) + 00, 350, gp, Gamepad.KEY_HOME, 'H')
        GamepadTest.draw_button_circle(s, (GamepadTest.W // 2) + 50, 350, gp, Gamepad.KEY_START, '+')

        GamepadTest.draw_button_rect(s, (GamepadTest.W // 2) - 100, 300, gp, Gamepad.KEY_LEFT_BUMPER, 'LB')
        GamepadTest.draw_button_rect(s, (GamepadTest.W // 2) + 100, 300, gp, Gamepad.KEY_RIGHT_BUMPER, 'RB')

        GamepadTest.draw_trigger(s, (GamepadTest.W // 2) - 200, 280, gp, Gamepad.AXIS_LEFT_TRIGGER_ANALOGUE, 'LT')
        GamepadTest.draw_trigger(s, (GamepadTest.W // 2) + 200, 280, gp, Gamepad.AXIS_RIGHT_TRIGGER_ANALOGUE, 'RT')


    def stop(self):
        pass


    @staticmethod
    def draw_stick(s: pygame.Surface, x: int, y: int, gp: Gamepad, axial_pair: tuple[_Key, _Key], press: _Key, label: str):
        radius = 30

        # read
        stick = gp.read_vector(*axial_pair)
        down = gp.digital_down(press)

        pygame.draw.circle(s, 'white', (x, y), radius)
        pygame.draw.circle(s, 'black' if down else 'grey', (x + stick.x * radius, y + stick.y * radius), radius / 3)

        Renderer.draw_text(s, label, (x - radius * 1.5, y + radius + 5, radius*3, 20), scale=0.5, justify='center')

        Renderer.draw_text(s, f"({stick.x:.1f}, {stick.y:.1f})", (x - radius * 1.5, y + radius + 15, radius*3, 20), scale=0.5, justify='center')

    
    @staticmethod
    def draw_dpad(s: pygame.Surface, x: int, y: int, gp: Gamepad, axial_pair: tuple[_Key, _Key], label: str):
        radius = 30

        # read
        vec = gp.read_vector(*axial_pair)

        pygame.draw.polygon(s, 'black' if vec.y > 0 else 'white', [
            (x, y),
            (x - radius / 4, y - radius / 4),
            (x - radius / 4, y - radius),
            (x + radius / 4, y - radius),
            (x + radius / 4, y - radius / 4),
        ])
        pygame.draw.polygon(s, 'black' if vec.y < 0 else 'white', [
            (x, y),
            (x - radius / 4, y + radius / 4),
            (x - radius / 4, y + radius),
            (x + radius / 4, y + radius),
            (x + radius / 4, y + radius / 4),
        ])
        pygame.draw.polygon(s, 'black' if vec.x < 0 else 'white', [
            (x, y),
            (x - radius / 4, y - radius / 4),
            (x - radius, y - radius / 4),
            (x - radius, y + radius / 4),
            (x - radius / 4, y + radius / 4),
        ])
        pygame.draw.polygon(s, 'black' if vec.x > 0 else 'white', [
            (x, y),
            (x + radius / 4, y - radius / 4),
            (x + radius, y - radius / 4),
            (x + radius, y + radius / 4),
            (x + radius / 4, y + radius / 4),
        ])

        Renderer.draw_text(s, label, (x - radius * 1.5, y + radius + 5, radius*3, 20), scale=0.5, justify='center')
        Renderer.draw_text(s, f"({vec.x:.1f}, {vec.y:.1f})", (x - radius * 1.5, y + radius + 15, radius*3, 20), scale=0.5, justify='center')


    @staticmethod
    def draw_button_circle(s: pygame.Surface, x: int, y: int, gp: Gamepad, key: _Key, label: str):
        radius = 15

        # read
        down = gp.digital_down(key)

        pygame.draw.circle(s, 'black' if down else 'white', (x, y), radius)
        Renderer.draw_text(s, label, (x-radius, y-5, radius*2, 20), scale=0.75, justify='center', color='black' if not down else 'white')

    @staticmethod
    def draw_button_rect(s: pygame.Surface, x: int, y: int, gp: Gamepad, key: _Key, label: str):
        w = 35
        h = 15
        rect = (x-w, y-h, w*2, h*2)

        # read
        down = gp.digital_down(key)

        pygame.draw.rect(s, 'black' if down else 'white', rect)
        Renderer.draw_text(s, label, (rect[0], rect[1]+10, rect[2], rect[3]), scale=0.75, justify='center', color='black' if not down else 'white')

    @staticmethod
    def draw_trigger(s: pygame.Surface, x: int, y: int, gp: Gamepad, key: _Key, label: str):
        w = 30
        h = 80

        # read
        axis = (gp.read_axis(key) + 1) / 2

        Renderer.draw_progress_bar(s, pygame.Vector2(x - w/2, y - h/2), h, w, axis, orientation='bottom_to_top', outline_width=4)

        Renderer.draw_text(s, label, (x - w/2, y + h/2, w, 20), scale=0.5, justify='center')
        Renderer.draw_text(s, f"{axis:.1f}", (x - w/2, y + h/2 + 10, w, 20), scale=0.5, justify='center')

if __name__ == "__main__":
    pygame.init()
    wnd = GamepadTest()
    wnd.run()