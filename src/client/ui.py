from __future__ import annotations
import pygame
import typing
import datetime
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

        Renderer.draw_text(surface, 
                           "lf:".ljust(3) + f"{round(self.rov.motors['lf'], 2)}".rjust(5) + "   " +
                           "rf:".ljust(3) + f"{round(self.rov.motors['rf'], 2)}".rjust(5) + "\n" + 
                           "lt:".ljust(3) + f"{round(self.rov.motors['lt'], 2)}".rjust(5) + "   " +
                           "rt:".ljust(3) + f"{round(self.rov.motors['rt'], 2)}".rjust(5) + "\n" + 
                           "lb:".ljust(3) + f"{round(self.rov.motors['lb'], 2)}".rjust(5) + "   " +
                           "rb:".ljust(3) + f"{round(self.rov.motors['rb'], 2)}".rjust(5) + "\n" +
                           "\n\n\n" +
                           f"camera angle: {round(self.rov.motors['ca'], 2)}\n" +
                           f"grip: {round(self.rov.motors['tg'], 2)}\n" +
                           f"wrist: {round(self.rov.motors['tw'], 2)}\n", 
                           (self.resolve_position(), pygame.Vector2(0, 0)),
                           color='black'
            )
        




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


class UiLineGraph(UiElement):
    """
    Draws a line graph. Origin is top left.
    """

    type _Axis = typing.Literal['x', 'y']

    def __init__(self, pos: pygame.Vector2):
        super().__init__(pos)

        self.x_label = "Time (s)"
        self.y_label = "Depth (m)"

        self.x_range_low = 0
        self.x_range_high = 0
        self.y_range_low = 0
        self.y_range_high = 0

        self.draw_points = True
        self.draw_lines = True
        self.draw_axis_labels = True
        self.draw_axis_numbers = True
        
        self.point_color: pygame.typing.ColorLike = 0xFF000000
        self.line_color: pygame.typing.ColorLike = 0xFF00FF00
        self.axis_color: pygame.typing.ColorLike = 0xFFFFFFFF

        self.axis_line_length = 400
        self.axis_line_width = 8
        self.point_size = 5
        self.line_width = 5
        self.axis_numbers = 5

        self.auto_calculate_bounds = True

        self.points: list[tuple[float, float]] = [(i, i**.5) for i in range(10)]

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        origin = self.resolve_position()
        horizontal = pygame.Vector2(self.axis_line_length, 0)
        vertical = pygame.Vector2(0, self.axis_line_length)

        # draw axis lines
        
        pygame.draw.line(surface, self.axis_color, origin, origin + horizontal, self.axis_line_width)
        # arrow head
        pygame.draw.line(surface, self.axis_color, origin + horizontal, origin+horizontal+pygame.Vector2(-20, 20), self.axis_line_width)
        pygame.draw.line(surface, self.axis_color, origin + horizontal, origin+horizontal+pygame.Vector2(-20, -20), self.axis_line_width)

        pygame.draw.line(surface, self.axis_color, origin, origin + vertical, self.axis_line_width)
        # arrow head
        pygame.draw.line(surface, self.axis_color, origin + vertical, origin+vertical+pygame.Vector2(20, -20), self.axis_line_width)
        pygame.draw.line(surface, self.axis_color, origin + vertical, origin+vertical+pygame.Vector2(-20, -20), self.axis_line_width)

        # draw axis labels
        if self.draw_axis_labels:
            Renderer.draw_text(surface, self.x_label, (origin + pygame.Vector2(0, -60), pygame.Vector2(self.axis_line_length, 30)), 'left_to_right', justify='center', color=self.axis_color, italic=True)
            Renderer.draw_text(surface, self.y_label, (origin + pygame.Vector2(-60, 0), pygame.Vector2(30, self.axis_line_length)), 'bottom_to_top', justify='center', color=self.axis_color, italic=True)

        # draw axis numbers
        if self.draw_axis_numbers:
            for i in range(self.axis_numbers):
                pos = origin + pygame.Vector2(i * self.axis_line_length / self.axis_numbers, -30)
                pygame.draw.line(surface, self.axis_color, pos + pygame.Vector2(0, 30), pos + pygame.Vector2(0, 20), self.axis_line_width // 2)
                Renderer.draw_text(surface, str(round(RovMath.map_no_midpoint(
                    0, self.axis_line_length,
                    i * self.axis_line_length / self.axis_numbers,
                    self.x_range_low, self.x_range_high
                ), 1)), (pos, pygame.Vector2()), 'left_to_right', color=self.axis_color)

            for i in range(self.axis_numbers):
                pos = origin + pygame.Vector2(-30, i * self.axis_line_length / self.axis_numbers)
                pygame.draw.line(surface, self.axis_color, pos + pygame.Vector2(30, 0), pos + pygame.Vector2(20, 0), self.axis_line_width // 2)
                Renderer.draw_text(surface, str(round(RovMath.map_no_midpoint(
                    0, self.axis_line_length,
                    i * self.axis_line_length / self.axis_numbers,
                    self.y_range_low, self.y_range_high
                ), 1)), (pos, pygame.Vector2()), 'bottom_to_top', color=self.axis_color)

        # draw points
        if self.draw_points:
            for (x, y) in self.points:
                pygame.draw.circle(
                    surface, 
                    self.point_color, 
                    (
                        origin.x + (self.axis_line_length * self._map_value('x', x)), 
                        origin.y + (self.axis_line_length * self._map_value('y', y))
                    ),
                    self.point_size
                    )
        
        # draw lines between points
        if self.draw_lines:
            last_point = self.points[0]
            for i, (x, y) in enumerate(self.points):
                if i == 0:
                    continue

                pygame.draw.line(surface, self.line_color, (
                    origin.x + (self.axis_line_length * self._map_value('x', last_point[0])), 
                    origin.y + (self.axis_line_length * self._map_value('y', last_point[1]))
                ), (
                    origin.x + (self.axis_line_length * self._map_value('x', x)), 
                    origin.y + (self.axis_line_length * self._map_value('y', y))
                ), self.line_width)
                last_point = (x, y)

    def update(self, dt: float, surface: pygame.Surface):
        super().update(dt, surface)

        if self.auto_calculate_bounds:
            self.x_range_low = self.points[0][0]
            self.x_range_high = self.points[0][0]
            self.y_range_low = self.points[0][1]
            self.y_range_high = self.points[0][1]

            for (x, y) in self.points:
                if x < self.x_range_low: self.x_range_low = x
                if x > self.x_range_high: self.x_range_high = x
                if y < self.y_range_low: self.y_range_low = y
                if y > self.y_range_high: self.y_range_high = y
    
    def _map_value(self, axis: _Axis, v: float) -> float:
        if axis == 'x':
            return RovMath.map_no_midpoint(
                self.x_range_low, self.x_range_high,
                v,
                0.0, 1.0
            )
        else:
            return RovMath.map_no_midpoint(
                self.y_range_low, self.y_range_high,
                v,
                0.0, 1.0
            )

class UiCountdownClock(UiElement):
    def __init__(self, pos: pygame.Vector2, seconds: float):
        super().__init__(pos)
        self.time = seconds
        self.ticking = True

    def update(self, dt: float, surface: pygame.Surface):
        super().update(dt, surface)
        if self.ticking and self.time > 0:
            self.time -= dt
            if self.time < 0:
                self.time = 0
    
    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        Renderer.draw_text(surface, str(datetime.timedelta(seconds=self.time)), (self.resolve_position(), pygame.Vector2()))