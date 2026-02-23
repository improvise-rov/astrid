from src.common import consts


class RovMath():
    type Number = int | float
    type Vec = tuple[Number, Number, Number]

    

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
    def clamp[T: Number](low: T, high: T, v: T) -> T:
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