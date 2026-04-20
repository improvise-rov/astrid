import typing
from src.common import rovmath

class Imu():
    """
    Placeholder class for an IMU driver
    """

    def __init__(self, i2c_addr: int) -> None:
        pass

    
    def gyro(self) -> rovmath.Vec:
        return (0, 0, 0) # yaw pitch roll
    
    def roll(self) -> float:
        return self.gyro()[2]

    
