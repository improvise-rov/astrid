from src.common import consts


class RovMath():
    type Number = int | float
    type Vec = tuple[Number, Number, Number]
    
    @staticmethod
    def calc_motor_dutycycle(throttle: float) -> int:
        assert throttle >= -1.0 and throttle <= 1.0

        pulse =  RovMath.map(
            -1.0, 0.0, 1.0,
            throttle,
            consts.PWM_ESC_REVERSE, consts.PWM_ESC_INITIALISE, consts.PWM_ESC_FORWARD
        )
        period = 1_000_000 / consts.PWM_FREQUENCY

        return int((pulse / period) * 0xFFFF)
    
    @staticmethod
    def calc_servo_dutycycle(angle: int, camera: bool) -> int:
        assert angle >= 0 and angle <= 180

        pulse =  RovMath.map(
            0, 90, 180,
            angle,
            consts.PWM_CAMERA_SERVO_MINIMUM if camera else consts.PWM_TOOL_SERVO_MINIMUM, 
            consts.PWM_CAMERA_SERVO_NEUTRAL if camera else consts.PWM_TOOL_SERVO_NEUTRAL, 
            consts.PWM_CAMERA_SERVO_MAXIMUM if camera else consts.PWM_TOOL_SERVO_MAXIMUM
        )
        period = 1_000_000 / consts.PWM_FREQUENCY

        return int((pulse / period) * 0xFFFF)

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