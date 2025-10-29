import socket
import threading
import typing
import json

from src.common import consts
from src.common import packets

"""
The networking needs to be able to do the following:
    - Establish a TCP connection over Ethernet between the two devices
    - Send packets to the other endpoint

Limitations:
    - I only need to be able to have two devices on the network

    
My main problem I've had with this before is way overcomplicating it.
"""


class NetworkEndpoint():
    """
    Abstract Base Class for networking. Use child classes for ROV or Poolside.
    """
    TARGET_PACKET_SIZE: int = 1024 * 8 # 8kb

    def __init__(self, ip: str, port: int = 8080):
        self.thread = threading.Thread(name="NetworkingThread", target=self._thread) # create a thread to handle networking activities
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a tcp socket
        self.is_open = False

        self.ip = ip
        self.port = port

    def connect(self):
        if not self.is_open:
            self.is_open = True
            self._connect()
        else:
            print("Tried to open socket, but it was already open!")

    def disconnect(self):
        if self.is_open:
            self.is_open = False
            self._disconnect()
        else:
            print("Tried to close socket, but it was already closed!")

    def send(self, data: bytes):
        if self.is_open:
            self.sock.send(data)
        else:
            print("Tried to send packet when socket was not open!")

    def on_recv(self):
        pass

    def _thread(self):
        while self.is_open:
            try:
                if self.sock:
                    self._raw_recv()

            except Exception as e:
                print("Ran into error while receiving: " + str(e))

    def _raw_recv(self):
        # we need to make sure we receive the right amount of bytes
        if self.is_open:
            bytes_read: int = 0
            chunks: list[bytes] = []

            while bytes_read < NetworkEndpoint.TARGET_PACKET_SIZE:
                chunks.append(self.sock.recv(NetworkEndpoint.TARGET_PACKET_SIZE))






    def _connect(self):
        pass

    def _disconnect(self):
        pass



class RovNet(NetworkEndpoint):
    def __init__(self, ip: str, port: int = 8080):
        super().__init__(ip, port)

    def _connect(self):
        self.sock.bind((self.ip, self.port)) # bind server to the desired IP
        self.sock.listen(1)

        # wait for connection
        self.sock.accept()
    
    def _disconnect(self):
        self.sock.close()