from __future__ import annotations
import typing
import time
from src.common import rovmath
from src.common import consts

try:
    from adafruit_pca9685 import PCA9685
except:
    pass

class Motor():
    def __init__(self, 
                 address: int, 
                 neutral: int = consts.PWM_BLUEROBOTICS_ESC_NEUTRAL, 
                 forward: int = consts.PWM_BLUEROBOTICS_ESC_FORWARD,
                 reverse: int = consts.PWM_BLUEROBOTICS_ESC_REVERSE,
                 bidirectional: bool = True,
                 flipped: bool = False) -> None:
        self.address = address
        self.neutral = neutral
        self.forward = forward
        self.reverse = reverse
        self.bidirectional = bidirectional
        self.flipped = flipped

        self._arm: typing.Callable[[PCA9685, bool, Motor], None] | None = None

        self._throttle = 0.0

    def set_throttle(self, interface: PCA9685, simulated: bool, power: float):
        if self.bidirectional:
            power = rovmath.clamp(-1.0, 1.0, power)
        else:
            power = rovmath.clamp(0.0, 1.0, power)

        if self.flipped:
            power = -power

        if power != self._throttle:
            self._throttle = power

            if simulated: # make sure we arent simulating
                return
        
            #
            interface.channels[self.address].duty_cycle = rovmath.calc_motor_dutycycle(self.reverse, self.neutral, self.forward, self.bidirectional, self._throttle)

    def set_dc(self, interface: PCA9685, simulated: bool, dc: int):
        interface.channels[self.address].duty_cycle = dc


    def get_throttle(self) -> float:
        return self._throttle
    
    def arm(self, interface: PCA9685, simulated: bool):
        if self._arm != None: 
            self._arm(interface, simulated, self)
        else:
            self.set_throttle(interface, simulated, 0.0)

    @staticmethod
    def esc_bluerobotics(address: int, reverse: bool = False) -> Motor:
        mot = Motor(address, flipped=reverse)
        # default arm behaviour works
        return mot
    
    @staticmethod
    def esc_4in1(address: int) -> Motor:
        mot = Motor(address, neutral=consts.PWM_4IN1_ESC_NEUTRAL, forward=consts.PWM_4IN1_ESC_FORWARD, reverse=0, bidirectional=False)
        def armer(i: PCA9685, s: bool, m: Motor):
            i.channels[m.address].duty_cycle = 205
            time.sleep(3)
            i.channels[m.address].duty_cycle = 410
        mot._arm = armer
        return mot
    