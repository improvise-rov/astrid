from __future__ import annotations
import pygame
import io

from src.client.irov import RovInterface
from src.client.logger import Logger
from src.client.callback import Callback
from src.client.render import Renderer
from src.common.network import Netsock
from src.common.rovmath import RovMath
from src.common import packets
from src.common import consts

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
        

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        string = f" ({self.net.ip}:{self.net.port})"
        Renderer.draw_boolean_circle(surface, self.resolve_position(), self.net.is_open(), "Connected" + string, "Not Connected" + string)

class UiCameraFeed(UiElement):
    def __init__(self, pos: pygame.Vector2, no_conn_img: pygame.Surface, net: Netsock):
        super().__init__(pos)
        self.net = net

        self._no_connection_frame = no_conn_img
        self._last_frame = pygame.Surface(self._no_connection_frame.size)
        self.net.add_packet_handler(packets.CAMERA, self._recv_camera_frame)

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

    def __init__(self, pos: pygame.Vector2, rov: RovInterface):
        super().__init__(pos)

        self.rov = rov

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        #Renderer.draw_text(surface, 
        #                   "lf:".ljust(3) + f"{round(self.rov.motors['lf'], 2)}".rjust(5) + "   " +
        #                   "rf:".ljust(3) + f"{round(self.rov.motors['rf'], 2)}".rjust(5) + "\n" + 
        #                   "lt:".ljust(3) + f"{round(self.rov.motors['lt'], 2)}".rjust(5) + "   " +
        #                   "rt:".ljust(3) + f"{round(self.rov.motors['rt'], 2)}".rjust(5) + "\n" + 
        #                   "lb:".ljust(3) + f"{round(self.rov.motors['lb'], 2)}".rjust(5) + "   " +
        #                   "rb:".ljust(3) + f"{round(self.rov.motors['rb'], 2)}".rjust(5) + "\n" +
        #                   "\n\n\n" +
        #                   f"camera angle: {round(self.rov.motors['ca'], 2)}\n" +
        #                   f"grip: {round(self.rov.motors['tg'], 2)}\n" +
        #                   f"wrist: {round(self.rov.motors['tw'], 2)}\n", 
        #                   (self.resolve_position(), pygame.Vector2(0, 0)),
        #                   color='black'
        #    )
        
        Renderer.draw_progress_bar(surface, self.resolve_position() + pygame.Vector2(0, 0), 80, 20, RovMath.map(
            consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_NEUTRAL, consts.MOTOR_THROTTLE_POSITIVE,
            -self.rov.motors['lf'],
            -1.0, 0.0, 1.0
        ), absolute=False, orientation='top_to_bottom')

        Renderer.draw_progress_bar(surface, self.resolve_position() + pygame.Vector2(50, 0), 80, 20, RovMath.map(
            consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_NEUTRAL, consts.MOTOR_THROTTLE_POSITIVE,
            -self.rov.motors['rf'],
            -1.0, 0.0, 1.0
        ), absolute=False, orientation='top_to_bottom')

        Renderer.draw_progress_bar(surface, self.resolve_position() + pygame.Vector2(0, 100), 80, 20, RovMath.map(
            consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_NEUTRAL, consts.MOTOR_THROTTLE_POSITIVE,
            -self.rov.motors['lt'],
            -1.0, 0.0, 1.0
        ), absolute=False, orientation='top_to_bottom')

        Renderer.draw_progress_bar(surface, self.resolve_position() + pygame.Vector2(50, 100), 80, 20, RovMath.map(
            consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_NEUTRAL, consts.MOTOR_THROTTLE_POSITIVE,
            -self.rov.motors['rt'],
            -1.0, 0.0, 1.0
        ), absolute=False, orientation='top_to_bottom')

        Renderer.draw_progress_bar(surface, self.resolve_position() + pygame.Vector2(0, 200), 80, 20, RovMath.map(
            consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_NEUTRAL, consts.MOTOR_THROTTLE_POSITIVE,
            -self.rov.motors['lb'],
            -1.0, 0.0, 1.0
        ), absolute=False, orientation='top_to_bottom')

        Renderer.draw_progress_bar(surface, self.resolve_position() + pygame.Vector2(50, 200), 80, 20, RovMath.map(
            consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_NEUTRAL, consts.MOTOR_THROTTLE_POSITIVE,
            -self.rov.motors['rb'],
            -1.0, 0.0, 1.0
        ), absolute=False, orientation='top_to_bottom')




class UiCorrectionSubsysStatus(UiElement):
    def __init__(self, pos: pygame.Vector2, rov: RovInterface):
        super().__init__(pos)
        self.rov = rov

        

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        string = "IMU-based Angular Correction "
        Renderer.draw_boolean_circle(surface, self.resolve_position(), self.rov.correction_enabled, string + "Enabled", string + "Disabled")

class UiTextLog(UiElement):
    def __init__(self, pos: pygame.Vector2, dimensions: pygame.Vector2, lines: int):
        super().__init__(pos)

        self.dimensions = dimensions

        self.recent_lines: list[str] = []
        self.lines = lines

        Callback.add_listener(Logger.LOG_EVENT, self._log)
        

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        pygame.draw.rect(surface, 0x000000, (
            self.resolve_position(),
            self.dimensions
        ))

        Renderer.draw_text(
                surface, "\n".join(self.recent_lines), 
                (self.resolve_position() + pygame.Vector2(15, 15), 
                 pygame.Vector2(self.dimensions.x - 15, 30))
                 )


    def _log(self, e: pygame.Event):
        line: str = f"[{e.dict['idx']}] {e.dict['s']}"
        self.recent_lines.append(line)
        if len(self.recent_lines) > self.lines:
            self.recent_lines.pop(0)
