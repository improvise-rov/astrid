import pygame

from src.client import Window

def main(ip: str, port: int):
    """
    Main Entrypoint for the client.
    """
    pygame.init() # initialise pygame

    wnd = Window()
    wnd.run()