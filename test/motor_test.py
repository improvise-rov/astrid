import typing
import time
from adafruit_servokit import ServoKit # we treat everything as a servo; even the brushless motors

def motor(i: ServoKit, address: int, throttle: float):
    i.continuous_servo[address].throttle = throttle

if __name__ == "__main__":
    interface = ServoKit(channels=16)
    t = 0.5
    motor(interface, 0, 0.0)
    while True:
        motor(interface, 0, t)
        print(t)
        time.sleep(0.01) # print and wait a bit
