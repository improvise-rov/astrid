import typing
import threading
import time
import struct
from src.common import consts
from src.common import types
from src.common import rovmath
from src.common.net import packets
from src.common.net.worker import Networker, _Addr
from src.rov.hardware import HardwareManager
from src.rov.camera import CameraFeed


class Rov():
    """
    General "orchestrator" class for the entire ROV control system.
    """

    def __init__(self, cam: CameraFeed, net: Networker, hardware: HardwareManager) -> None:
        self.cam = cam
        self.net = net
        self.hardware = hardware

        # values
        self.net_motor_cache: dict[types._MotorOrServo, rovmath.Number] = {
            "left_front": 0,
            "right_front": 0,
            "left_top": 0,
            "right_top": 0,
            "left_back": 0,
            "right_back": 0,

            "camera_angle": 0,
            "tool_ver": 0,
            "tool_hor": 0,
        }
        self.correction_enabled = False

        # register control packet
        net.register_listener(packets.CONTROL, self.control_packet)
        
        # register correction packets
        net.register_listener(packets.ENABLE_CORRECTION,  self.enable_correction)
        net.register_listener(packets.DISABLE_CORRECTION, self.disable_correction)

        # start camera thread
        self.camera_running = True
        self.camera_thread = threading.Thread(name="Camera Thread", target=self._camera_thread_activity)
        self.camera_thread.daemon = True
        self.camera_thread.start()

    def motor_init_seq(self, motor: types._Motor):
        # needs to go high?
        self.hardware.set_motor(motor, consts.PWM_ESC_INITIALISE)


    def tick(self, dt: float):

        lf = self.net_motor_cache['left_front']
        rf = self.net_motor_cache['right_front']
        lt = self.net_motor_cache['left_top']
        rt = self.net_motor_cache['right_top']
        lb = self.net_motor_cache['left_back']
        rb = self.net_motor_cache['right_back']

        # calculate
        if self.correction_enabled and not self.hardware.simulated:
            
            # roll
            correction = self.hardware.stabiliser.compute_modulation(self.hardware.imu.roll(), dt) * dt
            if   correction > 0: # roll is less than 0, (from back?) left needs up and right needs down
                lt +=  abs(correction)
                rt += -abs(correction)
            elif correction < 0:
                # roll is greater than 0, (from back?) left needs down and right needs up
                lt += -abs(correction)
                rt +=  abs(correction)



        # set motors
        self.hardware.set_motor('left_front',   lf)
        self.hardware.set_motor('right_front',  rf)
        self.hardware.set_motor('left_top',     lt)
        self.hardware.set_motor('right_top',    rt)
        self.hardware.set_motor('left_back',    lb)
        self.hardware.set_motor('right_back',   rb)

        self.hardware.set_servo('camera_angle', int(self.net_motor_cache['camera_angle']))
        self.hardware.set_servo('tool_ver',   int(self.net_motor_cache['tool_ver'] / 2), camera = False) # the tool gripper only actually needs to go 0..90, so i divide the range by 2 (because its transmitted as a number 0..180)
        self.hardware.set_servo('tool_hor',    int(self.net_motor_cache['tool_hor']), camera = False)

        # print if simulated
        if self.hardware.simulated:
            pass#self.hardware.print_states()


    def _camera_thread_activity(self):
        while self.camera_running: # loops until the client disconnects!
            if self.net.is_open():
                frame = self.cam.capture() # get frame from camera
                self.net.send(packets.CAMERA, frame) # send the camera frame down socket
                
                
    def enable_correction(self, addr: _Addr, args: ...):
        print("enabled correction")
        self.correction_enabled = True

    def disable_correction(self, addr: _Addr, args: ...):
        print("disabled correction")
        self.correction_enabled = False

    def control_packet(self, addr: _Addr, args: ...):
        """
        runs when the server receives information from the client about controls.

        this data, to reduce processing time, should not be validated (that should be done on the client)
        assume everything is always okay, and take numbers at face value.
        that is usually a terrible idea, but i dont care. its fine for this

        """

        left_front, right_front, left_top, right_top, left_back, right_back, camera_angle, tool_ver, tool_hor = args


        self.net_motor_cache['left_front'] = left_front    
        self.net_motor_cache['right_front'] = right_front    
        self.net_motor_cache['left_top'] = left_top    
        self.net_motor_cache['right_top'] = right_top    
        self.net_motor_cache['left_back'] = left_back    
        self.net_motor_cache['right_back'] = right_back

        self.net_motor_cache['camera_angle'] = camera_angle
        self.net_motor_cache['tool_ver'] = tool_ver
        self.net_motor_cache['tool_hor'] = tool_hor