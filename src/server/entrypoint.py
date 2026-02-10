
from src.server.camera import CameraFeed
from src.server.hardware import HardwareManager
from src.common.network import Netsock
from src.common import packets
from src.common import consts
import time
import struct
   
    

def server_main(ip: str, port: int, simulated_hardware: bool):
    """
    Main Entrypoint for the server.
    """

    if simulated_hardware:
        print("(simulating hardware)")

    net = Netsock(ip, port) # create networking socket
    cam = CameraFeed(cam_id=consts.CAMERA_ID) # create camera handler
    hardware = HardwareManager(simulated_hardware)

    # register control packet handler; 
    # this tells the networking socket's processing thread to run _recv_control 
    # whenever a new PACKET_CONTROL packet is received
    net.add_packet_handler(packets.PACKET_CONTROL, _recv_control, hardware)

    net.start_server() # start the server (blocks until client connects)

    while net.is_open(): # blocks until the client disconnects!
        frame = cam.capture() # get frame from camera
        net.send(packets.PACKET_CAMERA, frame) # send the camera frame down socket
        time.sleep(1/60) # try and keep at 60 loops / second (this is not really acccurate, as it takes time to do everything. but its approximate enough.)

def _recv_control(id: int, data: bytes, args: tuple):
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
    hardware: HardwareManager = args[0]

    lf, rf, lt, rt, lb, rb, ca, tw, tg = struct.unpack(packets.FORMAT_PACKET_CONTROL, data)


    hardware.set_motor('left_front', lf)
    hardware.set_motor('right_front', rf)
    hardware.set_motor('left_top', lt)
    hardware.set_motor('right_top', rt)
    hardware.set_motor('left_back', lb)
    hardware.set_motor('right_back', rb)

    hardware.set_servo('camera_angle', ca)
    hardware.set_servo('tool_wrist', tw)
    hardware.set_servo('tool_grip', tg)

    if hardware.simulated:
        hardware.print_states()