import pygame

from src.poolside.window import Window

def poolside_main(target_ip: str, target_port: int, port: int):
    """
    Main Entrypoint for the poolside.
    """
    pygame.init() # initialise pygame

    wnd = Window(target_ip, target_port, port)
    wnd.run()
