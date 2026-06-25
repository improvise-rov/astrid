NO_SERVOKIT: bool = False

try:
    import busio
    import board
    from adafruit_pca9685 import PCA9685 # we treat everything as a servo; even the brushless motors
except:
    print("** NO SERVOKIT LIB FOUND!! **")
    NO_SERVOKIT = True
from src.rov import imu
from src.rov import motor
from src.common import consts
from src.common import types
from src.common import rovmath



class HardwareManager():
    """
    Manage the hardware pins of the Pi.
    """
    ADDRESSES: dict[types._ServoKey, int] = {

        'camera_angle': consts.ADDRESS_SERVO_CAMERA_ANGLE,
        'tool_ver': consts.ADDRESS_SERVO_TOOL_VER,
        'tool_hor': consts.ADDRESS_SERVO_TOOL_HOR,
    }


    def __init__(self, simulated: bool = False) -> None:
        self.simulated = simulated
        if not self.simulated and not NO_SERVOKIT:
            self.i2c_bus = busio.I2C(board.SCL, board.SDA) # type: ignore
            self.motor_interface: PCA9685 = PCA9685(self.i2c_bus) # type: ignore # warning normally because ServoKit might not exist
            
            self.imu = imu.Imu(consts.IMU_I2C_ADDRESS)
            self.stabiliser = rovmath.PIDController(0.0)

            self.motor_interface.frequency = consts.PWM_FREQUENCY
        else:
            self.motor_interface = None # type: ignore # just so its declared...
            

        self.motors: dict[types._MotorKey, motor.Motor] = {
            'left_front': motor.Motor.esc_bluerobotics(consts.ADDRESS_ESC_MOTOR_FRONT_LEFT,     reverse=False),
            'right_front': motor.Motor.esc_bluerobotics(consts.ADDRESS_ESC_MOTOR_FRONT_RIGHT,   reverse=False),
            'left_top': motor.Motor.esc_bluerobotics(consts.ADDRESS_ESC_MOTOR_TOP_LEFT,         reverse=True),
            'right_top': motor.Motor.esc_bluerobotics(consts.ADDRESS_ESC_MOTOR_TOP_RIGHT,       reverse=True),
            'left_back': motor.Motor.esc_bluerobotics(consts.ADDRESS_ESC_MOTOR_BACK_LEFT,       reverse=True),
            'right_back': motor.Motor.esc_bluerobotics(consts.ADDRESS_ESC_MOTOR_BACK_RIGHT,     reverse=False)
        }
        self.servos: dict[types._ServoKey, int] = {}

    def get_gyroscope(self) -> rovmath.Vec:
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


    def set_motor(self, motor: types._MotorKey, throttle: float):
        self.motors[motor].set_throttle(self.motor_interface, self.simulated, throttle)


    def set_servo(self, servo: types._ServoKey, byte: int, camera: bool = True):
        if camera:
            byte = rovmath.clamp(0, 180, byte)
        else:
            byte = rovmath.clamp(consts.TOOL_LOW_LIMIT, consts.TOOL_HIGH_LIMIT, byte)

        self.servos[servo] = byte

        address = HardwareManager.ADDRESSES[servo]

        if self.simulated: # make sure we arent simulating
            return
        
        # since the range for this is 0..180 which is between 0..255 i can just encode the value directly
        self.motor_interface.channels[address].duty_cycle = rovmath.calc_servo_dutycycle(byte, camera)


    def print_states(self):
        print(
            "fl", rovmath.inv_calc_motor_dutycycle(self.motors['left_front']   .get_duty_cycle()),
            "fr", rovmath.inv_calc_motor_dutycycle(self.motors['right_front']  .get_duty_cycle()),
            "tl", rovmath.inv_calc_motor_dutycycle(self.motors['left_top']     .get_duty_cycle()),
            "tr", rovmath.inv_calc_motor_dutycycle(self.motors['right_top']    .get_duty_cycle()),
            "bl", rovmath.inv_calc_motor_dutycycle(self.motors['left_back']    .get_duty_cycle()),
            "br", rovmath.inv_calc_motor_dutycycle(self.motors['right_back']   .get_duty_cycle()),
            )  
        
    def cleanup(self):
        if self.simulated:
            return
        
        self.set_motor('left_front', 0.0)
        self.set_motor('right_front', 0.0)
        self.set_motor('left_top', 0.0)
        self.set_motor('right_top', 0.0)
        self.set_motor('left_back', 0.0)
        self.set_motor('left_back', 0.0)
        

