import typing
from src.common.rovmath import RovMath

class Imu():
    """
    Placeholder class for an IMU driver
    """

    def __init__(self, i2c_addr: int) -> None:
        pass

    
    def gyro(self) -> RovMath.Vec:
        return (0, 0, 0) # yaw pitch roll

    
