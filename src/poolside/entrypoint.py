import pygame

from src.poolside.window import Window

def poolside_main(ip: str, port: int):
    """
    Main Entrypoint for the client.
    """
    pygame.init() # initialise pygame

    wnd = Window(ip, port)
    wnd.run()
