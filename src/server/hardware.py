import typing
from adafruit_servokit import ServoKit # we treat everything as a servo; even the brushless motors
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
        if not self.simulated:
            self.interface = ServoKit(channels=consts.SERVOBOARD_CHANNEL_COUNT)

        self.registers: dict[str, int] = {} # technically THESE arent registers, but it makes the most sense for the analogy im going for


    def set_motor(self, motor: _Motor, byte: int):
        self.registers[motor] = byte

        address = HardwareManager.ADDRESSES[motor]

        if self.simulated: # make sure we arent simulating
            return
        
        # 
        self.interface.continuous_servo[address].throttle = RovMath.map(
                consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE,
                consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL,
                consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD,
                byte,
                consts.MOTOR_THROTTLE_NEGATIVE,
                consts.MOTOR_THROTTLE_NEUTRAL,
                consts.MOTOR_THROTTLE_POSITIVE
            )

    def set_servo(self, servo: _Servo, byte: int):
        self.registers[servo] = byte

        address = HardwareManager.ADDRESSES[servo]

        if self.simulated: # make sure we arent simulating
            return
        
        # since the range for this is 0..180 which is between 0..255 i can just encode the value directly
        self.interface.servo[address].angle = byte


    def print_states(self):
        print(
            self.registers.get('left_front', -1),
            self.registers.get('right_front', -1),
            self.registers.get('left_top', -1),
            self.registers.get('right_top', -1),
            self.registers.get('left_back', -1),
            self.registers.get('right_back', -1),
            self.registers.get('camera_angle', -1),
            self.registers.get('tool_wrist', -1),
            self.registers.get('tool_grip', -1),
            )  
        

