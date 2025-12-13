import pygame
import typing


class Callback():

    CALLBACKS: dict[int, list[typing.Callable[[pygame.Event], typing.Any]]] = {}

    @staticmethod
    def add_listener(signal: int, function: typing.Callable[[pygame.Event], typing.Any]):
        arr = Callback.CALLBACKS.get(signal, [])
        arr.append(function)
        Callback.CALLBACKS[signal] = arr