
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

    if simulated_hardware: # flag that is used in many places that basically says not to actually do anything with the hardware
        print("(simulating hardware)")

    net = Networker(target_ip, target_port, port, consts.PACKET_SIZE) # create networking socket
    net.start() # start the networker
    cam = CameraFeed(cam_id=consts.CAMERA_ID) # create camera handler
    hardware = HardwareManager(simulated_hardware)


    # register kill packet
    net.register_listener(packets.KILL, lambda addr, args: net.close())

    rov = Rov(cam, net, hardware)

    try:

        rov.arm()
        
        print("ready")
        net.build_packet(packets.REQ_SYNC_CAMERA)

        dt = 0.0
        last_frame_time = 0.0
        while net.is_open(): # loops until the networker is stopped
            last_frame_time = time.time()
            rov.tick(dt) # runs every process that the ROV continually does
            dt = time.time() - last_frame_time # how long did that take
    except Exception as e:
        print("oopsies!", e) # something went wrong, so we print the error. its not a great error catching system, but it works, i guess. multithreading is a nightmare

    rov.camera_running = False # STOP RECORDING ME!!!11!
    rov.hardware.cleanup() # cleanup hardware stuff
    net.close() # close the networker

    os.kill(os.getpid(), signal.SIGTERM) # is this bad? i almost guarantee it
    # getpid() returns the process id of this program, i.e. how the OS identifies the program internally