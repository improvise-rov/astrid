import typing
import time
import socket
import struct
import threading

type _Packet = tuple[int, str | None] # id, struct format string (raw bytes if none)
type _Addr = tuple[str, int] # ip, port
type _Listener = typing.Callable[[_Addr, tuple[typing.Any, ...]], None]

class Networker():
    """
    v2 ROV netcode. relatively abstract.

    uses UDP sockets
    """

    PACKET_HEADER: str = ">H16s"

    def __init__(self, target_ip: str, target_port: int, port: int,packet_size: int) -> None:
        self.target_ip = target_ip
        self.target_port = target_port
        self.port = port
        self.packet_size = packet_size

        self.open = False

        self.target_addr: _Addr | None = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.listeners: dict[_Packet, list[_Listener]] = {}
        self.recv_thread: threading.Thread

    def start(self) -> bool:
        print(f"starting networker (listening on port {self.port}, sending to {self.target_ip}:{self.target_port})")
        self.socket.bind(('', self.port))
        self.target_addr = (self.target_ip, self.target_port)
        self.open = True


        self.recv_thread = threading.Thread(name="NetworkerRecvThread", target=self._recv_thread)
        self.recv_thread.start()
        self.socket.settimeout(1.0)
        
        return True



    def build_packet(self, pkt_type: _Packet, *data) -> bytes:
        pkt_id, format = pkt_type

        pkt_bytes: bytes
        if format:
            pkt_bytes = struct.pack(format, *data)
        else:
            if len(data) <= 0:
                pkt_bytes = bytes()
            elif type(data[0]) is bytes:
                pkt_bytes = data[0]
            else:
                raise TypeError("cannot pack this type (packet type might have no data attachment or want raw bytes)")
        
        return self._build_raw_packet(pkt_type, pkt_bytes)
    
    def send(self, type: _Packet, *data):
        if self.target_addr:
            #print("send", type, self.target_addr)
            self._send(self.target_addr, self.build_packet(type, *data))

    def wait_for_packet(self, type: _Packet, timeout: float = 1.0) -> tuple[bytes, _Addr] | None:
        id = -1
        data = None

        start = time.time()

        while id != type[0] and time.time() <= start + timeout:
            result = self._recv()
            if result:
                id, data, addr = result
                if id[0] == type[0]:
                    return data, addr
                
        return None
    
    def register_listener(self, type: _Packet, func: _Listener) -> _Listener:
        arr = self.listeners.get(type, [])
        arr.append(func)
        self.listeners[type] = arr
            
        return func
    
    def is_open(self) -> bool:
        return self.open
    
    def close(self):
        print("closing")
        self.open = False

    def set_target_address(self, addr: _Addr):
        self.target_addr = addr

    def _send(self, addr: _Addr, pkt: bytes):
        if self.is_open():
            try:
                self.socket.sendto(pkt, addr)
            except TimeoutError:
                return

    def _recv(self) -> tuple[_Packet, bytes, _Addr] | None:
        if self.is_open():
            try:
                raw_pkt, addr = self.socket.recvfrom(self.packet_size)
                pkt_type, data = self._unpack_header(raw_pkt)
                #print("recv", pkt_type, self.target_addr)
                return pkt_type, data, addr
            except:
                return None
        else:
            return None


    def _build_raw_packet(self, id: _Packet, data: bytes) -> bytes:
        header_size = struct.calcsize(Networker.PACKET_HEADER)

        if len(data) > self.packet_size - header_size:
            raise OverflowError(f"packet data too big! (max: {self.packet_size - header_size}, got: {len(data)})")
        
        packet = [0x0 for i in range(self.packet_size)]

        # pack header
        pkt_id, format = id
        header = struct.pack(Networker.PACKET_HEADER, pkt_id, format.encode() if format else bytes())
        packet[0:len(header)] = header

        # pack data
        packet[len(header):self.packet_size] = data

        # pad
        while len(packet) < self.packet_size:
            packet += [0x0]

        assert len(packet) == self.packet_size
        return bytes(packet)
    
    def _unpack_header(self, raw_pkt: bytes) -> tuple[_Packet, bytes]:
        header_size = struct.calcsize(Networker.PACKET_HEADER)
        id, format = struct.unpack_from(Networker.PACKET_HEADER, raw_pkt)
        return (id, None if bytes(format).decode() == 16*'\0' else format), raw_pkt[header_size:]
    
    def _unpack_data(self, type: _Packet, data: bytes) -> tuple[typing.Any, ...]:
        if type[1] == None:
            return data,
        else:
            return struct.unpack(type[1], data)

    def _recv_thread(self):
        while self.open:
            packet = self._recv()
            if packet:
                type, data, addr = packet
                arr = self.listeners.get(type, [])
                for listener in arr:
                    listener(addr, *self._unpack_data(type, data))
