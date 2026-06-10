import typing
import time
import socket
import struct
import threading

type _Packet = tuple[int, str | None] # id, struct format string (raw bytes if none)
type _Addr = tuple[str, int] # ip, port
type _Listener = typing.Callable[..., None] # the first argument is ALWAYS of type _Addr, but the type system isnt complex enough to let me put that in

class Networker():
    """
    v2 ROV netcode. relatively abstract.

    uses UDP sockets
    """

    # this system is.. quite complicated
    # it is by no means perfect
    # i wrote it with the intention that it is not tied to this program (look at the import list, nothing from this project. everything this file needs is in this file)
    # however, the packets are defined elsewhere for simplicity
    # a packet is defined like this
    # PACKET_TYPE_AS_SOME_CONSTANT: _Packet = (<unique numerical id of the packet>, <format of the packet, or None (treated as raw bytes if None)>) 
    # 
    # the general structure of a packet is like this
    # <the header> <the data>
    # the header says what the id and the format is
    # internally the packets are referenced by the unique id
    # the unique id is stored as an unsigned short, so 16 bytes, can have up to (2^16)-1 types. more than enough!
    #
    # general rule of thumb: if a function is prefixed with an underscore, you probably shouldnt need to be using it outside this file

    PACKET_HEADER: str = ">H16s" # i cant remember what each character means. google "python struct formats"

    def __init__(self, target_ip: str, target_port: int, port: int, packet_size: int) -> None:
        self.target_ip = target_ip # where to send packets to?
        self.target_port = target_port # which port am i SENDING to
        self.port = port # which port am i RECEIVING on?
        self.packet_size = packet_size # how many (boosters) bytes are in the packets?

        self.open = False

        self.target_addr: _Addr | None = None # combination of target ip and target port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # actual socket object

        self.listeners: dict[int, list[_Listener]] = {} # callbacks for each packet type
        self.recv_thread: threading.Thread # thread that handles incoming traffic

    def start(self) -> bool:
        """
        starts up the network.
        """
        print(f"starting networker (listening on port {self.port}, sending to {self.target_ip}:{self.target_port})")
        self.socket.bind(('', self.port)) # set the listening port
        self.target_addr = (self.target_ip, self.target_port) # build target address
        self.open = True # declares the network open for business


        self.recv_thread = threading.Thread(name="NetworkerRecvThread", target=self._recv_thread) # build the thread
        self.recv_thread.start()
        self.socket.settimeout(1.0) # after how many seconds does it give up on waiting for a packet? (stops the program freezing)
        
        return True # i cant remember why i made it return true



    def build_packet(self, pkt_type: _Packet, *data) -> bytes:
        """
        bundles the packet and abstract data into bytes, ready to be sent.
        """
        pkt_id, format = pkt_type # we dont actually care about the packet id here..

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
        """
        sends a packet with type and its abstract data.
        """
        if self.target_addr: # if we have the target address..
            #print("send", type, self.target_addr) # debug line that prints out sent packets
            self._send(self.target_addr, self.build_packet(type, *data))

    def wait_for_packet(self, type: _Packet, timeout: float = 1.0) -> tuple[bytes, _Addr] | None:
        """
        waits to receive a packet of a certain type. useful when listening for specific packets
        """
        id = -1 # default id is negative one because you probably shouldnt do that.
        data = None

        start = time.time() # to count timeout

        while id != type[0] and time.time() <= start + timeout:
            result = self._recv() # receive..
            if result: # if we get a result
                id, data, addr = result # extract the data from the tuple
                if id[0] == type[0]: # if the type matches what we want
                    return data, addr
                
        return None
    
    def register_listener(self, type: _Packet, func: _Listener) -> _Listener:
        """
        register a callback to a certain packet type's reception.
        """
        arr = self.listeners.get(type[0], [])
        arr.append(func)
        self.listeners[type[0]] = arr
            
        return func
    
    def is_open(self) -> bool:
        """
        more or less, "are we connected?"
        """
        return self.open
    
    def close(self):
        """
        stop sending and receiving
        """
        print("closing")
        self.open = False

    def set_target_address(self, addr: _Addr):
        """
        update target address
        """
        self.target_ip = addr[0]
        self.target_port = addr[1]
        self.target_addr = addr

    def _send(self, addr: _Addr, pkt: bytes):
        """
        low level raw send bytes down socket. ignores timeouts.
        """
        if self.is_open():
            try:
                self.socket.sendto(pkt, addr)
            except TimeoutError:
                return

    def _recv(self) -> tuple[_Packet, bytes, _Addr] | None:
        """
        low level raw receive bytes from socket. ignores errors. returns the packet type, raw bytes and source address.
        """
        if self.is_open():
            try:
                raw_pkt, addr = self.socket.recvfrom(self.packet_size)
                pkt_type, data = self._unpack_header(raw_pkt)
                #print("recv", pkt_type, self.target_addr) # debug line that prints out received packets
                return pkt_type, data, addr
            except:
                return None
        else:
            return None


    def _build_raw_packet(self, id: _Packet, data: bytes) -> bytes:
        """
        builds a packet type and data bytes into a complete packet.
        """
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
        """
        unpack the packet type and data bytes from a complete packet
        """
        header_size = struct.calcsize(Networker.PACKET_HEADER)
        id, format = struct.unpack_from(Networker.PACKET_HEADER, raw_pkt)

        decoded_format = bytes(format).decode()
        if decoded_format == 16*'\0':
            decoded_format = None
        else:
            decoded_format = decoded_format.rstrip("\0")

        return (id,  decoded_format), raw_pkt[header_size:]
    
    def _unpack_data(self, type: _Packet, data: bytes) -> tuple[typing.Any, ...]:
        """
        unpacks an indeterminate amount of data according to the packet type structure from packet data
        """
        if type[1] == None:
            return data,
        else:
            # add padding bytes based off length
            format = type[1] + ("x" * (len(data) - struct.calcsize(type[1])))

            return struct.unpack(format, data)

    def _recv_thread(self):
        """
        process that runs to receive packets and handle the listeners
        """
        while self.open:
            packet = self._recv()
            if packet:
                type, data, addr = packet
                arr = self.listeners.get(type[0], [])
                for listener in arr:
                    listener(addr, *self._unpack_data(type, data))
