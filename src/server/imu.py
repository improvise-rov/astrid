import typing
import board
from common import consts
from adafruit_bus_device import i2c_device

class Imu():
    """
    Custom Driver for IMU (Inertial Measurement Unit) device. Quite abstract, at time of writing i dont know what kind of chip
    we'll be using. It also allows for customisation in case of a different device.

    Written with [MPU6050](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf) as a reference.
    

    Constant values can be found in `common/consts.py`.
    """

    def __init__(self) -> None:
        self._i2c = i2c_device.I2CDevice(board.I2C(), consts.IMU_I2C_ADDRESS)

        self._buffer = bytearray(consts.IMU_I2C_PAYLOAD_SIZE)

    
    def _read_payload(self):
        self._i2c.readinto(self._buffer)

    
