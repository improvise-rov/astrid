from __future__ import annotations
import pygame
import typing
import struct
import io

from src.client.gamepad import GamepadManager
from src.client.gamepad import Gamepad
from src.common.network import Netsock
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


    def _recv_camera_frame(self, id: int, data: bytes):
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

        self.pwm = {
            'lf': 0, # front left
            'rf': 0, # front right
            'lt': 0, # top left
            'rt': 0, # top right
            'lb': 0, # back left
            'rb': 0, # back right

            'ca': 0, # camera angle
            'tw': 0, # tool wrist
            'tg': 0, # tool grip
        }

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        text = self.font.render(
            "lf:".ljust(3) + f"{self.pwm['lf']}".rjust(5) + "   " +
            "rf:".ljust(3) + f"{self.pwm['rf']}".rjust(5) + "\n" + 
            "lt:".ljust(3) + f"{self.pwm['lt']}".rjust(5) + "   " +
            "rt:".ljust(3) + f"{self.pwm['rt']}".rjust(5) + "\n" + 
            "lb:".ljust(3) + f"{self.pwm['lb']}".rjust(5) + "   " +
            "rb:".ljust(3) + f"{self.pwm['rb']}".rjust(5) + "\n",
            False, 0x000000ff
        )

        surface.blit(text, self.resolve_position())



        if self.gamepad_manager.has():
            gp = self.gamepad_manager.fetch_first()

            pygame.draw.circle(surface, 0x000000, (800, 500), 100)
            pygame.draw.circle(surface, 0xffffff, pygame.Vector2(800, 500) + gp.read_vector(
                *Gamepad.LEFT_STICK
            ) * 100, 20)

            pygame.draw.circle(surface, 0x000000, (1200, 500), 100)
            pygame.draw.circle(surface, 0xffffff, pygame.Vector2(1200, 500) + gp.read_vector(
                *Gamepad.RIGHT_STICK
            ) * 100, 20)
    
    def update(self, dt: float, surface: pygame.Surface):

        # calculate speeds

        # manual override
        keys = pygame.key.get_pressed()
        reverse = keys[pygame.K_KP_0]

        self.pwm['lf'] = (consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE if reverse else consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD) if keys[pygame.K_KP_7] else consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL
        self.pwm['rf'] = (consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE if reverse else consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD) if keys[pygame.K_KP_9] else consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL
        self.pwm['lt'] = (consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE if reverse else consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD) if keys[pygame.K_KP_4] else consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL
        self.pwm['rt'] = (consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE if reverse else consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD) if keys[pygame.K_KP_6] else consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL
        self.pwm['lb'] = (consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE if reverse else consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD) if keys[pygame.K_KP_1] else consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL
        self.pwm['rb'] = (consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE if reverse else consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD) if keys[pygame.K_KP_3] else consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL


        # send data
        self.net.send(packets.PACKET_CONTROL, struct.pack(packets.FORMAT_PACKET_CONTROL,
                                                          self.pwm['lf'],
                                                          self.pwm['rf'],
                                                          self.pwm['lt'],
                                                          self.pwm['rt'],
                                                          self.pwm['lb'],
                                                          self.pwm['rb'],
                                                          self.pwm['ca'],
                                                          self.pwm['tw'],
                                                          self.pwm['tg'],
                                                          ))