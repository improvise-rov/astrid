from __future__ import annotations
import pygame
import typing

from src.client.draw import Renderer
from src.common.network import Netsock

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

class UiText(UiTexture):
    def __init__(self, pos: pygame.Vector2, text: str, color: pygame.typing.ColorLike, scale: pygame.Vector2 = pygame.Vector2(1, 1), rotation: float = 0, centered: bool = False, sysfont: str = 'consolas'):
        self.font = pygame.font.SysFont(sysfont, 24, False, False)
        super().__init__(pos, self.font.render(text, False, color), scale, rotation, centered)
        self.text = text
        self.color = color

    def set_text(self, text: str):
        self.text = text
        self._update_texture()

    def set_color(self, color: pygame.typing.ColorLike):
        self.color = color

    def _update_texture(self):
        self.original_texture = self.font.render(self.text, False, self.color)
        super()._update_texture()

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
        surface.blit(self.font.render(string, False, 0xffffffff), self.resolve_position() + pygame.Vector2(15, 0))