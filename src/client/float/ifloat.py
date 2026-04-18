import typing
import pygame
import struct
from src.common import packets
from src.common import consts
from src.common import types
from src.common import rovmath
from src.common.network import Netsock



class FloatInterface():
    """
    Interface to our float, Morag
    """
    FLOAT_IP: str = ""
    FLOAT_PORT: int = 8090

    def __init__(self) -> None:
        self.net = Netsock()