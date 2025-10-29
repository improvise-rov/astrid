import pygame

from src.client.window import Window

def client_main(ip: str, port: int):
    """
    Main Entrypoint for the client.
    """
    pygame.init() # initialise pygame

    wnd = Window()
    wnd.run()
