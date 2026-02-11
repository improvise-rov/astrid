import typing
import board
from adafruit_bus_device import i2c_device

class Driver():
    type byte = int

    @staticmethod
    def _assert_byte(byte: byte):
        if byte < 0 or byte > 255:
            raise ValueError("Byte must be in range 0..255, " + str(byte) + " is not")
        

    @staticmethod
    def write(address: byte, byte: byte):
        Driver._assert_byte(address)
        Driver._assert_byte(byte)
        #i2c_device.I2CDevice(board.I2C(), address).write()
        pass

    @staticmethod
    def read(address: byte) -> byte:
        Driver._assert_byte(address)
        pass