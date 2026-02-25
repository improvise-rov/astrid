NO_SERVOKIT: bool = False

import typing
import RPi.GPIO as GPIO
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

            GPIO.setmode(GPIO.BCM) # broadcom pins
            GPIO.setup(consts.PIN_FRONT_LEFT_MOTOR, GPIO.OUT)
            GPIO.setup(consts.PIN_FRONT_RIGHT_MOTOR, GPIO.OUT)
            GPIO.setup(consts.PIN_TOP_LEFT_MOTOR, GPIO.OUT)
            GPIO.setup(consts.PIN_TOP_RIGHT_MOTOR, GPIO.OUT)
            GPIO.setup(consts.PIN_BACK_LEFT_MOTOR, GPIO.OUT)
            GPIO.setup(consts.PIN_BACK_RIGHT_MOTOR, GPIO.OUT)
            self.mots: dict[_Motor, GPIO.PWM] = {
                'left_front': GPIO.PWM(consts.PIN_FRONT_LEFT_MOTOR, consts.ESC_PWM_FREQUENCY),
                'right_front': GPIO.PWM(consts.PIN_FRONT_RIGHT_MOTOR, consts.ESC_PWM_FREQUENCY),
                'left_top': GPIO.PWM(consts.PIN_TOP_LEFT_MOTOR, consts.ESC_PWM_FREQUENCY),
                'right_top': GPIO.PWM(consts.PIN_TOP_RIGHT_MOTOR, consts.ESC_PWM_FREQUENCY),
                'left_back': GPIO.PWM(consts.PIN_BACK_LEFT_MOTOR, consts.ESC_PWM_FREQUENCY),
                'right_back': GPIO.PWM(consts.PIN_BACK_RIGHT_MOTOR, consts.ESC_PWM_FREQUENCY),
            }
            for pin in self.mots:
                self.mots[pin].start(RovMath.calc_motor_dutycycle(0))

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

        self.motor_caches[motor] = throttle

        address = HardwareManager.ADDRESSES[motor]

        if self.simulated: # make sure we arent simulating
            return
        
        # 
        self.motor_interface.continuous_servo[address].throttle = throttle

    def set_servo(self, servo: _Servo, byte: int):
        byte = RovMath.clamp(0, 180, byte)

        self.motor_caches[servo] = byte

        address = HardwareManager.ADDRESSES[servo]

        if self.simulated: # make sure we arent simulating
            return
        
        # since the range for this is 0..180 which is between 0..255 i can just encode the value directly
        self.motor_interface.servo[address].angle = byte

    def set_motor_bypass(self, motor: _Motor, pw: int):
        """
        hardcoded alternative to set_motor where i manually calculate the duty cycle. just in case. i shouldnt need to use this.
        """
        address = HardwareManager.ADDRESSES[motor]

        if self.simulated: # make sure we arent simulating
            return
        
        # set pulsewidth
        self.motor_interface.continuous_servo[address]._pwm_out.duty_cycle = pw / 200 # at 50hz: dutycycle = pulsewidth/200


    def set_motor_rpi(self, motor: _Motor, throttle: float):
        throttle = RovMath.clamp(-1.0, 1.0, throttle)
        if self.simulated: # make sure we arent simulating
            return
        self.mots[motor].ChangeDutyCycle(RovMath.calc_motor_dutycycle(throttle))

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
        
        for pin in self.mots:
            self.mots[pin].stop()
        GPIO.cleanup()
        

