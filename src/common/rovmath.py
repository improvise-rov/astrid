from src.common import consts

type Number = int | float

class RovMath():
    @staticmethod
    def motor_to_byte(speed: float) -> int:
        speed = RovMath.clamp(-1.0, 1.0, speed)
        return int(RovMath.map(
            -1.0, 0.0, 1.0, speed,
            consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE,
            consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL,
            consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD,
        ))

    @staticmethod
    def servo_angle_to_byte(angle: float) -> int:
        angle = RovMath.clamp(-1.0, 1.0, angle)
        return int(RovMath.map(
            -1.0, 0.0, 1.0, angle,
            consts.SERVO_ANGLE_MIN,
            consts.SERVO_ANGLE_NEUTRAL,
            consts.SERVO_ANGLE_MAX,
        ))
    
    @staticmethod
    def clamp(low: Number, high: Number, v: Number) -> Number:
        if v > high:
            return high
        elif v < low:
            return low
        else:
            return v

    @staticmethod
    def map(low: Number, zero: Number, high: Number, map: Number, target_low: Number, target_zero: Number, target_high: Number) -> Number:
        
        if map == zero:
            return target_zero
        
        delta = (map - low) / (high - low)
        value = target_low + delta * (target_high - target_low)

        return RovMath.clamp(target_low, target_high, value)