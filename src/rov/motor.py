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
                 bidirectional: bool = True) -> None:
        self.address = address
        self.neutral = neutral
        self.forward = forward
        self.reverse = reverse
        self.bidirectional = bidirectional

        self._arm: typing.Callable[[PCA9685, bool, Motor], None] = lambda interface, sim, mot: None

        self._throttle = 0.0

    def set_throttle(self, interface: PCA9685, simulated: bool, power: float):
        if self.bidirectional:
            power = rovmath.clamp(-1.0, 1.0, power)
        else:
            power = rovmath.clamp(0.0, 1.0, power)

        if power != self._throttle:
            self._throttle = power

            if simulated: # make sure we arent simulating
                return
        
            #
            interface.channels[self.address].duty_cycle = rovmath.calc_motor_dutycycle(self.reverse, self.neutral, self.forward, self.bidirectional, self._throttle)

    def get_throttle(self) -> float:
        return self._throttle
    
    def arm(self, interface: PCA9685, simulated: bool):
        self._arm(interface, simulated, self)

    @staticmethod
    def esc_bluerobotics(address: int) -> Motor:
        mot = Motor(address)
        def _arm(interface: PCA9685, simulated: bool, mot: Motor):
            # neutral
            mot.set_throttle(interface, simulated, 0.0)
        mot._arm = _arm
        return mot
    
    @staticmethod
    def esc_4in1(address: int) -> Motor:
        mot = Motor(address, neutral=consts.PWM_4IN1_ESC_NEUTRAL, forward=consts.PWM_4IN1_ESC_FORWARD, reverse=0, bidirectional=False)
        def _arm(interface: PCA9685, simulated: bool, mot: Motor):
            # calibrate?
            #mot.set_throttle(interface, simulated, 1.0)
            #time.sleep(0.1)
            mot.set_throttle(interface, simulated, 0.0)
        mot._arm = _arm
        return mot
    