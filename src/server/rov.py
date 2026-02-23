import typing
import threading
import time
import struct
from src.common import packets
from src.common import consts
from src.common.network import Netsock
from src.common.rovmath import RovMath
from src.server.hardware import HardwareManager, _Motor, _Servo
from src.server.camera import CameraFeed


class Rov():
    """
    General "orchestrator" class for the entire ROV control system.
    """

    TARGET_ROLL: float = 0.0
    ROLL_CORRECTION: float = 0.01

    def __init__(self, cam: CameraFeed, net: Netsock, hardware: HardwareManager) -> None:
        self.cam = cam
        self.net = net
        self.hardware = hardware

        # values
        self.net_motor_cache: dict[_Motor | _Servo, int] = {
            "left_front": 0,
            "right_front": 0,
            "left_top": 0,
            "right_top": 0,
            "left_back": 0,
            "right_back": 0,

            "camera_angle": 0,
            "tool_wrist": 0,
            "tool_grip": 0,
        }
        self.correction_enabled = False

        # register control packet
        net.add_packet_handler(packets.CONTROL, self.control_packet)
        
        # register correction packets
        net.add_packet_handler(packets.ENABLE_CORRECTION,  self.enable_correction)
        net.add_packet_handler(packets.DISABLE_CORRECTION, self.disable_correction)

        # start camera thread
        self.camera_running = True
        self.camera_thread = threading.Thread(name="Camera Thread", target=self._camera_thread_activity)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        # motor init seq
        self.motor_init_seq('left_front')
        self.motor_init_seq('right_front')
        self.motor_init_seq('left_top')
        self.motor_init_seq('right_top')
        self.motor_init_seq('left_back')
        self.motor_init_seq('right_back')

    def motor_init_seq(self, motor: _Motor):
        # needs to go high?
        self.hardware.set_motor_pulsewidth_range(motor)
        self.hardware.set_motor(motor, consts.MOTOR_THROTTLE_POSITIVE)


    def tick(self):

        lf = self.hardware.decode_motor_byte(self.net_motor_cache['left_front'])
        rf = self.hardware.decode_motor_byte(self.net_motor_cache['right_front'])
        lt = self.hardware.decode_motor_byte(self.net_motor_cache['left_top'])
        rt = self.hardware.decode_motor_byte(self.net_motor_cache['right_top'])
        lb = self.hardware.decode_motor_byte(self.net_motor_cache['left_back'])
        rb = self.hardware.decode_motor_byte(self.net_motor_cache['right_back'])

        # calculate correction ; PID?? honestly i have no idea if this works
        if self.correction_enabled:
            yaw, pitch, roll = self.hardware.get_gyroscope()
            
            # roll
            roll_diff = roll - Rov.TARGET_ROLL
            if   roll_diff > 0: # roll is less than 0, (from back?) left needs up and right needs down
                lt +=  Rov.ROLL_CORRECTION * roll_diff
                rt += -Rov.ROLL_CORRECTION * roll_diff
            elif roll_diff < 0:
                # roll is greater than 0, (from back?) left needs down and right needs up
                lt += -Rov.ROLL_CORRECTION * roll_diff
                rt +=  Rov.ROLL_CORRECTION * roll_diff



        # set motors
        self.hardware.set_motor('left_front',   lf)
        self.hardware.set_motor('right_front',  rf)
        self.hardware.set_motor('left_top',     lt)
        self.hardware.set_motor('right_top',    rt)
        self.hardware.set_motor('left_back',    lb)
        self.hardware.set_motor('right_back',   rb)

        self.hardware.set_servo('camera_angle', self.net_motor_cache['camera_angle'])
        self.hardware.set_servo('tool_wrist', self.net_motor_cache['tool_wrist'])
        self.hardware.set_servo('tool_grip', self.net_motor_cache['tool_grip'])

        # print if simulated
        #if self.hardware.simulated:
        #    self.hardware.print_states()


    def _camera_thread_activity(self):
        while self.camera_running: # loops until the client disconnects!
            if self.net.is_open():
                frame = self.cam.capture() # get frame from camera
                self.net.send(packets.CAMERA, frame) # send the camera frame down socket
                time.sleep(1/60) # try and keep camera at 60 hz (this is not really acccurate, as it takes time to do everything. but its approximate enough.)

    def enable_correction(self, id: int, data: bytes, args: tuple):
        self.correction_enabled = True

    def disable_correction(self, id: int, data: bytes, args: tuple):
        self.correction_enabled = False

    def control_packet(self, id: int, data: bytes, args: tuple):
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


        self.net_motor_cache['left_front'] = lf    
        self.net_motor_cache['right_front'] = rf    
        self.net_motor_cache['left_top'] = lt    
        self.net_motor_cache['right_top'] = rt    
        self.net_motor_cache['left_back'] = lb    
        self.net_motor_cache['right_back'] = rb

        self.net_motor_cache['camera_angle'] = ca
        self.net_motor_cache['tool_wrist'] = tw
        self.net_motor_cache['tool_grip'] = tg