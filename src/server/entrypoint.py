
from src.server.camera import CameraFeed
from src.server.hardware import HardwareManager
from src.server.rov import Rov
from src.common.network import Netsock
from src.common import packets
from src.common import consts
import os, signal

def server_main(ip: str, port: int, simulated_hardware: bool):
    """
    Main Entrypoint for the server.
    """

    if simulated_hardware:
        print("(simulating hardware)")

    net = Netsock(ip, port) # create networking socket
    cam = CameraFeed(cam_id=consts.CAMERA_ID) # create camera handler
    hardware = HardwareManager(simulated_hardware)

    # register kill packet
    net.add_packet_handler(packets.STOP_SERVER, lambda id, data, args: net.stop_server())

    rov = Rov(cam, net, hardware)

    try:
        net.start_server() # start the server (blocks until client connects)

        
        while net.is_open(): # loops until the client disconnects!
            rov.tick()
    except:
        pass

    rov.camera_running = False
    net.close()

    os.kill(os.getpid(), signal.SIGTERM) # is this bad? i almost guarantee it
        
