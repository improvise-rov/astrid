from __future__ import annotations
import typing


def listen(func, observer: Observer):
    """
    decorator
    """
    observer._add(func)
    return func

class Observer():
    """
    implementation of observer pattern
    """
    def __init__(self) -> None:
        self.listeners: list[typing.Callable[..., None]] = []

    def _add(self, func: typing.Callable[..., None]):
        self.listeners.append(func)

    def invoke(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)