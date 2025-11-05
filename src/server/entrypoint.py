
from src.server.camera import CameraFeed
from src.common.network import Netsock
from src.common import packets
import time
import struct
   
    

def server_main(ip: str, port: int):
    """
    Main Entrypoint for the server.
    """

    net = Netsock(ip, port)
    cam = CameraFeed(cam_id=0)

    net.add_packet_handler(packets.PACKET_CONTROL, _recv_control)

    net.start_server()

    while net.is_open(): # blocks until the client disconnects!
        frame = cam.capture()
        net.send(packets.PACKET_CAMERA, frame)
        time.sleep(1/60) # try and keep at 60 loops / seconds

def _recv_control(id: int, data: bytes):
    lf, rf, lt, rt, lb, rb, ca, tw, tg = struct.unpack(packets.FORMAT_PACKET_CONTROL, data)

    print(lf, rf, lt, rt, lb, rb, ca, tw, tg)