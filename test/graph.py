##
import sys
sys.path[0] = sys.path[0][:-5] # hack around the fact that this file isnt in the main path so i can access src
##

import pygame
import typing
from src.common import consts
from src.common import rovmath
from src.poolside.callback import Callback
from src.poolside.render import Renderer
from src.poolside.ui import UiContainer, UiLineGraph

class ManualGrapher():
    
    TARGET_FPS: int = 60
    TITLE: str = "impROVise manual grapher"
    W: int = 1280
    H: int = 800

    DATA: list[tuple[float, float]] = [
        # time, depth
        (0, 10),
        (10, 20)
    ]
    
    def __init__(self) -> None:
        self.surf = pygame.display.set_mode((ManualGrapher.W, ManualGrapher.H))
        pygame.display.set_caption(ManualGrapher.TITLE)
        self.clock = pygame.Clock()
        self.running = False

        self.container = UiContainer()
        self.line_graph = UiLineGraph(
            pygame.Vector2(80, 80),
            lambda: ManualGrapher.DATA
        )
        self.line_graph.x_label = "Time (s)"
        self.line_graph.y_label = "Depth (m)"
        self.line_graph.drawn_points = -1
        self.line_graph.draw_points = False
        self.line_graph.axis_line_length = 600

        self.container.add(self.line_graph)


    def run(self):
        self.running = True
        dt = 0.0
        while self.running:
            self.update(dt)
            self.event()
            self.draw(self.surf)
            pygame.display.flip()
            dt = self.clock.tick(ManualGrapher.TARGET_FPS) / 1000
        self.stop()


    def update(self, dt: float):
        self.container.update(dt, self.surf)


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
        self.container.draw(s)
        
        Renderer.draw_text(s, ManualGrapher.TITLE, (20, 20, 0, 0), scale=0.5)

        Renderer.draw_text(s, f"Points: {len(ManualGrapher.DATA)}", (850, 20, 0, 0))
        


    def stop(self):
        pass


if __name__ == "__main__":
    pygame.init()
    wnd = ManualGrapher()
    wnd.run()