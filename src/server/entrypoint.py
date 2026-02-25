
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

        # motor init seq
        rov.motor_init_seq('left_front')
        rov.motor_init_seq('right_front')
        rov.motor_init_seq('left_top')
        rov.motor_init_seq('right_top')
        rov.motor_init_seq('left_back')
        rov.motor_init_seq('right_back')
        
        while net.is_open(): # loops until the client disconnects!
            rov.tick()
    except:
        pass

    rov.camera_running = False
    rov.hardware.cleanup()
    net.close()

    os.kill(os.getpid(), signal.SIGTERM) # is this bad? i almost guarantee it
        
