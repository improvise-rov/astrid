
from src.server.camera import CameraFeed
from src.server.gpio import GpioManager
from src.common.network import Netsock
from src.common import packets
from src.common import consts
import time
import struct
   
    

def server_main(ip: str, port: int, simulated_gpio: bool):
    """
    Main Entrypoint for the server.
    """

    if simulated_gpio:
        print("(simulating gpio)")

    net = Netsock(ip, port) # create networking socket
    cam = CameraFeed(cam_id=consts.CAMERA_ID) # create camera handler
    gpio = GpioManager(simulated_gpio)

    # register control packet handler; 
    # this tells the networking socket's processing thread to run _recv_control 
    # whenever a new PACKET_CONTROL packet is received
    net.add_packet_handler(packets.PACKET_CONTROL, _recv_control, gpio)

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
    gpio: GpioManager = args[0]

    lf, rf, lt, rt, lb, rb, ca, tw, tg = struct.unpack(packets.FORMAT_PACKET_CONTROL, data)


    gpio.set_motor('left_front', lf)
    gpio.set_motor('right_front', rf)
    gpio.set_motor('left_top', lt)
    gpio.set_motor('right_top', rt)
    gpio.set_motor('left_back', lb)
    gpio.set_motor('right_back', rb)

    gpio.set_servo('camera_angle', ca)
    gpio.set_servo('tool_wrist', tw)
    gpio.set_servo('tool_grip', tg)

    if gpio.simulated:
        gpio.print_states()