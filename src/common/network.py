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
    SIZE_PACKET_SIZE: int = 4
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

    def disconnect(self, send_packet: bool = True):
        if self.is_open:
            if send_packet:
                self._send_disconnect_packet()
            self.is_open = False
            self._disconnect()
        else:
            print("Tried to close socket, but it was already closed!")

    def send(self, id: int, data: dict[str, typing.Any]):
        data['id'] = id
        self._raw_send(json.dumps(data).encode('utf-8'))

    def on_recv(self):
        pass

    def _thread(self):
        while self.is_open:
            try:
                if self.sock:
                    data = self._raw_recv()
                    self._parse(data)

            except Exception as e:
                print("Ran into error while receiving: " + str(e))

    def _raw_send(self, data: bytes):
        if self.is_open:
            self.sock.send(data)
        else:
            print("Tried to send packet when socket was not open!")

    def _raw_recv(self) -> dict:
        # we need to make sure we receive the right amount of bytes
        if self.is_open:

            target_size = int.from_bytes(self.sock.recv(NetworkEndpoint.SIZE_PACKET_SIZE))

            bytes_read: int = 0
            chunks: list[bytes] = []

            while bytes_read < target_size:
                byte = self.sock.recv(target_size)
                chunks.append(byte)
                bytes_read += len(byte)

            return json.loads(b''.join(chunks).decode('utf-8')) # join up chunks and return parsed table
        
        raise RuntimeError("Tried to _raw_recv when not connected")


    def _connect(self):
        pass

    def _disconnect(self):
        pass

    def _parse(self, data: dict):
        pass

    def _send_disconnect_packet(self):
        pass



class RovNet(NetworkEndpoint):
    def _connect(self):
        self.sock.bind((self.ip, self.port)) # bind server to the desired IP
        self.sock.listen(1)

        # wait for connection
        self.sock.accept()
    
    def _disconnect(self):
        self.sock.close()

    def _parse(self, data: dict):
        match data['id']:
            case packets.PACKET_NONE:
                pass
            case packets.PACKET_S2C_HANDSHAKE:
                self.send(packets.PACKET_C2S_HANDSHAKE, {})
            case packets.PACKET_S2C_DISCONNECT:
                self.disconnect(send_packet=False)
            case packets.PACKET_S2C_CAMERA:
                pass

    def _send_disconnect_packet(self):
        self.send(packets.PACKET_S2C_DISCONNECT, {})

class PoolsideNet(NetworkEndpoint):
    def _connect(self):
        self.sock.connect((self.ip, self.port)) # bind server to the desired IP
    
    def _disconnect(self):
        self.sock.close()
    
    def _send_disconnect_packet(self):
        self.send(packets.PACKET_C2S_DISCONNECT, {})