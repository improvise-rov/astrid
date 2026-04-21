
from src.rov.camera import CameraFeed
from src.rov.hardware import HardwareManager
from src.rov.rov import Rov
from src.common.net.worker import Networker, _Addr
from src.common.net import packets
from src.common import consts
import os, signal, time

def rov_main(target_ip: str, target_port: int, simulated_hardware: bool, port: int):
    """
    Main Entrypoint for the ROV.
    """

    if simulated_hardware:
        print("(simulating hardware)")

    net = Networker(target_ip, target_port, port, consts.PACKET_SIZE) # create networking socket
    net.start() # start the networker
    cam = CameraFeed(cam_id=consts.CAMERA_ID) # create camera handler
    hardware = HardwareManager(simulated_hardware)


    # register kill packet
    net.register_listener(packets.KILL, lambda addr, args: net.close())

    rov = Rov(cam, net, hardware)

    try:

        # motor init seq
        rov.motor_init_seq('left_front')
        rov.motor_init_seq('right_front')
        rov.motor_init_seq('left_top')
        rov.motor_init_seq('right_top')
        rov.motor_init_seq('left_back')
        rov.motor_init_seq('right_back')
        
        print("ready")
        dt = 0.0
        last_frame_time = 0.0
        while net.is_open(): # loops until the networker is stopped
            last_frame_time = time.time()
            rov.tick(dt)
            dt = time.time() - last_frame_time
    except:
        pass

    rov.camera_running = False
    rov.hardware.cleanup()
    net.close()

    os.kill(os.getpid(), signal.SIGTERM) # is this bad? i almost guarantee it