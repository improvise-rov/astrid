import pygame

class Renderer():
    """
    This class is more just for nicer import structure; everything is a static method.
    That meaning, the methods do not belong to an _instance_ of the class, but rather the class itself.

    (If you think about the class as an object instance of 'Class' itself, then a static method is like a instance method on that class. Now you're thinking with ~~portals~~ classes!)
    """
    

    @staticmethod
    def render_text(surface: pygame.Surface, text: str, color: pygame.typing.ColorLike, size: int, pos: pygame.Vector2, bold: bool = False, italic: bool = False):
        font = pygame.font.SysFont('consolas', size, bold, italic)
        surface.blit(font.render(text, False, color), pos)