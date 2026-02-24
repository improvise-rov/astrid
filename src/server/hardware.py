NO_SERVOKIT: bool = False

import typing
try:
    from adafruit_servokit import ServoKit # we treat everything as a servo; even the brushless motors
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
            self.motor_interface = ServoKit(channels=consts.SERVOBOARD_CHANNEL_COUNT) # type: ignore # warning normally because ServoKit might not exist
            self.imu = imu.Imu(consts.IMU_I2C_ADDRESS)

        self.motor_registers: dict[_Motor | _Servo, float] = {} # technically THESE arent registers, but it makes the most sense for the analogy im going for

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
    
    def set_motor_pulsewidth_range(self, motor: _Motor):
        if self.simulated:
            return
        address = HardwareManager.ADDRESSES[motor]
        self.motor_interface.continuous_servo[address].set_pulse_width_range(consts.PWM_REVERSE_ESC_MICROSECONDS, consts.PWM_FORWARD_ESC_MICROSECONDS)

    def set_servo_pulsewidth_range(self, servo: _Servo):
        if self.simulated:
            return
        address = HardwareManager.ADDRESSES[servo]
        self.motor_interface.servo[address].set_pulse_width_range(consts.PWM_SERVO_MINIMUM, consts.PWM_SERVO_MAXIMUM)


    def set_motor(self, motor: _Motor, throttle: float):
        throttle = RovMath.clamp(-1.0, 1.0, throttle)

        self.motor_registers[motor] = throttle

        address = HardwareManager.ADDRESSES[motor]

        if self.simulated: # make sure we arent simulating
            return
        
        # 
        self.motor_interface.continuous_servo[address].throttle = throttle

    def set_servo(self, servo: _Servo, byte: int):
        byte = RovMath.clamp(0, 180, byte)

        self.motor_registers[servo] = byte

        address = HardwareManager.ADDRESSES[servo]

        if self.simulated: # make sure we arent simulating
            return
        
        # since the range for this is 0..180 which is between 0..255 i can just encode the value directly
        self.motor_interface.servo[address].angle = byte

    def set_motor_bypass(self, motor: _Motor, throttle: float):
        """
        hardcoded alternative to set_motor where i manually calculate the duty cycle. just in case. i shouldnt need to use this.
        """
        throttle = RovMath.clamp(-1.0, 1.0, throttle)

        self.motor_registers[motor] = throttle

        address = HardwareManager.ADDRESSES[motor]

        if self.simulated: # make sure we arent simulating
            return
        
        # set pulsewidth
        pulsewidth = RovMath.map(consts.MOTOR_THROTTLE_NEGATIVE, consts.MOTOR_THROTTLE_NEUTRAL, consts.MOTOR_THROTTLE_POSITIVE, 
                                 throttle,
                                 consts.PWM_REVERSE_ESC_MICROSECONDS, consts.PWM_INITIALISE_ESC_MICROSECONDS, consts.PWM_FORWARD_ESC_MICROSECONDS)
        self.motor_interface.servo[address]._pwm.duty_cycle = pulsewidth / 200 # at 50hz: dutycycle = pulsewidth/200

    def print_states(self):
        print(
            self.motor_registers.get('left_front', -1),
            self.motor_registers.get('right_front', -1),
            self.motor_registers.get('left_top', -1),
            self.motor_registers.get('right_top', -1),
            self.motor_registers.get('left_back', -1),
            self.motor_registers.get('right_back', -1),
            self.motor_registers.get('camera_angle', -1),
            self.motor_registers.get('tool_wrist', -1),
            self.motor_registers.get('tool_grip', -1),
            )  
        

