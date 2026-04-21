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

        self.value = 20
        self.decay_factor = 0.5
        self.time = 0.0
        self.pid = rovmath.PIDController(100)
        self.container = UiContainer()
        self.pid_history: list[tuple[float, float]] = []
        self.line_graph = UiLineGraph(
            pygame.Vector2(80, 80),
            lambda: self.pid_history
        )
        self.line_graph.x_label = "Time (s)"
        self.line_graph.y_label = "Value"
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
            dt = self.clock.tick(PidTest.TARGET_FPS) / 1000
        self.stop()


    def update(self, dt: float):
        self.container.update(dt, self.surf)
        self.time += dt

        modulate = self.pid.compute_modulation(self.value, dt)
            
        self.value += modulate * self.decay_factor * dt
        self.pid_history.append((self.time, self.value))

        # keypress
        press = pygame.key.get_just_pressed()
        if press[pygame.K_UP]: self.pid.target += 1
        if press[pygame.K_DOWN]: self.pid.target -= 1
        if press[pygame.K_LEFT]: self.decay_factor += 0.1
        if press[pygame.K_RIGHT]: self.decay_factor -= 0.1


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
        
        Renderer.draw_text(s, PidTest.TITLE, (20, 20, 0, 0), scale=0.5)

        Renderer.draw_text(s, f"Points: {len(self.pid_history)}", (850, 20, 0, 0))

        Renderer.draw_text(s, f"Value: {self.value:0.1f}", (850, 200, 0, 0))
        Renderer.draw_text(s, f"Target: {self.pid.target:0.1f}", (850, 220, 0, 0))
        Renderer.draw_text(s, f"Natural Decay: {self.decay_factor:0.1f}", (850, 240, 0, 0))

        Renderer.draw_text(s, f"kP: {self.pid.kp}", (850, 270, 0, 0))
        Renderer.draw_text(s, f"kI: {self.pid.ki}", (850, 290, 0, 0))
        Renderer.draw_text(s, f"kD: {self.pid.kd}", (850, 310, 0, 0))

        Renderer.draw_text(s, f"Error: {self.pid._previous_error:.1f}", (850, 340, 0, 0))
        Renderer.draw_text(s, f"Integral: {self.pid._integral:.1f}", (850, 360, 0, 0))
        Renderer.draw_text(s, f"Derivative: {self.pid._derivative:.1f}", (850, 380, 0, 0))
        


    def stop(self):
        pass


if __name__ == "__main__":
    pygame.init()
    wnd = PidTest()
    wnd.run()