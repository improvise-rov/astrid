import pygame
import typing


class Callback():
    type _CallbackFunction = typing.Callable[[pygame.Event], typing.Any]

    CALLBACKS: dict[int, list[_CallbackFunction]] = {}

    @staticmethod
    def add_listener(signal: int, function: _CallbackFunction):
        arr = Callback.CALLBACKS.get(signal, [])
        arr.append(function)
        Callback.CALLBACKS[signal] = arr