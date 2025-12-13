from __future__ import annotations
import pygame
import typing
import struct
import io

from src.client.gamepad import GamepadManager
from src.client.gamepad import Gamepad
from src.common.network import Netsock
from src.common.rovmath import RovMath
from src.common import consts
from src.common import packets

class UiContainer():
    """
    A `UiContainer` is a type of object that keeps track of `UiElement`s.
    """
    def __init__(self) -> None:
        self.elements: list[UiElement] = []
        self.global_offset = pygame.Vector2(0, 0)
        self.global_visible = True

    def add(self, element: UiElement) -> int:
        idx = len(self.elements)
        self.elements.append(element)
        return idx
    
    def get_element(self, idx: int) -> UiElement:
        return self.elements[idx]
    
    def draw(self, surface: pygame.Surface):
        if not self.global_visible:
            return
        for element in self.elements:
            element.draw(surface)

    def update(self, dt: float, surface: pygame.Surface):
        for element in self.elements:
            element.update(dt, surface)


class UiElement():
    """
    Abstract Base Class for Ui Elements. This includes things like the Camera Display, any text on screen and image holders.

    This isn't _needed_, per se, but I think its a good way of structuring the data, especially as we're forgoing any sort of
    scene management system. This may be being programmed using a gamedev library, but it isn't a game; no need to overcomplicate.
    """
    def __init__(self, pos: pygame.Vector2):
        self.pos = pos
        self.container: UiContainer | None = None

        self.visible = True

    def resolve_position(self) -> pygame.Vector2:
        if self.container:
            return self.pos + self.container.global_offset
        else:
            return self.pos

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

    def update(self, dt: float, surface: pygame.Surface):
        pass


class UiTexture(UiElement):
    def __init__(self, pos: pygame.Vector2, texture: pygame.Surface, scale: pygame.Vector2 = pygame.Vector2(1, 1), rotation: float = 0.0, centered: bool = False):
        """
        `rotation` is counter-clockwise in degrees.
        """

        super().__init__(pos)

        self.original_texture = texture

        self.texture = texture
        self.scale = scale
        self.rotation = rotation
        self.centered = centered

        self._update_texture()


    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        pos = self.resolve_position()
        if self.centered:
            pos = self.resolve_position() - pygame.Vector2(self.texture.size) / 2
        surface.blit(self.texture, pos)
    
    def set_scale(self, scale: float):
        self.scale = scale
        self._update_texture()

    def set_rotation(self, rot: float):
        self.rotation = rot
        self._update_texture()

    def _update_texture(self):
        self.texture = pygame.transform.scale_by(self.original_texture, self.scale)
        self.texture = pygame.transform.rotate(self.texture, self.rotation)


class UiServerConnectionStatusIndicator(UiElement):
    def __init__(self, pos: pygame.Vector2, net: Netsock):
        super().__init__(pos)
        self.net = net

        self.font = pygame.font.SysFont('consolas', 24)
        

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        pygame.draw.circle(surface, 0x000000, self.resolve_position(), 10)
        pygame.draw.circle(surface, 0x00ff00 if self.net.is_open() else 0xff0000, self.resolve_position(), 8)

        string = "Not Connected"
        if self.net.is_open():
            string = f"Connected ({self.net.ip}:{self.net.port})"
        surface.blit(self.font.render(string, False, 0xffffffff), self.resolve_position() + pygame.Vector2(15, -12))

class UiCameraFeed(UiElement):
    def __init__(self, pos: pygame.Vector2, no_conn_img: pygame.Surface, net: Netsock):
        super().__init__(pos)
        self.net = net

        self._no_connection_frame = no_conn_img
        self._last_frame = pygame.Surface(self._no_connection_frame.size)
        self.net.add_packet_handler(packets.PACKET_CAMERA, self._recv_camera_frame)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.net.is_open():
            surface.blit(self._last_frame, self.resolve_position())
        else:
            surface.blit(self._no_connection_frame, self.resolve_position())


    def _recv_camera_frame(self, id: int, data: bytes, args: tuple):
        pygame.transform.scale(
            pygame.image.load(io.BytesIO(data), 'jpg').convert(),
            self._last_frame.size,
            self._last_frame
        )

class UiControlMonitor(UiElement):
    """
    Half a UI Element, half just decentralised processing. 
    The UI Element system does a good job at seperating out things that need processing,
    and this needs processing.
    """

    def __init__(self, pos: pygame.Vector2, net: Netsock, gamepad_manager: GamepadManager):
        super().__init__(pos)

        self.font = pygame.font.SysFont('consolas', 24)
        self.net = net
        self.gamepad_manager = gamepad_manager

        self.values: dict[str, int | float] = {
            'lf': 0, # front left
            'rf': 0, # front right
            'lt': 0, # top left
            'rt': 0, # top right
            'lb': 0, # back left
            'rb': 0, # back right

            'ca': 0.0, # camera angle
            'tw': 0.0, # tool wrist
            'tg': 0.0, # tool grip
        }

        self.camera_angle_speed = 0.001
        self.wrist_rotate_speed = 0.001

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        text = self.font.render(
            "lf:".ljust(3) + f"{round(self.values['lf'], 2)}".rjust(5) + "   " +
            "rf:".ljust(3) + f"{round(self.values['rf'], 2)}".rjust(5) + "\n" + 
            "lt:".ljust(3) + f"{round(self.values['lt'], 2)}".rjust(5) + "   " +
            "rt:".ljust(3) + f"{round(self.values['rt'], 2)}".rjust(5) + "\n" + 
            "lb:".ljust(3) + f"{round(self.values['lb'], 2)}".rjust(5) + "   " +
            "rb:".ljust(3) + f"{round(self.values['rb'], 2)}".rjust(5) + "\n" +
            "\n\n\n" +
            f"camera angle: {round(self.values['ca'], 2)}\n" +
            f"grip: {round(self.values['tg'], 2)}\n" +
            f"wrist: {round(self.values['tw'], 2)}\n",
            False, 0x000000ff
        )

        surface.blit(text, self.resolve_position())

    
    def update(self, dt: float, surface: pygame.Surface):

        # calculate speeds
        if self.gamepad_manager.has():
            gp = self.gamepad_manager.fetch_first()

            camera_angle_change = gp.read_axis(self.gamepad_manager.keymap_translate('axis.camera_angle_change'))
            tool_grip = gp.read_axis(self.gamepad_manager.keymap_translate('axis.tool_grip'))
            wrist = gp.digital_down(self.gamepad_manager.keymap_translate('digital.rotate_wrist.cw')) - gp.digital_down(self.gamepad_manager.keymap_translate('digital.rotate_wrist.ccw'))

            forward = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.forward'))
            strafe = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.strafe'))
            rotate = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.rotate'))
            elevate = gp.read_axis(self.gamepad_manager.keymap_translate('axis.rov.elevate'))

            # calculate motors
            """
            rotate left             lf - rf   rotate right
            only used in elevation  lt - rt   only used in elevation
            rotate right            lb - rb   rotate left
            """

            self.values['lf'] = -rotate - strafe + forward 
            self.values['rf'] =  rotate + strafe + forward
            self.values['lt'] =  elevate
            self.values['rt'] =  elevate
            self.values['lb'] =  rotate - strafe - forward
            self.values['rb'] = -rotate + strafe - forward

            # TODO test that this is the right configuration lol


            self.values['ca'] = RovMath.clamp(-1, 1, self.values['ca'] + camera_angle_change * self.camera_angle_speed)
            self.values['tg'] = tool_grip
            self.values['tw'] = RovMath.clamp(-1, 1, self.values['tw'] + wrist * self.wrist_rotate_speed)


        # manual override
        keys = pygame.key.get_pressed()
        reverse = keys[pygame.K_KP_0]

        self.values['lf'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_7] else self.values['lf']
        self.values['rf'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_9] else self.values['rf']
        self.values['lt'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_4] else self.values['lt']
        self.values['rt'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_6] else self.values['rt']
        self.values['lb'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_1] else self.values['lb']
        self.values['rb'] = (-1.0 if reverse else 1.0) if keys[pygame.K_KP_3] else self.values['rb']


        # send data
        self.net.send(packets.PACKET_CONTROL, struct.pack(packets.FORMAT_PACKET_CONTROL,
                                                          RovMath.motor_to_byte(self.values['lf']),
                                                          RovMath.motor_to_byte(self.values['rf']),
                                                          RovMath.motor_to_byte(self.values['lt']),
                                                          RovMath.motor_to_byte(self.values['rt']),
                                                          RovMath.motor_to_byte(self.values['lb']),
                                                          RovMath.motor_to_byte(self.values['rb']),

                                                          RovMath.servo_angle_to_byte(self.values['ca']),
                                                          RovMath.servo_angle_to_byte(self.values['tw']),
                                                          RovMath.servo_angle_to_byte(self.values['tg']),
                                                          ))