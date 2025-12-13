from src.common import consts

class RovMath():
    @staticmethod
    def motor_to_byte(speed: float) -> int:
        speed = RovMath.clamp(-1.0, 1.0, speed)
        return RovMath.map(
            -1.0, 0.0, 1.0, speed,
            consts.ESC_BYTE_MOTOR_SPEED_FULL_REVERSE,
            consts.ESC_BYTE_MOTOR_SPEED_NEUTRAL,
            consts.ESC_BYTE_MOTOR_SPEED_FULL_FORWARD,
        )

    @staticmethod
    def servo_angle_to_byte(angle: float) -> int:
        angle = RovMath.clamp(-1.0, 1.0, angle)
        return RovMath.map(
            -1.0, 0.0, 1.0, angle,
            consts.SERVO_BYTE_COUNTER_CLOCKWISE,
            consts.SERVO_BYTE_CENTERED,
            consts.SERVO_BYTE_CLOCKWISE,
        )
    
    @staticmethod
    def clamp(low: int | float, high: int | float, v: int | float) -> int | float:
        if v > high:
            return high
        elif v < low:
            return low
        else:
            return v

    @staticmethod
    def map(low: int | float, zero: int | float, high: int | float, map: int | float, target_low: int, target_zero: int, target_high: int) -> int:
        
        if map == zero:
            return target_zero
        
        delta = (map - low) / (high - low)
        value = int(target_low + delta * (target_high - target_low))

        return int(RovMath.clamp(target_low, target_high, value))