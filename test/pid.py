##
import sys
sys.path[0] = sys.path[0][:-5] # hack around the fact that this file isnt in the main path so i can access src
##

import pygame
import typing
from src.common import consts
from src.common import rovmath
from src.client.callback import Callback
from src.client.render import Renderer
from src.client.ui import UiContainer, UiLineGraph

class PidTest():
    
    TARGET_FPS: int = 60
    TITLE: str = "impROVise PID Controller Tester"
    W: int = 1280
    H: int = 800
    
    def __init__(self) -> None:
        self.surf = pygame.display.set_mode((PidTest.W, PidTest.H))
        pygame.display.set_caption(PidTest.TITLE)
        self.clock = pygame.Clock()
        self.running = False

        self.value = 10000
        self.pid = rovmath.PIDController(lambda: self.value, 0, 1.0, 0.1, 0.05)
        self.time = 0.0
        self.container = UiContainer()
        self.pid_history: list[tuple[float, float]] = []
        self.line_graph = UiLineGraph(
            pygame.Vector2(200, 200),
            lambda: self.pid_history
        )
        self.line_graph.x_label = "Time (s)"
        self.line_graph.y_label = "Value"
        self.line_graph.draw_points = False

        self.container.add(self.line_graph)

    def run(self):
        self.running = True
        dt = 0.0
        while self.running:
            self.update(dt)
            self.event()
            self.draw(self.surf)
            pygame.display.flip()
            dt = self.clock.tick() / PidTest.TARGET_FPS
        self.stop()


    def update(self, dt: float):
        self.time += dt
        self.container.update(dt, self.surf)
        self.pid.update(dt)
        self.value = self.pid.value
        self.pid_history.append((self.time, self.pid.value))


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
        
        Renderer.draw_text(s, 'impROVise PID controller tester', (20, 20, 0, 0))

        


    def stop(self):
        pass


if __name__ == "__main__":
    pygame.init()
    wnd = PidTest()
    wnd.run()