import typing
import pygame

class Renderer():
    """
    Helper class for rendering stuff.
    """

    type _TextJustification = typing.Literal['left', 'right', 'center']
    type _Orientation = typing.Literal['left_to_right', 'right_to_left', 'top_to_bottom', 'bottom_to_top']
    type _LabelSupplier = typing.Callable[[str, pygame.typing.RectLike, pygame.Surface], None] | None

    @staticmethod
    def init():
        pass

    
    @staticmethod
    def draw_text(surface: pygame.Surface, text: str, rect: pygame.typing.RectLike, orientation: _Orientation = 'left_to_right', scale: float = 1.0, color: pygame.typing.ColorLike = 'white', justify: _TextJustification = 'left', font: str = 'src/resource/LeagueSpartan-SemiBold.ttf', sysfont: bool = False, bold: bool = False, italic: bool = False, underline: bool = False, strikethrough: bool = False, draw_rect: bool = False):
        
        # fix like types
        rect = pygame.Rect(rect)
        color = pygame.Color(color)

        # font
        if sysfont:
            f = pygame.font.SysFont(font, 24)
        else:
            f = pygame.font.Font(font, 24)
        f.set_bold(bold)
        f.set_italic(italic)
        f.set_underline(underline)
        f.set_strikethrough(strikethrough)

        if orientation == 'right_to_left':
            raise Exception("text cant be drawn right to left")
        
        match justify:
            case 'left': f.align = pygame.FONT_LEFT
            case 'center': f.align = pygame.FONT_CENTER
            case 'right': f.align = pygame.FONT_RIGHT

        # render
        major_length = 0
        match orientation:
            case 'left_to_right': major_length = rect.width
            case 'top_to_bottom': major_length = rect.height
            case 'bottom_to_top': major_length = rect.height

        s = f.render(text, color=color, antialias=False, wraplength=int(major_length/scale))

        if orientation != 'left_to_right':
            s = pygame.transform.rotate(s, 90)
            if orientation == 'top_to_bottom':
                s = pygame.transform.flip(s, True, True)

        og_rect = rect.copy()
        if scale != 1.0:
            s = pygame.transform.scale_by(s, scale)

        if justify == 'right':
            rect.x -= s.get_rect().w

        surface.blit(s, rect)
        if draw_rect:
            pygame.draw.rect(surface, 'red', og_rect, 2)

    @staticmethod
    def draw_boolean_circle(surface: pygame.Surface, pos: pygame.Vector2, bool: bool, true_label: str, false_label: str, label_supplier: _LabelSupplier = None):
        pygame.draw.circle(surface, 0x000000, pos, 10)
        pygame.draw.circle(surface, 0x00ff00 if bool else 0xff0000, pos, 8)
        Renderer._supply_label(true_label if bool else false_label, (pos + pygame.Vector2(15, -12), pygame.Vector2(0, 0)), surface, label_supplier)

    @staticmethod
    def draw_progress_bar(surface: pygame.Surface, topleft: pygame.Vector2, length: float, width: float, progress: float, absolute: bool = True, orientation: _Orientation = 'left_to_right', outline_color: pygame.typing.ColorLike = 'black', fill_color: pygame.typing.ColorLike = 'white', outline_width: int = 8):

        rect = pygame.Rect(topleft, pygame.Vector2(length, width))

        if absolute:
            progress = abs(progress)

            match orientation:
                case 'left_to_right': rect = rect
                case 'right_to_left': rect = rect
                case 'top_to_bottom': rect.w, rect.h = rect.h, rect.w
                case 'bottom_to_top': rect.w, rect.h = rect.h, rect.w

            pygame.draw.rect(surface, outline_color, rect, outline_width)

            if orientation == 'left_to_right':
                pygame.draw.rect(surface, fill_color, pygame.Rect(rect.x + outline_width, rect.y + outline_width, (rect.w - outline_width * 2) * progress, (rect.h - outline_width * 2)))
            elif orientation == 'right_to_left':
                pygame.draw.rect(surface, fill_color, pygame.Rect(
                    rect.x + outline_width - (rect.w - outline_width * 2) * (progress - 1), 
                    rect.y + outline_width,
                    (rect.w - outline_width * 2) * progress, 
                    (rect.h - outline_width * 2)
                    ))
            elif orientation == 'bottom_to_top':
                pygame.draw.rect(surface, fill_color, pygame.Rect(
                    rect.x + outline_width, 
                    rect.y + outline_width - (rect.h - outline_width * 2) * (progress - 1),
                    (rect.w - outline_width * 2), 
                    (rect.h - outline_width * 2) * progress
                    ))
            else:
                pygame.draw.rect(surface, fill_color, pygame.Rect(rect.x + outline_width, rect.y + outline_width, (rect.w - outline_width * 2), (rect.h - outline_width * 2) * progress))
        else:
            # im cheating

            xoff, yoff = 0, 0
            rect = pygame.Rect(rect.x, rect.y, rect.w / 2, rect.h)

            match orientation:
                case 'left_to_right': xoff, yoff =  rect.w,  0
                case 'right_to_left': xoff, yoff = -rect.w,  0
                case 'top_to_bottom': xoff, yoff =  0,  rect.w
                case 'bottom_to_top': xoff, yoff =  0, -rect.w

            # positive
            Renderer.draw_progress_bar(surface, pygame.Vector2(rect.x + xoff, rect.y + yoff), rect.w, rect.h, 0 if progress <= 0 else abs(progress), True, orientation=orientation, outline_color=outline_color, fill_color=fill_color, outline_width=outline_width)

            # negative
            Renderer.draw_progress_bar(surface, topleft, length, width, 0 if progress >= 0 else abs(progress), True, Renderer._get_opposite_orientation(orientation), outline_color, fill_color, outline_width)

            
    @staticmethod
    def _get_opposite_orientation(orientation: _Orientation) -> _Orientation:
        match orientation:
            case 'left_to_right': return 'right_to_left' 
            case 'right_to_left': return 'left_to_right' 
            case 'top_to_bottom': return 'bottom_to_top' 
            case 'bottom_to_top': return 'top_to_bottom' 

    @staticmethod
    def _supply_label(txt: str, r: pygame.typing.RectLike, s: pygame.Surface, label_supplier: _LabelSupplier):
        if label_supplier is None:
            Renderer.draw_text(s, txt, r)
        else:
            label_supplier(txt, r, s)