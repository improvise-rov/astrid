"""
Test script to simulate the float.

Since we dont have the ESP32s at time of writing, this stands as a test for the poolside code.
This is also a template for the networking micropython that needs to be written on them.
"""

import socket
import struct

from src.common import consts
from src.client.float import packets


class FloatNetworker():
    HEADER_FORMAT: str = '>H' # id
    POINT_FORMAT: str = '>ff' # time, depth
    OTHER_DATA_FORMAT: str = ">if" # profile no., temperature

    type _addr = tuple[str, int]

    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # use UDP
        self.client.settimeout(1)
    
    def send(self, packet: bytes):
        self.client.sendto(packet, (consts.FLOAT_IP, consts.FLOAT_PORT))

    def wait_for_packet(self, type: int) -> bytes | None:
        try:
            id = -1
            data = bytes()
            while id != type:
                data, addr = self.client.recvfrom(consts.FLOAT_PACKET_SIZE)
                id, = struct.unpack_from(FloatNetworker.HEADER_FORMAT, data)

            return data[struct.calcsize(FloatNetworker.HEADER_FORMAT):]
        except ConnectionResetError:
            return None
        except TimeoutError:
            return None
            

    @staticmethod
    def build_packet(id: int, data: bytes = bytes()) -> bytes:

        if len(data) > consts.FLOAT_PACKET_SIZE - struct.calcsize(FloatNetworker.HEADER_FORMAT):
            raise OverflowError(f"too much data! max is {consts.FLOAT_PACKET_SIZE - struct.calcsize(FloatNetworker.HEADER_FORMAT)}, this is {len(data)}")

        packet = [0x0 for i in range(consts.FLOAT_PACKET_SIZE)]
        header = struct.pack(FloatNetworker.HEADER_FORMAT, id)

        packet[0:len(header)] = header

        packet[len(header):consts.FLOAT_PACKET_SIZE] = data

        while len(packet) < 1024:
            packet += [0x0]

        return bytes(packet)
    