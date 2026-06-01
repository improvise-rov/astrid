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
    ADDRESSES: dict[types._MotorKey | types._ServoKey, int] = {
        'left_front': consts.ADDRESS_ESC_MOTOR_FRONT_LEFT,
        'right_front': consts.ADDRESS_ESC_MOTOR_FRONT_RIGHT,
        'left_top': consts.ADDRESS_ESC_MOTOR_TOP_LEFT,
        'right_top': consts.ADDRESS_ESC_MOTOR_TOP_RIGHT,
        'left_back': consts.ADDRESS_ESC_MOTOR_BACK_LEFT,
        'right_back': consts.ADDRESS_ESC_MOTOR_BACK_RIGHT,

        'camera_angle': consts.ADDRESS_SERVO_CAMERA_ANGLE,
        'tool_ver': consts.ADDRESS_SERVO_TOOL_VER,
        'tool_hor': consts.ADDRESS_SERVO_TOOL_HOR,
    }


    def __init__(self, simulated: bool = False) -> None:
        self.simulated = simulated
        if not self.simulated and not NO_SERVOKIT:
            self.i2c_bus = busio.I2C(board.SCL, board.SDA) # type: ignore
            self.motor_interface = PCA9685(self.i2c_bus) # type: ignore # warning normally because ServoKit might not exist
            
            self.imu = imu.Imu(consts.IMU_I2C_ADDRESS)
            self.stabiliser = rovmath.PIDController(0.0)

            self.motor_interface.frequency = consts.PWM_FREQUENCY
            

        self.motors: dict[types._MotorKey, motor.Motor] = {

        }
        self.servos: dict[types._ServoKey, float] = {}

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
        byte = rovmath.clamp(0, 180, byte)

        self.servos[servo] = byte

        address = HardwareManager.ADDRESSES[servo]

        if self.simulated: # make sure we arent simulating
            return
        
        # since the range for this is 0..180 which is between 0..255 i can just encode the value directly
        self.motor_interface.channels[address].duty_cycle = rovmath.calc_servo_dutycycle(byte, camera)


    def print_states(self):
        print(
            self.motors['left_front'].get_throttle(),
            self.motors['right_front'].get_throttle(),
            self.motors['left_top'].get_throttle(),
            self.motors['right_top'].get_throttle(),
            self.motors['left_back'].get_throttle(),
            self.motors['right_back'].get_throttle(),
            self.servos.get('camera_angle', -1),
            self.servos.get('tool_ver', -1),
            self.servos.get('tool_hor', -1),
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
        

