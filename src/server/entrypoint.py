
from src.server.camera import CameraFeed
from src.server.hardware import HardwareManager
from src.server.rov import Rov
from src.common.net.worker import Networker, _Addr
from src.common.net import packets
from src.common import consts
import os, signal

def server_main(ip: str, port: int, simulated_hardware: bool):
    """
    Main Entrypoint for the server.
    """

    if simulated_hardware:
        print("(simulating hardware)")

    net = Networker(port, consts.PACKET_SIZE) # create networking socket
    cam = CameraFeed(cam_id=consts.CAMERA_ID) # create camera handler
    hardware = HardwareManager(simulated_hardware)

    # register connect loop packet
    net.register_listener(packets.CONNECT, lambda addr, args: _connect(net, addr, args))

    # register kill packet
    net.register_listener(packets.STOP_SERVER, lambda addr, args: net.close())

    rov = Rov(cam, net, hardware)

    try:
        net.server() # start the server

        # motor init seq
        rov.motor_init_seq('left_front')
        rov.motor_init_seq('right_front')
        rov.motor_init_seq('left_top')
        rov.motor_init_seq('right_top')
        rov.motor_init_seq('left_back')
        rov.motor_init_seq('right_back')
        
        print("ready")
        while net.is_open(): # loops until the server is stopped
            rov.tick()
    except:
        pass

    rov.camera_running = False
    rov.hardware.cleanup()
    net.close()

    os.kill(os.getpid(), signal.SIGTERM) # is this bad? i almost guarantee it
        

def _connect(networker: Networker, addr: _Addr, *args):
    networker._remember_addr(addr, args)
    networker.send(packets.CONNECT_ACK)