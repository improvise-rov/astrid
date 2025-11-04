import socket
import threading
import typing
import struct

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
    type _PacketCallback = typing.Callable[[int, bytes], typing.Any]
    HEADER_STRUCT_FORMAT: str = '>LH'
    GIVE_UP_POINT: int = 10
    READ_SIZE: int = 4096

    def __init__(self, ip: str, port: int):
        self._make_socket()

        self.ip = ip
        self.port = port

        self._recent_packet_type: int = -1
        self._consecutive_errors: int = 0
        self._open = False
        self._is_server = False

        self._pipe_socket: socket.socket = self.sock

        self._packet_handlers: dict[int, list[Netsock._PacketCallback]] = {}

        self.add_packet_handler(packets.PACKET_DISCONNECT,
                                lambda id, data: self._remote_disconnect())


    def start_server(self):
        if self._open:
            return
        print("starting server", flush=True)

        self._open = True
        self._is_server = True

        self._make_socket()
        self.sock.bind((self.ip, self.port))
        self.sock.listen()
        self._pipe_socket, addr = self.sock.accept()
        print("accepted connection at " + str(addr))

        self.thread.start()

    def start_client(self):
        if self._open:
            return
        print("starting client", flush=True)
        
        try:
            self._is_server = False

            self._make_socket()
            self.sock.connect((self.ip, self.port))
            self._pipe_socket = self.sock
            print("connected to server")
            self._open = True

            self.thread.start()
        except:
            print("failed to start client (the server is probably not open yet)")

    def disconnect(self):
        self.send(packets.PACKET_DISCONNECT, b'')
        self.wait_for_packet(packets.PACKET_DISCONNECT_ACK)

    def close(self):
        self._open = False
        
        self._pipe_socket.close()
        if self._is_server:
            self.sock.close()

    def send(self, type: int, data: bytes):
        if not self._open:
            return

        try:
            lengthdata = struct.pack(Netsock.HEADER_STRUCT_FORMAT, len(data), type)
            self._pipe_socket.sendall(lengthdata + data)
            self._consecutive_errors = 0 # reset consecutive errors
        except Exception as e:
            if self._open:
                print(f"error sending data: " + str(e))
                self._consecutive_errors += 1
                self._check_giveup()

    def wait_for_packet(self, type: int):
        """
        blocks thread till a packet of the specified type is recv'd. useful for ack.
        """
        if not self._open:
            return

        while True:
            if self._recent_packet_type == type:
                break

    def is_open(self) -> bool:
        return self._open
            
    
    def _recv(self, n: int) -> bytes:
        data = b''
        while len(data) < n:
            pckt = self._pipe_socket.recv(n - len(data))
            if not pckt:
                raise ValueError("received None packet")
            data += pckt
        return data 

    def _recv_thread(self):
        while self._open:
            try:

                # recv length
                headersize = struct.calcsize(Netsock.HEADER_STRUCT_FORMAT)
                data = self._recv(headersize)
                size, id = struct.unpack(Netsock.HEADER_STRUCT_FORMAT, data)
                self._recent_packet_type = id

                # recv data
                data = self._recv(size)
                self._handle_packet(id, data)
                self._consecutive_errors = 0 # reset consecutive errors
            except Exception as e:
                if self._open:
                    print("error recv'ing data: " + str(e))
                    self._consecutive_errors += 1
                    self._check_giveup()

    def _handle_packet(self, id: int, data: bytes):
        callbacks = self._packet_handlers.get(id, [])
        for callback in callbacks:
            callback(id, data)

    def _check_giveup(self):
        if self._consecutive_errors >= Netsock.GIVE_UP_POINT:
            print("Reached give up threshold. Closing socket..")
            self.close()

    def _make_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = threading.Thread(name="Netsock Recv Thread", target=self._recv_thread, daemon=True)

    def _remote_disconnect(self):
        print("remote disconnecting, acknowledging...")
        self.send(packets.PACKET_DISCONNECT_ACK, b'')
        self.close()

    def add_packet_handler(self, id: int, callback: _PacketCallback):
        callbacks = self._packet_handlers.get(id, [])
        callbacks.append(callback)
        self._packet_handlers[id] = callbacks



