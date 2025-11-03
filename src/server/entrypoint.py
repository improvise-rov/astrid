
from src.server.camera import CameraFeed
from src.common.network import Netsock
from src.common import packets
import struct
   
    

def server_main(ip: str, port: int):
    """
    Main Entrypoint for the server.
    """

    net = Netsock(ip, port)
    cam = CameraFeed()

    net.start_server()

    while net.is_open(): # blocks until the client disconnects!
        frame = cam.capture()
        net.send(packets.PACKET_CAMERA, frame)
