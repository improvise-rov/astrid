from src.common import consts



type Number = int | float
type Vec = tuple[Number, Number, Number]

@staticmethod
def calc_motor_dutycycle(throttle: float) -> int:
    assert throttle >= -1.0 and throttle <= 1.0

    pulse =  map(
        -1.0, 0.0, 1.0,
        throttle,
        consts.PWM_ESC_REVERSE, consts.PWM_ESC_INITIALISE, consts.PWM_ESC_FORWARD
    )
    period = 1_000_000 / consts.PWM_FREQUENCY

    return int((pulse / period) * 0xFFFF)

@staticmethod
def calc_servo_dutycycle(angle: int, camera: bool) -> int:
    assert angle >= 0 and angle <= 180

    pulse =  map(
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
    angle = clamp(-1.0, 1.0, angle)
    return int(map(
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

    return clamp(target_low, target_high, value)

@staticmethod
def map_no_midpoint(low: Number, high: Number, map: Number, target_low: Number, target_high: Number) -> Number:
    delta = (map - low) / (high - low)
    value = target_low + delta * (target_high - target_low)

    return clamp(target_low, target_high, value)

@staticmethod
def move_toward(current: float, target: float, delta: float) -> float:
    if current == target:
        return target
    
    if current < target and current + delta > target:
        return target
    elif current > target and current - delta < target:
        return target

    if current > target:
        return current - delta
    else:
        return current + delta