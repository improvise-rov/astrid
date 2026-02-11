import typing
from adafruit_servokit import ServoKit # we treat everything as a servo; even the brushless motors

def servo(i: ServoKit, address: int, angle: int):
    i.servo[address].angle = angle

if __name__ == "__main__":
    interface = ServoKit(channels=16)
    ang = 0
    delta = 1
    while True:
        servo(interface, 0, ang)
        ang += delta
        if ang >= 180 or ang <= 0:
            delta = -delta
