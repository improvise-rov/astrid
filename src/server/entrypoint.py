
from src.server.camera import CameraFeed
from src.common.network import Netsock
from src.common import packets
import time
import struct
   
    

def server_main(ip: str, port: int):
    """
    Main Entrypoint for the server.
    """

    net = Netsock(ip, port) # create networking socket
    cam = CameraFeed(cam_id=0) # create camera handler

    # register control packet handler; 
    # this tells the networking socket's processing thread to run _recv_control 
    # whenever a new PACKET_CONTROL packet is received
    net.add_packet_handler(packets.PACKET_CONTROL, _recv_control)

    net.start_server() # start the server (blocks until client connects)

    while net.is_open(): # blocks until the client disconnects!
        frame = cam.capture() # get frame from camera
        net.send(packets.PACKET_CAMERA, frame) # send the camera frame down socket
        time.sleep(1/60) # try and keep at 60 loops / second (this is not really acccurate, as it takes time to do everything. but its approximate enough.)

def _recv_control(id: int, data: bytes):
    """
    runs when the server receives information from the client about controls.

    this data, to reduce processing time, should not be validated (that should be done on the client)
    assume everything is always okay, and take numbers at face value.
    that is usually a terrible idea, but i dont care. its fine for this

    lf: front left motor esc
    rf: front right motor esc
    lt: top left motor esc
    rt: top right motor esc
    lb: left back motor esc
    rb: right back motor esc
    ca: camera angle servo
    tw: tool wrist servo
    tg: tool grip servo
    """
    lf, rf, lt, rt, lb, rb, ca, tw, tg = struct.unpack(packets.FORMAT_PACKET_CONTROL, data)

    print(lf, rf, lt, rt, lb, rb, ca, tw, tg)