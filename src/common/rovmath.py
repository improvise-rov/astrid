from src.common import consts

class RovMath():
    type _Number = int | float

    @staticmethod
    def servo_angle(angle: float) -> int:
        angle = RovMath.clamp(-1.0, 1.0, angle)
        return RovMath.map(
            -1.0, 0.0, 1.0, angle,
            consts.PWM_SERVO_MINIMUM,
            consts.PWM_SERVO_NEUTRAL,
            consts.PWM_SERVO_MAXIMUM,
        )
    
    @staticmethod
    def clamp[T: _Number](low: T, high: T, v: T) -> T:
        if v > high:
            return high
        elif v < low:
            return low
        else:
            return v

    @staticmethod
    def map(low: _Number, zero: _Number, high: _Number, map: _Number, target_low: int, target_zero: int, target_high: int) -> int:
        
        if map == zero:
            return target_zero

        delta = (map - low) / (high - low)
        value = int(target_low + delta * (target_high - target_low))

        return RovMath.clamp(target_low, target_high, value)