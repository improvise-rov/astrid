
from src.server.camera import CameraFeed
from src.common.network import Netsock
from src.common import packets
import time
   
    

def server_main(ip: str, port: int):
    """
    Main Entrypoint for the server.
    """

    net = Netsock(ip, port)
    cam = CameraFeed(cam_id=1)

    net.add_packet_handler(packets.PACKET_MSG, lambda id, data: print(data.decode('utf-8')))

    net.start_server()

    while net.is_open(): # blocks until the client disconnects!
        frame = cam.capture()
        net.send(packets.PACKET_CAMERA, frame)
        time.sleep(1/60) # try and keep at 60 loops / seconds