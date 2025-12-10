import typing
from gpiozero import PWMOutputDevice
from src.common import consts
from src.common.rovmath import RovMath

class GpioManager():

    type _MotorKey = typing.Literal[
        'left_front', 'right_front',
        'left_top', 'right_top',
        'left_back', 'right_back'
        ]
    
    type _ServoKey = typing.Literal[
        'camera_angle', 'tool_wrist', 'tool_grip'
    ]
    

    def __init__(self, simulated: bool = False) -> None:
        self.simulated = simulated

        self.pins: dict[GpioManager._MotorKey | GpioManager._ServoKey, PWMOutputDevice] = {}

        if not self.simulated:
            self.pins = { # i just want to outputt PWM signals
                'left_front': PWMOutputDevice(consts.PIN_ESC_MOTOR_FRONT_LEFT),
                'right_front': PWMOutputDevice(consts.PIN_ESC_MOTOR_FRONT_RIGHT),
                'left_top': PWMOutputDevice(consts.PIN_ESC_MOTOR_TOP_LEFT),
                'right_top': PWMOutputDevice(consts.PIN_ESC_MOTOR_TOP_RIGHT),
                'left_back': PWMOutputDevice(consts.PIN_ESC_MOTOR_BACK_LEFT),
                'right_back': PWMOutputDevice(consts.PIN_ESC_MOTOR_BACK_RIGHT),

                'camera_angle': PWMOutputDevice(consts.PIN_SERVO_CAMERA_ANGLE),
                'tool_wrist': PWMOutputDevice(consts.PIN_SERVO_CLAW_WRIST),
                'tool_grip': PWMOutputDevice(consts.PIN_SERVO_CLAW_GRIP),
            }

        self.pin_bytes: dict[GpioManager._MotorKey | GpioManager._ServoKey, int] = {}

    def set_motor(self, motor: _MotorKey, byte: int):
        self.pin_bytes[motor] = byte

        pin = self.pins[motor]
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

    def set_servo(self, servo: _ServoKey, byte: int):
        self.pin_bytes[servo] = byte

        pin = self.pins[servo]
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

    def print_states(self):
        print(
            self.pin_bytes.get('left_front', -1),
            self.pin_bytes.get('right_front', -1),
            self.pin_bytes.get('left_top', -1),
            self.pin_bytes.get('right_top', -1),
            self.pin_bytes.get('left_back', -1),
            self.pin_bytes.get('right_back', -1),
            self.pin_bytes.get('camera_angle', -1),
            self.pin_bytes.get('tool_wrist', -1),
            self.pin_bytes.get('tool_grip', -1),
            )  
        

    def _set_pin(self, pin: PWMOutputDevice, microseconds: int):
        if self.simulated:
            return
        
        # since i deal with the pulses in uS and gpiozero deals with it in Hz, i need to convert
        # frequency is the number of oscillations/cycles per second
        # which means frequency and time are inversely proportional
        # so f = 1/t when t is in seconds
        #   (hz) = 1e6 / (us)

        pin.frequency = 1_000_000 / microseconds


