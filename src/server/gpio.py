import pigpio
import typing
from src.common import consts
from src.common.rovmath import RovMath

class GpioManager():

    type _Motor = typing.Literal[
        'left_front', 'right_front',
        'left_top', 'right_top',
        'left_back', 'right_back'
        ]
    
    type _Servo = typing.Literal[
        'camera_angle', 'tool_wrist', 'tool_grip'
    ]
    
    PINS: dict[_Motor | _Servo, int] = {
        'left_front': consts.PIN_ESC_MOTOR_FRONT_LEFT,
        'right_front': consts.PIN_ESC_MOTOR_FRONT_RIGHT,
        'left_top': consts.PIN_ESC_MOTOR_TOP_LEFT,
        'right_top': consts.PIN_ESC_MOTOR_TOP_RIGHT,
        'left_back': consts.PIN_ESC_MOTOR_BACK_LEFT,
        'right_back': consts.PIN_ESC_MOTOR_BACK_RIGHT,

        'camera_angle': consts.PIN_SERVO_CAMERA_ANGLE,
        'tool_wrist': consts.PIN_SERVO_CLAW_WRIST,
        'tool_grip': consts.PIN_SERVO_CLAW_GRIP,
    }

    def __init__(self, simulated: bool = False) -> None:
        self.simulated = simulated
        if self.simulated:
            self.pi = pigpio.pi()

    def set_motor(self, motor: _Motor, byte: int):
        pin = GpioManager.PINS[motor]
        self._set_pin(
            pin, RovMath.map(
                consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE,
                consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL,
                consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD,
                byte,
                consts.PWM_REVERSE_ESC_MICROSECONDS,
                consts.PWM_INITIALISE_ESC_MICROSECONDS,
                consts.PWM_FORWARD_ESC_MICROSECONDS,
            )
        )

    def set_servo(self, servo: _Servo, byte: int):
        pin = GpioManager.PINS[servo]
        self._set_pin(
            pin, RovMath.map(
                consts.SERVO_BYTE_COUNTER_CLOCKWISE,
                consts.SERVO_BYTE_CENTERED,
                consts.SERVO_BYTE_CLOCKWISE,
                byte,
                consts.PWM_SERVO_MINIMUM,
                consts.PWM_SERVO_NEUTRAL,
                consts.PWM_SERVO_MAXIMUM,
            )
        )

    
        

    def _set_pin(self, pin: int, microseconds: int):
        if self.simulated:
            return
        self.pi.set_servo_pulsewidth(pin, microseconds)


