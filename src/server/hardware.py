NO_SERVOKIT: bool = False

import typing
try:
    import busio
    import board
    from adafruit_pca9685 import PCA9685 # we treat everything as a servo; even the brushless motors
except:
    print("** NO SERVOKIT LIB FOUND!! **")
    NO_SERVOKIT = True
from src.server import imu
from src.common import consts
from src.common.rovmath import RovMath

type _Motor = typing.Literal[
        'left_front', 'right_front',
        'left_top', 'right_top',
        'left_back', 'right_back'
        ]
    
type _Servo = typing.Literal[
    'camera_angle', 'tool_wrist', 'tool_grip'
]

class HardwareManager():
    """
    Manage the hardware pins of the Pi.
    """
    ADDRESSES: dict[_Motor | _Servo, int] = {
        'left_front': consts.ADDRESS_ESC_MOTOR_FRONT_LEFT,
        'right_front': consts.ADDRESS_ESC_MOTOR_FRONT_RIGHT,
        'left_top': consts.ADDRESS_ESC_MOTOR_TOP_LEFT,
        'right_top': consts.ADDRESS_ESC_MOTOR_TOP_RIGHT,
        'left_back': consts.ADDRESS_ESC_MOTOR_BACK_LEFT,
        'right_back': consts.ADDRESS_ESC_MOTOR_BACK_RIGHT,

        'camera_angle': consts.ADDRESS_SERVO_CAMERA_ANGLE,
        'tool_wrist': consts.ADDRESS_SERVO_CLAW_WRIST,
        'tool_grip': consts.ADDRESS_SERVO_CLAW_GRIP,
    }


    def __init__(self, simulated: bool = False) -> None:
        self.simulated = simulated
        if not self.simulated and not NO_SERVOKIT:
            self.i2c_bus = busio.I2C(board.SCL, board.SDA) # type: ignore
            self.motor_interface = PCA9685(self.i2c_bus) # type: ignore # warning normally because ServoKit might not exist
            self.imu = imu.Imu(consts.IMU_I2C_ADDRESS)

            self.motor_interface.frequency = consts.ESC_PWM_FREQUENCY

            

        self.motor_caches: dict[_Motor | _Servo, float] = {}

    def get_gyroscope(self) -> RovMath.Vec:
        if self.simulated:
            return (0, 0, 0)
        #          (yaw, pitch, roll)
        
        # 
        # rotation around x axis (forward back) -> roll
        # rotation around y axis (left right) -> pitch
        # rotation around z axis (up down) -> yaw
        #
        # https://en.wikipedia.org/wiki/Aircraft_principal_axes
        #
        
        return self.imu.gyro()


    def set_motor(self, motor: _Motor, throttle: float):
        throttle = RovMath.clamp(-1.0, 1.0, throttle)

        self.motor_caches[motor] = throttle

        address = HardwareManager.ADDRESSES[motor]

        if self.simulated: # make sure we arent simulating
            return
        
        # 
        self.motor_interface.channels[address].duty_cycle = RovMath.calc_motor_dutycycle(throttle)

    def set_servo(self, servo: _Servo, byte: int):
        byte = RovMath.clamp(0, 180, byte)

        self.motor_caches[servo] = byte

        address = HardwareManager.ADDRESSES[servo]

        if self.simulated: # make sure we arent simulating
            return
        
        # since the range for this is 0..180 which is between 0..255 i can just encode the value directly
        #self.motor_interface.servo[address].angle = byte


    def print_states(self):
        print(
            self.motor_caches.get('left_front', -1),
            self.motor_caches.get('right_front', -1),
            self.motor_caches.get('left_top', -1),
            self.motor_caches.get('right_top', -1),
            self.motor_caches.get('left_back', -1),
            self.motor_caches.get('right_back', -1),
            self.motor_caches.get('camera_angle', -1),
            self.motor_caches.get('tool_wrist', -1),
            self.motor_caches.get('tool_grip', -1),
            )  
        
    def cleanup(self):
        if self.simulated:
            return
        
        pass
        

