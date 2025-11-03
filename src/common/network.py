import socket
import threading
import typing
import struct

from src.common import consts
from src.common import packets

"""
The networking needs to be able to do the following:
    - Establish a TCP connection over Ethernet between the two devices
    - Send packets to the other endpoint

Limitations:
    - I only need to be able to have two devices on the network

    
My main problem I've had with this before is way overcomplicating it.


Notes to self:
    - recv only receives what is available ; while loop till received expected amount '; bufsize should be relatively low ^2
    - send returns the number of bytes sent ; while loop till total is expected count
    - sendall does the above for you and blocks until everything is sent
"""

class Netsock():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = threading.Thread(name="Netsock Recv Thread", target=self._recv_thread)

        self._open = False

    def send(self, data: bytes):
        lengthdata = struct.pack(">L", len(data))
        self.sock.sendall(lengthdata + data)

    def _raw_recv(self, n: int) -> bytes:
        data = b''
        while len(data) < n:
            data += self.sock.recv(n - len(data))
        return data

    def _recv_thread(self):
        while self._open:
            # recv length
            target = struct.calcsize(">L")
            data = self._raw_recv(target)
            size = struct.unpack(">L", data)

            # recv data
            data = self._raw_recv(size)



